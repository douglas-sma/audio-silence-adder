#!/usr/bin/env python3
"""
Agregador de Silencio - motor y CLI por argumentos.

Agrega silencio al inicio de archivos de audio preservando los metadatos
(incluidas las carátulas) y la calidad del audio.

Usa ffmpeg/ffprobe del sistema para el procesamiento y mutagen para
limpiar/reparar las etiquetas y las portadas.
"""

import argparse
import base64
import json
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import mutagen
    from mutagen.id3 import ID3, APIC
    from mutagen.mp4 import MP4, MP4Cover
    from mutagen.flac import FLAC, Picture
    from mutagen.oggvorbis import OggVorbis
    from mutagen.oggopus import OggOpus

    MUTAGEN_OK = True
except ImportError:  # pragma: no cover - depende del entorno
    MUTAGEN_OK = False


INPUT_DIR = Path("Input")
OUTPUT_DIR = Path("Output")

SUPPORTED_SUFFIXES = {
    ".mp3", ".wav", ".flac", ".ogg", ".oga", ".opus",
    ".m4a", ".mp4", ".aac", ".wma", ".aiff", ".aif",
}

FORMAT_CHOICES = ["original", "mp3", "m4a", "flac", "wav", "ogg", "opus"]

# Formatos donde mutagen puede incrustar/leer carátulas.
COVER_SUPPORTED = {"mp3", "m4a", "mp4", "flac", "ogg", "oga", "opus"}

# Etiquetas internas que inyecta ffmpeg / el contenedor y que no aportan nada.
_JUNK_VORBIS = {
    "major_brand", "minor_version", "compatible_brands",
    "encoder", "encoding", "encoder_settings", "lavf",
}
_JUNK_ID3 = {"TSSE", "TENC"}
_JUNK_MP4 = {"\xa9too", "\xa9enc"}

_SAMPLE_FMT_BITS = {
    "u8": 8, "u8p": 8,
    "s16": 16, "s16p": 16,
    "s32": 32, "s32p": 32,
    "flt": 32, "fltp": 32,
    "dbl": 64, "dblp": 64,
    "s64": 64, "s64p": 64,
}

_PCM_FOR_BITS = {
    8: "pcm_u8",
    16: "pcm_s16le",
    24: "pcm_s24le",
    32: "pcm_s32le",
    64: "pcm_s64le",
}

_LOSSLESS_CODECS = {"flac", "alac", "wmalossless", "wavpack", "ape", "tak"}


class AudioSilenceAdder:
    """Agrega silencio al inicio de un audio conservando formato y metadatos."""

    def __init__(self, input_dir=INPUT_DIR, output_dir=OUTPUT_DIR):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

    # ------------------------------------------------------------------ utils
    @staticmethod
    def _require_tools():
        for tool in ("ffmpeg", "ffprobe"):
            if shutil.which(tool) is None:
                raise RuntimeError(
                    f"No se encontró '{tool}'. Instálalo con: sudo apt install ffmpeg"
                )

    def ensure_dirs(self):
        """Crea Input/ y Output/ si no existen."""
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def list_input_files(self):
        """Devuelve los audios soportados que hay en Input/."""
        self.ensure_dirs()
        return sorted(
            p for p in self.input_dir.iterdir()
            if p.is_file()
            and not p.name.startswith(".")
            and p.suffix.lower() in SUPPORTED_SUFFIXES
        )

    # ------------------------------------------------------------- análisis
    def _probe(self, path):
        cmd = [
            "ffprobe", "-v", "error", "-print_format", "json",
            "-show_format", "-show_streams", str(path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "ffprobe falló")
        return json.loads(result.stdout)

    @staticmethod
    def _is_lossless(codec_name):
        return codec_name.startswith("pcm") or codec_name in _LOSSLESS_CODECS

    def analyze(self, path):
        """Analiza el archivo con ffprobe y devuelve un diccionario de propiedades."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"El archivo no existe: {path}")

        data = self._probe(path)
        audio = next(
            (s for s in data.get("streams", []) if s.get("codec_type") == "audio"),
            None,
        )
        if audio is None:
            raise ValueError(f"El archivo no contiene pista de audio: {path.name}")

        fmt = data.get("format", {})
        codec = audio.get("codec_name", "")

        raw_bits = audio.get("bits_per_raw_sample")
        if raw_bits and str(raw_bits).isdigit():
            bits = int(raw_bits)
        else:
            bits = _SAMPLE_FMT_BITS.get(audio.get("sample_fmt"))
        if not self._is_lossless(codec):
            bits = None  # no tiene sentido mostrar profundidad en formatos con pérdida

        bitrate = None
        for source in (audio.get("bit_rate"), fmt.get("bit_rate")):
            if source and str(source).isdigit() and int(source) > 0:
                bitrate = int(source)
                break

        tags = {}
        tags.update(fmt.get("tags") or {})
        tags.update(audio.get("tags") or {})
        real_tags = [k for k in tags if not self._is_junk_key(k)]

        cover = any(
            s.get("codec_type") == "video"
            and (s.get("disposition") or {}).get("attached_pic")
            for s in data.get("streams", [])
        )

        return {
            "sufijo": path.suffix.lower(),
            "formato": (fmt.get("format_name") or path.suffix.lstrip(".")).split(",")[0],
            "codec": codec,
            "duracion": float(fmt.get("duration") or 0),
            "frecuencia": int(audio.get("sample_rate") or 0),
            "canales": int(audio.get("channels") or 0),
            "bits": bits,
            "bitrate": bitrate,
            "tamaño": path.stat().st_size,
            "etiquetas": len(real_tags),
            "portada": cover,
        }

    @staticmethod
    def _is_junk_key(key):
        base, _, desc = str(key).partition(":")
        low = str(key).lower()
        return (
            low in _JUNK_VORBIS
            or base in _JUNK_ID3
            or base in _JUNK_MP4
            or (base == "TXXX" and desc.lower() in _JUNK_VORBIS)
        )

    # ------------------------------------------------------- metadatos/portada
    def _read_cover(self, path):
        """Devuelve (bytes, mime) de la carátula incrustada, o None."""
        if not MUTAGEN_OK:
            return None
        try:
            f = mutagen.File(path)
        except Exception:
            return None
        if f is None:
            return None
        try:
            if isinstance(f, MP4):
                covr = f.tags.get("covr") if f.tags else None
                if covr:
                    item = covr[0]
                    img_fmt = getattr(item, "imageformat", MP4Cover.FORMAT_JPEG)
                    mime = "image/png" if img_fmt == MP4Cover.FORMAT_PNG else "image/jpeg"
                    return bytes(item), mime
            elif isinstance(f, FLAC):
                if f.pictures:
                    return f.pictures[0].data, f.pictures[0].mime or "image/jpeg"
            elif isinstance(f, (OggVorbis, OggOpus)):
                blocks = f.tags.get("metadata_block_picture") if f.tags else None
                if blocks:
                    pic = Picture(base64.b64decode(blocks[0]))
                    return pic.data, pic.mime or "image/jpeg"
            elif isinstance(f.tags, ID3):
                pics = f.tags.getall("APIC")
                if pics:
                    return pics[0].data, pics[0].mime or "image/jpeg"
        except Exception:
            return None
        return None

    def _write_cover(self, path, data, mime):
        """Incrusta la carátula en el archivo destino según su formato."""
        if not (MUTAGEN_OK and data):
            return False
        try:
            f = mutagen.File(path)
            if f is None:
                return False
            if isinstance(f, MP4):
                if f.tags is None:
                    f.add_tags()
                img_fmt = MP4Cover.FORMAT_PNG if "png" in mime.lower() else MP4Cover.FORMAT_JPEG
                f.tags["covr"] = [MP4Cover(data, img_fmt)]
            elif isinstance(f, FLAC):
                pic = Picture()
                pic.data = data
                pic.mime = mime or "image/jpeg"
                pic.type = 3
                f.clear_pictures()
                f.add_picture(pic)
            elif isinstance(f, (OggVorbis, OggOpus)):
                pic = Picture()
                pic.data = data
                pic.mime = mime or "image/jpeg"
                pic.type = 3
                f.tags["metadata_block_picture"] = [
                    base64.b64encode(pic.write()).decode("ascii")
                ]
            elif isinstance(f.tags, ID3):
                f.tags.add(
                    APIC(encoding=3, mime=mime or "image/jpeg", type=3, desc="Cover", data=data)
                )
            else:
                return False
            f.save()
            return True
        except Exception:
            return False

    def _scrub_tags(self, path):
        """Elimina etiquetas internas de ffmpeg/contenedor del archivo destino."""
        if not MUTAGEN_OK:
            return
        try:
            f = mutagen.File(path)
        except Exception:
            return
        if f is None or f.tags is None:
            return
        tags = f.tags
        try:
            if isinstance(tags, ID3):
                for key in list(tags.keys()):
                    if self._is_junk_key(key):
                        del tags[key]
            elif isinstance(f, MP4):
                for key in list(tags.keys()):
                    if key in _JUNK_MP4:
                        del tags[key]
            else:
                for key in list(tags.keys()):
                    if str(key).lower() in _JUNK_VORBIS:
                        del tags[key]
            f.save()
        except Exception:
            return

    # -------------------------------------------------------------- encoding
    @staticmethod
    def _bitrate_kbps(props, fallback):
        bitrate = props.get("bitrate") or 0
        if bitrate > 0:
            return f"{max(96, min(bitrate // 1000, 320))}k"
        return fallback

    @staticmethod
    def _pcm_codec(props):
        return _PCM_FOR_BITS.get(props.get("bits") or 16, "pcm_s16le")

    def _target_token(self, out_format, props):
        if not out_format or out_format == "original":
            return props["sufijo"].lstrip(".")
        return out_format.lower()

    def _encode_args(self, target, props):
        if target == "mp3":
            return ["-c:a", "libmp3lame", "-b:a", self._bitrate_kbps(props, "320k")]
        if target in ("m4a", "mp4", "aac"):
            return ["-c:a", "aac", "-b:a", self._bitrate_kbps(props, "256k")]
        if target == "flac":
            return ["-c:a", "flac", "-compression_level", "5"]
        if target == "wav":
            return ["-c:a", self._pcm_codec(props)]
        if target in ("ogg", "oga"):
            return ["-c:a", "libvorbis", "-q:a", "6"]
        if target == "opus":
            return ["-c:a", "libopus", "-b:a", self._bitrate_kbps(props, "128k")]
        if target == "wma":
            return ["-c:a", "wmav2", "-b:a", self._bitrate_kbps(props, "192k")]
        if target in ("aif", "aiff"):
            return ["-c:a", self._pcm_codec(props)]
        return []

    # ---------------------------------------------------------------- proceso
    def _resolve_output(self, input_path, output_path, target):
        if output_path is None:
            return self.output_dir / f"{input_path.stem}_con_silencio.{target}"
        output_path = Path(output_path)
        if output_path.suffix.lower() != f".{target}":
            output_path = output_path.with_suffix(f".{target}")
        return output_path

    def process(self, input_path, silence, out_format="original", output_path=None):
        """Agrega `silence` segundos al inicio y guarda el resultado."""
        self._require_tools()
        self.ensure_dirs()

        input_path = Path(input_path)
        if not input_path.is_absolute() and input_path.parent == Path("."):
            candidate = self.input_dir / input_path
            if candidate.exists():
                input_path = candidate

        if not input_path.exists():
            raise FileNotFoundError(f"El archivo no existe: {input_path}")
        if input_path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(f"Formato no soportado: {input_path.suffix}")
        if not (0 < silence <= 10):
            raise ValueError("La duración del silencio debe estar entre 0.1 y 10 segundos")

        props = self.analyze(input_path)
        target = self._target_token(out_format, props)
        output_path = self._resolve_output(input_path, output_path, target)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._print_source(input_path, props, target)

        result = subprocess.run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(input_path),
                "-af", f"adelay={int(round(silence * 1000))}:all=1",
                "-map", "0:a", "-map_metadata", "0",
                *self._encode_args(target, props),
                str(output_path),
            ],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg falló: {result.stderr.strip()}")

        # Reparar etiquetas y carátula (ffmpeg no cubre OGG/OPUS/WAV del todo).
        self._scrub_tags(output_path)
        if target in COVER_SUPPORTED:
            cover = self._read_cover(input_path)
            if cover:
                self._write_cover(output_path, *cover)

        final = self.analyze(output_path)
        self._print_result(input_path, props, output_path, final, silence, target)
        return str(output_path)

    # ------------------------------------------------------------------ salida
    @staticmethod
    def _print_source(input_path, props, target):
        print(f"\n📂 Procesando: {input_path.name}")
        print("🔍 Propiedades del archivo original:")
        print(f"   • Formato: {props['formato']} ({props['sufijo']})")
        print(f"   • Duración: {props['duracion']:.2f} segundos")
        print(f"   • Frecuencia de muestreo: {props['frecuencia']} Hz")
        canales = "Estéreo" if props["canales"] == 2 else "Mono"
        print(f"   • Canales: {props['canales']} ({canales})")
        if props["bits"]:
            print(f"   • Bits por muestra: {props['bits']}")
        print(
            "   • Bitrate: "
            + (f"{props['bitrate'] // 1000} kbps" if props["bitrate"] else "N/A")
        )
        print(f"   • Tamaño: {props['tamaño'] / (1024 * 1024):.2f} MB")
        if props["etiquetas"]:
            print(f"   • Metadatos: {props['etiquetas']} etiqueta(s)")
        print(f"   • Carátula: {'sí' if props['portada'] else 'no'}")
        if target != props["sufijo"].lstrip("."):
            print(f"   • Formato de salida: {target.upper()}")

    @staticmethod
    def _print_result(input_path, props, output_path, final, silence, target):
        print(f"\n🔇 Silencio agregado: {silence}s")
        print("✅ Proceso completado!")
        print(f"🎵 Duración final: {final['duracion']:.2f}s")
        print(f"📁 Guardado en: {output_path}")


# --------------------------------------------------------------------- CLI
def build_parser():
    parser = argparse.ArgumentParser(
        description="Agrega silencio al inicio de audios conservando metadatos y calidad.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Carpetas:
  Coloca los audios en Input/ y los resultados salen en Output/ por defecto.

Ejemplos:
  python add_silence.py                          # procesa todo Input/ (1.5s, formato original)
  python add_silence.py cancion.flac             # resuelve dentro de Input/
  python add_silence.py cancion.flac -s 3        # 3 segundos de silencio
  python add_silence.py cancion.m4a -s 2 -f flac # convierte a FLAC
  python add_silence.py vocal.m4a inst.mp3 -s 3 -s 2 -f m4a -f mp3
        """,
    )
    parser.add_argument("archivos", nargs="*", help="Archivos a procesar (si se omite, procesa todo Input/)")
    parser.add_argument(
        "-s", "--silencio", type=float, default=[], action="append",
        help="Duración del silencio en segundos (0.1-10). Se repite por archivo o se aplica a todos.",
    )
    parser.add_argument(
        "-f", "--format", dest="formato", default=[], action="append",
        choices=FORMAT_CHOICES, help="Formato de salida. Se repite por archivo o se aplica a todos.",
    )
    parser.add_argument("-o", "--output", help="Ruta de salida (solo para un archivo)")
    parser.add_argument("--input-dir", default=str(INPUT_DIR), help="Carpeta de entrada (default: Input)")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Carpeta de salida (default: Output)")
    return parser


def _resolve_inputs(names, adder):
    files = []
    for name in names:
        path = Path(name)
        if path.parent == Path(".") and (adder.input_dir / path).exists():
            path = adder.input_dir / path
        files.append(path)
    return files


def main(argv=None):
    args = build_parser().parse_args(argv)
    adder = AudioSilenceAdder(args.input_dir, args.output_dir)
    adder.ensure_dirs()

    if not MUTAGEN_OK:
        print("⚠️  mutagen no está instalado: no se limpiarán etiquetas ni carátulas.")

    try:
        if args.archivos:
            files = _resolve_inputs(args.archivos, adder)
        else:
            files = adder.list_input_files()
            if not files:
                print(f"⚠️  No hay archivos de audio en {adder.input_dir}/")
                return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    if len(files) > 1 and args.output:
        print("❌ Error: --output solo se puede usar con un solo archivo")
        return 1

    silencios = args.silencio or [1.5]
    formatos = args.formato or ["original"]
    if len(silencios) == 1:
        silencios *= len(files)
    if len(formatos) == 1:
        formatos *= len(files)
    if len(silencios) != len(files):
        print(f"❌ Error: {len(silencios)} valores de silencio para {len(files)} archivos")
        return 1
    if len(formatos) != len(files):
        print(f"❌ Error: {len(formatos)} formatos para {len(files)} archivos")
        return 1

    print("🎵 Agregador de Silencio")
    print("=" * 50)

    procesados = errores = 0
    for archivo, silencio, formato in zip(files, silencios, formatos):
        try:
            adder.process(archivo, silencio, formato, args.output if len(files) == 1 else None)
            procesados += 1
        except Exception as e:
            print(f"❌ Error procesando {archivo}: {e}")
            errores += 1

    print("\n" + "=" * 50)
    print(f"📊 Resumen: {procesados} procesado(s), {errores} error(es)")
    return 0 if errores == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

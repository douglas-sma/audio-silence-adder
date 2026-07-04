#!/usr/bin/env python3
"""
Herramienta para agregar silencio al principio de archivos de audio
Mantiene todas las propiedades y formato originales del archivo
"""

import os
import sys
from pydub import AudioSegment
from mutagen import File
import argparse
from pathlib import Path


class AudioSilenceAdder:
    def __init__(self):
        self.supported_formats = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma']
        self.problematic_formats = ['.m4a', '.aac', '.wma']

    def analyze_audio_properties(self, file_path):
        """Analiza las propiedades del archivo de audio"""
        try:
            audio_file = File(file_path)
            audio = AudioSegment.from_file(file_path)

            bitrate = 'N/A'
            if audio_file and hasattr(audio_file.info, 'bitrate'):
                bitrate = audio_file.info.bitrate

            properties = {
                'formato': file_path.suffix.lower(),
                'duracion_original': len(audio) / 1000.0,
                'frecuencia_muestreo': audio.frame_rate,
                'canales': audio.channels,
                'bits_por_muestra': audio.sample_width * 8,
                'sample_width': audio.sample_width,
                'bitrate': bitrate,
                'tamaño_archivo': os.path.getsize(file_path),
                'audio_file_object': audio_file,
            }

            if audio_file and audio_file.tags:
                properties['metadatos_count'] = len(audio_file.tags)
            else:
                properties['metadatos_count'] = 0

            return audio, properties

        except Exception as e:
            raise Exception(f"Error al analizar el archivo: {str(e)}")

    def _format_bitrate_for_ffmpeg(self, bitrate):
        """Convierte bitrate en bps (ej: 128000) al formato de ffmpeg (ej: '128k')"""
        if bitrate == 'N/A' or bitrate is None:
            return None
        try:
            return f"{int(bitrate) // 1000}k"
        except (ValueError, TypeError):
            return None

    def _get_export_params(self, target_format, properties):
        """Construye parámetros de exportación preservando calidad para el formato destino"""
        params = {'format': target_format, 'parameters': []}
        bitrate = self._format_bitrate_for_ffmpeg(properties.get('bitrate'))

        t = target_format.lower()

        if t == 'mp3':
            params['parameters'].extend(['-b:a', bitrate or '320k'])

        elif t in ('mp4', 'm4a'):
            params['format'] = 'mp4'
            params['parameters'].extend(['-c:a', 'aac', '-b:a', bitrate or '256k'])

        elif t == 'flac':
            params['parameters'].extend(['-compression_level', '5'])

        elif t == 'wav':
            bits = properties.get('bits_por_muestra', 16)
            params['parameters'].extend(['-acodec', f'pcm_s{bits}le'])

        return params

    def _export_audio(self, audio, output_path, properties, output_format=None):
        """Exporta el audio, opcionalmente convirtiendo a otro formato"""
        if output_format and output_format != 'original':
            output_path = output_path.with_suffix(f'.{output_format}')
            params = self._get_export_params(output_format, properties)
            try:
                audio.export(str(output_path), **params)
            except Exception as e:
                raise Exception(f"Error exportando como {output_format}: {e}")
        else:
            formato = properties['formato'][1:]
            format_mapping = {'m4a': 'mp4', 'aac': 'adts'}
            export_format = format_mapping.get(formato, formato)

            bitrate = self._format_bitrate_for_ffmpeg(properties.get('bitrate'))
            params = {'format': export_format, 'parameters': []}

            if properties['formato'] == '.mp3':
                params['parameters'].extend(['-b:a', bitrate or '320k'])
            elif properties['formato'] in ('.m4a', '.aac'):
                params['parameters'].extend(['-c:a', 'aac', '-b:a', bitrate or '256k'])
            elif properties['formato'] == '.wav':
                params['parameters'].extend(['-acodec', f"pcm_s{properties['bits_por_muestra']}le"])
            elif properties['formato'] == '.flac':
                params['parameters'].extend(['-compression_level', '5'])

            try:
                audio.export(str(output_path), **params)
            except Exception as e:
                print(f"   ⚠️ Error con formato original: {e}")
                mp3_output = output_path.with_suffix('.mp3')
                print(f"   🔄 Intentando MP3: {mp3_output.name}")
                try:
                    audio.export(str(mp3_output), format='mp3', parameters=['-b:a', '192k'])
                    output_path = mp3_output
                    print(f"   ✅ Guardado como MP3")
                except Exception:
                    wav_output = output_path.with_suffix('.wav')
                    print(f"   🔄 Intentando WAV: {wav_output.name}")
                    audio.export(str(wav_output), format='wav')
                    output_path = wav_output
                    print(f"   ✅ Guardado como WAV")

        return output_path

    def create_silence(self, duration_seconds, sample_rate, channels):
        """Crea un segmento de silencio con las mismas propiedades del audio"""
        silence_ms = int(duration_seconds * 1000)
        silence = AudioSegment.silent(duration=silence_ms, frame_rate=sample_rate)

        if channels == 2 and silence.channels == 1:
            silence = silence.set_channels(2)
        elif channels == 1 and silence.channels == 2:
            silence = silence.set_channels(1)

        return silence

    def add_silence_to_beginning(self, input_path, silence_duration, output_path=None, output_format=None):
        """Agrega silencio al principio del archivo de audio"""
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"El archivo {input_path} no existe")

        if input_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Formato no soportado. Formatos válidos: {', '.join(self.supported_formats)}")

        if not (0 < silence_duration <= 10):
            raise ValueError("La duración del silencio debe estar entre 0.1 y 10 segundos")

        print(f"📁 Analizando archivo: {input_path.name}")

        if input_path.suffix.lower() in self.problematic_formats:
            print(f"   ⚠️ Formato {input_path.suffix.upper()} puede requerir codificación alternativa")

        original_audio, properties = self.analyze_audio_properties(input_path)

        print("🔍 Propiedades del archivo original:")
        print(f"   • Formato: {properties['formato']}")
        print(f"   • Duración: {properties['duracion_original']:.2f} segundos")
        print(f"   • Frecuencia de muestreo: {properties['frecuencia_muestreo']} Hz")
        print(f"   • Canales: {properties['canales']} ({'Estéreo' if properties['canales'] == 2 else 'Mono'})")
        print(f"   • Bits por muestra: {properties['bits_por_muestra']}")

        if properties['bitrate'] != 'N/A':
            print(f"   • Bitrate: {properties['bitrate'] // 1000} kbps")
        else:
            print(f"   • Bitrate: N/A")

        print(f"   • Tamaño: {properties['tamaño_archivo'] / (1024 * 1024):.2f} MB")

        if properties['metadatos_count'] > 0:
            print(f"   • Metadatos: {properties['metadatos_count']} etiquetas encontradas (se copiarán todas)")

        if output_format and output_format != 'original':
            print(f"   • Formato de salida: {output_format.upper()}")

        print(f"\n🔇 Agregando {silence_duration} segundos de silencio al principio...")

        silence = self.create_silence(
            silence_duration,
            properties['frecuencia_muestreo'],
            properties['canales']
        )

        final_audio = silence + original_audio

        # Determinar ruta de salida
        if output_path is None:
            stem = input_path.stem
            suffix = f'.{output_format}' if output_format and output_format != 'original' else input_path.suffix
            output_path = input_path.parent / f"{stem}_con_silencio{suffix}"
        else:
            output_path = Path(output_path)

        print(f"💾 Guardando archivo modificado: {output_path.name}")

        output_path = self._export_audio(final_audio, output_path, properties, output_format)

        # Copiar metadatos si el formato destino lo soporta
        if properties['metadatos_count'] > 0 and output_path.suffix.lower() in ('.mp3', '.flac', '.ogg', '.m4a'):
            self.copy_all_metadata(input_path, output_path)

        final_properties = self.get_final_properties(output_path)

        print("\n✅ Proceso completado!")
        print(f"🎵 Archivo original: {properties['duracion_original']:.2f}s")
        print(f"🔇 Silencio agregado: {silence_duration}s")
        print(f"🎵 Archivo final: {final_properties['duracion_final']:.2f}s")
        print(f"📁 Guardado en: {output_path}")

        return str(output_path)

    def _get_tag_mapping(self, source_suffix, dest_suffix):
        """Mapea keys de metadatos entre formatos distintos (ej: ©ART → ARTIST)"""
        # Source → key mapping
        maps = {
            '.m4a': {
                '©ART': 'ARTIST', '©alb': 'ALBUM', '©nam': 'TITLE',
                '©gen': 'GENRE', '©day': 'DATE', '©wrt': 'COMPOSER',
                'aART': 'ALBUMARTIST', '©cmt': 'COMMENT',
                '©too': 'ENCODING',
            },
        }
        return maps.get(source_suffix, {})

    def _get_tag_value(self, value):
        """Extrae valor plano de un tag mutagen para compatibilidad entre formatos"""
        if isinstance(value, list):
            # Skip cover art objects
            if value and hasattr(value[0], 'imageformat'):
                return None
            # Convert all items to strings
            result = []
            for v in value:
                if isinstance(v, bytes):
                    result.append(v.decode('utf-8', errors='replace'))
                else:
                    result.append(str(v))
            return result
        if isinstance(value, bytes):
            return value.decode('utf-8', errors='replace')
        return str(value)

    def copy_all_metadata(self, source_path, dest_path):
        """Copia metadatos entre archivos, mapeando tags entre formatos distintos si es necesario"""
        try:
            source_file = File(source_path)
            dest_file = File(dest_path)

            if source_file is None or dest_file is None:
                print("   ℹ️ No hay metadatos para copiar")
                return

            if not source_file.tags:
                print("   ℹ️ No hay metadatos en el archivo original")
                return

            source_suffix = source_path.suffix.lower()
            dest_suffix = dest_path.suffix.lower()
            tag_map = self._get_tag_mapping(source_suffix, dest_suffix) if source_suffix != dest_suffix else {}

            copied = 0
            for key in source_file.tags.keys():
                try:
                    dest_key = tag_map.get(key, key)
                    value = self._get_tag_value(source_file.tags[key])
                    if value is not None:
                        dest_file.tags[dest_key] = value
                        copied += 1
                except Exception:
                    continue  # Saltar tags incompatibles sin ruido

            dest_file.save()

            if copied > 0:
                print(f"   ✓ {copied} metadatos copiados exitosamente (incluyendo carátulas si existen)")

        except Exception as e:
            print(f"   ⚠️ Advertencia: Error al copiar metadatos: {e}")
            print("   ℹ️ El archivo de audio se creó correctamente, pero algunos metadatos pueden faltar")

    def get_final_properties(self, file_path):
        """Obtiene las propiedades del archivo final"""
        audio = AudioSegment.from_file(file_path)
        return {
            'duracion_final': len(audio) / 1000.0,
            'tamaño_final': os.path.getsize(file_path),
        }


def main():
    parser = argparse.ArgumentParser(
        description='Agrega silencio al principio de archivos de audio manteniendo sus propiedades originales',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python add_silence.py cancion.mp3 --silencio 1.5
  python add_silence.py audio.wav --silencio 5 --output audio_modificado.wav
  python add_silence.py *.mp3 --silencio 2.5
  python add_silence.py cancion.mp3 --silencio 3 --format flac
  python add_silence.py cancion.m4a --silencio 2 --format m4a
        """,
    )

    parser.add_argument('archivos', nargs='+', help='Archivo(s) de audio a procesar')
    parser.add_argument('--silencio', '-s', type=float, default=1.5,
                        help='Duración del silencio en segundos (0.1-10, por defecto: 1.5)')
    parser.add_argument('--output', '-o', help='Archivo de salida (solo para un archivo)')
    parser.add_argument('--format', '-f', choices=['m4a', 'flac', 'original'], default='original',
                        help='Formato de salida: m4a, flac, u original (mantener formato original)')

    args = parser.parse_args()

    if len(args.archivos) > 1 and args.output:
        print("❌ Error: No se puede especificar --output cuando se procesan múltiples archivos")
        return 1

    adder = AudioSilenceAdder()

    print("🎵 Agregador de Silencio - Inicio del Audio")
    print("=" * 50)

    archivos_procesados = 0
    errores = 0

    for archivo in args.archivos:
        try:
            print(f"\n📂 Procesando: {archivo}")
            resultado = adder.add_silence_to_beginning(
                archivo,
                args.silencio,
                args.output,
                args.format,
            )
            archivos_procesados += 1

        except Exception as e:
            print(f"❌ Error procesando {archivo}: {e}")
            errores += 1
            continue

    print("\n" + "=" * 50)
    print(f"📊 Resumen: {archivos_procesados} archivo(s) procesado(s), {errores} error(es)")

    return 0 if errores == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

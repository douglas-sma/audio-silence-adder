#!/usr/bin/env python3
"""
CLI interactivo para agregar silencio al inicio de archivos de audio.

Los audios de entrada se toman de la carpeta Input/ y los resultados se
guardan en Output/. Ambas carpetas se crean automáticamente.
"""

import sys
from pathlib import Path

from add_silence import (
    AudioSilenceAdder,
    FORMAT_CHOICES,
    MUTAGEN_OK,
)

FORMAT_INFO = {
    "original": "Original (mantener el formato de entrada)",
    "mp3": "MP3 (compatible, buena calidad)",
    "m4a": "M4A/AAC (recomendado para voces)",
    "flac": "FLAC (sin pérdida, recomendado para instrumental)",
    "wav": "WAV (sin comprimir, sin pérdida)",
    "ogg": "OGG Vorbis",
    "opus": "OPUS (muy eficiente)",
}

SILENCE_PRESETS = [1.5, 3.0, 5.0, 10.0]


def _ask(prompt):
    return input(prompt).strip()


def _es_si(texto):
    return texto.lower() in ("s", "si", "sí", "y", "yes")


def elegir_archivos(adder):
    """Muestra los archivos de Input/ y devuelve la lista seleccionada."""
    archivos = adder.list_input_files()
    if not archivos:
        print(f"\n⚠️  No hay archivos de audio en {adder.input_dir}/")
        print(f"   Copia tus audios ahí y vuelve a intentarlo.")
        return None

    print(f"\n📁 Archivos disponibles en {adder.input_dir}/:")
    for i, path in enumerate(archivos, start=1):
        tamaño = path.stat().st_size / (1024 * 1024)
        print(f"  {i:>2}. {path.name}  ({tamaño:.2f} MB)")
    print("   0. Todos")

    while True:
        entrada = _ask("\nElige un número (0 = todos, q = salir): ")
        if entrada.lower() in ("q", "salir"):
            return None
        if entrada == "0":
            return archivos
        if entrada.isdigit() and 1 <= int(entrada) <= len(archivos):
            return [archivos[int(entrada) - 1]]
        print("❌ Opción inválida")


def elegir_silencio():
    """Solicita la duración del silencio."""
    print("\n🔇 Duración del silencio:")
    for i, seg in enumerate(SILENCE_PRESETS, start=1):
        print(f"  {i}. {seg} segundos")
    print(f"  {len(SILENCE_PRESETS) + 1}. Personalizado")

    while True:
        entrada = _ask(f"\nElige una opción (1-{len(SILENCE_PRESETS) + 1}): ")
        if entrada.isdigit():
            opcion = int(entrada)
            if 1 <= opcion <= len(SILENCE_PRESETS):
                return SILENCE_PRESETS[opcion - 1]
            if opcion == len(SILENCE_PRESETS) + 1:
                try:
                    valor = float(_ask("Segundos (0.1-10): "))
                    if 0.1 <= valor <= 10:
                        return valor
                    print("❌ Debe estar entre 0.1 y 10 segundos")
                except ValueError:
                    print("❌ Ingresa un número válido")
                continue
        print("❌ Opción inválida")


def elegir_formato():
    """Solicita el formato de salida."""
    print("\n📀 Formato de salida:")
    for i, fmt in enumerate(FORMAT_CHOICES, start=1):
        print(f"  {i}. {FORMAT_INFO[fmt]}")

    while True:
        entrada = _ask(f"\nElige una opción (1-{len(FORMAT_CHOICES)}): ")
        if entrada.isdigit() and 1 <= int(entrada) <= len(FORMAT_CHOICES):
            return FORMAT_CHOICES[int(entrada) - 1]
        print("❌ Opción inválida")


def main():
    print("🎵 Agregador de Silencio - CLI interactivo")
    print("=" * 45)

    adder = AudioSilenceAdder()
    adder.ensure_dirs()

    if not MUTAGEN_OK:
        print("⚠️  mutagen no está instalado: no se limpiarán etiquetas ni carátulas.")

    try:
        while True:
            archivos = elegir_archivos(adder)
            if archivos is None:
                break

            silencio = elegir_silencio()
            formato = elegir_formato()

            print("\n" + "-" * 45)
            for archivo in archivos:
                try:
                    adder.process(archivo, silencio, formato)
                except Exception as e:
                    print(f"❌ Error procesando {archivo.name}: {e}")
            print("-" * 45)

            if not _es_si(_ask("\n¿Procesar más archivos? (s/n): ")):
                break
    except KeyboardInterrupt:
        print()

    print("\n👋 ¡Hasta luego!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

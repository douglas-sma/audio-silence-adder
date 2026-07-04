#!/usr/bin/env python3
"""
Script simple para agregar silencio al principio de archivos de audio
Versión interactiva y fácil de usar
"""

import sys
from pathlib import Path
from add_silence import AudioSilenceAdder


def seleccionar_archivo():
    """Solicita y valida un archivo de audio"""
    adder = AudioSilenceAdder()

    while True:
        archivo = input("\n📁 Ingresa la ruta del archivo de audio: ").strip()

        if not archivo:
            print("❌ Por favor ingresa una ruta válida")
            continue

        path = Path(archivo)

        if not path.exists():
            print(f"❌ El archivo '{archivo}' no existe")
            continue

        if path.suffix.lower() not in adder.supported_formats:
            print(f"❌ Formato no soportado. Usa: {', '.join(adder.supported_formats)}")
            continue

        return path


def seleccionar_silencio():
    """Solicita la duración del silencio"""
    while True:
        print("\n🔇 Opciones de silencio:")
        print("  1. 1.5 segundos")
        print("  2. 5 segundos")
        print("  3. 10 segundos")
        print("  4. Personalizado")

        opcion = input("\nElige una opción (1-4): ").strip()

        if opcion == "1":
            return 1.5
        elif opcion == "2":
            return 5.0
        elif opcion == "3":
            return 10.0
        elif opcion == "4":
            try:
                silencio = float(input("Ingresa la duración en segundos (0.1-10): "))
                if 0.1 <= silencio <= 10:
                    return silencio
                else:
                    print("❌ Debe estar entre 0.1 y 10 segundos")
            except ValueError:
                print("❌ Ingresa un número válido")
        else:
            print("❌ Opción inválida")


def seleccionar_formato():
    """Solicita el formato de salida"""
    while True:
        print("\n📀 Formato de salida:")
        print("  1. M4A (AAC, buena compresión, recomendado para vocales)")
        print("  2. FLAC (sin pérdida, recomendado para instrumental)")
        print("  3. Original (mantener formato original)")

        opcion = input("\nElige una opción (1-3): ").strip()

        if opcion == "1":
            return "m4a"
        elif opcion == "2":
            return "flac"
        elif opcion == "3":
            return "original"
        else:
            print("❌ Opción inválida")


def procesar_archivo(archivo_path, silencio, formato):
    """Procesa un archivo de audio y muestra el resultado"""
    try:
        adder = AudioSilenceAdder()
        resultado = adder.add_silence_to_beginning(archivo_path, silencio, output_format=formato)
        print(f"\n🎉 ¡Éxito! Archivo creado: {resultado}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("🎵 Agregador de Silencio - Versión Simple")
    print("=" * 40)

    while True:
        archivo = seleccionar_archivo()
        silencio = seleccionar_silencio()
        formato = seleccionar_formato()

        procesar_archivo(archivo, silencio, formato)

        otra = input("\n¿Procesar otro archivo? (s/n): ").strip().lower()
        if otra not in ('s', 'si', 'sí', 'y', 'yes'):
            break

    print("\n👋 ¡Hasta luego!")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
        sys.exit(0)

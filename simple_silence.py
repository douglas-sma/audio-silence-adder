#!/usr/bin/env python3
"""
Script simple para agregar silencio al principio de archivos de audio
Versión interactiva y fácil de usar
"""

import os
import sys
from pathlib import Path
from add_silence import AudioSilenceAdder

def main():
    print("🎵 Agregador de Silencio - Versión Simple")
    print("=" * 40)
    
    # Solicitar archivo de entrada
    while True:
        archivo_entrada = input("\n📁 Ingresa la ruta del archivo de audio: ").strip()
        
        if not archivo_entrada:
            print("❌ Por favor ingresa una ruta válida")
            continue
            
        archivo_path = Path(archivo_entrada)
        
        if not archivo_path.exists():
            print(f"❌ El archivo '{archivo_entrada}' no existe")
            continue
            
        if archivo_path.suffix.lower() not in ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']:
            print("❌ Formato no soportado. Usa: .mp3, .wav, .flac, .ogg, .m4a, .aac")
            continue
            
        break
    
    # Solicitar duración del silencio
    while True:
        print("\n🔇 Opciones de silencio:")
        print("  1. 1.5 segundos")
        print("  2. 5 segundos") 
        print("  3. 10 segundos")
        print("  4. Personalizado")
        
        opcion = input("\nElige una opción (1-4): ").strip()
        
        if opcion == "1":
            silencio = 1.5
            break
        elif opcion == "2":
            silencio = 5.0
            break
        elif opcion == "3":
            silencio = 10.0
            break
        elif opcion == "4":
            try:
                silencio = float(input("Ingresa la duración en segundos (0.1-10): "))
                if 0.1 <= silencio <= 10:
                    break
                else:
                    print("❌ Debe estar entre 0.1 y 10 segundos")
            except ValueError:
                print("❌ Ingresa un número válido")
        else:
            print("❌ Opción inválida")
    
    # Procesar archivo
    try:
        adder = AudioSilenceAdder()
        resultado = adder.add_silence_to_beginning(archivo_path, silencio)
        
        print(f"\n🎉 ¡Éxito! Archivo creado: {resultado}")
        
        # Preguntar si desea procesar otro archivo
        otra = input("\n¿Procesar otro archivo? (s/n): ").strip().lower()
        if otra in ['s', 'si', 'sí', 'y', 'yes']:
            main()  # Reiniciar
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
        sys.exit(0)

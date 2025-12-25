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
        # Formatos que pueden presentar problemas de codificación
        self.problematic_formats = ['.m4a', '.aac', '.wma']
    
    def analyze_audio_properties(self, file_path):
        """Analiza las propiedades del archivo de audio"""
        try:
            # Usar mutagen para obtener metadatos (easy=True para claves estándar)
            audio_file = File(file_path, easy=True)
            
            # Cargar con pydub para propiedades técnicas
            audio = AudioSegment.from_file(file_path)
            
            properties = {
                'formato': file_path.suffix.lower(),
                'duracion_original': len(audio) / 1000.0,  # en segundos
                'frecuencia_muestreo': audio.frame_rate,
                'canales': audio.channels,
                'bits_por_muestra': audio.sample_width * 8,
                'bitrate': getattr(audio_file.info, 'bitrate', 'N/A') if audio_file else 'N/A',
                'tamaño_archivo': os.path.getsize(file_path),
            }
            
            # Metadatos usando claves estándar
            if audio_file and audio_file.tags:
                # Extraer solo metadatos estándar
                standard_metadata = {}
                for key, value in audio_file.tags.items():
                    if isinstance(value, list) and len(value) > 0:
                        standard_metadata[key] = value[0]
                    else:
                        standard_metadata[key] = str(value)
                
                properties['metadatos'] = standard_metadata
            else:
                properties['metadatos'] = {}
                
            return audio, properties
            
        except Exception as e:
            raise Exception(f"Error al analizar el archivo: {str(e)}")
    
    def create_silence(self, duration_seconds, sample_rate, channels):
        """Crea un segmento de silencio con las mismas propiedades del audio"""
        silence_ms = int(duration_seconds * 1000)
        silence = AudioSegment.silent(
            duration=silence_ms,
            frame_rate=sample_rate
        )
        
        # Asegurar que tenga el mismo número de canales
        if channels == 2 and silence.channels == 1:
            silence = silence.set_channels(2)
        elif channels == 1 and silence.channels == 2:
            silence = silence.set_channels(1)
            
        return silence
    
    def add_silence_to_beginning(self, input_path, silence_duration, output_path=None):
        """Agrega silencio al principio del archivo de audio"""
        
        input_path = Path(input_path)
        
        # Validar archivo de entrada
        if not input_path.exists():
            raise FileNotFoundError(f"El archivo {input_path} no existe")
        
        if input_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Formato no soportado. Formatos válidos: {', '.join(self.supported_formats)}")
        
        # Validar duración del silencio
        if not (0 < silence_duration <= 10):
            raise ValueError("La duración del silencio debe estar entre 0.1 y 10 segundos")
        
        print(f"📁 Analizando archivo: {input_path.name}")
        
        # Advertir sobre formatos problemáticos
        if input_path.suffix.lower() in self.problematic_formats:
            print(f"   ⚠️ Formato {input_path.suffix.upper()} puede requerir codificación alternativa")
        
        # Analizar propiedades del audio original
        original_audio, properties = self.analyze_audio_properties(input_path)
        
        print("🔍 Propiedades del archivo original:")
        print(f"   • Formato: {properties['formato']}")
        print(f"   • Duración: {properties['duracion_original']:.2f} segundos")
        print(f"   • Frecuencia de muestreo: {properties['frecuencia_muestreo']} Hz")
        print(f"   • Canales: {properties['canales']} ({'Estéreo' if properties['canales'] == 2 else 'Mono'})")
        print(f"   • Bits por muestra: {properties['bits_por_muestra']}")
        print(f"   • Bitrate: {properties['bitrate']}")
        print(f"   • Tamaño: {properties['tamaño_archivo'] / (1024*1024):.2f} MB")
        
        if properties['metadatos']:
            print(f"   • Metadatos: {len(properties['metadatos'])} etiquetas encontradas")
        
        print(f"\n🔇 Agregando {silence_duration} segundos de silencio al principio...")
        
        # Crear silencio con las mismas propiedades
        silence = self.create_silence(
            silence_duration,
            properties['frecuencia_muestreo'],
            properties['canales']
        )
        
        # Combinar silencio + audio original
        final_audio = silence + original_audio
        
        # Configurar archivo de salida
        if output_path is None:
            stem = input_path.stem
            suffix = input_path.suffix
            output_path = input_path.parent / f"{stem}_con_silencio{suffix}"
        else:
            output_path = Path(output_path)
        
        print(f"💾 Guardando archivo modificado: {output_path.name}")
        
        # Exportar manteniendo la calidad original
        formato = properties['formato'][1:]  # quitar el punto
        
        # Mapear formatos problemáticos
        format_mapping = {
            'm4a': 'mp4',  # M4A usa contenedor MP4
            'aac': 'adts'  # AAC usa formato ADTS
        }
        
        export_format = format_mapping.get(formato, formato)
        export_params = {
            'format': export_format,
            'parameters': []
        }
        
        # Configuraciones específicas por formato
        if properties['formato'] == '.mp3' and properties['bitrate'] != 'N/A':
            export_params['parameters'].extend(['-b:a', f"{properties['bitrate']}"])
        elif properties['formato'] == '.m4a':
            # Para M4A, usar codec AAC
            export_params['parameters'].extend(['-c:a', 'aac', '-b:a', '128k'])
        elif properties['formato'] == '.aac':
            # Para AAC, especificar bitrate
            export_params['parameters'].extend(['-c:a', 'aac', '-b:a', '128k'])
        
        # Exportar el archivo con manejo de errores
        try:
            final_audio.export(
                str(output_path),
                **export_params
            )
        except Exception as export_error:
            print(f"   ⚠️ Error con formato original: {export_error}")
            
            # Intentar exportar como MP3 como alternativa
            mp3_output = output_path.with_suffix('.mp3')
            print(f"   🔄 Intentando guardar como MP3: {mp3_output.name}")
            
            try:
                final_audio.export(
                    str(mp3_output),
                    format='mp3',
                    parameters=['-b:a', '192k']
                )
                output_path = mp3_output
                print(f"   ✅ Guardado exitosamente como MP3")
            except Exception as mp3_error:
                # Como último recurso, WAV
                wav_output = output_path.with_suffix('.wav')
                print(f"   🔄 Intentando guardar como WAV: {wav_output.name}")
                
                final_audio.export(str(wav_output), format='wav')
                output_path = wav_output
                print(f"   ✅ Guardado exitosamente como WAV")
        
        # Copiar metadatos si existen (solo si el formato lo permite)
        if properties['metadatos'] and output_path.suffix.lower() in ['.mp3', '.flac', '.ogg', '.m4a']:
            self.copy_metadata(input_path, output_path, properties['metadatos'])
        
        # Analizar el archivo final
        final_properties = self.get_final_properties(output_path)
        
        print("\n✅ Proceso completado!")
        print(f"🎵 Archivo original: {properties['duracion_original']:.2f}s")
        print(f"🔇 Silencio agregado: {silence_duration}s")
        print(f"🎵 Archivo final: {final_properties['duracion_final']:.2f}s")
        print(f"📁 Guardado en: {output_path}")
        
        return str(output_path)
    
    def copy_metadata(self, source_path, dest_path, metadata):
        """Copia los metadatos del archivo original al nuevo archivo"""
        try:
            # Leer metadatos del archivo original usando easy=True
            source_file = File(source_path, easy=True)
            dest_file = File(dest_path, easy=True)
            
            if source_file is not None and dest_file is not None and source_file.tags:
                # Copiar solo las etiquetas "fáciles" estándar
                standard_tags = [
                    'title', 'artist', 'album', 'albumartist', 'date', 
                    'genre', 'tracknumber', 'discnumber', 'comment'
                ]
                
                copied_count = 0
                for tag in standard_tags:
                    if tag in source_file:
                        dest_file[tag] = source_file[tag]
                        copied_count += 1
                
                dest_file.save()
                if copied_count > 0:
                    print(f"   ✓ {copied_count} metadatos copiados exitosamente")
                else:
                    print("   ℹ️ No se encontraron metadatos estándar para copiar")
            else:
                print("   ℹ️ No hay metadatos para copiar")
                
        except Exception as e:
            print(f"   ⚠️ Advertencia: No se pudieron copiar algunos metadatos: {e}")
    
    def get_final_properties(self, file_path):
        """Obtiene las propiedades del archivo final"""
        audio = AudioSegment.from_file(file_path)
        return {
            'duracion_final': len(audio) / 1000.0,
            'tamaño_final': os.path.getsize(file_path)
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
        """
    )
    
    parser.add_argument('archivos', nargs='+', help='Archivo(s) de audio a procesar')
    parser.add_argument('--silencio', '-s', type=float, default=1.5,
                       help='Duración del silencio en segundos (0.1-10, por defecto: 1.5)')
    parser.add_argument('--output', '-o', help='Archivo de salida (solo para un archivo)')
    
    args = parser.parse_args()
    
    # Validar argumentos
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
                args.output
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

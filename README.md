# Agregador de Silencio 🎵

Una herramienta para agregar silencio al principio de archivos de audio, manteniendo todas las propiedades y formato originales.

## Características

- ✅ Mantiene el formato original del audio
- ✅ Preserva todos los metadatos (título, artista, álbum, etc.)
- ✅ Conserva la calidad de audio original
- ✅ Soporta múltiples formatos: MP3, WAV, FLAC, OGG, M4A, AAC
- ✅ Análisis detallado de propiedades del audio
- ✅ Silencio configurable de 0.1 a 10 segundos

## Instalación

1. Crea un entorno virtual (recomendado):
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Prueba que todo funcione:
```bash
python test.py
```

### Uso Rápido

Puedes usar el script de activación automática:
```bash
# Activar entorno y abrir shell
./run.sh

# O ejecutar directamente con argumentos
./run.sh archivo.mp3 --silencio 1.5
```

## Uso

### Versión Simple (Interactiva)

Para uso rápido y fácil:

```bash
python simple_silence.py
```

El script te guiará paso a paso:
1. Selecciona el archivo de audio
2. Elige la duración del silencio (1.5s, 5s, 10s o personalizado)
3. ¡Listo! El archivo se guarda automáticamente

### Versión Avanzada (Línea de comandos)

Para mayor control y procesamiento en lote:

```bash
# Agregar 1.5 segundos de silencio (por defecto)
python add_silence.py cancion.mp3

# Especificar duración personalizada
python add_silence.py cancion.mp3 --silencio 5

# Especificar archivo de salida
python add_silence.py cancion.mp3 --silencio 2.5 --output cancion_modificada.mp3

# Procesar múltiples archivos
python add_silence.py *.mp3 --silencio 3

# Ver ayuda completa
python add_silence.py --help
```

## Ejemplos

### Ejemplo 1: Archivo individual
```bash
python add_silence.py mi_cancion.mp3 --silencio 1.5
```
**Resultado:** `mi_cancion_con_silencio.mp3`

### Ejemplo 2: Múltiples archivos
```bash
python add_silence.py cancion1.mp3 cancion2.wav cancion3.flac --silencio 5
```
**Resultado:** 
- `cancion1_con_silencio.mp3`
- `cancion2_con_silencio.wav` 
- `cancion3_con_silencio.flac`

## Formatos Soportados

| Formato | Extensión | Metadatos | Calidad | Notas |
|---------|-----------|-----------|---------|-------|
| MP3     | .mp3      | ✅        | ✅      | Totalmente compatible |
| WAV     | .wav      | ✅        | ✅      | Totalmente compatible |
| FLAC    | .flac     | ✅        | ✅      | Totalmente compatible |
| OGG     | .ogg      | ✅        | ✅      | Totalmente compatible |
| M4A     | .m4a      | ✅        | ✅      | Puede requerir conversión |
| AAC     | .aac      | ✅        | ✅      | Puede requerir conversión |

**Nota:** Los formatos M4A y AAC pueden presentar problemas de codificación en algunos sistemas. En estos casos, la herramienta automáticamente intentará guardar como MP3 o WAV como alternativa.

## Análisis de Propiedades

La herramienta analiza y muestra:

- 📊 **Formato y duración**
- 🔊 **Frecuencia de muestreo**
- 🎵 **Número de canales (mono/estéreo)**
- 💾 **Bits por muestra**
- 📈 **Bitrate**
- 📁 **Tamaño del archivo**
- 🏷️ **Metadatos** (título, artista, álbum, etc.)

## Estructura del Proyecto

```
Add silence/
├── requirements.txt      # Dependencias
├── add_silence.py       # Script principal (línea de comandos)
├── simple_silence.py    # Script simple (interactivo)
└── README.md           # Esta documentación
```

## Dependencias

- **pydub**: Manipulación de audio
- **mutagen**: Manejo de metadatos
- **numpy**: Operaciones numéricas

## Notas Técnicas

- El silencio se genera con las mismas propiedades técnicas que el audio original
- Los metadatos se copian íntegramente al nuevo archivo
- El archivo original nunca se modifica
- La calidad del audio se mantiene sin pérdidas adicionales

## Limitaciones

- Duración máxima de silencio: 10 segundos
- Requiere que el archivo original sea válido y no esté corrupto
- Algunos formatos propietarios no están soportados

## Solución de Problemas

### Error: "Formato no soportado"
- Verifica que el archivo tenga una extensión válida
- Convierte el archivo a un formato soportado

### Error: "Encoding failed" con M4A/AAC
- La herramienta automáticamente intentará guardar como MP3 alternativo
- Considera convertir tus archivos M4A a MP3 antes del procesamiento
- Instala ffmpeg completo: `sudo apt install ffmpeg`

### Error: "No se pudieron copiar los metadatos"
- El archivo se creará correctamente, pero sin algunos metadatos
- Esto es normal en algunos formatos menos comunes

### Audio con ruido
- Verifica que el archivo original no esté corrupto
- Prueba con un archivo de audio diferente

---

¿Necesitas ayuda? ¡Crea un issue con los detalles del problema!

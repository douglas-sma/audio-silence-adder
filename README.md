# Agregador de Silencio 🎵

Una herramienta para agregar silencio al principio de archivos de audio, manteniendo todas las propiedades y formato originales.

## Características

- ✅ Mantiene el formato original del audio o permite convertir a M4A/FLAC
- ✅ Preserva **TODOS** los metadatos (título, artista, álbum, carátulas, letras, etc.)
- ✅ Conserva la calidad de audio original (bitrate, bits por muestra, frecuencia)
- ✅ Soporta múltiples formatos: MP3, WAV, FLAC, OGG, M4A, AAC
- ✅ Análisis detallado de propiedades del audio
- ✅ Silencio configurable de 0.1 a 10 segundos
- ✅ Copia automática de carátulas de álbum y artwork

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
3. Elige el formato de salida (M4A, FLAC, u original)
4. ¡Listo! El archivo se guarda automáticamente

### Versión Avanzada (Línea de comandos)

Para mayor control y procesamiento en lote:

```bash
# Agregar 1.5 segundos de silencio (por defecto)
python add_silence.py cancion.mp3

# Especificar duración personalizada
python add_silence.py cancion.mp3 --silencio 5

# Convertir a M4A en la salida
python add_silence.py cancion.wav --silencio 3 --format m4a

# Convertir a FLAC
python add_silence.py cancion.m4a --silencio 2 --format flac

# Especificar archivo de salida
python add_silence.py cancion.mp3 --silencio 2.5 --output cancion_modificada.mp3

# Procesar múltiples archivos (mismo formato y silencio para todos)
python add_silence.py *.mp3 --silencio 3 --format m4a

# Procesar múltiples archivos con settings distintos por archivo
python add_silence.py vocal.m4a instrumental.mp3 -s 3 -s 2 -f m4a -f flac

# Procesar manteniendo formato original (por defecto)
python add_silence.py cancion.flac --silencio 1.5 --format original

# Ver ayuda completa
python add_silence.py --help
```

## Ejemplos

### Ejemplo 1: Archivo individual
```bash
python add_silence.py mi_cancion.mp3 --silencio 1.5
```
**Resultado:** `mi_cancion_con_silencio.mp3`

### Ejemplo 2: Convertir a FLAC
```bash
python add_silence.py mi_cancion.m4a --silencio 2 --format flac
```
**Resultado:** `mi_cancion_con_silencio.flac`

### Ejemplo 3: Archivos con espacios o caracteres especiales
```bash
# IMPORTANTE: Usa comillas para nombres con espacios
python add_silence.py "Artista - Canción.m4a" --silencio 4
python add_silence.py "./Audio/Mi Canción (Remix).mp3" --silencio 2
```

### Ejemplo 4: Múltiples archivos (mismo setting global)
```bash
python add_silence.py cancion1.mp3 cancion2.wav cancion3.flac --silencio 5 --format m4a
```
**Resultado:**
- `cancion1_con_silencio.m4a`
- `cancion2_con_silencio.m4a`
- `cancion3_con_silencio.m4a`

### Ejemplo 5: Múltiples archivos (settings por archivo)
```bash
# Cada archivo con su propio silencio y formato
python add_silence.py vocal.m4a instrumental.mp3 -s 3 -s 2 -f m4a -f flac
```
**Resultado:**
- `vocal_con_silencio.m4a` (3s de silencio)
- `instrumental_con_silencio.flac` (2s de silencio)

> Las flags `-s` y `-f` se repiten por archivo. Si solo das un valor, se aplica a todos.

### Ejemplo 6: Todos los archivos de una carpeta
```bash
# Procesar todos los MP3 de una carpeta
python add_silence.py ./Audio/*.mp3 --silencio 3

# Si hay espacios en la ruta, usa comillas
python add_silence.py "./Mi Carpeta"/*.mp3 --silencio 2
```

## Formatos Soportados

| Formato | Extensión | Metadatos | Carátulas | Calidad | Bitrate Original |
|---------|-----------|-----------|-----------|---------|------------------|
| MP3     | .mp3      | ✅ Todos  | ✅        | ✅ 100% | ✅ Preservado    |
| WAV     | .wav      | ✅ Todos  | ✅        | ✅ 100% | ✅ Preservado    |
| FLAC    | .flac     | ✅ Todos  | ✅        | ✅ 100% | ✅ Sin pérdidas  |
| OGG     | .ogg      | ✅ Todos  | ✅        | ✅ 100% | ✅ Preservado    |
| M4A     | .m4a      | ✅ Todos  | ✅        | ✅ 100% | ✅ Preservado    |
| AAC     | .aac      | ✅ Todos  | ✅        | ✅ 100% | ✅ Preservado    |

**Nota:** Los formatos M4A y AAC mantienen su bitrate original completo. En caso de problemas de codificación, la herramienta automáticamente intentará guardar como MP3 o WAV manteniendo la máxima calidad posible.

## Formato de Salida

Puedes elegir entre 3 opciones:

| Opción | Descripción | Ideal para |
|--------|-------------|------------|
| **M4A** | AAC con buena compresión, excelente calidad | Vocales, pistas con voz |
| **FLAC** | Sin pérdida, calidad idéntica al original | Instrumental, archivos maestros |
| **Original** | Mantiene el mismo formato de entrada | Compatibilidad total |

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

## Tips y Mejores Prácticas

### Archivos con Espacios o Caracteres Especiales

**Siempre usa comillas** cuando el nombre del archivo contenga:
- Espacios: `"Mi Canción.mp3"`
- Paréntesis: `"Canción (Remix).mp3"`
- Caracteres Unicode: `"Magic∞world.m4a"`
- Rutas con espacios: `"./Mi Carpeta/archivo.mp3"`

```bash
# ✅ CORRECTO
python add_silence.py "Artista - Canción (Remix).mp3" --silencio 4

# ❌ INCORRECTO (sin comillas)
python add_silence.py Artista - Canción (Remix).mp3 --silencio 4
# Esto se interpreta como múltiples archivos: Artista, -, Canción, (Remix).mp3
```

### Procesamiento en Lote

```bash
# Procesar todos los archivos de un formato
for file in ./Audio/*.m4a; do
    python add_silence.py "$file" --silencio 4 --format flac
done

# O usar el wildcard directamente
python add_silence.py ./Audio/*.m4a --silencio 4 --format m4a
```

### Verificar metadatos

```bash
# Ver metadatos de un archivo con mutagen
python -c "from mutagen import File; f=File('archivo.mp3'); print(f.pprint())"
```

## Notas Técnicas

- ✅ El silencio se genera con las **mismas propiedades exactas** que el audio original
- ✅ **TODOS** los metadatos se copian íntegramente (incluyendo carátulas, letras, comentarios extendidos)
- ✅ El **bitrate original** se preserva al mantener el formato; al convertir se usa la máxima calidad
- ✅ Los **bits por muestra** originales se mantienen (16-bit, 24-bit, etc.)
- ✅ La **frecuencia de muestreo** se preserva exactamente
- ✅ El archivo original **nunca se modifica**
- ✅ La calidad del audio se mantiene **sin pérdidas adicionales**

## Limitaciones

- Duración máxima de silencio: 10 segundos
- Requiere que el archivo original sea válido y no esté corrupto
- Algunos formatos propietarios no están soportados

## Solución de Problemas

### Error: "El archivo no existe" con nombres que tienen espacios
- **Causa:** No usaste comillas en el nombre del archivo
- **Solución:** Encierra el nombre entre comillas: `"archivo con espacios.mp3"`
- **Ejemplo:** `python add_silence.py "./Audio/Mi Canción.mp3" --silencio 4`

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

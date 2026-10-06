# Agregador de Silencio 🎵

Herramienta para agregar silencio al inicio de archivos de audio, conservando
los metadatos (título, artista, álbum, **carátulas**, etc.) y la calidad del audio.

## Características

- ✅ **Carpetas obligatorias `Input/` y `Output/`**: dejas los audios en `Input/` y los resultados salen en `Output/`.
- ✅ **CLI interactivo** (`cli.py`) y **CLI por argumentos** (`add_silence.py`).
- ✅ **Conserva los metadatos** entre formatos (MP3 ↔ FLAC ↔ M4A ↔ …) usando ffmpeg.
- ✅ **Conserva la carátula** (imagen embebida) cuando el formato de salida la soporta.
- ✅ **Limpia etiquetas basura** que suelen inyectar ffmpeg/contenedor (`major_brand`, `encoder`, `TSSE`, …).
- ✅ Mantiene la **profundidad de bits** y la frecuencia de muestreo originales (24-bit, 16-bit, etc.).
- ✅ Respeta el **bitrate original** al reconvertir formato (con topes razonables).
- ✅ El archivo original **nunca se modifica**.
- ✅ Silencio configurable de **0.1 a 10 segundos**.

## Requisitos

- Python 3.8+
- **ffmpeg / ffprobe** instalados en el sistema:
  ```bash
  sudo apt install ffmpeg     # Debian/Ubuntu
  sudo pacman -S ffmpeg       # Arch
  brew install ffmpeg         # macOS
  ```

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Estructura del Proyecto

```
Add silence/
├── Input/               # Audios de entrada (creada automáticamente)
├── Output/              # Resultados (creada automáticamente)
├── add_silence.py       # Motor + CLI por argumentos
├── cli.py               # CLI interactivo
├── run.sh               # Activa el venv y ejecuta la herramienta
├── requirements.txt     # Dependencias de Python
└── README.md            # Esta documentación
```

## Uso

### CLI interactivo (recomendado)

```bash
python cli.py
# o
./run.sh
```

El menú paso a paso:

1. Muestra los audios que hay en `Input/` y eliges uno o **todos**.
2. Eliges la duración del silencio (1.5s, 3s, 5s, 10s o personalizado).
3. Eliges el formato de salida.
4. El resultado se guarda automáticamente en `Output/`.

### CLI por argumentos

```bash
# Procesar todo lo que haya en Input/ (1.5s, formato original)
python add_silence.py

# Un archivo (se resuelve dentro de Input/)
python add_silence.py cancion.flac --silencio 3

# Convertir a otro formato
python add_silence.py cancion.m4a -s 2 -f flac
python add_silence.py cancion.wav -s 3 -f m4a

# Ruta explícita y salida explícita
python add_silence.py "./Mi Carpeta/tema.mp3" -s 2.5 -o "salida.mp3"

# Varios archivos, un ajuste por archivo
python add_silence.py vocal.m4a instrumental.mp3 -s 3 -s 2 -f m4a -f flac

# Ayuda
python add_silence.py --help
```

> `-s` y `-f` se repiten por archivo. Si pones un solo valor, se aplica a todos.

## Formatos

### Entrada soportada

`MP3`, `WAV`, `FLAC`, `OGG/OGG`, `OPUS`, `M4A`, `MP4`, `AAC`, `WMA`, `AIFF`.

### Salida

| Formato    | Descripción                         | Carátula |
|------------|-------------------------------------|----------|
| `original` | Mismo formato de entrada            | ✅*      |
| `mp3`      | MP3 (LAME)                          | ✅       |
| `m4a`      | AAC en contenedor M4A               | ✅       |
| `flac`     | FLAC sin pérdida                    | ✅       |
| `wav`      | PCM sin comprimir                   | ❌       |
| `ogg`      | OGG Vorbis                          | ✅       |
| `opus`     | OPUS                                | ✅       |

\* La carátula se conserva si el formato de entrada/salida la soporta. `WAV` no
almacena carátulas, por lo que se omite en ese caso.

## Notas técnicas

- El silencio se añade con el filtro `adelay` de ffmpeg, generando silencio con las
  mismas propiedades (frecuencia, canales y formato de muestra) que el audio original.
- Los metadatos se copian con `-map_metadata 0`, que traduce las etiquetas entre
  contenedores (por ejemplo ID3 ↔ Vorbis ↔ MP4).
- Las carátulas se leen y reescriben con **mutagen**, de modo que funcionan incluso
  en OGG/OPUS, donde ffmpeg no las maneja bien.
- Se eliminan las etiquetas internas de ffmpeg/contenedor para dejar los metadatos limpios.

## Limitaciones

- Duración máxima de silencio: 10 segundos.
- `WAV` y `AIFF` no admiten carátula.
- Al convertir a un formato **con pérdida** (MP3/M4A/OGG/OPUS) el audio se recodifica,
  por lo que hay una generación de pérdida inevitable.

## Solución de Problemas

### "No se encontró 'ffmpeg'"
- Instala ffmpeg/ffprobe (ver **Requisitos**).

### "Formato no soportado"
- Verifica que la extensión del archivo sea una de las soportadas.

### Los metadatos no aparecen en la salida
- Asegúrate de tener `mutagen` instalado (`pip install -r requirements.txt`).
- Algunos formatos (WAV) tienen soporte muy limitado de etiquetas por diseño.

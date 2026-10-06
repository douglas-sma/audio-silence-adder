#!/bin/bash
# Activa el entorno virtual y ejecuta la herramienta.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"

# Verificar si el entorno virtual existe
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Error: No se encontró el entorno virtual"
    echo "💡 Ejecuta: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activar entorno virtual
source "$VENV_PATH/bin/activate"

# Sin argumentos -> CLI interactivo. Con argumentos -> CLI por argumentos.
if [ $# -gt 0 ]; then
    python "$SCRIPT_DIR/add_silence.py" "$@"
else
    python "$SCRIPT_DIR/cli.py"
fi

#!/bin/bash
# Script para activar el entorno virtual y ejecutar la herramienta

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

echo "🎵 Agregador de Silencio - Entorno activado"
echo "🚀 Uso:"
echo "   • Script simple: python simple_silence.py"
echo "   • Script avanzado: python add_silence.py archivo.mp3 --silencio 1.5"
echo "   • Ayuda: python add_silence.py --help"
echo ""

# Si se pasan argumentos, ejecutar el script principal
if [ $# -gt 0 ]; then
    python "$SCRIPT_DIR/add_silence.py" "$@"
else
    # Si no hay argumentos, abrir shell con entorno activado
    exec "$SHELL"
fi

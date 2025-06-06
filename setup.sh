#!/bin/bash

VENV_DIR=".venv"

echo "🛠 Setting up Python virtual environment for docAnalyser..."

# Remove old venv if it exists
if [ -d "$VENV_DIR" ]; then
    echo "🧹 Removing existing virtual environment at $VENV_DIR"
    rm -rf "$VENV_DIR"
fi

# Create new virtual environment
echo "🐍 Creating virtual environment at $VENV_DIR"
python3 -m venv "$VENV_DIR"

# Activate it for this script
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing Python dependencies from requirements.txt"
pip install -r requirements.txt

# Completion message
echo ""
echo "✅ Setup complete!"
if [[ "$0" == "$BASH_SOURCE" ]]; then
    echo "❗ Virtual environment is ready, but not active in this shell."
    echo "👉 To activate it later, run: source $VENV_DIR/bin/activate"
else
    echo "🟢 Virtual environment '$VENV_DIR' is activated."
fi

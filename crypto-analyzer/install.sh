#!/bin/bash

echo "🚀 Crypto Analyzer - Script de Instalação para Linux/Mac"
echo ""

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Python3 encontrado"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ Python encontrado"
else
    echo "❌ Python não foi encontrado!"
    echo ""
    echo "📋 Para resolver:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo ""
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "📋 Versão do Python: $PYTHON_VERSION"

# Instalar dependências
echo ""
echo "📦 Instalando dependências..."
$PYTHON_CMD -m pip install --user -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

# Tornar arquivos executáveis
chmod +x src/main.py
chmod +x setup_test.py

# Executar testes
echo ""
echo "🧪 Executando testes..."
$PYTHON_CMD setup_test.py

echo ""
echo "✨ Instalação concluída!"
echo ""
echo "💡 Para usar:"
echo "   $PYTHON_CMD src/main.py"
echo "   ou"
echo "   ./src/main.py  # se tiver shebang"
echo ""
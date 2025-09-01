#!/bin/bash

# Multi-Agent Discussion System Environment Setup

echo "🚀 Setting up Multi-Agent Discussion System Environment..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment  
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To activate the environment and run the system:"
echo "  source venv/bin/activate"
echo "  python3 src/main.py"
echo ""
echo "To run in demo mode (no API keys needed):"
echo "  source venv/bin/activate" 
echo "  python3 src/main.py --demo"
echo ""
echo "To deactivate the environment when done:"
echo "  deactivate"
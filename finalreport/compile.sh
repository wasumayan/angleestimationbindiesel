#!/bin/bash
# Compilation script for Final_Project_Report.tex
# This script compiles the LaTeX document twice to resolve all references

set -e  # Exit on error

echo "=========================================="
echo "Compiling Final Project Report"
echo "=========================================="
echo ""

# Check if pdflatex is available
if ! command -v pdflatex &> /dev/null; then
    echo "ERROR: pdflatex not found!"
    echo ""
    echo "Please install LaTeX first:"
    echo "  brew install --cask basictex"
    echo ""
    echo "Then add to PATH:"
    echo '  eval "$(/usr/libexec/path_helper)"'
    echo ""
    echo "Or restart your terminal after installation."
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

echo "Step 1/2: First compilation (generating references)..."
pdflatex -interaction=nonstopmode Final_Project_Report.tex > /dev/null 2>&1 || {
    echo "First compilation had warnings/errors. Showing output:"
    pdflatex -interaction=nonstopmode Final_Project_Report.tex
}

echo ""
echo "Step 2/2: Second compilation (resolving references)..."
pdflatex -interaction=nonstopmode Final_Project_Report.tex > /dev/null 2>&1 || {
    echo "Second compilation had warnings/errors. Showing output:"
    pdflatex -interaction=nonstopmode Final_Project_Report.tex
}

echo ""
echo "=========================================="
if [ -f "Final_Project_Report.pdf" ]; then
    echo "✅ SUCCESS: PDF generated!"
    echo "   File: $(pwd)/Final_Project_Report.pdf"
    echo "   Size: $(ls -lh Final_Project_Report.pdf | awk '{print $5}')"
    echo ""
    echo "Opening PDF..."
    open Final_Project_Report.pdf 2>/dev/null || echo "   (Run 'open Final_Project_Report.pdf' to view)"
else
    echo "❌ ERROR: PDF not generated. Check errors above."
    exit 1
fi
echo "=========================================="


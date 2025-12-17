# Installing LaTeX for Local Compilation

## Quick Install (macOS)

Run this command in your terminal:

```bash
brew install --cask basictex
```

After installation completes, add LaTeX to your PATH:

```bash
eval "$(/usr/libexec/path_helper)"
```

Or simply **restart your terminal** - the path will be set automatically.

## Verify Installation

Check that pdflatex is available:

```bash
pdflatex --version
```

You should see version information.

## Compile the Report

Once LaTeX is installed, you can compile using:

```bash
cd /Users/Mayan/Documents/CarLab/angleestimationbindiesel/finalreport
./compile.sh
```

Or manually:

```bash
pdflatex Final_Project_Report.tex
pdflatex Final_Project_Report.tex  # Run twice for references
```

## Alternative: Use Overleaf (No Installation Needed)

If you prefer not to install LaTeX locally, you can use Overleaf:
1. Go to https://www.overleaf.com
2. Create a new project
3. Upload all files
4. Click "Recompile"

See `OVERLEAF_SETUP.md` for detailed instructions.


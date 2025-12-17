# How to Compile the LaTeX Report

## Prerequisites

You need a LaTeX distribution installed:
- **Mac**: MacTeX or BasicTeX
- **Windows**: MiKTeX or TeX Live
- **Linux**: `sudo apt-get install texlive-full` (or similar)

## Compilation Steps

### Option 1: Using pdflatex (Command Line)

```bash
cd /Users/Mayan/Documents/CarLab/angleestimationbindiesel/finalreport
pdflatex Final_Project_Report.tex
pdflatex Final_Project_Report.tex  # Run twice for references
```

### Option 2: Using Overleaf (Online - Recommended)

1. Go to https://www.overleaf.com
2. Create a new project
3. Upload `Final_Project_Report.tex`
4. Upload all images from `diagrams/` and `data/` folders
5. Upload all code files from `code/` folder
6. Click "Recompile"

### Option 3: Using LaTeX Editor (TeXShop, TeXworks, etc.)

1. Open `Final_Project_Report.tex` in your LaTeX editor
2. Click "Typeset" or "Compile"
3. Run twice to resolve all references

## Required LaTeX Packages

The document uses these packages (usually included in full LaTeX distributions):
- `graphicx` - For images
- `listings` - For code
- `xcolor` - For colors
- `hyperref` - For hyperlinks
- `amsmath` - For equations
- `booktabs` - For tables
- `float` - For figure placement
- `caption` - For captions
- `subcaption` - For subfigures
- `fancyhdr` - For headers/footers

If you get package errors, install them:
```bash
# Mac (MacTeX)
tlmgr install <package-name>

# Linux
sudo apt-get install texlive-<package-name>
```

## Before Compiling

1. **Add missing images** (see `IMAGES_TO_ADD.md`):
   - Physical layout diagram
   - Buck converter photo
   - Motor inverter circuit diagram
   - CAD drawing
   - Pose detection screenshot

2. **Create hardware folder**:
   ```bash
   mkdir -p hardware
   ```

3. **Check image paths**: Make sure all images are in the correct folders

## Troubleshooting

### "File not found" errors
- Check that image paths are correct
- Make sure images are in the right folders
- Use relative paths (they should work if you compile from `finalreport/` folder)

### Code listings too long
- The code files are included in full
- If PDF is too large, you can:
  - Comment out some code sections
  - Use `\lstinputlisting[firstline=X, lastline=Y]` to show only parts
  - Move some code to separate appendix sections

### Missing references
- Run `pdflatex` twice (needed for cross-references)
- Or run: `pdflatex → bibtex → pdflatex → pdflatex` (if using bibliography)

## Output

After compilation, you'll get:
- `Final_Project_Report.pdf` - Your complete report!

## Customization

To customize:
- **Author name**: Edit line with `\author{Your Name}`
- **Date**: Edit `\date{\today}` or set specific date
- **Colors**: Edit color definitions at the top
- **Page margins**: Edit `\geometry{margin=1in}`

## Quick Test

To test if everything works:
1. Comment out sections with missing images (add `%` before `\includegraphics`)
2. Compile
3. Check if PDF generates successfully
4. Add images one by one


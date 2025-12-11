# NCNN Installation for Raspberry Pi

## Quick Answer

**Good news:** The `ultralytics` package automatically handles NCNN models! When you use an NCNN model, ultralytics will automatically install the required `ncnn` package if it's not already installed.

## What You Need

### 1. Standard Dependencies (Already in requirements.txt)

Install the standard requirements first:

```bash
pip install -r requirements.txt
```

This includes:
- `ultralytics>=8.0.0` - Handles NCNN models automatically
- `torch>=2.0.0` - Still needed (ultralytics uses it internally)
- Other standard dependencies

### 2. NCNN Package (Auto-Installed)

When you first load an NCNN model, ultralytics will automatically:
- Detect that `ncnn` package is missing
- Auto-install it via `pip install ncnn`
- Install the correct ARM version for Raspberry Pi

**You don't need to manually install `ncnn`** - it happens automatically!

### 3. Verify Installation

After pulling the latest code and installing requirements, test NCNN model loading:

```bash
python3 -c "from ultralytics import YOLO; model = YOLO('yolo11n-pose_ncnn_model'); print('✓ NCNN model loaded!')"
```

If `ncnn` is missing, ultralytics will auto-install it (you'll see a message about "AutoUpdate").

## Installation Steps on Pi

### Step 1: Pull Latest Code

```bash
cd ~/path/to/bindiesel
git pull origin main
```

### Step 2: Install/Update Requirements

```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Install/update requirements
pip install -r requirements.txt --upgrade
```

### Step 3: Test NCNN Model

```bash
# This will auto-install ncnn if needed
python3 -c "from ultralytics import YOLO; m = YOLO('yolo11n-pose_ncnn_model'); print('Success!')"
```

### Step 4: Verify Models Exist

```bash
ls -la *_ncnn_model/
```

You should see:
- `yolo11n_ncnn_model/`
- `yolo11n-pose_ncnn_model/`
- `yolo11n-obb_ncnn_model/`

## Troubleshooting

### If NCNN Auto-Install Fails

If ultralytics fails to auto-install `ncnn`, manually install it:

```bash
pip install ncnn
```

**Note:** On Raspberry Pi (ARM architecture), ultralytics will automatically install the ARM-compatible version of `ncnn`.

### If Models Don't Load

1. **Check models exist:**
   ```bash
   ls -la *_ncnn_model/
   ```

2. **Check config.py:**
   ```python
   USE_NCNN = True  # Should be True
   ```

3. **Try fallback to PyTorch:**
   ```python
   # In config.py
   USE_NCNN = False  # Temporarily disable NCNN
   ```

### Python 3.13.5 Compatibility

Python 3.13.5 on Raspberry Pi should work fine with:
- `ultralytics>=8.0.0` (supports Python 3.8+)
- `ncnn` (has ARM builds for Python 3.11+)

If you encounter issues, check:
```bash
python3 --version  # Should show 3.13.5
pip3 --version    # Should be recent version
```

## Summary

**Minimal extra steps needed:**
1. ✅ Pull latest code (models are already converted)
2. ✅ Run `pip install -r requirements.txt` (if not already done)
3. ✅ Test loading an NCNN model (auto-installs `ncnn` if needed)
4. ✅ Done!

The NCNN models are already in the repository, so you don't need to convert them on the Pi. Just pull the code and run!


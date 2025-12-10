# What to Do After Cloning the Repository

Follow these steps **after** you've cloned the repository on your Raspberry Pi.

---

## Step 1: Navigate to Project Directory

```bash
cd ~/Desktop/bindiesel
```

*(Or wherever you cloned it)*

---

## Step 2: Create Virtual Environment

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

**Verify you're in venv (should show `(venv)` in prompt):**
```bash
which python
```

---

## Step 3: Upgrade Pip

```bash
pip install --upgrade pip
```

---

## Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**This may take 10-15 minutes.**

**If you get numpy/opencv conflicts:**
```bash
pip install opencv-contrib-python
```

**If ultralytics not found:**
```bash
pip install ultralytics --upgrade
```

---

## Step 5: Create .env File

```bash
nano .env
```

**Add these lines (replace with your actual keys):**
```
PICOVOICE_ACCESS_KEY=your_picovoice_key_here
OPENAI_API_KEY=your_openai_key_here
```

**Save and exit:**
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter` to save

**Verify .env file:**
```bash
cat .env
```

---

## Step 6: Pre-download YOLO Models (Optional)

**This will download the pose model (~6MB):**
```bash
python -c "from ultralytics import YOLO; YOLO('yolo11n-pose.pt')"
```

**Note:** Models will auto-download on first use if you skip this step.

---

## Step 7: Verify Wake Word Model

```bash
ls -la bin-diesel_en_raspberry-pi_v3_0_0/bin-diesel_en_raspberry-pi_v3_0_0.ppn
```

**If it doesn't exist:**
- Download from Picovoice console
- Place in `bin-diesel_en_raspberry-pi_v3_0_0/` folder

---

## Step 8: Test Installation

**Test Python imports:**
```bash
python -c "import cv2; import numpy; from ultralytics import YOLO; print('All imports OK!')"
```

**Test camera:**
```bash
libcamera-hello --list-cameras
```

**If camera not detected:**
```bash
sudo raspi-config
```
*Navigate to: Interface Options → Camera → Enable*

---

## Step 9: Test Components

**Test YOLO pose tracking:**
```bash
python test_yolo_pose_tracking.py --fps
```
*(Press Ctrl+C to exit)*

**Test hand gestures:**
```bash
python hand_gesture_controller.py
```
*(Press Ctrl+C to exit)*

---

## Step 10: Run Main System

```bash
python main.py
```

**You should see:**
- System initializing messages
- "Waiting for wake word: 'bin diesel'"
- Press Ctrl+C to exit

---

## Step 11: Set Up Auto-Activation (Optional)

**Add to ~/.bashrc for auto-activation:**
```bash
nano ~/.bashrc
```

**Add at the end:**
```bash
# Auto-activate bindiesel venv
cd ~/Desktop/bindiesel  # Your project path
source venv/bin/activate
```

**Save and exit:**
- Press `Ctrl+X`
- Press `Y`
- Press `Enter`

**Reload:**
```bash
source ~/.bashrc
```

---

## Quick Reference: Daily Use

**Pull latest changes:**
```bash
cd ~/Desktop/bindiesel
git pull
source venv/bin/activate  # If not auto-activated
```

**Run main system:**
```bash
python main.py
```

**Check git status:**
```bash
git status
```

**View recent changes:**
```bash
git log --oneline -5
```

---

## Troubleshooting

### If venv not activated:
```bash
cd ~/Desktop/bindiesel
source venv/bin/activate
```

### If imports fail:
```bash
pip install -r requirements.txt --upgrade
```

### If camera errors:
```bash
sudo raspi-config
# Interface Options → Camera → Enable
```

### If disk space low:
```bash
df -h
pip cache purge
```

---

**You're all set!** 🎉


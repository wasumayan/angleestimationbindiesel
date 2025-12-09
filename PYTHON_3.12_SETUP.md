# Python 3.12 Setup Guide for Raspberry Pi

This guide will help you install Python 3.12 on your Raspberry Pi and set it as the default version, replacing Python 3.13.

## Prerequisites

- Raspberry Pi with Raspberry Pi OS
- SSH access or direct terminal access
- sudo privileges

## Step 1: Check Current Python Version

First, verify your current Python version:

```bash
python3 --version
python3.13 --version  # If available
```

## Step 2: Install Python 3.12

### Option A: Using pyenv (Recommended - Clean and Isolated)

This is the cleanest method as it doesn't interfere with system Python:

```bash
# Install dependencies
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
liblzma-dev python3-openssl git

# Install pyenv
curl https://pyenv.run | bash

# Add pyenv to PATH (add to ~/.bashrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload shell
source ~/.bashrc

# Install Python 3.12.7 (latest 3.12.x)
pyenv install 3.12.7

# Set as global default
pyenv global 3.12.7

# Verify installation
python3 --version  # Should show 3.12.7
```

### Option B: Build from Source (Alternative)

If pyenv doesn't work, build Python 3.12 from source:

```bash
# Install build dependencies
sudo apt update
sudo apt install -y build-essential zlib1g-dev libncurses5-dev \
libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev \
libsqlite3-dev wget libbz2-dev

# Download Python 3.12.7 source
cd /tmp
wget https://www.python.org/ftp/python/3.12.7/Python-3.12.7.tgz
tar -xzf Python-3.12.7.tgz
cd Python-3.12.7

# Configure and build
./configure --enable-optimizations --prefix=/usr/local
make -j4  # Use 4 cores, adjust based on your Pi model
sudo make altinstall  # Use altinstall to avoid replacing system python3

# Create symlink
sudo ln -sf /usr/local/bin/python3.12 /usr/local/bin/python3

# Update alternatives
sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.12 1
sudo update-alternatives --config python3  # Select option 1
```

### Option C: Using deadsnakes PPA (Debian/Ubuntu-based)

**Note:** This may not work on Raspberry Pi OS, but worth trying:

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

## Step 3: Verify Python 3.12 Installation

```bash
# Check Python version
python3 --version
# Should output: Python 3.12.x

# Check pip version
python3 -m pip --version

# Check Python location
which python3
```

## Step 4: Update pip and Install Dependencies

```bash
# Upgrade pip
python3 -m pip install --upgrade pip

# Install MediaPipe and other dependencies
python3 -m pip install --break-system-packages mediapipe==0.10.11
python3 -m pip install --break-system-packages -r requirements.txt
```

## Step 5: Update Virtual Environment (if using venv)

If you're using a virtual environment, recreate it with Python 3.12:

```bash
# Remove old venv
rm -rf venv

# Create new venv with Python 3.12
python3.12 -m venv --system-site-packages venv

# Activate venv
source venv/bin/activate

# Verify Python version in venv
python --version  # Should show 3.12.x

# Install dependencies
pip install -r requirements.txt
```

## Step 6: Test MediaPipe Installation

```bash
python3 -c "import mediapipe as mp; print('MediaPipe version:', mp.__version__)"
```

If this works, MediaPipe is successfully installed!

## Step 7: Update System Python3 Symlinks (Optional)

If you want to make Python 3.12 the system default:

```bash
# Backup current python3
sudo mv /usr/bin/python3 /usr/bin/python3.backup

# Create symlink to Python 3.12
sudo ln -s /usr/local/bin/python3.12 /usr/bin/python3

# Or if using pyenv:
sudo ln -s $HOME/.pyenv/versions/3.12.7/bin/python3 /usr/bin/python3
```

**Warning:** Be careful with this step as some system scripts may depend on the original Python version.

## Step 8: Verify Everything Works

Test the combined detection script:

```bash
python3 test_mediapipe_combined.py --fps
```

## Troubleshooting

### Issue: MediaPipe installation fails

```bash
# Try installing specific version
python3 -m pip install --break-system-packages mediapipe==0.10.11

# If that fails, try without --break-system-packages
python3 -m pip install mediapipe==0.10.11
```

### Issue: "python3.12: command not found"

Make sure Python 3.12 is in your PATH:

```bash
# Check if it exists
which python3.12
ls -la /usr/local/bin/python3.12

# Add to PATH if needed
export PATH="/usr/local/bin:$PATH"
```

### Issue: picamera2 not working

```bash
# Reinstall picamera2
sudo apt install -y python3-picamera2
python3 -m pip install --break-system-packages picamera2
```

### Issue: OpenCV issues

```bash
# Reinstall opencv-python
python3 -m pip install --break-system-packages --upgrade opencv-python
```

## Python 3.12 Compatibility Notes

The codebase has been checked for Python 3.12 compatibility. Key points:

1. **MediaPipe**: Requires Python 3.8-3.12 (3.13 not yet supported)
2. **Type hints**: All type hints use Python 3.8+ syntax (compatible)
3. **f-strings**: Used throughout (Python 3.6+)
4. **No deprecated features**: Code uses modern Python features

## Reverting to Python 3.13 (if needed)

If you need to revert:

```bash
# If using pyenv
pyenv global 3.13.x

# If using alternatives
sudo update-alternatives --config python3  # Select Python 3.13

# If using symlinks
sudo rm /usr/bin/python3
sudo mv /usr/bin/python3.backup /usr/bin/python3
```

## References

- [Python 3.12 Release Notes](https://docs.python.org/3.12/whatsnew/3.12.html)
- [MediaPipe Installation](https://ai.google.dev/edge/mediapipe/solutions/setup_python)
- [pyenv Installation](https://github.com/pyenv/pyenv#installation)


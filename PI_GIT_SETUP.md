# Git Setup on Raspberry Pi

## Step 1: Install Git (if not already installed)

```bash
sudo apt update
```

```bash
sudo apt install -y git
```

```bash
git --version
```

---

## Step 2: Configure Git User

```bash
git config --global user.name "Your Name"
```

```bash
git config --global user.email "your.email@example.com"
```

**Verify configuration:**
```bash
git config --global --list
```

---

## Step 3: Set Up Authentication (Choose One Method)

### Method A: HTTPS with Credential Helper (Easiest)

**Install credential helper:**
```bash
sudo apt install -y git-credential-libsecret
```

**Configure credential helper:**
```bash
git config --global credential.helper libsecret
```

**When you clone/pull, Git will prompt for your GitHub username and password (or Personal Access Token).**

**Note:** GitHub no longer accepts passwords for HTTPS. You'll need a **Personal Access Token**:
1. Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Select scopes: `repo` (full control of private repositories)
4. Copy the token and use it as your password when Git prompts

---

### Method B: SSH Keys (More Secure, No Password Prompts)

**Generate SSH key:**
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
```

**Press Enter to accept default location (`~/.ssh/id_ed25519`)**

**Press Enter twice for no passphrase (or set one if you want extra security)**

**Start SSH agent:**
```bash
eval "$(ssh-agent -s)"
```

**Add SSH key to agent:**
```bash
ssh-add ~/.ssh/id_ed25519
```

**Display public key:**
```bash
cat ~/.ssh/id_ed25519.pub
```

**Copy the output (starts with `ssh-ed25519`)**

**Add to GitHub:**
1. Go to GitHub.com → Settings → SSH and GPG keys
2. Click "New SSH key"
3. Title: "Raspberry Pi"
4. Paste your public key
5. Click "Add SSH key"

**Test SSH connection:**
```bash
ssh -T git@github.com
```

**You should see: "Hi wasumayan! You've successfully authenticated..."**

**Update remote URL to use SSH:**
```bash
cd ~/Desktop/bindiesel  # After cloning
git remote set-url origin git@github.com:wasumayan/bindiesel.git
```

---

## Step 4: Clone Repository

**Navigate to desired location:**
```bash
cd ~/Desktop
```

**Clone the repository:**
```bash
git clone https://github.com/wasumayan/bindiesel.git bindiesel
```

**OR if using SSH (after setting up SSH keys):**
```bash
git clone git@github.com:wasumayan/bindiesel.git bindiesel
```

**Navigate into project:**
```bash
cd bindiesel
```

---

## Step 5: Set Up Branch Tracking (Optional but Recommended)

**Check current branch:**
```bash
git branch
```

**Set upstream tracking:**
```bash
git branch --set-upstream-to=origin/main main
```

**Now you can use:**
```bash
git pull  # Instead of git pull origin main
```

---

## Quick Reference Commands

**Pull latest changes:**
```bash
cd ~/Desktop/bindiesel
git pull
```

**Check status:**
```bash
git status
```

**View recent commits:**
```bash
git log --oneline -10
```

**View remote URL:**
```bash
git remote -v
```

---

## Troubleshooting

### If "Permission denied" with SSH:
```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

### If credential helper not working:
```bash
git config --global credential.helper store
```
*(Stores credentials in plain text - less secure but works)*

### If you need to change remote URL:
```bash
git remote set-url origin https://github.com/wasumayan/bindiesel.git
```
*(For HTTPS)*

```bash
git remote set-url origin git@github.com:wasumayan/bindiesel.git
```
*(For SSH)*

---

**Recommended:** Use SSH keys (Method B) for better security and no password prompts!


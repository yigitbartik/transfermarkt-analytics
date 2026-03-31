# 🚀 Startup Script Guide

**Version**: 2.0.0  
**Updated**: 2024-03-31

This guide explains how to use the included startup scripts to run Transfermarkt Analytics Pro.

---

## 📋 Quick Start

### Windows Users
```bash
# Simply double-click this file:
run.bat
```

### macOS/Linux Users
```bash
# Open Terminal in the project folder, then run:
chmod +x run.sh
./run.sh
```

**That's it!** The scripts handle everything automatically. ✅

---

## 🔧 What the Scripts Do

Both `run.bat` (Windows) and `run.sh` (macOS/Linux) automatically:

1. ✅ **Verify Python Installation**
   - Checks if Python 3.9+ is installed
   - Provides helpful error message if not
   - Shows Python version being used

2. ✅ **Create Virtual Environment**
   - Creates `venv/` folder if it doesn't exist
   - Isolates project dependencies
   - Prevents conflicts with system Python

3. ✅ **Install Dependencies**
   - Only runs on first startup
   - Installs packages from `requirements.txt`
   - Takes 2-3 minutes on first run
   - Subsequent runs are instant

4. ✅ **Launch Application**
   - Starts Streamlit server
   - Opens browser to `http://localhost:8501`
   - Shows helpful status messages
   - Handles port conflicts automatically

5. ✅ **Error Handling**
   - Provides clear error messages
   - Suggests solutions for common problems
   - Safe rollback on failure

---

## 💻 Windows Startup Script (`run.bat`)

### Features

- **Automatic venv creation and activation**
- **Friendly colored status messages**
- **Port conflict detection and handling**
- **Python version verification**
- **Detailed error messages with solutions**
- **Keeps window open on error for debugging**

### Usage

#### Method 1: Double-Click (Easiest)
1. Extract `transfermarkt-analytics-pro.zip`
2. **Double-click** `run.bat`
3. Script runs automatically
4. Browser opens with app

#### Method 2: Command Line
```bash
cd transfermarkt-analytics
run.bat
```

### What You'll See

```
=========================================
  Transfermarkt Analytics Pro v2.0
  Windows Startup Script
=========================================

[OK] Python 3.11.7 found

[SETUP] Creating virtual environment...
[1/3] Creating venv folder...
[2/3] Activating virtual environment...
[3/3] Installing dependencies (this may take 2-3 minutes)
  - Installing streamlit...
  - Installing pandas...
  - Installing plotly...
  [OK] Dependencies installed successfully

=========================================
  Starting Application
=========================================

[INFO] Opening at: http://localhost:8501
[INFO] Press Ctrl+C to stop the server
[INFO] First load may take 30 seconds...

Streamlit is running...
```

### Troubleshooting Windows Script

#### Problem: "Python not found"
**Solution**:
- Install Python from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation
- Restart your computer after installation
- Try again

#### Problem: "Port 8501 already in use"
**Solution**:
- Script automatically tries port 8502
- Or close the other app using port 8501
- Or use: `streamlit run app.py --server.port 8503`

#### Problem: Permission denied
**Solution**:
- Run Command Prompt as Administrator
- Try again

#### Problem: Script won't exit
**Solution**:
- Press `Ctrl+C` to stop Streamlit
- Close the window

---

## 🐧 macOS/Linux Startup Script (`run.sh`)

### Features

- **Automatic venv creation and activation**
- **Colored output for easy reading**
- **Python version checking (3.9+ required)**
- **Dependency installation tracking**
- **Port availability checking**
- **Detailed error messages with solutions**
- **Full source code transparency**

### Usage

#### Method 1: Direct Execution
```bash
cd transfermarkt-analytics
./run.sh
```

#### Method 2: Manual Activation
```bash
cd transfermarkt-analytics
chmod +x run.sh        # Make executable (one time only)
source run.sh          # Run it
```

#### Method 3: Long Form
```bash
bash ./run.sh
```

### What You'll See

```
=========================================
  Transfermarkt Analytics Pro v2.0
  macOS/Linux Startup Script
=========================================

[OK] Python 3.11 found

[INFO] Setting up virtual environment...
[OK] Virtual environment created
[INFO] Activating virtual environment...

[INFO] Installing dependencies (may take 2-3 minutes)...

Successfully installed streamlit-1.28.1
Successfully installed pandas-2.2.0
Successfully installed plotly-5.18.0
...

[OK] Dependencies installed successfully

[INFO] Launching Streamlit application...

=========================================
  Starting Application
=========================================

[OK] Opening at: http://localhost:8501

[INFO] Press Ctrl+C to stop the server
[INFO] First load may take 30 seconds...

Streamlit is running...
```

### Troubleshooting macOS/Linux Script

#### Problem: "Python 3 not found"
**Solution**:
```bash
# macOS with Homebrew
brew install python@3.11

# Ubuntu/Debian
sudo apt-get install python3.11

# Fedora/RHEL
sudo dnf install python3.11

# Alpine
apk add python3
```

#### Problem: "Permission denied" when running
**Solution**:
```bash
chmod +x run.sh
./run.sh
```

#### Problem: "python3-venv" error on Linux
**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install python3.11-venv

# Fedora
sudo dnf install python3.11-venv

# Alpine
apk add python3-venv
```

#### Problem: Port already in use
**Solution**:
- Script automatically finds next available port
- Or kill the process: `lsof -ti :8501 | xargs kill -9`
- Or specify port: `streamlit run app.py --server.port 8502`

#### Problem: "Permission denied" on app startup
**Solution**:
```bash
# Make sure you have write permissions
chmod 755 .

# Or run with appropriate permissions
sudo ./run.sh  # Not recommended unless necessary
```

---

## 🔄 Virtual Environment Explained

### What is a Virtual Environment?

A virtual environment is an isolated Python workspace that:
- ✅ Keeps project dependencies separate
- ✅ Prevents version conflicts with system Python
- ✅ Makes the project portable
- ✅ Allows multiple projects with different versions

### Where is it Created?

Both scripts create a `venv/` folder in your project directory:

```
transfermarkt-analytics/
├── app.py
├── config.py
├── requirements.txt
├── run.bat
├── run.sh
└── venv/                    ← Created by scripts
    ├── bin/ (macOS/Linux)
    ├── Scripts/ (Windows)
    └── lib/
        └── python3.11/
            └── site-packages/  ← All packages here
```

### Size

The virtual environment takes up about 200-300 MB. This is normal and expected.

### Managing the venv

**View size:**
```bash
du -sh venv/  # macOS/Linux
```

**Manually activate (optional):**
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**Deactivate (optional):**
```bash
deactivate
```

**Delete and recreate:**
```bash
# macOS/Linux
rm -rf venv
./run.sh

# Windows
rmdir /s venv
run.bat
```

---

## 📝 First Run Checklist

When running for the first time:

- [ ] Extracted ZIP file
- [ ] Navigated to `transfermarkt-analytics/` folder
- [ ] Run `run.bat` (Windows) or `./run.sh` (macOS/Linux)
- [ ] Wait for browser to open (might take 30 seconds)
- [ ] See Streamlit app at `http://localhost:8501`
- [ ] Dashboard loads successfully
- [ ] Click "Update Data" to fetch initial data

---

## 🔄 Subsequent Runs

After first setup:

- [ ] Simply run the script again
- [ ] It recognizes existing `venv/` folder
- [ ] Skips installation, just activates
- [ ] App starts in seconds
- [ ] Ready to use immediately

---

## ⚙️ Advanced: Manual Execution

If you prefer to run without scripts:

```bash
# 1. Create virtual environment
python -m venv venv           # Windows/macOS/Linux

# 2. Activate it
source venv/bin/activate      # macOS/Linux
# OR
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py

# 5. Deactivate when done
deactivate
```

---

## 🌍 Cross-Platform Notes

### Windows-Specific
- Uses `.bat` batch file format
- Automatically detects Python in PATH
- Shows Windows-style file paths
- Uses netstat to check port availability

### macOS-Specific
- Uses bash shell script
- Supports both Intel and Apple Silicon
- Uses `lsof` to check port availability
- May need Xcode command line tools
  ```bash
  xcode-select --install
  ```

### Linux-Specific
- Uses bash shell script
- Compatible with all distributions
- Uses `lsof` to check port availability
- May need additional package managers

---

## 🐛 Debug Mode

### Windows
Edit `run.bat` and change:
```batch
REM Remove >nul 2>&1 to see all output
python --version
```

### macOS/Linux
Run with debug output:
```bash
bash -x run.sh
```

---

## 🔐 Safety

The scripts:
- ✅ Only use Python's built-in `venv` module
- ✅ Don't require elevated permissions (except venv-venv)
- ✅ Don't modify system Python
- ✅ Are fully reversible (just delete `venv/`)
- ✅ Don't install to system `site-packages`

---

## 📊 Performance

### First Run
- Virtual environment creation: 5-10 seconds
- Dependency installation: 1-2 minutes
- App startup: 30 seconds
- **Total**: 2-3 minutes

### Subsequent Runs
- Activation: 1-2 seconds
- App startup: 10-30 seconds
- **Total**: < 1 minute

---

## 🆘 Need Help?

1. **Check error message** - Scripts provide helpful error text
2. **Review requirements** - Ensure Python 3.9+ installed
3. **Check permissions** - Make sure you can write to folder
4. **Verify internet** - Some downloads needed on first run
5. **Disk space** - Need at least 500 MB free

---

## 💡 Tips & Tricks

### Tip 1: Run in Background (Advanced)

**macOS/Linux:**
```bash
./run.sh &
```

**Windows (PowerShell):**
```powershell
Start-Process run.bat
```

### Tip 2: Create Custom Launcher

**macOS:**
Create `start.command`:
```bash
#!/bin/bash
cd "$(dirname "$0")"
./run.sh
```

**Linux:**
Create `start.sh` with same content

**Windows:**
Create `start.cmd`:
```batch
@echo off
call run.bat
```

### Tip 3: Different Port

Without editing script:
```bash
# macOS/Linux
streamlit run app.py --server.port 8502

# Windows
streamlit run app.py --server.port 8502
```

### Tip 4: Read-Only Project Folder

If folder is read-only:
1. Copy entire folder to new location
2. Run script from new location
3. Or contact administrator for write permissions

---

## 📞 Troubleshooting Checklist

| Issue | Check | Solution |
|-------|-------|----------|
| Python not found | `python --version` | Install Python 3.9+ |
| Permission denied | File permissions | Run: `chmod +x run.sh` |
| Port in use | `lsof -i :8501` | Use port 8502+ or close app |
| venv won't create | Disk space | Free up 500 MB+ |
| Slow install | Internet speed | Normal on first run |
| Dependencies fail | Internet connection | Check connectivity |

---

## 📚 Related Files

- **README.md** - Full documentation
- **QUICKSTART.md** - Quick reference
- **INSTALLATION_GUIDE.md** - Detailed setup
- **requirements.txt** - Python packages list
- **config.py** - Application configuration

---

## 📋 Script Comparison

| Feature | run.bat | run.sh |
|---------|---------|--------|
| Platform | Windows | macOS/Linux |
| Port detection | netstat | lsof |
| Colors | Limited | Full ANSI |
| Error handling | Batch | Bash |
| Portability | Windows only | Universal Unix |

---

## ✅ Summary

The startup scripts make running the application **extremely easy**:

```
Windows: Double-click run.bat
macOS/Linux: ./run.sh
```

That's literally all you need to do! The scripts handle:
- Python checking
- Virtual environment setup
- Dependency installation
- Port conflict resolution
- Error handling
- App startup

**Everything is automated!** 🚀

---

**For more help, see:**
- INSTALLATION_GUIDE.md - Detailed troubleshooting
- README.md - Full documentation
- QUICKSTART.md - Quick reference

---

**Version**: 2.0.0  
**Last Updated**: 2024-03-31  
**Status**: Production Ready ✅

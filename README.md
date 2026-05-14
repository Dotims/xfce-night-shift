# XFCE Night Shift

A color temperature tray app for XFCE on Arch Linux.  
Reduces blue light by adjusting the screen temperature via `redshift` (X11) or `gammastep` (Wayland).

The icon lives in the notification area of the panel. Click it to open a slider popup.

---

## Features

- Panel tray icon (moon/sun) with tooltip showing current state
- Popup with a slider (1000 K – 6500 K)
- Editable temperature field (type a value directly)
- Quick presets: Day / Office / Sunset / Night / Deep
- Enable / disable toggle
- Remembers last setting in `~/.config/night-shift.json`
- Auto-detects `redshift` (X11) or `gammastep` (Wayland)

---

## Requirements

| Package | Install |
|---------|---------|
| `python` | pre-installed |
| `python-gobject` | `sudo pacman -S python-gobject` |
| `redshift` (X11) | `sudo pacman -S redshift` |
| `gammastep` (Wayland) | `sudo pacman -S gammastep` |

---

## Installation

```bash
# 1. Install system dependencies
sudo pacman -S python-gobject redshift   # X11 / XFCE

# 2. Clone and install
git clone https://github.com/YOUR_USERNAME/xfce-night-shift.git
cd xfce-night-shift
chmod +x install.sh
./install.sh
```

The installer:
- Copies the package to `~/.local/lib/night-shift/`
- Installs the `night-shift` launcher to `~/.local/bin/`
- Creates an autostart entry so the icon appears automatically after login

Make sure `~/.local/bin` is in your `PATH`:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Usage

```bash
night-shift          # start (shows tray icon)
python -m night_shift  # alternative (run from project directory)
```

- **Left-click** tray icon → open / close slider popup
- **Right-click** tray icon → Turn ON/OFF or Quit
- Popup closes on `Escape` or when it loses focus

---

## Project structure

```
night_shift/
├── app.py        # main coordinator (state, popup placement)
├── backend.py    # redshift / gammastep interface
├── config.py     # constants + JSON load/save
├── popup.py      # GTK popup window widget
├── style.py      # minimal CSS (border only, rest uses GTK theme)
├── tray.py       # StatusIcon + right-click menu
├── __init__.py
└── __main__.py   # entry point for python -m night_shift
night-shift       # thin launcher script
install.sh        # installer
uninstall.sh      # uninstaller
pyproject.toml    # packaging metadata
```

---

## Temperature reference

| Kelvin | Feel |
|--------|------|
| 6500 K | Neutral white (daylight) |
| 5000 K | Office / cool white |
| 3400 K | Warm / sunset |
| 2300 K | Night lamp |
| 1000 K | Deep amber |

---

## Uninstall

```bash
./uninstall.sh
```

---

## License

MIT

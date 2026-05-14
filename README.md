# XFCE Night Shift

A native color temperature panel plugin for XFCE on Arch Linux.  
Reduces blue light by adjusting the screen temperature via `redshift` (X11) or `gammastep` (Wayland).

Instead of using a system tray icon, this plugin runs natively in the XFCE Panel (via a minimal C wrapper) and spawns a beautiful Python/GTK popup window with controls.

---

## Features

- Native XFCE Panel plugin (addable via *Panel Preferences → Items*)
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
| `xfce4-panel` (headers) | pre-installed or `xfce4-dev-tools` |
| `gtk3` (headers) | pre-installed |
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
sudo ./install.sh
```

**After installation:**
1. Restart your panel to load the new module:
   ```bash
   xfce4-panel -r
   ```
2. Right-click your panel → **Panel Preferences** → **Items** tab.
3. Click the **+** (Add) button.
4. Search for **Night Shift** and click **Add**.

---

## Architecture

XFCE 4.20 removed the ability to use purely external scripts (`X-XFCE-Exec`) as panel plugins. This project solves this elegantly:

1. **`c_plugin/`**: A minimal native C wrapper (`libnightshift.so`) compiled and loaded directly by `xfce4-panel`. It draws the panel button and moon icon.
2. **Click Event**: When the panel button is clicked, the C plugin gets its screen coordinates and spawns the Python GTK application.
3. **`night-shift-py`**: The Python popup receives its exact coordinates from the C wrapper, draws the UI seamlessly next to the panel, modifies the backend state, and cleanly exits when focus is lost.

```text
xfce4-panel 
  └── libnightshift.so (C Plugin)
         ├── Draws Panel Button 
         └── On Click: Spawns `night-shift-py --x X --y Y`
                 └── Python GTK Window (Slider, Presets, Redshift API)
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
sudo ./uninstall.sh
```

---

## License

MIT

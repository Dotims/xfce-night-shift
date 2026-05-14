#!/usr/bin/env bash
# Night Shift – Installer for Arch Linux / XFCE
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GRN='\033[0;32m'; YLW='\033[1;33m'; CYN='\033[0;36m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GRN}[OK]${NC}  $*"; }
info() { echo -e "${CYN}[..]${NC}  $*"; }
warn() { echo -e "${YLW}[!!]${NC}  $*"; }
err()  { echo -e "${RED}[ERR]${NC} $*"; exit 1; }

echo -e "\n${CYN}Night Shift Installer${NC}\n"

# 1. Check python-gobject
info "Checking python-gobject..."
python3 -c "import gi; gi.require_version('Gtk','3.0'); from gi.repository import Gtk" \
    || err "Missing python-gobject.  Run: sudo pacman -S python-gobject"
ok "python-gobject OK"

# 2. Check backend
if   command -v redshift   &>/dev/null; then ok "Backend: redshift"
elif command -v gammastep  &>/dev/null; then ok "Backend: gammastep"
else
    warn "No backend found.  Install one of:"
    echo "    sudo pacman -S redshift    (X11/XFCE)"
    echo "    sudo pacman -S gammastep   (Wayland)"
    read -rp "Continue anyway? [y/N] " a; [[ "$a" =~ ^[Yy]$ ]] || exit 1
fi

# 3. Install via pip (editable install — night_shift package stays in project dir)
info "Installing with pip..."
pip install --user -e "$DIR" --quiet \
    || err "pip install failed. Try: pip install --user -e $DIR"
ok "Package installed (pip --user)"

# 4. Verify the launcher is in PATH
LAUNCHER="$(python3 -m site --user-base)/bin/night-shift"
if command -v night-shift &>/dev/null; then
    ok "Launcher in PATH: $(command -v night-shift)"
else
    warn "Launcher not in PATH yet."
    echo "  Add to ~/.bashrc or ~/.zshrc:"
    echo "    export PATH=\"\$(python3 -m site --user-base)/bin:\$PATH\""
fi

# 5. Autostart entry
AUTOSTART="$HOME/.config/autostart"
mkdir -p "$AUTOSTART"
EXEC_PATH="$(python3 -m site --user-base)/bin/night-shift"
cat > "$AUTOSTART/night-shift.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Night Shift
Comment=Color temperature tray icon
Exec=$EXEC_PATH
Icon=weather-clear-night
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
ok "Autostart: $AUTOSTART/night-shift.desktop"

echo -e "\n${GRN}Done!${NC}\n"
echo "  Start now:   night-shift"
echo "  Or directly: python -m night_shift"
echo ""
echo "  The tray icon appears in the panel notification area."
echo "  It will start automatically on every login."

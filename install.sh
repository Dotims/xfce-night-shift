#!/usr/bin/env bash
# Night Shift – XFCE Panel Plugin Installer
# Installs a native C plugin (.so) + Python GTK app via GtkPlug/GtkSocket
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GRN='\033[0;32m'; YLW='\033[1;33m'; CYN='\033[0;36m'; RED='\033[0;31m'; NC='\033[0m'
ok()   { echo -e "${GRN}[OK]${NC}  $*"; }
info() { echo -e "${CYN}[..]${NC}  $*"; }
err()  { echo -e "${RED}[ERR]${NC} $*"; exit 1; }

echo -e "\n${CYN}Night Shift – XFCE Panel Plugin Installer${NC}\n"

[ "$(id -u)" -eq 0 ] || err "Run with sudo:  sudo ./install.sh"

# 1. Check dependencies
info "Checking python-gobject..."
python3 -c "import gi; gi.require_version('Gtk','3.0'); from gi.repository import Gtk" 2>/dev/null \
    || err "Missing python-gobject.  Run: sudo pacman -S python-gobject"
ok "python-gobject"

if   command -v redshift  &>/dev/null; then ok "Backend: redshift"
elif command -v gammastep &>/dev/null; then ok "Backend: gammastep"
else echo -e "${YLW}[!!]${NC}  No backend – install: sudo pacman -S redshift"; fi

# 2. Build the C plugin
info "Building C plugin..."
cd "$DIR/c_plugin"
make clean 2>/dev/null || true
make 2>&1 | grep -v "^gcc" || true
[ -f libnightshift.so ] || err "Build failed — see errors above"
ok "libnightshift.so built"
cd "$DIR"

# 3. Install files
info "Installing plugin .so..."
install -Dm755 c_plugin/libnightshift.so /usr/lib/xfce4/panel/plugins/libnightshift.so
ok "libnightshift.so → /usr/lib/xfce4/panel/plugins/"

info "Installing Python launcher..."
install -Dm755 night-shift-py /usr/lib/xfce4/panel/plugins/night-shift-py
ok "night-shift-py → /usr/lib/xfce4/panel/plugins/"

info "Installing Python package..."
rm -rf /usr/lib/night-shift
mkdir -p /usr/lib/night-shift
cp -r night_shift /usr/lib/night-shift/
ok "night_shift package → /usr/lib/night-shift/"

info "Installing .desktop..."
install -Dm644 night-shift.desktop /usr/share/xfce4/panel/plugins/night-shift.desktop
ok "night-shift.desktop → /usr/share/xfce4/panel/plugins/"

info "Installing background service launcher..."
install -Dm755 night-shift /usr/bin/night-shift
ok "night-shift → /usr/bin/"

info "Configuring autostart..."
mkdir -p /etc/xdg/autostart
cat << 'EOF' > /etc/xdg/autostart/night-shift-autostart.desktop
[Desktop Entry]
Type=Application
Name=Night Shift
Comment=Color temperature background service
Exec=/usr/bin/night-shift --headless
Icon=weather-clear-night
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
ok "Autostart configured → /etc/xdg/autostart/"

echo ""
echo -e "${GRN}Installation complete!${NC}"
echo ""
echo "  Now restart the panel (as your normal user, NOT sudo):"
echo "      xfce4-panel -r"
echo ""
echo "  Then: Panel → right-click → Panel Preferences → Items → Add"
echo "        Search: Night Shift → Add"

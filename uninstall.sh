#!/usr/bin/env bash
# Night Shift XFCE Plugin – Uninstaller
set -euo pipefail

GRN='\033[0;32m'; CYN='\033[0;36m'; NC='\033[0m'
ok()   { echo -e "${GRN}[OK]${NC}   $*"; }
info() { echo -e "${CYN}[..]${NC}   $*"; }

echo -e "\n${CYN}Night Shift XFCE Plugin – Uninstaller${NC}\n"

remove() { [ -e "$1" ] && rm -f "$1" && ok "Removed: $1" || info "Not found: $1"; }

remove "/usr/lib/xfce4/panel/plugins/libnightshift.so"
remove "/usr/lib/xfce4/panel/plugins/night-shift-py"
remove "/usr/share/xfce4/panel/plugins/night-shift.desktop"
remove "/usr/bin/night-shift"
remove "/etc/xdg/autostart/night-shift-autostart.desktop"
[ -d "/usr/lib/night-shift" ] && rm -rf "/usr/lib/night-shift" && ok "Removed: /usr/lib/night-shift" || info "Not found: /usr/lib/night-shift"

read -rp "Remove config file (~/.config/xfce4/night-shift.json)? [y/N] " ans
[[ "$ans" =~ ^[Yy]$ ]] && remove "$HOME/.config/xfce4/night-shift.json"

# Reset color temperature
for cmd in redshift gammastep; do
    command -v "$cmd" &>/dev/null && { "$cmd" -x 2>/dev/null || true; ok "Temperature reset via $cmd"; break; }
done

echo -e "\n${GRN}Done.${NC} Remember to remove the item from the panel manually.\n"

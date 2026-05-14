#!/usr/bin/env bash
# Night Shift XFCE Plugin – Uninstaller
set -euo pipefail

GRN='\033[0;32m'; CYN='\033[0;36m'; NC='\033[0m'
ok()   { echo -e "${GRN}[OK]${NC}   $*"; }
info() { echo -e "${CYN}[..]${NC}   $*"; }

echo -e "\n${CYN}Night Shift XFCE Plugin – Uninstaller${NC}\n"

remove() { [ -e "$1" ] && rm -f "$1" && ok "Removed: $1" || info "Not found: $1"; }

remove "$HOME/.local/bin/night-shift-plugin"
remove "/usr/local/bin/night-shift-plugin"
remove "$HOME/.local/share/xfce4/panel/plugins/night-shift.desktop"
remove "/usr/share/xfce4/panel/plugins/night-shift.desktop"

read -rp "Remove config file (~/.config/xfce4/night-shift.json)? [y/N] " ans
[[ "$ans" =~ ^[Yy]$ ]] && remove "$HOME/.config/xfce4/night-shift.json"

# Reset color temperature
for cmd in redshift gammastep; do
    command -v "$cmd" &>/dev/null && { "$cmd" -x 2>/dev/null || true; ok "Temperature reset via $cmd"; break; }
done

echo -e "\n${GRN}Done.${NC} Remember to remove the item from the panel manually.\n"

"""System tray icon (Gtk.StatusIcon)."""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class TrayIcon:
    """Manages the status-bar icon and its right-click menu."""

    def __init__(self, *, on_click, on_toggle, on_quit) -> None:
        self._on_click  = on_click
        self._on_toggle = on_toggle
        self._on_quit   = on_quit
        self._enabled   = False

        self._icon = Gtk.StatusIcon()
        self._icon.connect('activate',   lambda *_: self._on_click())
        self._icon.connect('popup-menu', self._show_menu)
        self.refresh(enabled=False, temp=4500)

    def refresh(self, *, enabled: bool, temp: int) -> None:
        """Update icon and tooltip to reflect current state."""
        self._enabled = enabled
        self._icon.set_from_icon_name(
            'weather-clear-night' if enabled else 'weather-clear'
        )
        state = f"ON · {temp} K" if enabled else "OFF"
        self._icon.set_tooltip_text(f"Night Shift  [{state}]")

    def get_geometry(self):
        """Proxy to StatusIcon.get_geometry() for popup placement."""
        return self._icon.get_geometry()

    # ── Private ───────────────────────────────────────────────────────────────

    def _show_menu(self, icon, btn: int, t: int) -> None:
        menu  = Gtk.Menu()
        label = "Turn OFF" if self._enabled else "Turn ON"

        item_toggle = Gtk.MenuItem(label=label)
        item_toggle.connect('activate', lambda *_: self._on_toggle())
        menu.append(item_toggle)

        menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect('activate', lambda *_: self._on_quit())
        menu.append(item_quit)

        menu.show_all()
        menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, btn, t)

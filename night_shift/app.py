"""Main application coordinator — wires backend, tray and popup together."""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

from . import config
from .backend import Backend
from .popup   import PopupWindow
from .style   import CSS
from .tray    import TrayIcon


class NightShift:
    """
    Top-level coordinator.

    Responsibilities:
      - Owns the mutable state (temp, enabled).
      - Creates and wires TrayIcon ↔ PopupWindow ↔ Backend.
      - Handles popup placement relative to the panel.
      - Persists config on every state change.
    """

    def __init__(self, *, headless: bool = False) -> None:
        self._backend = Backend()
        cfg = config.load()
        self._temp    = cfg['temp']
        self._enabled = cfg['on']
        self._popup: PopupWindow | None = None

        if self._enabled:
            self._backend.apply(self._temp)

        if headless:
            return

        self._apply_css()

        self._tray = TrayIcon(
            on_click  = self._toggle_popup,
            on_toggle = self._toggle,
            on_quit   = self._quit,
        )
        self._tray.refresh(enabled=self._enabled, temp=self._temp)

    # ── CSS ───────────────────────────────────────────────────────────────────

    def _apply_css(self) -> None:
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    # ── Popup management ──────────────────────────────────────────────────────

    def _toggle_popup(self) -> None:
        if self._popup is None:
            self._popup = PopupWindow(
                temp            = self._temp,
                enabled         = self._enabled,
                on_temp_changed = self._on_temp_changed,
                on_toggle       = self._on_popup_toggle,
                on_preset       = self._on_preset,
            )
        if self._popup.get_visible():
            self._popup.hide()
        else:
            self._popup.show_all()
            self._place_popup()
            self._popup.present()

    def _place_popup(self) -> None:
        """Snap popup flush with the panel boundary, centred on the tray icon."""
        geo, work = self._monitor_areas()
        w_req = self._popup.get_preferred_width()[1]
        h_req = self._popup.get_preferred_height()[1]

        # Horizontal: centre on the tray icon
        ok, _screen, area, _orient = self._tray.get_geometry()
        icon_cx = (area.x + area.width // 2) if ok else (work.x + work.width - w_req // 2)
        x = max(work.x, min(icon_cx - w_req // 2, work.x + work.width - w_req))

        # Vertical: derive panel location from workarea vs full geometry
        bottom_panel_h = geo.height - work.height - work.y
        top_panel_h    = work.y

        if bottom_panel_h >= top_panel_h:
            y = work.y + work.height - h_req   # bottom panel → popup above
        else:
            y = work.y                          # top panel    → popup below

        self._popup.move(x, y)

    @staticmethod
    def _monitor_areas():
        """Return (geometry, workarea) for the primary monitor."""
        monitor = Gdk.Display.get_default().get_primary_monitor()
        return monitor.get_geometry(), monitor.get_workarea()

    # ── Callbacks from tray / popup ───────────────────────────────────────────

    def _on_temp_changed(self, temp: int) -> None:
        self._temp = temp
        self._tray.refresh(enabled=self._enabled, temp=temp)
        if self._enabled:
            self._backend.apply(temp)
        self._save()

    def _on_popup_toggle(self, enabled: bool) -> None:
        self._enabled = enabled
        self._tray.refresh(enabled=enabled, temp=self._temp)
        self._backend.apply(self._temp) if enabled else self._backend.reset()
        self._save()

    def _toggle(self) -> None:
        """Toggle from tray right-click menu."""
        self._enabled = not self._enabled
        if self._popup:
            self._popup.set_state(self._temp, self._enabled)
        self._tray.refresh(enabled=self._enabled, temp=self._temp)
        self._backend.apply(self._temp) if self._enabled else self._backend.reset()
        self._save()

    def _on_preset(self, temp: int) -> None:
        self._temp    = temp
        self._enabled = True
        if self._popup:
            self._popup.set_state(temp, True)
        self._tray.refresh(enabled=True, temp=temp)
        self._backend.apply(temp)
        self._save()

    def _quit(self) -> None:
        self._backend.reset()
        Gtk.main_quit()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _save(self) -> None:
        config.save({'temp': self._temp, 'on': self._enabled})

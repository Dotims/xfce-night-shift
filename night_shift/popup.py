"""Popup window: slider, spin-button and preset buttons."""

import math
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk
import cairo

from .config import TEMP_MIN, TEMP_MAX, PRESETS


class PopupWindow(Gtk.Window):
    """
    Floating popup attached to the panel edge.

    All user interactions are forwarded via callbacks:
      on_temp_changed(temp: int)  – slider or spin-button moved
      on_toggle(enabled: bool)    – toggle button clicked
      on_preset(temp: int)        – preset button clicked
    """

    def __init__(
        self,
        *,
        temp: int,
        enabled: bool,
        on_temp_changed,
        on_toggle,
        on_preset,
    ) -> None:
        super().__init__(type=Gtk.WindowType.TOPLEVEL)

        self._cb_temp   = on_temp_changed
        self._cb_toggle = on_toggle
        self._cb_preset = on_preset
        self._temp      = temp
        self._enabled   = enabled
        self._updating  = False   # re-entrancy guard: True while we update widgets programmatically

        self._scale:      Gtk.Scale        | None = None
        self._spin:       Gtk.SpinButton   | None = None
        self._btn_toggle: Gtk.ToggleButton | None = None
        self._box:        Gtk.Box          | None = None  # used in _on_draw for theme colour

        self._configure_window()
        self._build()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_state(self, temp: int, enabled: bool) -> None:
        """Sync all widgets to (temp, enabled) without triggering callbacks."""
        self._updating = True
        try:
            self._temp    = temp
            self._enabled = enabled

            if self._scale:
                self._scale.set_value(TEMP_MAX - temp + TEMP_MIN)
            if self._spin:
                self._spin.set_value(temp)
            if self._btn_toggle:
                self._btn_toggle.set_active(enabled)
                self._btn_toggle.set_label("Enabled" if enabled else "Disabled")
        finally:
            self._updating = False

    # ── Window setup ──────────────────────────────────────────────────────────

    def _configure_window(self) -> None:
        self.get_style_context().add_class('ns-popup')
        self.set_title("Night Shift")
        self.set_decorated(False)
        self.set_app_paintable(True)
        screen = self.get_screen()
        if screen and screen.is_composited():
            visual = screen.get_rgba_visual()
            if visual:
                self.set_visual(visual)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_resizable(False)
        self.connect('draw', self._on_draw)
        self.connect(
            'key-press-event',
            lambda w, e: w.hide() if e.keyval == Gdk.KEY_Escape else None,
        )
        self.connect('focus-out-event', lambda w, e: w.hide())

    def _on_draw(self, widget, cr: cairo.Context) -> bool:
        """Paint the rounded-rectangle background directly on the window surface.

        This must be done here (in the window's own draw handler) rather than
        via CSS border-radius on a child widget.  Child widgets draw *over* the
        compositor window surface without clipping its rectangular boundary, so
        any border-radius on a child leaves the corner pixels opaque/black.
        Drawing the rounded rect here operates on the surface itself, so the
        compositor correctly sees those corner pixels as fully transparent.
        """
        alloc = widget.get_allocation()
        w, h  = alloc.width, alloc.height
        r     = 6.0   # border-radius (keep in sync with CSS if changed)

        # Retrieve the theme background colour from the *inner box*, not the
        # window itself — the window's CSS is `background-color: transparent`
        # so querying it would return alpha=0 and produce a see-through popup.
        if self._box is not None:
            style = self._box.get_style_context()
        else:
            style = widget.get_style_context()
        bg = style.get_background_color(Gtk.StateFlags.NORMAL)

        # Step 1: clear the entire window surface to fully transparent so that
        # the compositor sees nothing in the corner regions outside the radius.
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()

        # Step 2: draw the rounded rectangle filled with the theme background.
        # OPERATOR_OVER writes with proper alpha so the compositor blends it.
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.new_sub_path()
        cr.arc(r,     r,     r,  math.pi,       1.5 * math.pi)  # top-left
        cr.arc(w - r, r,     r, -0.5 * math.pi, 0)              # top-right
        cr.arc(w - r, h - r, r,  0,             0.5 * math.pi)  # bottom-right
        cr.arc(r,     h - r, r,  0.5 * math.pi, math.pi)        # bottom-left
        cr.close_path()
        cr.set_source_rgba(bg.red, bg.green, bg.blue, bg.alpha)
        cr.fill_preserve()

        # Step 3: draw a subtle border on top.
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.30)
        cr.set_line_width(1.0)
        cr.stroke()

        return False

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self) -> None:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.get_style_context().add_class('ns-box')
        self._box = box
        self.add(box)

        box.pack_start(self._make_header(),    False, False, 0)
        box.pack_start(self._make_slider(),    False, False, 0)
        box.pack_start(self._make_end_labels(), False, False, 0)
        box.pack_start(self._make_spin_row(),  False, False, 0)
        box.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)
        box.pack_start(self._make_presets(),   False, False, 0)

    def _make_header(self) -> Gtk.Box:
        row = Gtk.Box(spacing=8)

        title = Gtk.Label(label="Night Shift")
        title.set_halign(Gtk.Align.START)
        row.pack_start(title, True, True, 0)

        self._btn_toggle = Gtk.ToggleButton(
            label="Enabled" if self._enabled else "Disabled"
        )
        self._btn_toggle.set_active(self._enabled)
        self._btn_toggle.connect('toggled', self._on_toggle_btn)
        row.pack_end(self._btn_toggle, False, False, 0)
        return row

    def _make_slider(self) -> Gtk.Scale:
        # Inverted: left = cool (6500 K), right = warm (1000 K)
        adj = Gtk.Adjustment(
            value=TEMP_MAX - self._temp + TEMP_MIN,
            lower=TEMP_MIN,
            upper=TEMP_MAX,
            step_increment=100,
            page_increment=500,
        )
        self._scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj
        )
        self._scale.set_draw_value(False)
        self._scale.set_size_request(260, -1)
        self._scale.connect('value-changed', self._on_slider)
        return self._scale

    def _make_end_labels(self) -> Gtk.Box:
        row = Gtk.Box()
        for text, pack in [("Cool", row.pack_start), ("Warm", row.pack_end)]:
            lbl = Gtk.Label(label=text)
            lbl.set_sensitive(False)
            pack(lbl, False, False, 0)
        return row

    def _make_spin_row(self) -> Gtk.Box:
        row = Gtk.Box(spacing=6)
        row.pack_start(Gtk.Label(label="Temperature:"), False, False, 0)

        adj = Gtk.Adjustment(
            value=self._temp,
            lower=TEMP_MIN,
            upper=TEMP_MAX,
            step_increment=100,
            page_increment=500,
        )
        self._spin = Gtk.SpinButton(adjustment=adj, climb_rate=100, digits=0)
        self._spin.set_width_chars(6)
        self._spin.connect('value-changed', self._on_spin)
        row.pack_start(self._spin, False, False, 0)
        row.pack_start(Gtk.Label(label="K"), False, False, 0)
        return row

    def _make_presets(self) -> Gtk.Box:
        row = Gtk.Box(spacing=4)
        row.set_halign(Gtk.Align.CENTER)
        for label, temp in PRESETS:
            btn = Gtk.Button(label=label)
            btn.connect('clicked', lambda _, t=temp: self._cb_preset(t))
            row.pack_start(btn, False, False, 0)
        return row

    # ── GTK callbacks ─────────────────────────────────────────────────────────

    def _on_toggle_btn(self, btn: Gtk.ToggleButton) -> None:
        if self._updating:
            return
        self._enabled = btn.get_active()
        btn.set_label("Enabled" if self._enabled else "Disabled")
        self._cb_toggle(self._enabled)

    def _on_slider(self, scale: Gtk.Scale) -> None:
        if self._updating:
            return
        temp = max(TEMP_MIN, min(TEMP_MAX,
                   int(TEMP_MAX - scale.get_value() + TEMP_MIN)))
        self._temp = temp
        # Sync spin without triggering _on_spin
        self._updating = True
        try:
            if self._spin:
                self._spin.set_value(temp)
        finally:
            self._updating = False
        self._cb_temp(temp)

    def _on_spin(self, spin: Gtk.SpinButton) -> None:
        if self._updating:
            return
        temp = int(spin.get_value())
        self._temp = temp
        # Sync slider without triggering _on_slider
        self._updating = True
        try:
            if self._scale:
                self._scale.set_value(TEMP_MAX - temp + TEMP_MIN)
        finally:
            self._updating = False
        self._cb_temp(temp)

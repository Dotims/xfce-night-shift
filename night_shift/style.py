"""GTK CSS - popup uses system theme; only border and padding are overridden."""

CSS = b"""
/* The window surface must be transparent so the compositor sees the rounded
   corners as fully see-through.  The actual background rectangle is drawn in
   Cairo inside PopupWindow._on_draw, which reads the colour from .ns-box's
   style context - so .ns-box keeps background-color for colour lookup, but
   border and border-radius are omitted (Cairo handles the rounded rect). */
window.ns-popup {
    background-color: transparent;
}
.ns-box {
    padding: 12px 14px;
    background-color: @theme_bg_color;   /* queried by Cairo _on_draw */
    border: none;                         /* border drawn by Cairo stroke */
}
"""

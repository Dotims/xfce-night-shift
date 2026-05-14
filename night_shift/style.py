"""GTK CSS - popup uses system theme; only border and padding are overridden."""

CSS = b"""
/* The window surface must be transparent so the compositor sees the rounded
   corners as fully see-through.  The actual background rectangle is drawn in
   Cairo inside PopupWindow._on_draw, which reads the colour from a dummy class.
   .ns-box must be transparent so it doesn't paint a sharp rectangle over our
   Cairo rounded corners. */
window.ns-popup {
    background-color: transparent;
}
.ns-box {
    padding: 12px 14px;
    background-color: transparent;        /* Must be transparent to reveal Cairo corners */
    border: none;                         /* border drawn by Cairo stroke */
}
/* Dummy class used purely to extract the theme background colour in Python */
.ns-theme-color {
    background-color: @theme_bg_color;
}
"""

"""GTK CSS — popup uses system theme; only border and padding are overridden."""

CSS = b"""
window.ns-popup {
    border: 1px solid rgba(128, 128, 128, 0.30);
    border-radius: 6px;
}
.ns-box {
    padding: 12px 14px;
}
"""

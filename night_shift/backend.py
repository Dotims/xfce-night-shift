"""Wrapper around redshift / gammastep CLI."""

import os
import subprocess


class Backend:
    """Detects and controls redshift or gammastep."""

    def __init__(self) -> None:
        self.name: str | None = self._detect()

    @property
    def available(self) -> bool:
        return self.name is not None

    def apply(self, temp: int) -> None:
        """Set a constant color temperature (one-shot mode)."""
        if self.name:
            subprocess.Popen(
                [self.name, '-P', '-O', str(temp)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def reset(self) -> None:
        """Remove all color adjustments."""
        if self.name:
            subprocess.Popen(
                [self.name, '-x'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    # ── Private ───────────────────────────────────────────────────────────────

    @staticmethod
    def _detect() -> str | None:
        wayland = (
            bool(os.environ.get('WAYLAND_DISPLAY'))
            or os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland'
        )
        candidates = ['gammastep', 'redshift'] if wayland else ['redshift', 'gammastep']
        for name in candidates:
            try:
                subprocess.run([name, '--help'], capture_output=True, timeout=2)
                return name
            except FileNotFoundError:
                pass
        return None

"""Entry point for `python -m night_shift`."""

import signal
import warnings
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

warnings.filterwarnings('ignore', category=DeprecationWarning)

from . import NightShift


def main() -> None:
    signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())
    signal.signal(signal.SIGINT,  lambda *_: Gtk.main_quit())
    NightShift()
    Gtk.main()


if __name__ == '__main__':
    main()

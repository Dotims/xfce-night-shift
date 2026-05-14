"""Entry point for `python -m night_shift`."""

import argparse
import os
import signal
import warnings
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

warnings.filterwarnings('ignore', category=DeprecationWarning)

from . import NightShift


def main() -> None:
    parser = argparse.ArgumentParser(description="Night Shift tray app")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--headless",
        action="store_true",
        help="Apply the saved temperature and exit (no tray UI)",
    )
    group.add_argument(
        "--tray",
        action="store_true",
        help="Force tray UI even when started by autostart",
    )
    args = parser.parse_args()

    auto_start = bool(os.environ.get("DESKTOP_AUTOSTART_ID"))
    headless = args.headless or (auto_start and not args.tray)

    signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())
    signal.signal(signal.SIGINT,  lambda *_: Gtk.main_quit())
    NightShift(headless=headless)
    if not headless:
        Gtk.main()


if __name__ == '__main__':
    main()

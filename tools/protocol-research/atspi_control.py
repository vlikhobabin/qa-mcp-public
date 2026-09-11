#!/usr/bin/env python3
"""AT-SPI control app: a minimal GTK3 window with a named, editable Entry. If THIS shows up in the AT-SPI
tree (with EditableText) but the 1C client does not, the a11y stack works and 1C simply does not expose its
UI via accessibility. Run with the same DISPLAY + DBUS_SESSION_BUS_ADDRESS + a11y env as the 1C client."""
import gi  # type: ignore

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # type: ignore  # noqa: E402

win = Gtk.Window(title="ATSPI_CONTROL_WINDOW")
win.set_default_size(300, 80)
entry = Gtk.Entry()
entry.set_text("control_value_123")
acc = entry.get_accessible()
acc.set_name("CONTROL_ENTRY")
win.add(entry)
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

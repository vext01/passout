# Copyright (c) 2014, Edd Barrett <vext01@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
# OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

try:
    from gi.repository import Gtk
except ImportError:
    print("No GTK support for Python found, cannot run tray")

import subprocess
import distutils.spawn

from passout import get_password_names_grouped, load_clipboard

NOTIFY_SEND = distutils.spawn.find_executable("notify-send")


class PasswordMenuItem(Gtk.MenuItem):
    """Each password has a PasswordMenuItem. We need this so we can
    store the underlying password name (complete with group prefix)
    inside the item."""

    def __init__(self, password_name, label):
        self.password_name = password_name
        Gtk.MenuItem.__init__(self, label)


class PassoutSysTrayApp(object):
    def __init__(self, cfg):
        self.cfg = cfg

        # Tray Icon itself
        self.tray = Gtk.StatusIcon()
        self.tray.set_from_stock(Gtk.STOCK_DIALOG_AUTHENTICATION)
        self.tray.connect('popup-menu', self.show_menu)
        # self.tray.set_tooltip("PassOut")
        self.tray.set_visible(True)

    def _notify(self, message):
        if NOTIFY_SEND:
            subprocess.check_call([NOTIFY_SEND, message])

    def clip_password(self, item):
        pwname = item.password_name

        load_clipboard(self.cfg, pwname)
        self._notify("Loaded password '%s' into clipboard" % pwname)

    def _add_items_to_menu(self, menu, item_dct, cur_path=tuple()):
        """Recursively add items to the menu"""

        for item, sub_items in item_dct.iteritems():
            sub_path = cur_path + (item, )

            if sub_items:  # i.e. non-empty dict
                menu_item = Gtk.MenuItem(item)
                sub_menu = Gtk.Menu()
                menu_item.set_submenu(sub_menu)
                self._add_items_to_menu(sub_menu, sub_items, sub_path)
            else:  # sub_items is an empty dict
                menu_item = PasswordMenuItem("__".join(sub_path), item)
                menu_item.connect('activate', self.clip_password)

            menu_item.show()
            menu.append(menu_item)

    def show_menu(self, icon, button, time):
        self.menu = Gtk.Menu()

        menu_dct = get_password_names_grouped()
        self._add_items_to_menu(self.menu, menu_dct)

        sep = Gtk.SeparatorMenuItem()
        sep.show()
        self.menu.append(sep)

        # Exit
        exit = Gtk.MenuItem("Exit")
        exit.show()
        self.menu.append(exit)
        exit.connect('activate', Gtk.main_quit)

        self.menu.popup(None, None, None, None, button, time)


def run_tray(cfg):
    PassoutSysTrayApp(cfg)
    Gtk.main()

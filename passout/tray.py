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
    import gtk
except ImportError:
    print("No GTK support for Python found, cannot run tray")


class PassoutSysTrayApp(object):
    def __init__(self, cfg):
        self.cfg = cfg

        # Tray Icon itself
        self.tray = gtk.StatusIcon()
        self.tray.set_from_stock(gtk.STOCK_DIALOG_AUTHENTICATION)
        self.tray.connect('popup-menu', self.show_menu)
        self.tray.set_tooltip("PassOut")
        self.tray.set_visible(True)

    def clip_password(self, item):
        pwname = item.get_label()

        from passout import put_password_into_clipboard
        put_password_into_clipboard(self.cfg, pwname)

    def show_menu(self, icon, button, time):
        self.menu = gtk.Menu()

        from passout import get_all_password_names
        for pwname in sorted(get_all_password_names()):
            item = gtk.MenuItem(pwname)
            item.show()
            self.menu.append(item)
            item.connect('activate', self.clip_password)

        self.menu.popup(None, None, gtk.status_icon_position_menu,
                        button, time, self.tray)

        sep = gtk.SeparatorMenuItem()
        sep.show()
        self.menu.append(sep)

        # Exit
        exit = gtk.MenuItem("Exit")
        exit.show()
        self.menu.append(exit)
        exit.connect('activate', gtk.main_quit)

        self.menu.popup(None, None, gtk.status_icon_position_menu,
                        button, time, self.tray)


def run_tray(cfg):
    PassoutSysTrayApp(cfg)
    gtk.main()

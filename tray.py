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
        self.tray.set_visible (True)

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

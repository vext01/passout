#!/usr/bin/env python2.7

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
"""
PassOut as a library.
"""

import os
import sys
import stat
import getpass
import subprocess
import collections

PASSOUT_HOME = os.environ.get("PASSOUT_HOME")
if not PASSOUT_HOME:
    PASSOUT_HOME = os.path.join(os.environ["HOME"], ".passout")

CRYPTO_DIR = os.path.join(PASSOUT_HOME, "crytpo_store")
CONFIG_FILE = os.path.join(PASSOUT_HOME, "passoutrc")


class PassOutError(Exception):
    pass


def _check_dirs():
    """ Check that the passout dot dir is there and looking right """
    dirs = [PASSOUT_HOME, CRYPTO_DIR]
    for d in dirs:
        if not os.path.exists(d):
            os.mkdir(d)
        if not os.path.isdir(d):
            raise PassOutError("'%s' is not a directory" % d)


def _get_pass_file(passname):
    _check_dirs()
    return os.path.join(CRYPTO_DIR, passname) + ".gpg"


def _sort_dict(dct):
    new_dct = collections.OrderedDict()

    for k, v in sorted(dct.items()):
        if not v:  # i.e. empty dict
            new_dct[k] = v
        else:
            new_dct[k] = _sort_dict(v)

    return new_dct


# //////// Exposed API functions below //////////////


def get_password(cfg, pwname, testing=False):
    pw_file = _get_pass_file(pwname)

    if not os.path.exists(pw_file):
        raise PassOutError("No password called '%s'" % pwname)

    # Have not found a way for this to work with mutt+msmtp without using
    # a GUI pinentry. /dev/tty not configured. Annoying XXX
    gpg_args = (cfg["gpg"], "-u", cfg["id"], "--no-tty", "-d", pw_file)

    # When we are testing we cannot pass a stdin.
    # (pytest capture upsets subprocess)
    if testing:
        stdin = None
    else:
        stdin = sys.stdin

    try:
        pipe = subprocess.Popen(
            gpg_args, stdin=stdin, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, universal_newlines=True
        )
    except OSError:
        raise PassOutError("GPG utility '%s' not found" % cfg["gpg"])

    (out, err) = pipe.communicate()

    if pipe.returncode != 0:
        raise PassOutError("gpg returned non-zero\nSTDOUT: %s\nSTDERR: %s" %
                           (out, err))

    return out


def get_config():
    """ return a configuration (using config file if exists) """

    _check_dirs()

    # default config
    cfg = {
        "gpg":    "gpg2",
        "id":     None,
    }

    if not os.path.exists(CONFIG_FILE):
        raise PassOutError("Please create the config file '%s'" % CONFIG_FILE)

    with open(CONFIG_FILE, "r") as fh:
        line_no = 0
        for line in fh:
            line_no += 1
            line = line.strip()
            if line.startswith("#") or line == "":
                continue

            elems = line.split("=")
            if len(elems) != 2:
                raise PassOutError(
                    "config file '%s': syntax error on line %d" %
                    (CONFIG_FILE, line_no)
                )
            (key, val) = elems

            if key not in cfg.keys():
                raise PassOutError(
                    "config file '%s': unknown key '%s' on line %d" %
                    (CONFIG_FILE, key, line_no)
                )
            cfg[key] = val

    if not cfg["id"]:
        raise PassOutError("No 'id' in %s" % CONFIG_FILE)

    return cfg


def load_clipboard(cfg, pw_name, testing=False):
    from gi.repository import Gtk, Gdk

    passwd = get_password(cfg, pw_name, testing)
    # Copy to both X11 and GTK clipboards (sigh)
    # XXX despite my best attempts, the X11 clipboard does not persist after
    # the process exits. Only a problem from the CLI, as the tray sits
    # around for the length of the desktop session.
    for clip_target in [Gdk.SELECTION_PRIMARY, Gdk.SELECTION_CLIPBOARD]:
        clipboard = Gtk.Clipboard.get(clip_target)
        clipboard.set_can_store(None)
        clipboard.set_text(passwd, -1)
        clipboard.store()


def get_password_names():
    _check_dirs()
    return [x[:-4] for x in os.listdir(CRYPTO_DIR) if x.endswith(".gpg")]


def get_password_names_grouped(sort=True):
    """Builds a tree of passwords in their groupings.
    Returns a dict of the form: Name -> SubItems"""
    dct = {}
    for pwname in sorted(get_password_names()):
        sub = dct
        elems = pwname.split("__")
        for e in elems:
            if e not in sub:
                sub[e] = {}
            sub = sub[e]
    if not sort:
        return dct
    else:
        return _sort_dict(dct)


def add_password(cfg, pw_name, passwd=None):
    out_file = _get_pass_file(pw_name)
    if os.path.exists(out_file):
        raise PassOutError("A password called '%s' already exists" % pw_name)

    if passwd is None:
        passwd = getpass.getpass()

    gpg_args = (cfg["gpg"], "-u", cfg["id"], "-e", "-r", cfg["id"])

    fd = os.open(out_file, os.O_WRONLY | os.O_CREAT, stat.S_IRUSR)
    try:
        pipe = subprocess.Popen(
            gpg_args,  stdin=subprocess.PIPE, stdout=fd,
            universal_newlines=True
        )
    except OSError:
        os.close(fd)
        os.unlink(out_file)
        raise PassOutError("GPG utility '%s' not found" % cfg["gpg"])

    (out, err) = pipe.communicate(passwd)
    os.close(fd)

    if pipe.returncode != 0:
        raise PassOutError("gpg returned non-zero")


def remove_password(pw_name):

    pw_file = _get_pass_file(pw_name)

    if not os.path.exists(pw_file):
        raise PassOutError("No password named '%s'" % pw_name)

    os.unlink(pw_file)

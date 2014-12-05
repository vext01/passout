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
import logging
import subprocess

PASSOUT_HOME = os.environ.get("PASSOUT_HOME")
if not PASSOUT_HOME:
    PASSOUT_HOME = os.path.join(os.environ["HOME"], ".passout")

CRYPTO_DIR = os.path.join(PASSOUT_HOME, "crytpo_store")
CONFIG_FILE = os.path.join(PASSOUT_HOME, "passoutrc")


# XXX this needs to go.
# The library should raise, not print and die.
def die(msg):
    """ Exit with a failure message """
    logging.error(msg)
    sys.exit(666)


def _check_dirs():
    """ Check that the passout dot dir is there and looking right """
    dirs = [PASSOUT_HOME, CRYPTO_DIR]
    for d in dirs:
        if not os.path.exists(d):
            logging.info("Creating '%s'" % d)
            os.mkdir(d)
        if not os.path.isdir(d):
            die("'%s' is not a directory" % d)


def _get_pass_file(passname):
    return os.path.join(CRYPTO_DIR, passname) + ".gpg"


# //////// Exposed API functions below //////////////


def get_password(cfg, pwname):
    pw_file = _get_pass_file(pwname)

    if not os.path.exists(pw_file):
        die("No password called '%s'" % pwname)

    # Have not found a way for this to work with mutt+msmtp without using
    # a GUI pinentry. /dev/tty not configured. Annoying XXX
    gpg_args = (cfg["gpg"], "-u", cfg["id"], "--no-tty", "-d", pw_file)

    try:
        pipe = subprocess.Popen(
            gpg_args, stdin=sys.stdin, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, universal_newlines=True
        )
    except OSError:
        die("GPG utility '%s' not found" % cfg["gpg"])

    (out, err) = pipe.communicate()

    if pipe.returncode != 0:
        die("gpg returned non-zero\nSTDOUT: %s\nSTDERR: %s" % (out, err))

    return out


def get_config():
    """ return a configuration (using config file if exists) """

    # default config
    cfg = {
        "gpg":    "gpg2",
        "id":     None,
        "xclip": "xclip",
    }

    if not os.path.exists(CONFIG_FILE):
        die("Please create the config file '%s'" % CONFIG_FILE)

    with open(CONFIG_FILE, "r") as fh:
        line_no = 0
        for line in fh:
            line_no += 1
            line = line.strip()
            if line.startswith("#") or line == "":
                continue

            elems = line.split("=")
            if len(elems) != 2:
                die(
                    "config file '%s': syntax error on line %d" %
                    (CONFIG_FILE, line_no)
                )
            (key, val) = elems

            if key not in cfg.keys():
                die(
                    "config file '%s': unknown key '%s' on line %d" %
                    (CONFIG_FILE, key, line_no)
                )
            cfg[key] = val

    if not cfg["id"]:
        die("please set 'id=<email>' (your gpg id) in the '%s'" % CONFIG_FILE)

    return cfg


def load_clipboard(cfg, pwname):
    passwd = get_password(cfg, pwname)

    try:
        pipe = subprocess.Popen(
            cfg["xclip"], stdin=subprocess.PIPE, universal_newlines=True
        )
    except OSError:
        die("Xclip utility '%s' not found" % cfg["xclip"])

    (out, err) = pipe.communicate(passwd)

    if pipe.returncode != 0:
        die(
            "'%s' returned non-zero\nSTDOUT: %s\nSTDERR: %s" %
            (cfg["xclip"], out, err)
        )


def get_password_names():
    return [x[:-4] for x in os.listdir(CRYPTO_DIR) if x.endswith(".gpg")]


def add_password(cfg, pw_name):
    out_file = _get_pass_file(pw_name)
    if os.path.exists(out_file):
        die("A password called '%s' already exists" % pw_name)

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
        die("GPG utility '%s' not found" % cfg["gpg"])

    (out, err) = pipe.communicate(passwd)
    os.close(fd)

    if pipe.returncode != 0:
        die("gpg returned non-zero")


def remove_password(cfg, pw_name):

    pw_file = _get_pass_file(pw_name)

    if not os.path.exists(pw_file):
        die("No password named '%s'" % pw_name)

    os.unlink(pw_file)

# /////////// Import time actions /////////////

_check_dirs()

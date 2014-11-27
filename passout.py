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

import os
import sys
import stat
import getpass
import logging
import argparse
import subprocess

PASSOUT_HOME = os.environ.get("PASSOUT_HOME")
if not PASSOUT_HOME:
    PASSOUT_HOME = os.path.join(os.environ["HOME"], ".passout")

CRYPTO_DIR = os.path.join(PASSOUT_HOME, "crytpo_store")
CONFIG_FILE = os.path.join(PASSOUT_HOME, "passoutrc")


def die(msg):
    """ Exit with a failure message """
    logging.error(msg)
    sys.exit(666)


def check_dirs():
    """ Check that the passout dot dir is there and looking right """
    dirs = [PASSOUT_HOME, CRYPTO_DIR]
    for d in dirs:
        if not os.path.exists(d):
            logging.info("Creating '%s'" % d)
            os.mkdir(d)
        if not os.path.isdir(d):
            die("'%s' is not a directory" % d)


def get_pass_file(passname):
    return os.path.join(CRYPTO_DIR, passname) + ".gpg"


def get_password(cfg, pwname):
    pw_file = get_pass_file(pwname)

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


# keys that can appear in the config file.
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


def put_password_into_clipboard(cfg, pwname):
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


def get_all_password_names():
    return [x[:-4] for x in os.listdir(CRYPTO_DIR) if x.endswith(".gpg")]


def cmd_add(cfg, pwname):
    out_file = get_pass_file(pwname)
    if os.path.exists(out_file):
        die("A password called '%s' already exists" % pwname)

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


def cmd_ls(cfg):
    for p in sorted(get_all_password_names()):
        print(p)


def cmd_rm(cfg, pwname):
    pw_file = get_pass_file(pwname)

    if not os.path.exists(pw_file):
        die("No password named '%s'" % pwname)

    os.unlink(pw_file)


def cmd_stdout(cfg, pwname):
    """ Prints a password out of stdout (for use with, e.g. mutt) """
    print(get_password(cfg, pwname))


def cmd_clip(cfg, pwname):
    """ Puts a password in the GUI clipboard """
    put_password_into_clipboard(cfg, pwname)


def cmd_printconfig(cfg):
    print(cfg)


def cmd_tray(cfg):
    from tray import run_tray
    run_tray(cfg)


def _entrypoint(args):
    func_args = [get_config()]

    if hasattr(args, "pass_name"):
        func_args.append(args.pass_name)

    args.func(*func_args)


def main():
    """ Execution begins here """

    logging.basicConfig(level=logging.INFO)
    check_dirs()
    pass_name_parser = []

    parser = argparse.ArgumentParser(description="Simple password manager built on gpg")
    subparsers = parser.add_subparsers(title="command")

    # ls
    ls = subparsers.add_parser("ls", help="List passwords stored")
    ls.set_defaults(func=cmd_ls)

    # add
    add = subparsers.add_parser("add", help="Add a new password")
    add.set_defaults(func=cmd_add)
    pass_name_parser.append(add)

    # rm
    rm = subparsers.add_parser("rm", help="Remove a stored password")
    rm.set_defaults(func=cmd_rm)
    pass_name_parser.append(rm)

    # stdout
    stdout = subparsers.add_parser("stdout", help="Print password to stdout")
    stdout.set_defaults(func=cmd_rm)
    pass_name_parser.append(stdout)

    # clip
    clip = subparsers.add_parser("clip", help="Put the password in the X buffer")
    clip.set_defaults(func=cmd_clip)
    pass_name_parser.append(clip)

    # config
    config = subparsers.add_parser("config", help="Print the current passout configuration")
    config.set_defaults(func=cmd_printconfig)

    # tray
    tray = subparsers.add_parser("tray", help="Start the GTK tray icon")
    tray.set_defaults(func=cmd_tray)

    for p in pass_name_parser:
        p.add_argument("pass_name", help="Name of password")

    args = parser.parse_args()
    _entrypoint(args)

if __name__ == "__main__":
    main()


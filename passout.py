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
Command line client to PassOut.
"""

import sys
import logging

import passout


def usage(retcode):
    """ Print usage and exit """
    print(__doc__)
    print("Usage: passout.py <command> <args>\n")
    print("Available commands:")
    print("  ls")
    print("  add <pass_name>")
    print("  rm <pass_name>")
    print("  stdout <pass_name>")
    print("  clip <pass_name>")
    print("  printconfig")
    print("  tray")
    sys.exit(retcode)


def die(msg):
    """ Exit with a failure message """
    logging.error(msg)
    sys.exit(666)


def cmd_add(cfg, *args):
    (pw_name, ) = args
    passout.add_password(cfg, pw_name)


def cmd_ls(cfg, *args):
    for p in sorted(passout.get_password_names()):
        print(p)


def cmd_rm(cfg, *args):
    (pw_name, ) = args
    passout.remove_password(cfg, pw_name)


def cmd_stdout(cfg, *args):
    """ Prints a password out of stdout (for use with, e.g. mutt) """
    (pw_name, ) = args
    print(passout.get_password(cfg, pw_name))


def cmd_clip(cfg, *args):
    """ Puts a password in the GUI clipboard """
    (pw_name, ) = args
    passout.load_clipboard(cfg, pw_name)


def cmd_printconfig(cfg, *args):
    print(cfg)


def cmd_tray(cfg, *args):
    passout.tray.run_tray(cfg)


# Table of commands
# command_name : (n_args, func)
CMD_TAB = {
    "ls":          (0, cmd_ls),
    "add":         (1, cmd_add),
    "rm":          (1, cmd_rm),
    "stdout":      (1, cmd_stdout),
    "clip":        (1, cmd_clip),
    "printconfig": (0, cmd_printconfig),
    "tray":        (0, cmd_tray),
}


def entrypoint():
    """ Execution begins here """

    logging.basicConfig(level=logging.INFO)
    cfg = passout.get_config()

    try:
        cmd = sys.argv[1]
    except IndexError:
        usage(666)

    try:
        (expect_n_args, func) = CMD_TAB[cmd]
    except KeyError:
        die("Unknown command '%s'" % cmd)
        usage(666)

    n_args = len(sys.argv) - 2
    if n_args != expect_n_args:
        die("Wrong argument count for command '%s'" % cmd)

    func(cfg, *sys.argv[2:])

if __name__ == "__main__":
    entrypoint()

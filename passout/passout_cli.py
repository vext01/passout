#!/usr/bin/env python

# Copyright (c) 2014-2015 Edd Barrett <vext01@gmail.com>
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

import __init__ as passout
import argparse
import argspander
import json
import time
from logging import info


@argspander.expand
def cmd_ls(*args, **kwargs):
    for p in sorted(passout.get_password_names()):
        print(p)


@argspander.expand
def cmd_add(cfg, pass_name):
    passout.add_password(cfg, pass_name)


@argspander.expand
def cmd_rm(pass_name):
    passout.remove_password(pass_name)


@argspander.expand
def cmd_stdout(cfg, pass_name):
    """ Prints a password out of stdout (for use with, e.g. mutt) """
    print(passout.get_password(cfg, pass_name))


@argspander.expand
def cmd_clip(cfg, pass_name):
    """ Puts a password in the GUI clipboard """
    passout.load_clipboard(cfg, pass_name)

    secs = cfg["clip_clear_time"]
    if secs > 0:
        info("Clipboard loaded. Destroying in %s second(s)..." % secs)
        time.sleep(secs)
        passout.clear_clipboard(cfg)


@argspander.expand
def cmd_printconfig(cfg):
    # The json.dumps with sorted keys is a way to work around
    # Python 3's non-deterministic dictionary ordering.
    # We need an order for tests.
    print(json.dumps(cfg, sort_keys=True))


@argspander.expand
def cmd_tray(cfg):
    from passout import tray
    tray.run_tray(cfg)


@argspander.expand
def cmd_version(cfg):
    print("Passout-%s" % passout.VERSION)


def entrypoint():
    """ Execution begins here """

    cfg = passout.get_config()
    pass_name_str = "pass_name"

    parser = argparse.ArgumentParser(
        description="Simple password manager built on gpg")
    subparsers = parser.add_subparsers(title="command")

    # ls
    ls = subparsers.add_parser("ls", help="List passwords stored")
    ls.set_defaults(func=cmd_ls)

    # add
    add = subparsers.add_parser("add", help="Add a new password")
    add.set_defaults(func=cmd_add, cfg=cfg)
    add.add_argument(pass_name_str, help="Name of the password to add")

    # rm
    rm = subparsers.add_parser("rm", help="Remove a stored password")
    rm.set_defaults(func=cmd_rm, cfg=cfg)
    rm.add_argument(pass_name_str, help="Name of the password to remove")

    # stdout
    stdout = subparsers.add_parser("stdout", help="Print password to stdout")
    stdout.set_defaults(func=cmd_stdout, cfg=cfg)
    stdout.add_argument(pass_name_str, help="Name of the password to print")

    # clip
    clip = subparsers.add_parser("clip",
                                 help="Put the password in the X clipboard")
    clip.set_defaults(func=cmd_clip, cfg=cfg)
    clip.add_argument(pass_name_str,
                      help="Name of the password to place in the X clipboard")

    # config
    config = subparsers.add_parser("config",
                                   help="Print the current "
                                   "passout configuration")
    config.set_defaults(func=cmd_printconfig, cfg=cfg)

    # tray
    tray = subparsers.add_parser("tray", help="Start the GTK tray icon")
    tray.set_defaults(func=cmd_tray, cfg=cfg)

    # version
    version = subparsers.add_parser("version", help="Show version and exit")
    version.set_defaults(func=cmd_version, cfg=cfg)

    args = parser.parse_args()
    args.func(args, expand=True)


if __name__ == "__main__":
    entrypoint()

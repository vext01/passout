#!/usr/bin/env python3.3
import sys, os, logging

PASSOUT_DIR = os.path.join(os.environ["HOME"], ".passout")
CRYPTO_DIR = os.path.join(PASSOUT_DIR, "crytpo_store")

def usage(retcode):
    """ Print usage and exit """
    print("Usage: passout.py <command> <args>\n")
    print("Available commands:")
    print("  list")
    print("  add <pass_name>")
    sys.exit(retcode)

def die(msg):
    """ Exit with a failure message """
    logging.error(msg)
    sys.exit(666)

def check_dirs():
    """ Check that the passout dot dir is there and looking right """
    dirs = [ PASSOUT_DIR, CRYPTO_DIR ]
    for d in dirs:
        if not os.path.lexists(d):
            logging.info("Creating '%s'" % d)
            os.mkdir(d)
        if not os.path.isdir(d):
            die("'%s' is not a directory" % d)

def cmd_list(*args):
    pass

# Table of commands
# command_name : (n_args, func)
CMD_TAB = {
    "list" :        (0, cmd_list),
}
def entrypoint():
    """ Execution begins here """

    logging.basicConfig(level=logging.INFO)
    check_dirs()

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

    func(sys.argv[2:])

if __name__ == "__main__":
    entrypoint()

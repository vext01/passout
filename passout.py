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
    loggin.error(msg)
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

def entrypoint():
    """ Execution begins here """
    logging.basicConfig(level=logging.INFO)
    check_dirs()

    # XXX argparse or getopt


if __name__ == "__main__":
    entrypoint()

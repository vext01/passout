#!/usr/bin/env python3.3
import sys, os, logging, io, getpass, subprocess
from tmp import GPG_ID # XXX

 # configurable XXX
GPG_BIN = "gpg2"
PASSOUT_DIR = os.path.join(os.environ["HOME"], ".passout")
CRYPTO_DIR = os.path.join(PASSOUT_DIR, "crytpo_store")

def usage(retcode):
    """ Print usage and exit """
    print("Usage: passout.py <command> <args>\n")
    print("Available commands:")
    print("  ls")
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

def get_pass_file(passname):
    return os.path.join(CRYPTO_DIR, passname) + ".gpg"

def cmd_add(*args):
    (pwname, ) = args

    out_file = get_pass_file(pwname)
    if os.path.lexists(out_file):
        die("A password called '%s' already exists" % pwname)

    passwd = getpass.getpass()

    gpg_args = (GPG_BIN, "-e", "-o", out_file, "-r", GPG_ID)
    pipe = subprocess.Popen(gpg_args,
            stdin=subprocess.PIPE, universal_newlines=True)
    (out, err) = pipe.communicate(passwd)

    if pipe.returncode != 0:
        die("gpg returned non-zero")

def cmd_ls(*args):
    for e in os.listdir(CRYPTO_DIR):
        if e.endswith(".gpg"):
            print(e[:-4])

def cmd_rm(*args):
    (pwname, ) = args

    pw_file = get_pass_file(pwname)

    if not os.path.lexists(pw_file):
        die("No password named '%s'" % pwname)

    os.unlink(pw_file)

def cmd_stdout(*args):
    """ Prints a password out of stdout (for use with, e.g. mutt) """
    (pwname, ) = args

    pw_file = get_pass_file(pwname)

    if not os.path.lexists(pw_file):
        die("No password called '%s'" % pwname)

    gpg_args = (GPG_BIN, "-d", pw_file)
    pipe = subprocess.Popen(gpg_args,
            stdin=sys.stdin, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, universal_newlines=True)
    (out, err) = pipe.communicate()

    if pipe.returncode != 0:
        die("gpg returned non-zero\nSTDOUT: %s\nSTDERR: %s" % (out, err))

    print(out)

# Table of commands
# command_name : (n_args, func)
CMD_TAB = {
    "ls" :          (0, cmd_ls),
    "add" :         (1, cmd_add),
    "rm" :          (1, cmd_rm),
    "stdout" :      (1, cmd_stdout),
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

    func(*sys.argv[2:])

if __name__ == "__main__":
    entrypoint()

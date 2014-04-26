#!/usr/bin/env python3.3
import sys, os, logging, io, getpass, subprocess, stat

PASSOUT_DIR = os.path.join(os.environ["HOME"], ".passout")
CRYPTO_DIR = os.path.join(PASSOUT_DIR, "crytpo_store")
CONFIG_FILE = os.path.join(PASSOUT_DIR, "passoutrc")

def usage(retcode):
    """ Print usage and exit """
    print("Usage: passout.py <command> <args>\n")
    print("Available commands:")
    print("  ls")
    print("  add <pass_name>")
    print("  rm <pass_name>")
    print("  stdout <pass_name>")
    print("  clip <pass_name>")
    print("  printconfig")
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

def get_password(cfg, pwname):
    pw_file = get_pass_file(pwname)

    if not os.path.lexists(pw_file):
        die("No password called '%s'" % pwname)

    # Have not found a way for this to work with mutt+msmtp without using
    # a GUI pinentry. /dev/tty not configured. Annoying XXX
    gpg_args = (cfg["gpg"], "-u", cfg["id"], "--no-tty", "-d", pw_file)

    try:
        pipe = subprocess.Popen(gpg_args,
                stdin=sys.stdin, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, universal_newlines=True)
    except FileNotFoundError:
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
            "gpg" :     "gpg2",
            "id" :      None,
            "xclip" :   "xclip",
    }

    if not os.path.lexists(CONFIG_FILE):
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
                die("config file '%s': syntax error on line %d" %
                        (CONFIG_FILE, line_no))
            (key, val) = elems

            if key not in cfg.keys():
                die("config file '%s': unknown key '%s' on line %d" %
                        (CONFIG_FILE, key, line_no))
            cfg[key] = val

    if not cfg["id"]:
        die("please set 'id=<email>' (your gpg id) in the '%s'" % CONFIG_FILE)

    return cfg

def cmd_add(cfg, *args):
    (pwname, ) = args

    out_file = get_pass_file(pwname)
    if os.path.lexists(out_file):
        die("A password called '%s' already exists" % pwname)

    passwd = getpass.getpass()
    gpg_args = (cfg["gpg"], "-u", cfg["id"], "-e", "-r", cfg["id"])

    fd = os.open(out_file, os.O_WRONLY | os.O_CREAT, stat.S_IRUSR)
    try:
        pipe = subprocess.Popen(gpg_args,
                stdin=subprocess.PIPE, stdout=fd,
                universal_newlines=True)
    except FileNotFoundError:
        die("GPG utility '%s' not found" % cfg["gpg"])

    (out, err) = pipe.communicate(passwd)
    os.close(fd)

    if pipe.returncode != 0:
        die("gpg returned non-zero")

def cmd_ls(cfg, *args):
    for e in os.listdir(CRYPTO_DIR):
        if e.endswith(".gpg"):
            print(e[:-4])

def cmd_rm(cfg, *args):
    (pwname, ) = args

    pw_file = get_pass_file(pwname)

    if not os.path.lexists(pw_file):
        die("No password named '%s'" % pwname)

    os.unlink(pw_file)

def cmd_stdout(cfg, *args):
    """ Prints a password out of stdout (for use with, e.g. mutt) """
    (pwname, ) = args
    print(get_password(cfg, pwname))

def cmd_clip(cfg, *args):
    """ Puts a password in the GUI clipboard """

    (pwname, ) = args
    passwd = get_password(cfg, pwname)

    try:
        pipe = subprocess.Popen(cfg["xclip"],
                stdin=subprocess.PIPE, universal_newlines=True)
    except FileNotFoundError:
        die("Xclip utility '%s' not found" % cfg["xclip"])

    (out, err) = pipe.communicate(passwd)

    if pipe.returncode != 0:
        die("'%s' returned non-zero\nSTDOUT: %s\nSTDERR: %s" %
                (cfg["xclip"], out, err))

def cmd_printconfig(cfg, *args):
    print(cfg)

# Table of commands
# command_name : (n_args, func)
CMD_TAB = {
    "ls" :          (0, cmd_ls),
    "add" :         (1, cmd_add),
    "rm" :          (1, cmd_rm),
    "stdout" :      (1, cmd_stdout),
    "clip" :        (1, cmd_clip),
    "printconfig" : (0, cmd_printconfig),
}
def entrypoint():
    """ Execution begins here """

    logging.basicConfig(level=logging.INFO)
    check_dirs()
    cfg = get_config()

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

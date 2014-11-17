from distutils.spawn import find_executable

import pytest
import os
import re
import uuid
import shutil

import pexpect
import sh

# setup a fake home to put gpg and passout stuff in
# XXX dangerous, add an environment variable for this purpose.
# XXX using $HOME also means PYTHON doesn't see ~/.local after
# XXX we change $HOME.
SCRIPT_PATH = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
os.environ["HOME"] = SCRIPT_DIR

GPGS = ["gpg2", "gpg"]
GPG_TEMPLATE = os.path.join(SCRIPT_DIR, "key_template")
GPG_DIR = os.path.join(SCRIPT_DIR, ".gnupg")
GPG_ID = "test@localhost"

PASSOUT = os.path.join(SCRIPT_DIR, "..", "passout.py")
PASSOUT_DIR = os.path.join(SCRIPT_DIR, ".passout")
PASSOUT_CONFIG = os.path.join(PASSOUT_DIR, "passoutrc")


class TestError(Exception):
    pass


def _find_gpg():
    for gpg in GPGS:
        if find_executable(gpg):
            return gpg
    raise TestError("Cannot locate gpg! Tried %s" % GPGS)


def _make_key(gpg):
    gpg_cmd = sh.Command(gpg)
    gpg_cmd("--batch", "--gen-key", GPG_TEMPLATE)


def _get_key_id(gpg):
    gpg_cmd = sh.Command(gpg)
    out = gpg_cmd("-K").stdout
    for line in out.splitlines():
        match = re.match("^sec +1024R/(.*) [0-9]{4}-[0-9]{2}-[0-9]{2}$", line)
        if match:
            break

    if not match or len(match.groups()) != 1:
        raise TestError("Failed to extract GPG id for tests")

    return match.groups(1)


def _remove_passout_dir():
    if os.path.exists(PASSOUT_DIR):
        shutil.rmtree(PASSOUT_DIR)


def _make_fresh_passout_dir(gpg):
    _remove_passout_dir()

    os.mkdir(PASSOUT_DIR)
    with open(PASSOUT_CONFIG, "w") as config:
        config.write("id=%s\ngpg=%s\n" % (GPG_ID, gpg))


@pytest.fixture(autouse=True)
def passout(request):
    """Fixture implicitely run once for each test.

    Creates a fresh passout setup ready for testing. This includes
    making a gpg key if one does not exist in the test dir."""

    gpg = _find_gpg()
    if not os.path.exists(GPG_DIR):
        _make_key(gpg)

    gpg_id = _get_key_id(gpg)
    _make_fresh_passout_dir(gpg_id)

    def finalise():
        _remove_passout_dir()

    request.addfinalizer(finalise)


@pytest.fixture
def pw_name():
    return uuid.uuid1().hex


rand_pw = pw_name


def run_passout(*args):
    return pexpect.spawn("%s %s" % (PASSOUT, " ".join(args)))

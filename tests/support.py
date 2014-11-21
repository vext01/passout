from distutils.spawn import find_executable

import pytest
import os
import re
import uuid
import shutil

import pexpect
import sh

# Trick PassOut and GPG into looking in the test dir
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PASSOUT_DIR = os.path.join(TEST_DIR, ".passout")
GPG_DIR = os.path.join(TEST_DIR, ".gnupg")
os.environ["PASSOUT_HOME"] = PASSOUT_DIR
os.environ["GNUPGHOME"] = GPG_DIR

GPGS = ["gpg2", "gpg"]
GPG_TEMPLATE = os.path.join(TEST_DIR, "key_template")
GPG_ID = "test@localhost"

PASSOUT = os.path.join(TEST_DIR, "..", "passout.py")
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

    _make_fresh_passout_dir(gpg)

    def finalise():
        _remove_passout_dir()

    request.addfinalizer(finalise)


@pytest.fixture
def pw_name():
    return uuid.uuid1().hex


rand_pw = pw_name


def run_passout(*args):
    return pexpect.spawn("%s %s" % (PASSOUT, " ".join(args)))

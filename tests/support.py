import os
import shutil
import uuid
import sys
from distutils.spawn import find_executable

import pexpect
import pytest
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


def _remove_gpg_dir():
    if os.path.exists(GPG_DIR):
        shutil.rmtree(GPG_DIR)


def _make_fresh_passout_dir(gpg):
    _remove_passout_dir()

    os.mkdir(PASSOUT_DIR)
    with open(PASSOUT_CONFIG, "w") as config:
        config.write("id=%s\ngpg=%s\n" % (GPG_ID, gpg))


class PexpectTest(object):
    @pytest.fixture(autouse=True)
    def passout(self, request):
        """Fixture implicitely run once for each test.

        Creates a fresh passout setup ready for testing. This includes
        making a gpg key if one does not exist in the test dir."""

        gpg = _find_gpg()
        if not os.path.exists(GPG_DIR):
            _make_key(gpg)

        _make_fresh_passout_dir(gpg)

        def finalise():
            _remove_passout_dir()
            _remove_gpg_dir()

        request.addfinalizer(finalise)

    @pytest.fixture
    def _uuid_hex(self):
        """Generates a random password name or password name for tests"""
        return uuid.uuid1().hex

    rand_pw = _uuid_hex
    rand_pwname = _uuid_hex

    def run_passout(self, *args):
        return pexpect.spawn("%s %s" % (PASSOUT, " ".join(args)))

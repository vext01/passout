import os

import pexpect
import pytest
import sys

import support

from passout import VERSION
from distutils.spawn import find_executable


class TestCLI(support.PassOutCliTest):
    """ These test loosely check the command line interface.
    These tests are supplemented with proper function-level unit tests"""

    def test_basic_add_and_stdout(self, rand_pwname, rand_pw):
        child = self.run_passout("add", rand_pwname)
        child.expect("Password: ")
        child.sendline(rand_pw)
        child.expect(pexpect.EOF)

        child2 = self.run_passout("stdout", rand_pwname)
        child2.expect(rand_pw)
        child2.expect(pexpect.EOF)

    def test_config(self):
        child1 = self.run_passout("config")
        child1.expect('{"gpg": ".*?", "id": ".*?"}')
        child1.expect(pexpect.EOF)

    def test_ls(self, rand_pwname, rand_pw):
        child1 = self.run_passout("add", rand_pwname)
        child1.expect_exact("Password: ")
        child1.sendline(rand_pw)
        child1.expect(pexpect.EOF)

        rand_pwname2 = rand_pwname + "2"
        child2 = self.run_passout("add", rand_pwname2)
        child2.expect_exact("Password: ")
        child2.sendline(rand_pw)
        child2.expect(pexpect.EOF)

        child3 = self.run_passout("ls")
        child3.expect(rand_pwname)
        child3.expect(rand_pwname2)
        child3.expect(pexpect.EOF)

    def test_add_same_pw_twice(self, rand_pwname, rand_pw):
        child1 = self.run_passout("add", rand_pwname)
        child1.expect_exact("Password: ")
        child1.sendline(rand_pw)
        child1.expect_exact(pexpect.EOF)

        child2 = self.run_passout("add", rand_pwname)
        child2.expect(
            "A password called '%s' already exists" % rand_pwname)
        child2.expect_exact(pexpect.EOF)

    def test_rm(self, rand_pwname, rand_pw):
        child1 = self.run_passout("add", rand_pwname)
        child1.expect_exact("Password: ")
        child1.sendline(rand_pw)
        child1.expect_exact(pexpect.EOF)

        child2 = self.run_passout("rm", rand_pwname)
        child2.expect_exact(pexpect.EOF)

    @pytest.mark.skipif("DISPLAY" not in os.environ, reason="No X11")
    @pytest.mark.skipif(find_executable("xclip") is None, reason="No xclip")
    @pytest.mark.xfail(reason="broken")
    def test_clip(self, rand_pwname, rand_pw):
        child1 = self.run_passout("add", rand_pwname)
        child1.expect_exact("Password: ")
        child1.sendline(rand_pw)
        child1.expect_exact(pexpect.EOF)
        child1.close()

        child2 = self.run_passout("clip", rand_pwname)
        child2.expect(pexpect.EOF)
        child2.close()

        # XXX for some reason the above child2 doesn't always correctly set the
        # clipboard. It works outside tests though. Why is beyond me, but seems
        # like a race condition perhaps. Luckily we have a library-level test
        # for clipboards which does work.

        # Testing all clipboards
        import passout
        for clip in passout.XCLIP_CLIPBOARDS:
            data = support.get_clipboard_text(clip)
            assert data == rand_pw

    def test_rm_nonexisting_pw(self, rand_pwname):
        child1 = self.run_passout("rm", rand_pwname)
        child1.expect_exact(
            "No password named '%s'" % rand_pwname)
        child1.expect_exact(pexpect.EOF)

    def test_version(self):
        child1 = self.run_passout("version")
        child1.expect_exact("Passout-%s" % VERSION)
        child1.expect_exact(pexpect.EOF)

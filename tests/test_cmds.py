import subprocess
import os

import pexpect
import pytest

import support


class TestCmds(support.PexpectTest):
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

    def test_printconfig(self):
        child1 = self.run_passout("printconfig")
        child1.expect("{'gpg': '.*?', 'id': '.*?', 'xclip': '.*?'}")
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

    @pytest.mark.skipif(os.environ["DISPLAY"] is None, reason="No X11")
    def test_xclip(self, rand_pwname, rand_pw):
        from distutils.spawn import find_executable
        xclip = find_executable("xclip")

        if not xclip:
            pytest.skip("no xclip found")

        child1 = self.run_passout("add", rand_pwname)
        child1.expect_exact("Password: ")
        child1.sendline(rand_pw)
        child1.expect_exact(pexpect.EOF)

        child2 = self.run_passout("clip", rand_pwname)
        child2.expect(pexpect.EOF)

        child3 = pexpect.spawn("%s -o" % xclip)
        child3.expect(rand_pw)
        child3.expect_exact(pexpect.EOF)

    def test_rm_nonexisting_pw(self, rand_pwname):
        child1 = self.run_passout("rm", rand_pwname)
        child1.expect_exact(
            "No password named '%s'" % rand_pwname)
        child1.expect_exact(pexpect.EOF)

    # XXX Try to add a password under a non-existent GPG id. Should fail.

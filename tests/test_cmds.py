import os
import sys

import pexpect
import pytest

import support


class TestCmds(support.PassOutCliTest):
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
        child1.expect("{'gpg': '.*?', 'id': '.*?'}")
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
    def test_clip(self, rand_pwname, rand_pw):
        try:
            from gi.repository import Gtk, Gdk
        except ImportError:
            pytest.skip("No pygobject available")

        child1 = self.run_passout("add", rand_pwname)
        child1.expect_exact("Password: ")
        child1.sendline(rand_pw)
        child1.expect_exact(pexpect.EOF)

        child2 = self.run_passout("clip", rand_pwname)
        child2.expect(pexpect.EOF)

        # Testing both X11 and GTK clipboards
        for clip_target in [Gdk.SELECTION_CLIPBOARD]:
            clipboard = Gtk.Clipboard.get(clip_target)
            data = clipboard.wait_for_contents(Gdk.SELECTION_TYPE_STRING)

            data_s = data.get_data()

            # Sigh
            if sys.version_info[0] >= 3:
                assert data_s == bytes(rand_pw, "ascii")
            else:
                assert data_s == rand_pw

    def test_rm_nonexisting_pw(self, rand_pwname):
        child1 = self.run_passout("rm", rand_pwname)
        child1.expect_exact(
            "No password named '%s'" % rand_pwname)
        child1.expect_exact(pexpect.EOF)

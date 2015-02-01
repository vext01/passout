import os
import sys

import pytest

import support
import passout
from passout import PassOutError


class TestLib(support.PassOutLibTest):
    """These test loosely check the command line interface.
    These tests are supplemented with proper function-level unit tests"""

    def test_add_and_stdout(self, cfg, rand_pwname, rand_pw):
        passout.add_password(cfg, rand_pwname, rand_pw)
        got = passout.get_password(cfg, rand_pwname, testing=True)
        assert got == rand_pw

    def test_ls(self, cfg, rand_pwname, rand_pw):
        rand_pwname2 = rand_pwname + "2"

        passout.add_password(cfg, rand_pwname, rand_pw)
        passout.add_password(cfg, rand_pwname2, rand_pw)
        got = passout.get_password_names()
        got.sort()

        assert got == [rand_pwname, rand_pwname2]

    def test_add_same_pw_twice(self, cfg, rand_pwname, rand_pw):
        passout.add_password(cfg, rand_pwname, rand_pw)
        with pytest.raises(PassOutError) as exc_info:
            passout.add_password(cfg, rand_pwname, rand_pw)

        err_str = "A password called '%s' already exists" % rand_pwname
        assert exc_info.value.args[0] == err_str

    def test_rm(self, cfg, rand_pwname, rand_pw):
        passout.add_password(cfg, rand_pwname, rand_pw)
        passout.remove_password(rand_pwname)
        got = passout.get_password_names()
        assert got == []

    @pytest.mark.skipif(os.environ["DISPLAY"] is None, reason="No X11")
    def test_clip(self, cfg, rand_pwname, rand_pw):
        try:
            from gi.repository import Gtk, Gdk
        except ImportError:
            pytest.skip("No pygobject available")

        passout.add_password(cfg, rand_pwname, rand_pw)
        passout.load_clipboard(cfg, rand_pwname, testing=True)

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
        with pytest.raises(PassOutError) as exc_info:
            passout.remove_password(rand_pwname)

        err_str = "No password named '%s'" % rand_pwname
        assert exc_info.value.args[0] == err_str

    def test_use_bad_gpg_id(self, cfg, rand_pwname, rand_pw):
        cfg['id'] = "BOGUS@WiBbLe.CoM"
        with pytest.raises(PassOutError) as exc_info:
            passout.add_password(cfg, rand_pwname, rand_pw)

        err_str = "gpg returned non-zero"
        assert exc_info.value.args[0] == err_str

    def test_get_password_names_empty(self, cfg, rand_pw):
        assert passout.get_password_names() == []

    def test_get_password_names_grouped(self, cfg, rand_pw):
        passout.add_password(cfg, "pass-1", rand_pw)
        passout.add_password(cfg, "group1__pass1-1", rand_pw)
        passout.add_password(cfg, "group1__group1-1__pass1-1-1", rand_pw)
        passout.add_password(cfg, "group1__group1-1__pass1-1-2", rand_pw)
        passout.add_password(cfg, "group2__pass2-1", rand_pw)

        got_dct = passout.get_password_names_grouped()

        expect_dct = {
            'pass-1': {},
            'group1': {
                'pass1-1': {},
                'group1-1': {
                    'pass1-1-1': {},
                    'pass1-1-2': {},
                },
            },
            'group2': {
                'pass2-1': {}
            },
        }

        assert got_dct == expect_dct

    def test_get_password_names_grouped_sort(self, cfg, rand_pw):
        passout.add_password(cfg, "aaa", rand_pw)
        passout.add_password(cfg, "xxx", rand_pw)
        passout.add_password(cfg, "bbb", rand_pw)
        passout.add_password(cfg, "www", rand_pw)

        got_dct = passout.get_password_names_grouped()

        order = [i for i in got_dct]
        assert order == ["aaa", "bbb", "www", "xxx"]

    def test_get_password_names_grouped_sort2(self, cfg, rand_pw):
        passout.add_password(cfg, "x__aaa", rand_pw)
        passout.add_password(cfg, "x__xxx", rand_pw)
        passout.add_password(cfg, "x__bbb", rand_pw)
        passout.add_password(cfg, "x__www", rand_pw)

        got_dct = passout.get_password_names_grouped()["x"]

        order = [i for i in got_dct]
        assert order == ["aaa", "bbb", "www", "xxx"]

    def test_get_password_names_grouped_empty(self):
        got_dct = passout.get_password_names_grouped()
        assert got_dct == {}

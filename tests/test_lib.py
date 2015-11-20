import os

import pytest
import json

import support
import passout
from passout import PassOutError


def dummy_check_dirs():
    pass


def mk_dummy_json_load(dct):
    def dummy_json_load(*args, **kwargs):
        return dct
    return dummy_json_load


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
        # XXX skip if xclip not found

        passout.add_password(cfg, rand_pwname, rand_pw)
        passout.load_clipboard(cfg, rand_pwname, testing=True)

        # Testing all clipboards
        for clip in passout.XCLIP_CLIPBOARDS:
            data = support.get_clipboard_text(clip)
            assert data == rand_pw

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

    def test_get_config0001(self, monkeypatch):
        """If we specify all config options, we get back a dict
        simply containing those options"""

        config = {u"id": u"jim@bob.com", u"gpg": u"gpg2"}

        monkeypatch.setattr(json, "loads", mk_dummy_json_load(config))
        monkeypatch.setattr(passout, "_check_dirs", dummy_check_dirs)

        config2 = passout.get_config()
        assert config == config2

    def test_get_config0002(self, monkeypatch):
        """a config without a 'gpg' field gets a default one"""

        config = {u"id": u"jim@bob.com"}
        expect = {u"id": u"jim@bob.com", u"gpg": u"gpg2"}

        monkeypatch.setattr(json, "loads", mk_dummy_json_load(config))
        monkeypatch.setattr(passout, "_check_dirs", dummy_check_dirs)

        config = passout.get_config()
        assert config == expect

    def test_get_config0003(self, monkeypatch):
        """a config without a 'id' field crashes"""

        config = {u"gpg": u"gpg2"}

        monkeypatch.setattr(json, "loads", mk_dummy_json_load(config))
        monkeypatch.setattr(passout, "_check_dirs", dummy_check_dirs)

        with pytest.raises(passout.PassOutError):
            config = passout.get_config()

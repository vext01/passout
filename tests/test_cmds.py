import pexpect

import support


class TestCmds(support.PexpectTest):

    def test_basic_add_and_stdout(self, rand_pwname, rand_pw):
        child1 = self.run_passout("add", rand_pwname)
        child1.expect("Password: ")
        child1.sendline(rand_pw)
        child1.expect(pexpect.EOF)

        child2 = self.run_passout("stdout", rand_pwname)
        child2.expect(rand_pw)
        child2.expect(pexpect.EOF)

    # XXX Test printconfig

    # XXX Test 'ls'

    # XXX add a password, delete a password,
    # try to print a password, should fail

    # XXX Test xclip route.

    # XXX add a password, add a password of the same name, should fail.

    # XXX delete a password without adding one, should fail.

    # XXX Try to add a password under a non-existent GPG id. Should fail.

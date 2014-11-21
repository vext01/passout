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

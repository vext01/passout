import os
import pexpect

# linters will complain but you really do need these.
from support import pw_name, rand_pw, run_passout, TEST_DIR, passout

# XXX I hate this.
os.environ["HOME"] = TEST_DIR


def test_basic_add_and_stdout(pw_name, rand_pw):
    child1 = run_passout("add", pw_name)
    child1.expect("Password: ")
    child1.sendline(rand_pw)
    child1.expect(pexpect.EOF)

    child2 = run_passout("stdout", pw_name)
    child2.expect(rand_pw)
    child2.expect(pexpect.EOF)

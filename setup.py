import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from passout import VERSION

LONG_DESCRIPTION = open("README.md", "r").read()

REQUIREMENTS = [
    "argspander",
    "pexpect",
    "pytest",
    "sh",
]


class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name="passout",
    version=VERSION,
    license="ISC",
    description="Really simple password manager built on gpg",
    long_description=LONG_DESCRIPTION,
    author="Edd Barret",
    author_email="vext01@gmail.com",
    packages=find_packages(exclude="tests"),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    keywords="password manager gpg",
    scripts=["passout_cli"],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)

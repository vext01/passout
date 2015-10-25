from setuptools import setup, find_packages
from passout import VERSION

LONG_DESCRIPTION = open("README.md", "r").read()

REQUIREMENTS = [
    "argspander",
    "pexpect",
    "pytest",
    "sh",
]


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
    entry_points={
        "console_scripts": [
            "passout = passout.passout_cli:entrypoint"
        ]
    },
    tests_require=['pytest'],
)

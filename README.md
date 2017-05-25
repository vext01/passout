# PassOut

A simple password manager built on GnuPG.

## Why?

I use a lot of programs that require passwords, e.g. offlineimap/msmtp/...
(you do too). To avoid having to memorise these passwords you either:

 * Put them in clear text in a config file, e.g. `.netrc`.
 * Use a password manager such as gnome-keyring, pwsafe, keepassx, etc.

The former is obviously annoying. The latter works, but I found that these
tools were either too heavyweight, or required me to type the master
password every time I needed to access the password store.

Therefore, I made PassOut; a simple password manager written in Python.

## Dependencies

  * GnuPG version 1 or 2 (2 recommended)
  * Python 2.7 or >=3.3 (2.7 may be deprecated soon).
  * The argspander module.
  * A GUI pinentry program, e.g. `gtk-pinentry-2` (for X11 integration only).
  * PyGobject (System tray integration only).

For developers:

  * pytest.
  * The pexpect module.
  * The sh module.

## Quick Start

Generate a GnuPG key (if you don't yet have one):

```
gpg2 --gen-key
```

For info on this step, see the GnuPG docs for more info:
http://www.gnupg.org/gph/en/manual.html#AEN26

Tell PassOut about your key in a JSON config file:

```
mkdir ~/.passout && echo -e \
    '{"gpg": <your_gpg_binary>, "id": <your_gpg_id>}' > \
	~/.passout/passout.json
```

Where `<your_gpg_binary>` is the path to the gpg binary you want to use (I
recommend using version 2) and `<your_gpg_id>` is the hash or email address
associated with the GnuPG key you want to use with PassOut. I recommend using
the hash.

Now add your passwords, e.g. to add a password named 'my-email':

```
passout.py add my-email
```

You will be prompted for the password. The password will not echo. Passwords
are stored GnuPG encrypted in `~/.passout/crypto_store`.

To retrieve a password to stdout:

```
passout.py stdout my-email
```

You will be prompted to unlock the GnuPG keychain and the password will be
printed.

Similarly, you can put the password in the X clipboard like this:

```
passout.py clip my-email
```

## Graphical PIN Entry

Modern versions of GnuPG use `gpg-agent` manage the key-chain and cache
passwords. If you are using X11, then you probably want to use a graphical
PIN entry program like `pinentry-gtk-2`. This will cause a graphical
window to appear to prompt for the key-chain password when it is needed.

To use `pinentry-gtk-2`, put the following in your `${GNUPGHOME}/gpg-agent.conf`:

```
pinentry-program /usr/local/bin/pinentry-gtk-2
```

Obviously tweaking paths for your platform.

## Changing the Cache TTL in GnuPG

`gpg-agent` has quite a short TTL by default, meaning that you will end up
having to type your key-chain PIN quite frequently. You can change the TTL by
adding a line as follows to `${GNUPGHOME}/gpg-agent.conf`:

```
max-cache-ttl 14400
```

Here 14400 is the number of seconds to cache the PIN (4 hours in this case).

## System Tray Support

You can also run `passout.py tray` to place an icon in your desktop
environment's system tray. Right click the icon and select a password name
to have the password placed in the system clipboard.

When using the system tray, passwords can be organised into groups which
appear as sub-menus. To achieve this, use double underscore in your password
name to indicate groups. E.g. a password called `mail__gmail` will put a
`gmail` password into a `mail` sub-menu. Groups can be nested arbitrarily
deep.

## Tests

To run the test suite, from the source directory run:

```
py.test tests/
```

## Configuration File

PassOut is configured with a JSON config file at `~/.passout/passout.json`.

The following key is required:

 * `id`: The GnuPG key hash/email to use.

Then the following fields are optional:

 * `gpg`: Path to the GnuPG binary to use. (Default=`"gpg2"`).
 * `clip_clear_time`: Seconds after loading the clipboard before
   auto-destruction. (Default=`5`).
 * `notify_cmd`: Command used to notify of clipboard load/clears. Typically you
   would set this to `"notify-send"`. (Default=None).


## Troubleshooting

Try setting the `PASSOUT_DEBUG` environment. You can set this to any of
the levels accepted by the logging module.

E.g.:

```
export PASSOUT_DEBUG=DEBUG
```

## License

PassOut is distributed under the ISC license.

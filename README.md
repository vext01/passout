# PassOut

A *really* simple password manager built on gpg.

## Why?

I use a lot of programs that require passwords, e.g. offlineimap/msmtp/...
(you do too). To avoid having to memorise these passwords you either:

 * Put them in clear text in a config file, e.g. `.netrc`.
 * Use a password manager such as gnome-keyring, pwsafe, keepassx, etc.
 
The former is obviously annoying. The latter works, but I found that these
tools were either too heavyweight, or required me to type the master
password every time I needed to access the password store.

Therefore, I hacked up PassOut; a super-mega easy password manager written
in Python 3. You can set it up in minutes.

## Dependencies

  * GPG.
  * Python 3.
  * xclip (for clipboard support only).
  * A GUI pinentry program, e.g. `gtk-pinentry-2` (for X11 integration only).

## Quick Start

Generate a GPG key (if you don't yet have one):

```
gpg2 --gen-key
```

For info on this step, see the GPG docs for more info:
http://www.gnupg.org/gph/en/manual.html#AEN26

Tell PassOut about your key:

```
mkdir ~/.passout && echo "gpg=<your_gpg_binary>\nid=<your_gpg_id>\n" > \
	~/.passout/passoutrc
```

Where `<your_gpg_binary>` is the path to the gpg binary you want to use (I
recommend using version 2) and `<your_gpg_id>` is the email address
associate with the gpg key you want to use with PassOut.

Now add your passwords, e.g. to add a password named 'my-email':

```
passout.py add my-email
```

You will be prompted for the password. The password will not echo. Passwords
are stored GPG encrypted in `~/.pass/crypto_store`.

To retrieve a password to stdout:

```
passout.py stdout my-email
```

You will be prompted to unlock the GPG keychain and the password will be
printed.

Similarly, you can put the password in the X clipboard like this:

```
passout.py clip my-email
```

## X11 Integration

If you don't want to type your GPG password every time, you can use `gpg-agent`
with your X11 session. If you are using a `.xinitrc` or a `.xsession` (i.e.
you use `startx` or `xdm`) then you can add something like:

```
eval `/usr/local/bin/gpg-agent --daemon --pinentry-program /usr/local/bin/pinentry-gtk-2`
```

Obviously tweaking paths for your platform. You will now only need to unlock
the GPG key upon first use after X11 login, and then periodically when the
`gpg-agent` cache expires. To tweak the expiration time, pass a
`--max-cache-ttl` argument to `gpg-agent`.

If someone knows how to integrate with gdm/kdm, please send a pull request.

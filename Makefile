name = passout
python = python3
venv_name = $(name)_venv_$(python)
venv_sh = $(venv_name)/bin/activate

install:
	$(python) setup.py install

test:
	py.test tests

venv_test: $(venv_name) $(name).egg-info
	. $(venv_sh); py.test tests

$(venv_name):
	virtualenv -p $(python) $(venv_name)

$(name).egg-info:
	. $(venv_sh); $(python) setup.py develop;

clean:
	rm -rf $(venv_name) $(name).egg-info

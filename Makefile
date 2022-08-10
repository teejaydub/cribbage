all: run

depends:
	# First pass - not tested!
	curl https://pyenv.run | bash
	python3 -m pip install --user pipx
	pipx install pipenv
	pipenv install

remove-depends:
	pipenv --rm
	# maybe:
	# rm ~/.local/share/virtualenvs

run:
	pipenv run compare

compile_requirements:
	pip-compile requirements.in

git.init_pre_commit:
	pre-commit install
	pre-commit install --hook-type pre-push

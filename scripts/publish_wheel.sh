#!/bin/bash
# copyright 2024 Snow Leopard, Inc - all rights reserved


if [[ "$0" == "$BASH_SOURCE" ]]; then
	# we only want to do the things in this block when we're directly executed (not sourced)

	PROG_DESCRIPTION="publish python sdist and wheel"
	PROG_USAGE=""

	SCRIPT="$(readlink -f $0)"
	SCRIPT_DIR="$(dirname $SCRIPT)"
	. "$SCRIPT_DIR/common.sh"
fi


# --- notes


# * eventually we will switch to a CI workflow for publishing packages, so we won't need this


# --- init paths


initPaths


# --- setup validation


# before running this script, the caller must make a ~/.pypirc file; see docs:
#   https://packaging.python.org/en/latest/specifications/pypirc/
#   https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-the-distribution-archives
# TODO: if we end up using this for a while, explore other ways of storing auth info:
#   * explicitly provide .gitignored `--config-file repoRoot/pypirc` to twine
#   * use keyring package which twine installs; see warning box in this docs section:
#     https://packaging.python.org/en/latest/specifications/pypirc/#using-another-package-index
PYPI_CONFIG_PATH=$HOME/.pypirc
if [[ ! -r "$PYPI_CONFIG_PATH" ]]; then
	exitError "pypi configuration does not exist: \"$PYPI_CONFIG_PATH\""
fi


# --- publish


# swap to `testpypi` for testing
#SL_PYPI_REPOSITORY=testpypi
SL_PYPI_REPOSITORY=pypi

# NOTE: ./build_wheel.sh generates both the sdist and wheel in the wheel directory right now;
#   this will change in the future (see comments in that script)
"$PYTHON_BUILD_VENV_BUILDER_PYTHON" -m twine upload --repository $SL_PYPI_REPOSITORY "$PYTHON_BUILD_WHEEL_DIR"/*

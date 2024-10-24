#!/bin/bash
# copyright 2024 Snow Leopard, Inc - all rights reserved


if [[ "$0" == "$BASH_SOURCE" ]]; then
	# we only want to do the things in this block when we're directly executed (not sourced)

	PROG_DESCRIPTION="make virtualenv, install dependencies and local packages"
	PROG_USAGE="<pythonExecutablePath> [venvDirOverride]"

	SCRIPT="$(readlink -f $0)"
	SCRIPT_DIR="$(dirname $SCRIPT)"
	. "$SCRIPT_DIR/common.sh"
fi


# --- init paths


initPaths


# --- command line validation


PYTHON_BIN=$1
if [[ ! -x "$PYTHON_BIN" ]]; then
	exitError "pythonExecutablePath must be executable, got: \"$PYTHON_BIN\""
fi


VENV_DIR_OVERRIDE=$2
if [[ -n "$VENV_DIR_OVERRIDE" ]]; then
	if [[ -e "$VENV_DIR_OVERRIDE" ]]; then
		printStderr "warning: venvDirOverride exists: \"$VENV_DIR_OVERRIDE\""
	fi
	# after this point, $VENV_DIR will be $VENV_DIR_OVERRIDE
	setVenvPaths "$VENV_DIR_OVERRIDE"
fi


# --- create and init virtualenv


# TODO: allow override of virtualenv dir
makeVenv "$1" "$VENV_DIR"

# TODO: install pinned dependencies

"$VENV_PIP" install --editable "$SNOWLEOPARD_PACKAGE"

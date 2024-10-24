#!/bin/bash
# copyright 2024 Snow Leopard, Inc - all rights reserved


if [[ "$0" == "$BASH_SOURCE" ]]; then
	# we only want to do the things in this block when we're directly executed (not sourced)

	PROG_DESCRIPTION="build python sdist and wheel"
	PROG_USAGE="<pythonExecutablePath>"

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


# --- build prep


makeBuilderVenv "$PYTHON_BIN"


# --- test


# TODO: make a temp virtualenv, run tests there


# --- build


# NOTE: we currently build both the sdist and wheel to the wheel dir; eventually we will want to
#   build the sdist, then build wheels for other platforms from the sdist into the wheel dir
"$PYTHON_BUILD_VENV_BUILDER_PYTHON" -m build --outdir "$PYTHON_BUILD_WHEEL_DIR" "$SNOWLEOPARD_PACKAGE"

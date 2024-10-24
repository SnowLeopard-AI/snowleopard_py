#!/bin/bash
# copyright 2024 Snow Leopard, Inc - all rights reserved
if [[ "$0" == "$BASH_SOURCE" ]]; then
	echo "this file is intended to be sourced by another script, not directly executed" 1>&2
	# NOTE: the shebang above is for editor syntax highlighting.  this script
	#   should not have its executable flag set; the check in this if block
	#   is for people who ignore this comment
	exit 1
fi


# scripts wishing to use common.sh must define these variables
#   PROG_DESCRIPTION
#   PROG_USAGE
# TODO: document these (for now, see function `usage`)


set -e


# ---------------------------
# paths and constants


PROJECT_ROOT=$SCRIPT_DIR/..

# --- build, cache, and data paths

BUILD_DIR=$PROJECT_ROOT/sl_build

PYTHON_BUILD_ROOT=$BUILD_DIR/python

# python build process: virtualenv root
PYTHON_BUILD_VENV_ROOT=$PYTHON_BUILD_ROOT/venv
# python build process: builder virtualenv; see build_wheel.sh for more info
PYTHON_BUILD_VENV_BUILDER=$PYTHON_BUILD_VENV_ROOT/builder
# python build process: temp virtualenv; see build_wheel.sh for more info
PYTHON_BUILD_VENV_TEMP=$PYTHON_BUILD_VENV_ROOT/temp

# python build process: SL package build/install
PYTHON_BUILD_DIR=$PYTHON_BUILD_ROOT/build
PYTHON_BUILD_SDIST_DIR=$PYTHON_BUILD_DIR/sdist
PYTHON_BUILD_WHEEL_DIR=$PYTHON_BUILD_DIR/wheel

# --- python paths

# NOTE: see "global defaults" section to see where default VENV_DIR is set
VENV_DIR_DEFAULT="$PROJECT_ROOT/venv"

# python build process: builder virtualenv executable paths
PYTHON_BUILD_VENV_BUILDER_BIN=$PYTHON_BUILD_VENV_BUILDER/bin
PYTHON_BUILD_VENV_BUILDER_PYTHON=$PYTHON_BUILD_VENV_BUILDER_BIN/python
PYTHON_BUILD_VENV_BUILDER_PIP=$PYTHON_BUILD_VENV_BUILDER_BIN/pip

# --- python packages

SNOWLEOPARD_PACKAGE_NAME=snowleopard

SNOWLEOPARD_PACKAGE=$PROJECT_ROOT


# ---------------------------
# helper functions


function printStderr
{
	echo "$1" 1>&2
} # function printStderr


function usage
{
	printStderr "usage: $0 $PROG_USAGE"
	printStderr "$PROG_DESCRIPTION"
} # function usage


function exitError
{
	printStderr "error: $1"
	usage
	exit 1
} # function exitError


function setVenvPaths
{
	# --- standard venv paths

	VENV_DIR="$1"
	VENV_BIN="$VENV_DIR/bin"
	VENV_PYTHON="$VENV_BIN/python"
	VENV_PIP="$VENV_BIN/pip"
} # function setVenvPaths


function initBuild
{
	# container build
	mkdir -p "$PYTHON_BUILD_VENV_ROOT"

	mkdir -p "$PYTHON_BUILD_SDIST_DIR"
	mkdir -p "$PYTHON_BUILD_WHEEL_DIR"
}


function initPaths
{
	initBuild
}


# makeVenv(): create a python virtualenv and optionally install packages.
# WARNING: this function deletes the provided virtualenv path ($2) without confirmation when the
#   python executable is not found
# parameters
#   $1: path to the python installation from which the virtualenv will be created
#   $2: path to the virtualenv to create; WARNING: this path may be deleted by this function
#   $3: path to a requirements.txt file to install (this is skipped if $2 is empty or unspecified)
function makeVenv
{
	# skip creation if the virtualenv already exists (we assume the installation is complete if
	#   the executable is present)
	if [[ ! -x "$2/bin/python" ]]; then
		# clean up partial venv if anything exists
		rm -rf "$2"

		"$1" -m venv "$2"
		"$2/bin/python" -m pip install --upgrade pip

		if [[ "x$3" != "x" ]]; then
			"$2/bin/pip" install --requirement "$3"
		fi
	fi
}


# makeBuilderVenv(): ensure a builder virtualenv exists based on the same python version we use to
#   deploy.  the builder venv contains the `build` package, its dependencies, and nothing else.
#   this is separate to ensure it doesn't contaminate the tests we're about to run in the temp
#   venv.
# parameters
#   $1: path to the python installation from which the virtualenv will be created
function makeBuilderVenv
{
	makeVenv "$1" "$PYTHON_BUILD_VENV_BUILDER" "$SCRIPT_DIR/reqs_builder.txt"
}


# ---------------------------
# global defaults


setVenvPaths "$VENV_DIR_DEFAULT"

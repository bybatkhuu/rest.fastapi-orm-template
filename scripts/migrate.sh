#!/bin/bash
set -euo pipefail


## --- Base --- ##
# Getting path of this script file:
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
_PROJECT_DIR="$(cd "${_SCRIPT_DIR}/.." >/dev/null 2>&1 && pwd)"
cd "${_PROJECT_DIR}" || exit 2

# Loading base script:
# shellcheck disable=SC1091
source ./scripts/base.sh

# Loading .env file (if exists):
if [ -f ".env" ]; then
	# shellcheck disable=SC1091
	source .env
fi


if [ -z "$(which alembic)" ]; then
	echoError "'alembic' not found or not installed."
	exit 1
fi

cd ./src || exit 2
## --- Base --- ##


## --- Functions --- ##
_createRevision()
{
	_msg="${1:-New migration.}"
	echoInfo "Creating alembic migration with message: ${_msg}"
	alembic revision --autogenerate -m "${_msg}"
	echoOk "Migration created successfully."
}

_upgradeMigration()
{
	_target="${1:-head}"
	echoInfo "Upgrading database to: ${_target}"
	alembic -x data=true upgrade "${_target}"
	echoOk "Database upgraded to: ${_target}"
}

_downgradeMigration()
{
	_target="${1:--1}"
	echoInfo "Downgrading database to: ${_target}"
	alembic downgrade "${_target}"
	echoOk "Database downgraded to: ${_target}"
}

_showHistory()
{
	echoInfo "Showing alembic migration history:"
	alembic history
	echoOk "Done."
}

_showCurrent()
{
	echoInfo "Current alembic migration:"
	alembic current -v
	echoOk "Done."
}

_checkChanges()
{
	echoInfo "Checking alembic migration changes:"
	alembic check
	echoOk "Done."
}

_showHeads()
{
	echoInfo "Showing alembic migration heads:"
	alembic heads
	echoOk "Done."
}
## --- Functions --- ##


## --- Menu arguments --- ##
main()
{
	if [ -z "${1:-}" ]; then
		_createRevision
		exit 0
	fi

	_action="${1:-}"
	shift || true
	case ${_action} in
		create | new | revision | rev)
			_createRevision "${@:-}"
			;;
		upgrade | up)
			_upgradeMigration "${@:-}"
			;;
		downgrade | down)
			_downgradeMigration "${@:-}"
			;;
		history | hist)
			_showHistory
			;;
		current | cur | now)
			_showCurrent
			;;
		check | validate)
			_checkChanges
			;;
		heads | head)
			_showHeads
			;;
		*)
			echoError "Failed to parsing input: ${_action}"
			echoInfo "USAGE: ${0}  revision | upgrade | downgrade | history | current | check | heads"
			exit 1
			;;
	esac

	exit 0
}

main "${@:-}"
## --- Menu arguments --- ##

#!/bin/bash
set -euo pipefail


_doStart()
{
	# sleep 3

	# echo "INFO: Starting alembic migration..."
	# _max_attempts=3
	# _attempt_counter=0
	# _sleep_seconds=5

	# while true; do
	# 	if alembic upgrade head 2>/dev/null; then
	# 		echo -e "OK: Alembic migration completed successfully.\n"
	# 		break
	# 	else
	# 		if (( _attempt_counter == _max_attempts )); then
	# 			echo "ERROR: Maximum attempts reached. Failed to connect database!"
	# 			exit 1
	# 		fi

	# 		_attempt_counter=$((_attempt_counter + 1))
	# 		echo "WARN: Unable to connect database ${_attempt_counter} time(s), retrying in ${_sleep_seconds} second(s)..."
	# 		sleep ${_sleep_seconds}
	# 	fi
	# done
	# echo "OK: Database is ready. Continuing with application startup..."

	echo "INFO: Starting alembic migration..."
	alembic upgrade head || exit 2
	echo -e "OK: Alembic migration completed successfully.\n"

	echo "OK: Database is ready. Continuing with application startup..."
	exec python -u ./main.py || exit 2
	# exec uvicorn main:app --host=0.0.0.0 --port="${FOT_APP_PORT:-8000}" --no-server-header --proxy-headers --forwarded-allow-ips='*' --no-access-log || exit 2
	exit 0
}

main()
{
	sudo chown -Rc "${USER}:${GROUP}" "${FOT_APP_DIR}" "${FOT_APP_DATA_DIR}" "${FOT_APP_LOGS_DIR}" || exit 2
	find "${FOT_APP_DIR}" "${FOT_APP_DATA_DIR}" -type d -exec chmod 770 {} + || exit 2
	find "${FOT_APP_DIR}" "${FOT_APP_DATA_DIR}" -type f -exec chmod 660 {} + || exit 2
	find "${FOT_APP_DIR}" "${FOT_APP_DATA_DIR}" -type d -exec chmod ug+s {} + || exit 2
	find "${FOT_APP_LOGS_DIR}" -type d -exec chmod 775 {} + || exit 2
	find "${FOT_APP_LOGS_DIR}" -type f -exec chmod 664 {} + || exit 2
	find "${FOT_APP_LOGS_DIR}" -type d -exec chmod +s {} + || exit 2
	chmod ug+x "${FOT_APP_HOME}/main.py" || exit 2
	echo "${USER} ALL=(ALL) ALL" | sudo tee -a "/etc/sudoers.d/${USER}" > /dev/null || exit 2
	echo ""

	## Parsing input:
	case ${1:-} in
		"" | -s | --start | start | --run | run)
			_doStart;;
			# shift;;

		-b | --bash | bash | /bin/bash)
			shift
			if [ -z "${*:-}" ]; then
				echo "INFO: Starting bash..."
				/bin/bash
			else
				echo "INFO: Executing command -> ${*}"
				exec /bin/bash -c "${@}" || exit 2
			fi
			exit 0;;
		*)
			echo "ERROR: Failed to parsing input -> ${*}"
			echo "USAGE: ${0} -s, --start, start | -b, --bash, bash, /bin/bash"
			exit 1;;
	esac
}

main "${@:-}"

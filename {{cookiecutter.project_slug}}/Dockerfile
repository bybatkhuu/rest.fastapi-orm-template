# syntax=docker/dockerfile:1

ARG PYTHON_VERSION={{cookiecutter.python_version}}
ARG BASE_IMAGE=python:${PYTHON_VERSION}-slim-bookworm

ARG DEBIAN_FRONTEND=noninteractive
ARG {{cookiecutter.env_prefix}}API_SLUG="{{cookiecutter.project_slug}}"


## Here is the builder image:
FROM ${BASE_IMAGE} AS builder

ARG DEBIAN_FRONTEND
ARG {{cookiecutter.env_prefix}}API_SLUG

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR "/usr/src/{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_SLUG}"

RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=private \
	--mount=type=cache,target=/root/.cache,sharing=locked \
	_BUILD_TARGET_ARCH=$(uname -m) && \
	echo "BUILDING TARGET ARCHITECTURE: ${_BUILD_TARGET_ARCH}" && \
	rm -rfv /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* && \
	apt-get clean -y && \
	# echo "Acquire::http::Pipeline-Depth 0;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	# echo "Acquire::http::No-Cache true;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	# echo "Acquire::BrokenProxy true;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	apt-get update --fix-missing -o Acquire::CompressionTypes::Order::=gz && \
	apt-get install -y --no-install-recommends \
		build-essential \
		libpq-dev && \
	python3 -m pip install --timeout 60 -U pip

# COPY ./requirements* ./
RUN	--mount=type=cache,target=/root/.cache,sharing=locked \
	--mount=type=bind,source=requirements.txt,target=requirements.txt \
	python3 -m pip install --prefix=/install --timeout 60 -r ./requirements.txt


## Here is the base image:
FROM ${BASE_IMAGE} AS base

ARG DEBIAN_FRONTEND
ARG {{cookiecutter.env_prefix}}API_SLUG

ARG {{cookiecutter.env_prefix}}HOME_DIR="/app"
ARG {{cookiecutter.env_prefix}}API_DIR="{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}HOME_DIR}/{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_SLUG}"
ARG {{cookiecutter.env_prefix}}API_DATA_DIR="/var/lib/{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_SLUG}"
ARG {{cookiecutter.env_prefix}}API_LOGS_DIR="/var/log/{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_SLUG}"
ARG {{cookiecutter.env_prefix}}API_TMP_DIR="/tmp/{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_SLUG}"
ARG {{cookiecutter.env_prefix}}API_PORT=8000
## IMPORTANT!: Get hashed password from build-arg!
## echo "{{cookiecutter.env_prefix}}USER_PASSWORD123" | openssl passwd -5 -stdin
ARG HASH_PASSWORD="\$5\$S6d3bt3eXvBW3zT1\$GcPvS36pfZ1Sk/oE8ixklLYrvQegc1xFjtE7gxlzJU8"
ARG UID=1000
ARG GID=11000
ARG USER={{cookiecutter.project_abbr}}-user
ARG GROUP={{cookiecutter.project_abbr}}-group

ENV {{cookiecutter.env_prefix}}HOME_DIR="{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}HOME_DIR}" \
	{{cookiecutter.env_prefix}}API_DIR="{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DIR}" \
	{{cookiecutter.env_prefix}}API_DATA_DIR="{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DATA_DIR}" \
	{{cookiecutter.env_prefix}}API_LOGS_DIR="{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_LOGS_DIR}" \
	{{cookiecutter.env_prefix}}API_TMP_DIR="{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_TMP_DIR}" \
	{{cookiecutter.env_prefix}}API_PORT={% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_PORT} \
	UID=${UID} \
	GID=${GID} \
	USER=${USER} \
	GROUP=${GROUP} \
	PYTHONIOENCODING=utf-8 \
	PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN rm -rfv /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /root/.cache/* && \
	apt-get clean -y && \
	# echo "Acquire::http::Pipeline-Depth 0;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	# echo "Acquire::http::No-Cache true;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	# echo "Acquire::BrokenProxy true;" >> /etc/apt/apt.conf.d/99fixbadproxy && \
	apt-get update --fix-missing -o Acquire::CompressionTypes::Order::=gz && \
	apt-get install -y --no-install-recommends \
		sudo \
		locales \
		tzdata \
		procps \
		iputils-ping \
		iproute2 \
		curl \
		nano \
		libpq5 && \
	apt-get clean -y && \
	sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
	sed -i -e 's/# en_AU.UTF-8 UTF-8/en_AU.UTF-8 UTF-8/' /etc/locale.gen && \
	sed -i -e 's/# ko_KR.UTF-8 UTF-8/ko_KR.UTF-8 UTF-8/' /etc/locale.gen && \
	dpkg-reconfigure --frontend=noninteractive locales && \
	update-locale LANG=en_US.UTF-8 && \
	echo "LANGUAGE=en_US.UTF-8" >> /etc/default/locale && \
	echo "LC_ALL=en_US.UTF-8" >> /etc/default/locale && \
	addgroup --gid ${GID} ${GROUP} && \
	useradd -lmN -d "/home/${USER}" -s /bin/bash -g ${GROUP} -G sudo -u ${UID} ${USER} && \
	echo "${USER} ALL=(ALL) NOPASSWD: ALL" > "/etc/sudoers.d/${USER}" && \
	chmod 0440 "/etc/sudoers.d/${USER}" && \
	echo -e "${USER}:${HASH_PASSWORD}" | chpasswd -e && \
	echo -e "\nalias ls='ls -aF --group-directories-first --color=auto'" >> /root/.bashrc && \
	echo -e "alias ll='ls -alhF --group-directories-first --color=auto'\n" >> /root/.bashrc && \
	echo -e "\numask 0002" >> "/home/${USER}/.bashrc" && \
	echo "alias ls='ls -aF --group-directories-first --color=auto'" >> "/home/${USER}/.bashrc" && \
	echo -e "alias ll='ls -alhF --group-directories-first --color=auto'\n" >> "/home/${USER}/.bashrc" && \
	rm -rfv /var/lib/apt/lists/* /var/cache/apt/archives/* /tmp/* /root/.cache/* "/home/${USER}/.cache/*" && \
	mkdir -pv "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DIR}" "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DATA_DIR}" "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_LOGS_DIR}" "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_TMP_DIR}" && \
	chown -Rc "${USER}:${GROUP}" "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}HOME_DIR}" "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DATA_DIR}" "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_LOGS_DIR}" "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_TMP_DIR}" && \
	find "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DIR}" "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DATA_DIR}" -type d -exec chmod -c 770 {} + && \
	find "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DIR}" "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DATA_DIR}" -type d -exec chmod -c ug+s {} + && \
	find "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_LOGS_DIR}" "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_TMP_DIR}" -type d -exec chmod -c 775 {} + && \
	find "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_LOGS_DIR}" "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_TMP_DIR}" -type d -exec chmod -c +s {} +

ENV LANG=en_US.UTF-8 \
	LANGUAGE=en_US.UTF-8 \
	LC_ALL=en_US.UTF-8

COPY --from=builder --chown=${UID}:${GID} /install /usr/local


## Here is the final image:
FROM base AS app

WORKDIR "{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DIR}"
COPY --chown=${UID}:${GID} ./src {% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DIR}
COPY --chown=${UID}:${GID} --chmod=770 ./scripts/docker/*.sh /usr/local/bin/

# VOLUME ["{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_DATA_DIR}"]
# EXPOSE {% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_PORT}

USER ${UID}:${GID}
# HEALTHCHECK --start-period=30s --start-interval=1s --interval=5m --timeout=5s --retries=3 \
# 	CMD curl -f http://localhost:{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_PORT}/api/v{% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_VERSION:-1}/ping || exit 1

ENTRYPOINT ["docker-entrypoint.sh"]
# CMD ["-b", "uvicorn main:app --host=0.0.0.0 --port={% raw %}${{% endraw %}{{cookiecutter.env_prefix}}API_PORT:-8000} --no-access-log --no-server-header --proxy-headers --forwarded-allow-ips='*'"]

FROM python:{{cookiecutter.python_version}}-slim-bullseye

# Setup environment to match variables set by repo2docker as much as possible
# Tell apt-get to not block installs by asking for interactive human input
ENV DEBIAN_FRONTEND=noninteractive \
    # Set username, uid and gid (same as uid) of non-root user the container will be run as
    APP_USER=jovyan \
    APP_UID=1000 \
    # Use /bin/bash as shell, not the default /bin/sh (arrow keys, etc don't work then)
    SHELL=/bin/bash \
    # Setup locale to be UTF-8, avoiding gnarly hard to debug encoding errors
    LANG=C.UTF-8  \
    LC_ALL=C.UTF-8

# Home directory of our non-root user
ENV HOME=/home/${APP_USER}

RUN echo "Creating ${APP_USER} user..." \
    # Create a group for the user to be part of, with gid same as uid
    && groupadd --gid ${APP_UID} ${APP_USER}  \
    # Create non-root user, with given gid, uid and create $HOME
    && useradd --create-home --gid ${APP_UID} --no-log-init --uid ${APP_UID} ${APP_USER} \
    # Make sure that /srv is owned by non-root user, so we can install things there
    && chown -R ${APP_USER}:${APP_USER} /srv

# Get uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install basic apt packages
RUN echo "Installing apt-get packages..." \
    && apt-get update --fix-missing > /dev/null \
    && apt-get install -y apt-utils build-essential > /dev/null \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add TZ configuration - https://github.com/PrefectHQ/prefect/issues/3061
ENV TZ=UTC

# Switch User & Workdir
USER ${APP_USER}
WORKDIR ${HOME}

# Copy remaining project files
COPY --chown=jovyan:jovyan . ${HOME}

# Setup python env
RUN uv sync --frozen --no-cache

CMD ["bash"]

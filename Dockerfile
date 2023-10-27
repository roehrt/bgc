FROM debian
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    pypy3 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY scripts/ /.scripts/bin
ENV PATH="${PATH}:/.scripts/bin"
COPY game /game
ENTRYPOINT [ "mypython", "/game/game.py" ]
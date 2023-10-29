FROM debian
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    pypy3 \
    pypy3-dev \
    pypy3-lib \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN echo "PP{wR0nG_CHa11eNg3}" > /flag.txt && chmod 400 /flag.txt
COPY scripts/ /.scripts/bin
ENV PATH="${PATH}:/.scripts/bin"
COPY game /game
#ENTRYPOINT [ "mypython", "/game/game.py" ]
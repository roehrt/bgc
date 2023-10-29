FROM debian
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    pypy3 \
    pypy3-dev \
    pypy3-lib \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY submissions /submissions
COPY scripts/ /scripts/bin
ENV PATH="${PATH}:/scripts/bin"
COPY game /game

# to confuse CTF people
RUN echo "PP{wR0nG_tYp3_0f_CHa11eNg3}" > /flag.txt && chmod 400 /flag.txt

FROM python:3.11-slim-bookworm

RUN apt update && apt upgrade -y \
    && apt install -y git curl python3-pip ffmpeg unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Deno for yt-dlp YouTube JavaScript challenges
RUN curl -fsSL https://deno.land/install.sh | sh

ENV PATH="/root/.deno/bin:${PATH}"

WORKDIR /MusicPlayer

COPY . /MusicPlayer

RUN pip3 install --upgrade pip
RUN pip3 install -U -r /MusicPlayer/requirements.txt

RUN chmod +x /MusicPlayer/startup.sh

CMD ["/bin/bash", "/MusicPlayer/startup.sh"]

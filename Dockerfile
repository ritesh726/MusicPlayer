FROM python:3.11-slim-bookworm

RUN apt update && apt upgrade -y
RUN apt install git curl python3-pip ffmpeg -y

WORKDIR /MusicPlayer

COPY . /MusicPlayer

RUN pip3 install --upgrade pip
RUN pip3 install -U -r /MusicPlayer/requirements.txt

RUN chmod +x /MusicPlayer/startup.sh

CMD ["/bin/bash", "/MusicPlayer/startup.sh"]

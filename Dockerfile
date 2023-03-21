FROM continuumio/miniconda3:22.11.1

ENV TZ=Europe/Zurich

WORKDIR /app

RUN apt-get -y update && apt-get install -y \
    git \
    python3-pip \
    zip \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone


RUN mkdir /models

RUN curl --header "Deploy-Token: T11beRJhaW2RF7UazR_F" --remote-name --location "https://gitlab.idiap.ch/api/v4/projects/5649/packages/generic/wenet-api/latest/models.zip" --user "bot:T11beRJhaW2RF7UazR_F"
RUN unzip models.zip -d / && rm models.zip
COPY . .

RUN pip install .

CMD ["python3", "-m", "activity_predictor.main", "--env", "dev", "--models_path", "/models"]

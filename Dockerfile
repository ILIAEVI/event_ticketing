FROM continuumio/miniconda3
LABEL authors="giorgi"

RUN mkdir -p /home/djangoapp/src

WORKDIR /home/djangoapp/src

COPY ./requirements.txt /home/djangoapp/src/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /home/djangoapp/src/

EXPOSE 8000
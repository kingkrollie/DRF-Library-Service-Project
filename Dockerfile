FROM python:3.13-slim
LABEL maintainer="HotFix_Heroes"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/media && mkdir -p /app/static

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

RUN chown -R my_user /app
RUN chown -R my_user /app/media
RUN chmod -R 755 /app/media

USER my_user

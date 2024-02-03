FROM debian:sid

# Use a valid Debian Sid repository mirror
RUN echo 'deb http://deb.debian.org/debian sid main contrib non-free' > /etc/apt/sources.list

RUN apt update && apt upgrade -y
RUN apt-get install tzdata -y
RUN apt install -y python3 python3-dev python3-pip python3-venv npm git

RUN python3 -m venv /venv
ENV PYTHON=/venv/bin/python3
RUN $PYTHON -m pip install poetry gunicorn

WORKDIR /app

COPY poetry.lock pyproject.toml /app/
RUN $PYTHON -m poetry config virtualenvs.create false && $PYTHON -m poetry install --no-interaction --only main

COPY app/static/package.json /app/static/package-lock.json app/static/
RUN npm install --prefix app/static

COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000"]
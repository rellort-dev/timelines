# BaseImage
FROM python:3.9-slim

# WORKDIR
WORKDIR /Users/cyanaspect/Projects/timelines

# COPY
COPY backend backend
COPY config config
COPY ml ml
COPY db.sqlite3 dbsqlite3
COPY manage.py manage.py 
COPY requirements.txt requirements.txt
COPY setup.py setup.py

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install --upgrade pip setuptools wheel \
    && python3 -m pip install -e . --no-cache-dir \
    && python3 -m pip install protobuf==3.20.1 --no-cache-dir \
    && apt-get purge -y --auto-remove gcc build-essential

# expose ports
EXPOSE 3000

# Start app
ENTRYPOINT python3 manage.py runserver 0:3000

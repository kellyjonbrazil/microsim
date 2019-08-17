# Dockerfile for microsimserver

# run as:
# docker run -d --rm \
#    -e LISTEN_PORT=5000 \
#    -e RESPOND_BYTES=1024 \
#    -e STOP_SECONDS=300 \
#    -p 5000:5000 \
#    kellybrazil/microsimserver

FROM python:3.7-alpine

RUN mkdir /app

COPY microsimserver.py /app

WORKDIR /app

CMD [ "python", "./microsimserver.py" ]

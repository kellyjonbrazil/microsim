# Dockerfile for microsimserver

# run as:
# docker run -d --rm \
#     -e LISTEN_PORT=8080 \
#     -e STATS_PORT=5001 \
#     -e STATSD_HOST="172.17.0.2" \
#     -e STATSD_PORT=8100 \
#     -e RESPOND_BYTES=1024 \
#     -e STOP_SECONDS=300 \
#     -e STOP_PADDING=True \
#     -p 8080:8080 \
#     -p 5001:5001 \
#     kellybrazil/microsimserver

FROM python:3.7-alpine

RUN mkdir /app
RUN pip install statsd
RUN apk --no-cache add curl

COPY microsimserver.py /app

WORKDIR /app

CMD [ "python", "-u", "./microsimserver.py" ]

# Dockerfile for microsimserver

# run as:
# docker run -d --rm \
#    -e LISTEN_PORT=5000 \
#    -e STATS_PORT=5001 \
#    -e STATSD_HOST=localhost \
#    -e STATSD_PORT=8125 \
#    -e RESPOND_BYTES=1024 \
#    -e STOP_SECONDS=300 \
#    -p 5000:5000 \
#    -p 5001:5001 \
#    kellybrazil/microsimserver

FROM python:3.7-alpine

RUN mkdir /app
RUN pip install statsd
RUN apk --no-cache add curl

COPY microsimserver.py /app

WORKDIR /app

CMD [ "python", "-u", "./microsimserver.py" ]

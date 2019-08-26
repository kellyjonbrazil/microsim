# Dockerfile for microsimclient

# run as:
# docker run -d --rm \
#     -e STATS_PORT=5000 \
#     -e STATSD_HOST="172.17.0.2" \
#     -e STATSD_PORT=8100 \
#     -e REQUEST_URLS="http://service1.default.svc.cluster.local:8080,http://service2.default.svc.cluster.local:5000" \
#     -e REQUEST_INTERNET=True \
#     -e REQUEST_MALWARE=True \
#     -e SEND_SQLI=True \
#     -e SEND_DIR_TRAVERSAL=True \
#     -e SEND_XSS=True \
#     -e SEND_DGA=True \
#     -e REQUEST_WAIT_SECONDS=0.5 \
#     -e REQUEST_BYTES=128 \
#     -e REQUEST_PROBABILITY=0.9 \
#     -e EGRESS_PROBABILITY=0.3 \
#     -e ATTACK_PROBABILITY=0.05 \
#     -e STOP_SECONDS=300 \
#     -e STOP_PADDING=True \
#     -p 5000:5000 \
#     kellybrazil/microsimclient

FROM python:3.7-alpine

RUN mkdir /app
RUN pip install requests
RUN pip install statsd
RUN apk --no-cache add curl

COPY microsimclient.py /app

WORKDIR /app

CMD [ "python", "-u", "./microsimclient.py" ]

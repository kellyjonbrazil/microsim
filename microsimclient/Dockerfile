# Dockerfile for microsimclient

# run as:
# docker run -d --rm \
#    -e STATS_PORT=5001 \
#    -e STATSD_HOST=localhost \
#    -e STATSD_PORT=8125 \
#    -e REQUEST_URLS="http://service1.default.svc.cluster.local:8080,http://service2.default.svc.cluster.local:5000" \
#    -e REQUEST_INTERNET=True \
#    -e REQUEST_MALWARE=True \
#    -e SEND_SQLI=True \
#    -e SEND_DIR_TRAVERSAL=True \
#    -e SEND_XSS=True \
#    -e SEND_DGA=True \
#    -e REQUEST_WAIT_SECONDS=1 \
#    -e REQUEST_BYTES=128 \
#    -e STOP_SECONDS=300 \
#    -e ATTACK_PROBABILITY=0.01 \
#    -e EGRESS_PROBABILITY=0.1 \
#    -p 5001:5001
#    kellybrazil/microsimclient

FROM python:3.7-alpine

RUN mkdir /app
RUN pip install requests
RUN pip install statsd
RUN apk --no-cache add curl

COPY microsimclient.py /app

WORKDIR /app

CMD [ "python", "-u", "./microsimclient.py" ]

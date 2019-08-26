# microsim

The purpose of this project is to be able to easily set up kubernetes deployments with somewhat realistic/controllable traffic and attacks to test load balancing, WAF, and other security solutions in the cluster.

Also available on Docker Hub:

https://hub.docker.com/r/kellybrazil/microsimserver

https://hub.docker.com/r/kellybrazil/microsimclient

This application generates traffic between simulated microservices using JSON over HTTP. Many parameters can be set on the client and server apps (`microsimclient` and `microsimserver`) to specify the listening port, the amount of traffic generated, whether requests are sent to the internet, whether certain application attacks are sent, and whether malware is downloaded. You can also set the client and server to kill themselves after a number of seconds.

Sample Kubernetes deployments can be found in the https://github.com/kellyjonbrazil/microsim/tree/master/k8s_deployments folder.

![Simple Deployment](https://github.com/kellyjonbrazil/microsim/blob/master/k8s_deployments/images/simple.png)

## Usage

All parameters are set via environment variables. Unset parameters will use the defaults:

`microsimserver`

| Parameter          | Values          | Default          | Description                                     |
| ------------------ |-----------------| -----------------| ------------------------------------------------|
| `LISTEN_PORT`      | `1` - `65535`   | `8080`           | Port the HTTP server listens on                 |
| `STATS_PORT`       | `1` - `65535`   | None             | Enable the HTTP stats server running on the specified port |
| `STATSD_HOST`      | `"1.2.3.4"`     | None             | Enable sending StatsD stats to the specified host |
| `STATSD_PORT`      | `1` - `65535`   | `8125`           | Modify the default StatsD destination port, if desired |
| `RESPOND_BYTES`    | `1` - ?         | `16384`          | How many data bytes are added to the response   |
| `STOP_SECONDS`     | `0` - ?         | `0` (never stop) | Kill the server after x seconds                 |
| `STOP_PADDING`     | `True`/`False`  | `False`          | Add random padding to `STOP_SECONDS`            |

`microsimclient`

| Parameter             | Values          | Default  | Description                                     |
| --------------------- |-----------------| ---------| ------------------------------------------------|
| `STATS_PORT`          | `1` - `65535`   | None     | Enable the HTTP stats server running on the specified port |
| `STATSD_HOST`         | `"1.2.3.4"`     | None             | Enable sending StatsD stats to the specified host |
| `STATSD_PORT`         | `1` - `65535`   | `8125`           | Modify the default StatsD destination port, if desired |
| `REQUEST_URLS`          | `"http://auth:8080,http://db:8080"` | None      | One or more comma separated URLs to send requests to. *Note: this is a required parameter* |
| `REQUEST_INTERNET`      | `True`/`False`      | `False`    | Send regular requests to the internet if True             |
| `REQUEST_MALWARE`       | `True`/`False`      | `False`    | Occasionally download an eicar sample from the internet   |
| `SEND_SQLI`             | `True`/`False`      | `False`    | Occasionally send SQLi to the REQUEST_URLS                |
| `SEND_XSS`              | `True`/`False`      | `False`    | Occasionally send XSS to the REQUEST_URLS                 |
| `SEND_DIR_TRAVERSAL`    | `True`/`False`      | `False`    | Occasionally send Directory Traversal to the REQUEST_URLS |
| `SEND_DGA`              | `True`/`False`      | `False`    | Occasionally send DGA DNS requests to the resolver        |
| `REQUEST_WAIT_SECONDS`  | `0` - ? (float)  | `1.0`        | Number of seconds to wait between request loop runs |
| `REQUEST_BYTES`         | `1` - `7980`        | `1024`     | How many data bytes are added to the request              |
| `REQUEST_PROBABILITY`   | `0.9`               | `1.0`      | Float value representing the percentage probability of an internal request triggering per loop |
| `EGRESS_PROBABILITY`    | `0.1` (float)       | `0.1`      | Float value representing the percentage probability of an egress Internet request triggering per loop |
| `ATTACK_PROBABILITY`    | `0.01` (float)      | `0.01`     | Float value representing the percentage probability of one of the attack behaviors triggering per loop |
| `STOP_SECONDS`          | `0` - ?             | `0` (never stop) | Kill the client after x seconds     |
| `STOP_PADDING`          | `True`/`False`      | `False`    | Add random padding to `STOP_SECONDS`            |

Example docker commands:
```
docker run -d --rm \
    -e LISTEN_PORT=8080 \
    -e STATS_PORT=5001 \
    -e STATSD_HOST="172.17.0.2" \
    -e STATSD_PORT=8100 \
    -e RESPOND_BYTES=1024 \
    -e STOP_SECONDS=300 \
    -e STOP_PADDING=True \
    -p 8080:8080 \
    kellybrazil/microsimserver
```

```
docker run -d --rm \
    -e STATS_PORT=5000 \
    -e STATSD_HOST="172.17.0.2" \
    -e STATSD_PORT=8100 \
    -e REQUEST_URLS="http://service1.default.svc.cluster.local:8080,http://service2.default.svc.cluster.local:5000" \
    -e REQUEST_INTERNET=True \
    -e REQUEST_MALWARE=True \
    -e SEND_SQLI=True \
    -e SEND_DIR_TRAVERSAL=True \
    -e SEND_XSS=True \
    -e SEND_DGA=True \
    -e REQUEST_WAIT_SECONDS=0.5 \
    -e REQUEST_BYTES=128 \
    -e REQUEST_PROBABILITY=0.9 \
    -e EGRESS_PROBABILITY=0.3 \
    -e ATTACK_PROBABILITY=0.05 \
    -e STOP_SECONDS=300 \
    -e STOP_PADDING=True \
    kellybrazil/microsimclient
```

Example response from the `microsimserver`:
```
$ curl -X POST localhost:8080/any_arbitrary_path | jq .
{
  "data": "3BbTvDWTD7yWBsWkffiTft5V875EpldKSehv2uXvUSHgl6Sjjl",
  "time": "Sat Aug 17 15:34:09 2019",
  "hostname": "laptop.local",
  "ip": "192.168.1.221",
  "remote": "127.0.0.1",
  "hostheader": "localhost:8080",
  "path": "/any_arbitrary_path"
}
```
The `data` field is randomly generated text. The number of characters is controlled with the `RESPOND_BYTES` parameter.

If a normal `GET` request is sent, then the response will look like this:
```
$ curl localhost:8080/any_arbitrary_path
f0QRurmXLiuungowUkQMJf3z687BDgsUpV3Lupaln2WUH4egk007En3m11lIurSwcekiI1PqhyRHpzPzYB
Sat Aug 17 15:42:29 2019   hostname: laptop.local   ip: 192.168.1.221   remote: 127.0.0.1   hostheader: localhost:8080   path: /any_arbitrary_path
```

In this case, the first line is the `data` field sent from the `microsimserver`.

The `microsimclient` similarly POST's a `data` field in the request body which is filled with randomly generated text. The number of characters is controled with the `REQUEST_BYTES` parameter.

## Local Statistics

If desired, a realtime statistics HTTP server can be enabled by specifying the `STATS_PORT` parameter for both the client and the server. The curl command is included in the Docker container so local and remote stats can also be pulled from within the container. Example output:

`microsimserver`:
```
$ curl localhost:5001
{
  "time": "Mon Aug 26 15:26:18 2019",
  "runtime": 42,
  "hostname": "server01",
  "ip": "192.168.1.221",
  "stats": {
    "Requests": 138,
    "Sent Bytes": 2284728,
    "Received Bytes": 142968,
    "Attacks": 2,
    "SQLi": 1,
    "XSS": 0,
    "Directory Traversal": 1
  },
  "config": {
    "LISTEN_PORT": 8080,
    "STATS_PORT": 5001,
    "STATSD_HOST": null,
    "STATSD_PORT": 8125,
    "RESPOND_BYTES": 16384,
    "STOP_SECONDS": 60,
    "STOP_PADDING": true,
    "TOTAL_STOP_SECONDS": 102
  }
}
```

`microsimclient`:
```
$ curl localhost:5000
{
  "time": "Mon Aug 26 15:10:40 2019",
  "runtime": 40,
  "hostname": "client01",
  "ip": "192.168.1.221",
  "stats": {
    "Requests": 125,
    "Sent Bytes": 129500,
    "Received Bytes": 2216193,
    "Internet Requests": 12,
    "Attacks": 0,
    "SQLi": 0,
    "XSS": 0,
    "Directory Traversal": 0,
    "DGA": 0,
    "Malware": 0,
    "Error": 3
  },
  "config": {
    "STATS_PORT": 5000,
    "STATSD_HOST": null,
    "STATSD_PORT": 8125,
    "REQUEST_URLS": "http://127.0.0.1:8080",
    "REQUEST_INTERNET": true,
    "REQUEST_MALWARE": true,
    "SEND_SQLI": true,
    "SEND_DIR_TRAVERSAL": true,
    "SEND_XSS": true,
    "SEND_DGA": true,
    "REQUEST_WAIT_SECONDS": 0.3,
    "REQUEST_BYTES": 1024,
    "STOP_SECONDS": 60,
    "STOP_PADDING": true,
    "TOTAL_STOP_SECONDS": 75,
    "REQUEST_PROBABILITY": 1.0,
    "EGRESS_PROBABILITY": 0.1,
    "ATTACK_PROBABILITY": 0.01
  }
}
```

## StatsD Statistics

By configuring the `STATSD_HOST` and the optional `STATSD_PORT` (default UDP port is `8125`) parameter the client and server will send regular request, response, attack, and error stats to the StatsD server for aggregation and graphing.

## Logging

Both the client and server log output to stdout, which will show up in docker and kubernetes logs. The logs will summarize the requests and errors and will also print a summary every 30 seconds of total stats and the stats for the last 30 seconds.

`microsimclient`:
```
Request to http://localhost:8080/   Request size: 1036   Response size: 100172
Directory Traversal sent: http://localhost:8080/?username=joe%40example.com&password=..%2F..%2F..%2F..%2F..%2Fpasswd
Internet request to: http://mirror.grid.uchicago.edu/pub/linux/centos/
Request to http://localhost:8080/   Request size: 1036   Response size: 100172
{"Total": {"Requests": 545, "Sent Bytes": 564620, "Received Bytes": 55301055, "Internet Requests": 58, "Attacks": 5, "SQLi": 0, "XSS": 0, "Directory Traversal": 2, "DGA": 3, "Malware": 0, "Error": 0}, "Last 30 Seconds": {"Requests": 42, "Sent Bytes": 43512, "Received Bytes": 4269205, "Internet Requests": 6, "Attacks": 1, "SQLi": 0, "XSS": 0, "Directory Traversal": 0, "DGA": 1, "Malware": 0, "Error": 0}}
Request to http://localhost:8080/   Request size: 1036   Response size: 100172
Request to http://localhost:8080/   Request size: 1036   Response size: 100172
Request to http://localhost:8080/   Request size: 1036   Response size: 100172
DGA query sent: xdcc5481252db5f38d5fc18c9ad3b2f7fd.cn   Response: 23.202.231.169
Request to http://localhost:8080/   Request size: 1036   Response size: 100172
Request to http://localhost:8080/   Request size: 1036   Response size: 100172
Request to http://localhost:8080/   Request size: 1036   Response size: 100172
Request to http://localhost:8080/   Request size: 1036   Response size: 100172
Internet request to: http://mirrors.oit.uci.edu/centos/
Request to http://localhost:8080/   Request size: 1036   Response size: 100172
Request to http://localhost:8080/   Request size: 1036   Response size: 100172
```

`microsimserver`:
```
127.0.0.1 - - [26/Aug/2019 15:30:01] "POST / HTTP/1.1" 200 -
127.0.0.1 - - [26/Aug/2019 15:30:02] "POST / HTTP/1.1" 200 -
127.0.0.1 - - [26/Aug/2019 15:30:02] "GET /?username=joe%40example.com&password=pwd%3Cscript%3Ealert%28%27attacked%27%29%3C%2Fscript%3E HTTP/1.1" 200 -
XSS attack detected
127.0.0.1 - - [26/Aug/2019 15:30:02] "POST / HTTP/1.1" 200 -
127.0.0.1 - - [26/Aug/2019 15:30:02] "POST / HTTP/1.1" 200 -
{"Total": {"Requests": 391, "Sent Bytes": 6473451, "Received Bytes": 404040, "Attacks": 1, "SQLi": 0, "XSS": 1, "Directory Traversal": 0}, "Last 30 Seconds": {"Requests": 97, "Sent Bytes": 1605932, "Received Bytes": 100492, "Attacks": 0, "SQLi": 0, "XSS": 0, "Directory Traversal": 0}}
127.0.0.1 - - [26/Aug/2019 15:30:03] "POST / HTTP/1.1" 200 -
127.0.0.1 - - [26/Aug/2019 15:30:03] "POST / HTTP/1.1" 200 -
```

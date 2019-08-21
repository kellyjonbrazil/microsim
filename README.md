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
| `STATS_PORT`       | `1` - `65535`   | None             | Enable the stats server running on the specified port |
| `RESPOND_BYTES`    | `1` - ?         | `16384`          | How many data bytes are added to the response   |
| `STOP_SECONDS`     | `0` - ?         | `0` (never stop) | Kill the server after x seconds           |

`microsimclient`

| Parameter             | Values          | Default  | Description                                     |
| --------------------- |-----------------| ---------| ------------------------------------------------|
| `STATS_PORT`          | `1` - `65535`   | None     | Enable the stats server running on the specified port |
| `REQUEST_URLS`          | `"http://auth.default.svc.cluster.local:8080,http://db.default.svc.cluster.local:8080"` | None      | One or more comma separated URLs to send requests to. *Note: this is a required parameter* |
| `REQUEST_INTERNET`      | `True`/`False`      | `False`    | Send regular requests to the internet if True             |
| `REQUEST_MALWARE`       | `True`/`False`      | `False`    | Occasionally download an eicar sample from the internet   |
| `SEND_SQLI`             | `True`/`False`      | `False`    | Occasionally send SQLi to the REQUEST_URLS                |
| `SEND_XSS`              | `True`/`False`      | `False`    | Occasionally send XSS to the REQUEST_URLS                 |
| `SEND_DIR_TRAVERSAL`    | `True`/`False`      | `False`    | Occasionally send Directory Traversal to the REQUEST_URLS |
| `SEND_DGA`              | `True`/`False`      | `False`    | Occasionally send DGA DNS requests to the resolver        |
| `REQUEST_WAIT_SECONDS`  | `0.01` - ? (float)  | `3`        | Number of seconds to wait between request loop runs       |
| `REQUEST_BYTES`         | `1` - `7980`        | `1024`     | How many data bytes are added to the request              |
| `ATTACK_PROBABILITY`    | `0.01` (float)      | `0.01`     | Float value representing the percentage probability of one of the attack behaviors triggering per loop |
| `EGRESS_PROBABILITY`    | `0.1` (float)       | `0.1`      | Float value representing the percentage probability of an egress Internet request triggering per loop |
| `STOP_SECONDS`          | `0` - ?             | `0` (never stop) | Kill the client after x seconds                     |

Example docker commands:
```
docker run -d --rm \
    -e LISTEN_PORT=8080 \
    -e STATS_PORT=5001 \
    -e RESPOND_BYTES=1024 \
    -e STOP_SECONDS=300 \
    -p 8080:8080 \
    kellybrazil/microsimserver
```

```
docker run -d --rm \
    -e STATS_PORT=5000 \
    -e REQUEST_URLS="http://service1.default.svc.cluster.local:8080,http://service2.default.svc.cluster.local:5000" \
    -e REQUEST_INTERNET=True \
    -e REQUEST_MALWARE=True \
    -e SEND_SQLI=True \
    -e SEND_DIR_TRAVERSAL=True \
    -e SEND_XSS=True \
    -e SEND_DGA=True \
    -e REQUEST_WAIT_SECONDS=0.5 \
    -e REQUEST_BYTES=128 \
    -e ATTACK_PROBABILITY=0.05 \
    -e EGRESS_PROBABILITY=0.3 \
    -e STOP_SECONDS=300 \
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

## Statistics

If desired, a realtime statistics HTTP server can be enabled by specifying the `STATS_PORT` parameter for both the client and the server.  Example output:

`microsimserver`:
```
$ curl localhost:5000
{
  "time": "Tue Aug 20 18:29:32 2019",
  "runtime": 80,
  "hostname": "laptop.local",
  "ip": "10.3.192.150",
  "stats": {
    "Requests": 131,
    "Sent Bytes": 13122535,
    "Received Bytes": 132608,
    "Attacks": 3,
    "SQLi": 1,
    "XSS": 1,
    "Directory Traversal": 1
  },
  "config": {
    "LISTEN_PORT": 8080,
    "STATS_PORT": 5000,
    "RESPOND_BYTES": 100000,
    "STOP_SECONDS": 0
  }
}
```

`microsimclient`:
```
$ curl localhost:5001
{
  "time": "Tue Aug 20 18:29:44 2019",
  "runtime": 90,
  "hostname": "laptop.local",
  "ip": "10.3.192.150",
  "stats": {
    "Requests": 149,
    "Sent Bytes": 154364,
    "Received Bytes": 14925479,
    "Internet Requests": 0,
    "Attacks": 3,
    "SQLi": 1,
    "XSS": 1,
    "Directory Traversal": 1,
    "DGA": 0,
    "Malware": 0,
    "Error": 0
  },
  "config": {
    "STATS_PORT": 5001,
    "REQUEST_URLS": "http://localhost:8080",
    "REQUEST_INTERNET": false,
    "REQUEST_MALWARE": false,
    "SEND_SQLI": true,
    "SEND_DIR_TRAVERSAL": true,
    "SEND_XSS": true,
    "SEND_DGA": false,
    "REQUEST_WAIT_SECONDS": 0.5,
    "REQUEST_BYTES": 1024,
    "STOP_SECONDS": 0,
    "ATTACK_PROBABILITY": 0.01,
    "EGRESS_PROBABILITY": 0.1
  }
}
```

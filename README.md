# microsim

Also available on Docker Hub:

https://hub.docker.com/r/kellybrazil/microsimserver

https://hub.docker.com/r/kellybrazil/microsimclient

This application generates traffic between simulated microservices using JSON over HTTP. Many parameters can be set on the client and server apps (`microsimserver` and `microsimclient`) to specify the listening port, the amount of traffic generated, whether requests are sent to the internet, whether certain application attacks are sent, and whether malware is downloaded. You can also set the client and server to kill themselves after a number of seconds.

All parameters are set via environment variables. Unset parameters will use the defaults:

`microsimserver`

| Parameter        | Values          | Default  | Description                                     |
| ---------------- |-----------------| ---------| ------------------------------------------------|
| LISTEN_PORT      | 1 - 65535       | 8080     | Port the HTTP server listens on                 |
| RESPOND_BYTES    | 1 - ?           | 16384    | How many data bytes are added to the response   |
| STOP_SECONDS     | 0 - ?           | 0 (never stop) | Kill the server after x seconds           |

`microsimclient`

| Parameter        | Values          | Default  | Description                                     |
| ---------------- |-----------------| ---------| ------------------------------------------------|
| REQUEST_URLS     | "http:/www.example.com,http://www.server.com" | None      | One or more comma separated URLs to send requests to |
| REQUEST_INTERNET | True/False      | False    | Send regular requests to the internet if True   |
| REQUEST_MALWARE  | True/False      | False    | Occasionally download an eicar sample from the internet |
| SEND_SQLI        | True/False      | False    | Occasionally send SQLi to the REQUEST_URLS |
| SEND_XSS         | True/False      | False    | Occasionally send XSS to the REQUEST_URLS |
| SEND_DIR_TRAVERSAL | True/False    | False   | Occasionally send Directory Traversal to the REQUEST_URLS |
| SEND_DGA         | True/False      | False    | Occasionally send DGA DNS requests to the resolver |
| REQUEST_WAIT_SECONDS | 1 - ?     | 3    | Number of seconds to wait between request loop runs |
| REQUEST_BYTES    | 1 - 7980      | 1024       | How many data bytes are added to the request |

Example docker commands:
```
docker run -d --rm \
    -e LISTEN_PORT=5000 \
    -e RESPOND_BYTES=1024 \
    -e STOP_SECONDS=300 \
    -p 5000:5000 \
    kellybrazil/microsimserver
```

```
docker run -d --rm \
    -e REQUEST_URLS="http://service1.default.svc.cluster.local:8080,http://service2.default.svc.cluster.local:5000" \
    -e REQUEST_INTERNET=True \
    -e REQUEST_MALWARE=True \
    -e SEND_SQLI=True \
    -e SEND_DIR_TRAVERSAL=True \
    -e SEND_XSS=True \
    -e SEND_DGA=True \
    -e REQUEST_WAIT_SECONDS=3 \
    -e REQUEST_BYTES=128 \
    -e STOP_SECONDS=300 \
    kellybrazil/microsimclient
```

Example response from the `microsimserver`:
```
$ curl -X POST localhost:8080/this_is_the_path | jq .
{
  "time": "Sat Aug 17 15:34:09 2019",
  "hostname": "laptop.local",
  "ip": "192.168.1.221",
  "remote": "127.0.0.1",
  "hostheader": "localhost:8080",
  "path": "/this_is_the_path",
  "data": "3BbTvDWTD7yWBsWkffiTft5V875EpldKSehv2uXvUSHgl6Sjjl"
}
```
The `data` field is randomly generated text. The number of characters is controled with the `RESPOND_BYTES` parameter.

The `microsimclient` similarly `POST`s a `data` field in the request which is filled with randomly generated text. The number of characters is controled with the `REQUEST_BYTES` parameter.

If a normal `GET` request is sent, then the response will look like this:
```
$ curl localhost:8080/this_is_the_path
f0QRurmXLiuungowUkQMJf3z687BDgsUpV3Lupaln2WUH4egk007En3m11lIurSwcekiI1PqhyRHpzPzYB
Sat Aug 17 15:42:29 2019   hostname: laptop.local   ip: 192.168.1.221   remote: 127.0.0.1   hostheader: localhost:8080   path: /this_is_the_path
```
In this case, the first line is the `data` field sent from the `microsimserver`.

# Kubernetes Deployments

These deployments have been tested on Google Kubernetes Engine (GKE). Simply copy/paste the YAML file into your Google Console with `vi` and run the following to run the deployment:

```
kubectl create -f deployment.yaml
```

To  delete the deployment, run:

```
kubectl delete -f deployment.yaml
```

## Simple Deployment

This deployment simulates a simple web app that communicates via JSON/HTTP to back-end authentication and database services.

![Simple Deployment](https://github.com/kellyjonbrazil/microsim/blob/master/k8s_deployments/images/simple.png)

The following features are enabled in this deployment:

- WWW Service
    - 3 Pods running the Server and Client
    - Service is publicly exposed via LoadBalancer on port 80
    - Each client makes HTTP requests to the `auth` and `db` services on port 8080 every 3 seconds
        - request size is 1KB
    - Each client makes HTTP requests out to the internet on port 80 approximately every 10 requests
    - Each client sends a SQLi attack to the `auth` and `db` services approximately every 100 requests
- Auth Service
    - 3 Pods running the Server
    - Internal service only running on port 8080
    - Response size is 16KB
- DB Service
    - 3 Pods running the Server
    - Internal service only running on port 8080
    - Response size is 16KB

## Monitoring Deployment

This deployment is a bit more complex and uses multiple internal and external services to enable monitoring of the traffic and attacks from a standard Graphite engine using StatsD.

![Monitoring Deployment](https://github.com/kellyjonbrazil/microsim/blob/master/k8s_deployments/images/monitoring.png)

With this deployment you can monitor the realtime stats on the front-end microsimclient pod by browsing to its public IP:

```
$ curl http://34.83.139.87
{
  "time": "Thu Aug 22 18:41:55 2019",
  "runtime": 3365,
  "hostname": "www-76d4dfd6d9-cf4x6",
  "ip": "10.20.1.16",
  "stats": {
    "Requests": 10149,
    "Sent Bytes": 41692092,
    "Received Bytes": 340885433,
    "Internet Requests": 534,
    "Attacks": 359,
    "SQLi": 81,
    "XSS": 113,
    "Directory Traversal": 104,
    "DGA": 9,
    "Malware": 52,
    "Error": 58
  },
  "config": {
    "STATS_PORT": 5000,
    "STATSD_HOST": "statsd-stats.default.svc.cluster.local",
    "STATSD_PORT": 8125,
    "REQUEST_URLS": "http://auth.default.svc.cluster.local:8080,http://db.default.svc.cluster.local:8080",
    "REQUEST_INTERNET": true,
    "REQUEST_MALWARE": true,
    "SEND_SQLI": true,
    "SEND_DIR_TRAVERSAL": true,
    "SEND_XSS": true,
    "SEND_DGA": true,
    "REQUEST_WAIT_SECONDS": 0.5,
    "REQUEST_BYTES": 4096,
    "STOP_SECONDS": 0,
    "ATTACK_PROBABILITY": 0.01,
    "EGRESS_PROBABILITY": 0.1
  }
}
```

Realtime stats on the servers can be seen by curling to their internal IP addresses or by opening a shell to them (e.g. `kubectl exec -it <podname> sh`) and then running `curl localhost:5000` from within the container:

```
user@cloudshell:~ (project-250223)$ kubectl get pods
NAME                      READY   STATUS    RESTARTS   AGE
auth-c695bf984-smhxm      1/1     Running   0          79m
auth-c695bf984-vrgjs      1/1     Running   0          79m
db-6c7c5f9d6d-kt8bz       1/1     Running   0          79m
db-6c7c5f9d6d-whhd5       1/1     Running   0          79m
statsd-5d49485cbf-q5b26   1/1     Running   0          79m
www-76d4dfd6d9-cf4x6      1/1     Running   0          79m
user@cloudshell:~ (project-250223)$ kubectl exec -it db-6c7c5f9d6d-kt8bz sh
/app # curl localhost:5000
{
  "time": "Thu Aug 22 19:05:19 2019",
  "runtime": 4765,
  "hostname": "db-6c7c5f9d6d-kt8bz",
  "ip": "10.20.1.19",
  "stats": {
    "Requests": 3729,
    "Sent Bytes": 122908266,
    "Received Bytes": 14928472,
    "Attacks": 95,
    "SQLi": 26,
    "XSS": 32,
    "Directory Traversal": 37
  },
  "config": {
    "LISTEN_PORT": 8080,
    "STATS_PORT": 5000,
    "STATSD_HOST": "statsd-stats.default.svc.cluster.local",
    "STATSD_PORT": 8125,
    "RESPOND_BYTES": 32768,
    "STOP_SECONDS": 0
  }
}
```

You can also see individual or aggregate stats for the client and servers via the Graphite StatsD pod by browsing to its public IP:

```
user@cloudshell:~ (project-250223)$ kubectl get services
NAME           TYPE           CLUSTER-IP    EXTERNAL-IP      PORT(S)             AGE
auth           ClusterIP      10.0.3.211    <none>           8080/TCP,5000/TCP   108s
db             ClusterIP      10.0.10.223   <none>           8080/TCP,5000/TCP   108s
kubernetes     ClusterIP      10.0.0.1      <none>           443/TCP             3m12s
statsd-stats   ClusterIP      10.0.13.117   <none>           8125/UDP            108s
statsd-www     LoadBalancer   10.0.0.146    35.233.247.165   80:30211/TCP        108s  <-- use this external ip
www            LoadBalancer   10.0.0.192    35.233.200.142   80:31238/TCP        109s
```

![StatsD UI](https://github.com/kellyjonbrazil/microsim/blob/master/k8s_deployments/images/graphite.png)

The following features are enabled in this deployment:

- WWW Service
    - 1 Pod running the Client with the realtime stats http server enabled on port 5000
    - Service is publicly exposed via LoadBalancer on port 80
    - Client makes HTTP requests to the `auth` and `db` services on port 8080 every .5 seconds
        - request size is 4KB
    - Client makes HTTP requests out to the internet on port 80 approximately every 10 requests
    - Client sends one of: SQLi, XSS, Directory Traversal, Malware Download, and DGA attacks to the `auth` and `db` services and Internet with a 1% chance per loop
- Auth Service
    - 2 Pods running the Server with the realtime stats http server enabled on port 5000
    - Internal service only running on port 8080
    - Response size is 32KB
- DB Service
    - 2 Pods running the Server with the realtime stats http server enabled on port 5000
    - Internal service only running on port 8080
    - Response size is 32KB
- StatsD Stats Service
    - 1 Pod running a standard StatsD and Graphite engine
    - Listens on UDP 8125 for statsd updates from the client and servers
    - Service publicy exposed via LoadBalancer on port 80 for the Graphite UI

> Note: this deployment may require more CPU than the minimal Cluster configuration in GKE


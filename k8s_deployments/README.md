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
        - response size is 16KB
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

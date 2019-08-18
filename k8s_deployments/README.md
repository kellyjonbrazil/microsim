# Kubernetes Deployments

These deployments have been tested on Google Kubernetes Engine (GKE). Simply copy/paste the YAML file into your Google Console via `vim` and run the following to run the deployment:

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
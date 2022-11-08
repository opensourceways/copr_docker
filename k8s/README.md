# Deploy Copr build system in Kubernetes

This directory contains the deployment yamls and upgraded configuration for kubernetes
cluster, you can deploy COPR into your cluster within several changes. Note this deployment
is for pre-production usage.

## Before launch
1. [Kustomize](https://github.com/kubernetes-sigs/kustomize) tool, the yamls are organized within kustomize, download it
first and use `kustomize build kubernetes/kustomize` to generate the final yamls.
2. Docker Images, the local images which are generated within command `docker compose build` will be used in default, you
can overwrite the image name and tag in kustomization yamls if you needed.
```yaml
# builder image
- name: copr_builder:latest
  newName: organization/image_name
  newTag: image_tag
````
3. Domain name and certificate, now all the COPR UI including frontend, cgit and backend result are exposed via identical domain
`https://sample.copr.org` you have to replace this all into your own domain (just search 'sample.copr.org' in yaml and configuration),
also you need to update `cert/tls.key` and `cert/tls.crt` within your domain certificate content. If you have cert manager or
other cert automation tools deployed, please remove these two files and upgrade the Ingress yaml.
4. Persistent storage class, please upgrade the storage class name correspondingly before deploy.
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: copr-database-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: ssd
```
5. COPR builder, the only builder instance is deployed in kubernetes within `privileged` mode for demonstration usage, please
refer to the document on how to integrate COPR with AWS or other cloud provider VM Instance.
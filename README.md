# k3s-manifest-generator

Python script to automatically generate Kubernetes manifests (Deployment + Service + Ingress) and deploy them via GitOps using Gitea + ArgoCD on a K3s cluster.

## Architecture

![GitOps Flow](gitops-flow.png)

## Prerequisites

- Python 3.x
- Git
- Local clone of your Gitea repository
- K3s cluster with ArgoCD and Ingress NGINX configured

## Usage

```bash
python k3sgen.py
```

The script will prompt you for:

- Service name
- Target namespace
- Container image
- Port
- Replicas
- Service type (ClusterIP / NodePort)
- Ingress (yes/no)
- Resource limits (yes/no)

## Example Output

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-world
  namespace: homelab
...
```

## GitOps Flow

1. Run `python k3sgen.py`
2. Script generates YAML and saves it to local Gitea repo clone
3. `git add . && git commit && git push`
4. ArgoCD detects the change and syncs to K3s cluster
5. Add `service-name.homelab` → `192.168.1.150` in Pi-hole DNS

## Stack

- **K3s** — Lightweight Kubernetes on 3x Raspberry Pi 4
- **ArgoCD** — GitOps continuous deployment
- **Gitea** — Self-hosted Git repository
- **Ingress NGINX** — Ingress controller
- **Pi-hole** — Local DNS resolution

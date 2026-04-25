![Python](https://img.shields.io/badge/Python-3.13+-blue?logo=python&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-K3s-326CE5?logo=kubernetes&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-GitOps-EF7B4D?logo=argo&logoColor=white)
![Gitea](https://img.shields.io/badge/Gitea-Self--Hosted-609926?logo=gitea&logoColor=white)
![Git](https://img.shields.io/badge/Git-Version%20Control-F05032?logo=git&logoColor=white)

# k3s-manifest-generator

A Python script that generates production-ready Kubernetes manifests (Deployment + Service + Ingress) through an interactive CLI, and saves them directly to a local Git repository for ArgoCD to auto-sync to a K3s cluster.

No more writing YAML by hand. Fill in the prompts, run the script, push to Git — ArgoCD handles the rest.

---

## GitOps Flow

![GitOps Flow](gitops-flow.png)

The script sits at the start of the GitOps pipeline. Once the manifest is generated and pushed, ArgoCD detects the change and applies it to the cluster automatically — no manual `kubectl apply` required.

---

## Prerequisites

- Python 3.13 or newer
- VSCode or any Python-compatible editor
- A K3s cluster with ArgoCD + Gitea configured — see [argocd-k3s-gitea](https://github.com/AdrianStudio/argocd-k3s-gitea) for a step-by-step setup guide
- Local clone of your Gitea repository (`git clone http://your-gitea/repo`)
- A DNS server resolving your custom domain (Pi-hole, CoreDNS, or equivalent)

---

## Setup

Clone this repository:

```bash
git clone https://github.com/AdrianStudio/k3s-manifest-generator
cd k3s-manifest-generator
```

Update `ruta_base` in `k3sgen.py` to point to your local Gitea repo clone:

```python
ruta_base = r"C:\your\path\to\homelab\k3s\argocd"
```

---

## Usage

```bash
python k3sgen.py
```

The script will prompt you for the service configuration:

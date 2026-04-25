# GitOps flow: local repo → Gitea → ArgoCD auto-sync → K3s cluster
# This script generates Kubernetes manifests (Deployment + Service + Ingress)
# and saves them to the local Gitea repo clone for ArgoCD to pick up.

import os

servicio = {
    "nombre": "",
    "namespace": "",
    "imagen": "",
    "puerto": 0,
    "tipo_servicio": "",
    "replicas": 1,
    "env": [],
    "ingress": False,
    "resources": False
}

#This is the base path for the local clone of the Gitea repo, update if the repo location changes
ruta_base = r"C:\Users\adrian\Desktop\Python Scripts\KUBERNETES\homelab\k3s\argocd"

#Service Config
servicio['nombre'] = input("Service name: ")
servicio['namespace'] = input("Target namespace: ")
servicio['imagen'] = input("Container image (e.g., nginxdemos/hello:latest): ")
servicio['puerto'] = int(input("Container port to expose: "))
servicio['replicas'] = int(input("Number of replicas [default: 1]: ") or "1")

#Service Type
servicio['tipo_servicio'] = input("Service type (ClusterIP / NodePort / LoadBalancer): ").strip()
#This is to prevent crashes, it will not take any number outside the range or invalid numbers.
if servicio['tipo_servicio'].lower() == 'nodeport':
    while True:
        try:
            np = int(input("NodePort to expose (valid range: 30000-32767): "))# NodePort valid range per Kubernetes spec: 30000-32767
            if 30000 <= np <= 32767:
                servicio['node_port'] = np
                break
            else:
                print("Error: NodePort must be between 30000 and 32767. Try again.")
        except ValueError:
            print("Error: Please enter a valid number. Try again.")
    
#Features
servicio['ingress'] = input("Enable Ingress? (yes/no): ").strip().lower() == "yes"
servicio['resources'] = input("Configure CPU/memory resource limits? (yes/no): ").strip().lower() == "yes"

def valservicio(s):
    if s["nombre"] == "":
        print("Error: The name can't be blank")
        return False
    if " " in s["nombre"]:
        print("Error: The name can't contain spaces or blank characters")
        return False
    if 1 > s["puerto"]:
        print("The port number can't be lower than 1")
        return False
    if 65535 < s["puerto"]:
        print("The port number can't be higher than 65535")
        return False
    if s["imagen"] == "":
        print("Error: The image can't be blank")
        return False
    if s["tipo_servicio"].lower() == "nodeport":
        if "node_port" not in s:
            print("Error: NodePort requires node_port")
            return False
    print("Validation OK")
    return True


valid = valservicio(servicio)
if valid:
    print("Validation perfect, proceeding")

    env_yaml = ""
    if servicio["env"]:
        env_yaml = "        env:\n"
        for var in servicio["env"]:
            env_yaml += f'        - name: {var["name"]}\n'
            env_yaml += f'          value: "{var["value"]}"\n'
            
    resources_yaml = "" #RPi4 fixed resource limits, only adjust if your hardware can handle it.
    if servicio["resources"]:
        resources_yaml = (
            "        resources:\n"
            "          requests:\n"
            "            memory: \"64Mi\"\n"
            "            cpu: \"100m\"\n"
            "          limits:\n"
            "            memory: \"128Mi\"\n"
            "            cpu: \"200m\""
        )
        
    ingress_yaml = ""  # Ingress uses NGINX ingress controller with Pi-hole DNS for .homelab domain resolution
    if servicio["ingress"]:
        ingress_yaml = f"""\
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {servicio['nombre']}-ingress
  namespace: {servicio['namespace']}
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: {servicio['nombre']}.homelab
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {servicio['nombre']}
            port:
              number: {servicio['puerto']}"""

    service_nodeport_yaml = ""
    if servicio["tipo_servicio"] == "NodePort":
        service_nodeport_yaml = f"    nodePort: {servicio['node_port']}\n"

    separador_ingress = "\n---\n" if ingress_yaml else ""

    yaml_final = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {servicio['nombre']}
  namespace: {servicio['namespace']}
spec:
  replicas: {servicio['replicas']}
  selector:
    matchLabels:
      app: {servicio['nombre']}
  template:
    metadata:
      labels:
        app: {servicio['nombre']}
    spec:
      containers:
      - name: {servicio['nombre']}
        image: {servicio['imagen']}
        ports:
        - containerPort: {servicio['puerto']}
{env_yaml}{resources_yaml}
---
apiVersion: v1
kind: Service
metadata:
  name: {servicio['nombre']}
  namespace: {servicio['namespace']}
spec:
  type: {servicio['tipo_servicio']}
  selector:
    app: {servicio['nombre']}
  ports:
  - port: {servicio['puerto']}
    targetPort: {servicio['puerto']}
{service_nodeport_yaml}{separador_ingress}{ingress_yaml}"""

    print(yaml_final)
    
    #This is confirm that the base route exists, if not it will create it.
    os.makedirs(f"{ruta_base}/{servicio['nombre']}", exist_ok=True)
    
    #This generates the file into the base route and saves it as a yaml file.
    with open(f"{ruta_base}/{servicio['nombre']}/{servicio['nombre']}.yaml", "w") as f:
        f.write(yaml_final)
    print(f"File generated: {ruta_base}/{servicio['nombre']}/{servicio['nombre']}.yaml")
    print(f"Don't forget to add {servicio['nombre']}.homelab → 192.168.1.150 in Pi-hole")
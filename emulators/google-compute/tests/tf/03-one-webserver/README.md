# One Webserver — GCP instance + firewall rule

Deploys a VM that starts a simple HTTP server on port 8080 and a
firewall rule to allow traffic to it.

## Usage

```bash
export GOOGLE_BACKEND_OVERRIDE=http://localhost:9100
terraform init && terraform apply -auto-approve
```

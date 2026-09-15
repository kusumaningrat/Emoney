# Nomad job template for deployments rendered by the platform.
#
# This file is rendered into nomad/nomad.hcl in the target repository and
# executed by the reusable GitHub Actions workflow (nomad job run).
#
# Placeholders (all required, replaced with string substitution):
#   ningrat           deployment / job name
#   default          Nomad namespace to deploy into
#   global             Nomad region (optional, e.g. global)
#           Comma-separated datacenters, e.g. dc1, dc2
#   image-reg.ops.glynac.ai              Container image to run, e.g. ghcr.io/acme/api:v1
#   deploy-89743eca-35db-405f-9575-a7e5b43496f9       Vault ACL policy the job receives (platform-managed)
#   secret/data/deployment/ningrat  Full KV path holding the deployment secrets,
#                          e.g. secret/data/deployments/<id>
#
# When Nomad is configured with Vault enabled (vault { enabled = true } on the
# server and agents), the job authenticates to Vault with the policy above and
# secrets are injected at runtime via template blocks. Secrets never appear in
# the repository.
job "ningrat" {
  region      = "global"
  datacenters = [""]
  type        = "service"
  namespace   = "default"

  group "ningrat" {
    network {
      port "http" {}
    }

    task "app" {
      driver = "docker"

      config {
        image = "image-reg.ops.glynac.ai"
      }

      vault {
        policies = ["deploy-89743eca-35db-405f-9575-a7e5b43496f9"]
      }

      template {
        data = <<EOF
{{ with secret "secret/data/deployment/ningrat" }}
DB_DSN="{{ .Data.data.db_dsn }}"
{{ end }}
EOF
        destination = "local/app.env"
        env         = true
      }

      service {
        name = "ningrat"
        port = "http"
      }
    }
  }
}
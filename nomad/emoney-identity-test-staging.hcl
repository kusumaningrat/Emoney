job "emoney-identity-test" {
  region      = "global"
  datacenters = ["peternakclouds-dc"]
  type        = "service"
  namespace   = "default"

  group "emoney-identity-test" {
    count = 1

    network {
      port "http" {}
    }

    task "emoney-identity-test" {
      driver = "docker"

      config {
        image = "image-reg.ops.glynac.ai/emoney-identity-test:${IMAGE_TAG}"
      }

      vault {
        policies = ["deploy-30e8fe98-773f-454e-b018-4b88cd20001d"]
      }

      template {
        data = <<EOF
{{ with secret "secret/data/deployments/etest" }}
DB_DSN="{{ .Data.data.db_dsn }}"
{{ end }}
EOF
        destination = "local/app.env"
        env         = true
      }

      resources {
        cpu    = 500
        memory = 512
      }

      service {
        name = "emoney-identity-test"
        port = "http"

        check {
          type     = "http"
          path     = "/"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
}

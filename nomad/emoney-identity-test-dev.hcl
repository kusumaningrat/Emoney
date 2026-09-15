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
        policies = ["backend"]
      }

      template {
        data = <<EOF
{{ with secret "secret/data/Backend-Service/auth-dev" }}
{{ range $key, $value := .Data.data }}{{ $key }}={{ $value }}
{{ end }}{{ end }}
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
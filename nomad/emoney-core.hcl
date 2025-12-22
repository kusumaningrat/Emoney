job "Emoney-core-App" {
  datacenters = ["glynac-dc"]
  type = "service"
  namespace = "extraction-service"

  update {
    max_parallel     = 1
    health_check     = "task_states"
    min_healthy_time = "30s"
  }

  group "emoney-core" {
    count = 1

    network {
      port "http" {
        static       = 5730
        to           = 5730
        host_network = "private"
      }
    }

    service {
      name = "emoney-core"
      tags = ["apps", "logs.promtail"]
      port = "http"
      check {
        name     = "api-health"
        type     = "tcp"
        port     = "http"
        interval = "15s"
        timeout  = "5s"
      }
    }

    constraint {
      attribute = "${attr.unique.hostname}"
      value     = "Worker-03"
    }

    task "emoney-core" {
      driver = "docker"

      config {
        image = "harbor-registry.service.consul:8085/emoney-advisor/emoney-core:IMAGE_TAG_PLACEHOLDER"
        ports = ["http"]
        dns_servers = ["172.17.0.1", "172.18.0.1", "8.8.8.8", "8.8.4.4", "1.1.1.1"]
        auth {
          username = "admin"
          password = "GlynacP455"
          server_address = "harbor-registry.service.consul:8085"
        }
      }

      vault {
        role = "emoney-advisor"
      }

      template {
        destination = "secrets/env"
        env         = true
        data = <<EOF

APP_NAME="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.APP_NAME }}{{ end }}"
API_VERSION="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.API_VERSION }}{{ end }}"
DEBUG="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.DEBUG }}{{ end }}"
ENVIRONMENT="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.ENVIRONMENT }}{{ end }}"
API_KEY="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.API_KEY }}{{ end }}"
SECRET_KEY="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.SECRET_KEY }}{{ end }}"
ACCESS_TOKEN_EXPIRE_MINUTES="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.ACCESS_TOKEN_EXPIRE_MINUTES }}{{ end }}"
DATABASE_URL="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.DATABASE_URL }}{{ end }}"
ALLOWED_ORIGINS="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.ALLOWED_ORIGINS }}{{ end }}"
DEFAULT_SERVICE_TIMEOUT="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.DEFAULT_SERVICE_TIMEOUT }}{{ end }}"
SCAN_RESULT_RETENTION_DAYS="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.SCAN_RESULT_RETENTION_DAYS }}{{ end }}"
MAX_RETRY_ATTEMPTS="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.MAX_RETRY_ATTEMPTS }}{{ end }}"
RATE_LIMIT_RETRY_AFTER="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.RATE_LIMIT_RETRY_AFTER }}{{ end }}"
EMONEY_ACCOUNT_URL_STAGE="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_ACCOUNT_URL_STAGE }}{{ end }}"
EMONEY_CLIENT_URL_STAGE="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_CLIENT_URL_STAGE }}{{ end }}"
EMONEY_FINANCIAL_PLANNING_URL_STAGE="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_FINANCIAL_PLANNING_URL_STAGE }}{{ end }}"
EMONEY_IDENTITY_URL_STAGE="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_IDENTITY_URL_STAGE }}{{ end }}"
EMONEY_DEFAULT_API_KEY="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_DEFAULT_API_KEY }}{{ end }}"
EMONEY_DEFAULT_CLIENT_ID="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_DEFAULT_CLIENT_ID }}{{ end }}"
EMONEY_DEFAULT_FIRM_ID="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_DEFAULT_FIRM_ID }}{{ end }}"
EMONEY_DEFAULT_SCOPE="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_DEFAULT_SCOPE }}{{ end }}"
EMONEY_JWT_EXPIRY_HOURS="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_JWT_EXPIRY_HOURS }}{{ end }}"
EMONEY_DEFAULT_BATCH_SIZE="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_DEFAULT_BATCH_SIZE }}{{ end }}"
EMONEY_MAX_BATCH_SIZE="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_MAX_BATCH_SIZE }}{{ end }}"
EMONEY_PAGINATION_LIMIT="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.EMONEY_PAGINATION_LIMIT }}{{ end }}"
LOG_LEVEL="{{ with secret "secrets/emoney/emoney-core" }}{{ .Data.data.LOG_LEVEL }}{{ end }}"
EOF
      }

      resources {
        cpu    = 200
        memory = 200
      }
    }
  }
}
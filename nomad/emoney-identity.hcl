job "Emoney-identity-App" {
  datacenters = ["glynac-dc"]
  type        = "service"
  namespace   = "extraction-service"

  update {
    max_parallel     = 1
    health_check     = "task_states"
    min_healthy_time = "30s"
  }

  group "emoney-identity" {
    count = 1

    network {
      port "http" {
        static       = 5709
        to           = 5709
        host_network = "private"
      }
    }

    service {
      name = "emoney-identity"
      tags = ["apps", "logs.promtail"]
      port = "http"
      check {
        name     = "api-health"
        type     = "http"
        path     = "/api/health"
        interval = "30s"
        timeout  = "10s"
      }
    }

    constraint {
      attribute = "${attr.unique.hostname}"
      value     = "Worker-03"
    }

    task "emoney-identity" {
      driver = "docker"

      config {
        image       = "harbor-registry.service.consul:8085/emoney-advisor/emoney-identity:IMAGE_TAG_PLACEHOLDER"
        ports       = ["http"]
        dns_servers = ["172.17.0.1", "172.18.0.1", "8.8.8.8", "8.8.4.4", "1.1.1.1"]
        auth {
          username       = "admin"
          password       = "GlynacP455"
          server_address = "harbor-registry.service.consul:8085"
        }
      }

      vault {
        role = "emoney-advisor"
      }

      template {
        destination = "secrets/env"
        env         = true
        data        = <<EOF

APP_VERSION="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.APP_VERSION }}{{ end }}"
APP_TITLE="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.APP_TITLE }}{{ end }}"
APP_DESCRIPTION="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.APP_DESCRIPTION }}{{ end }}"
FLASK_ENV="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.FLASK_ENV }}{{ end }}"
FLASK_DEBUG="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.FLASK_DEBUG }}{{ end }}"
SECRET_KEY="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.SECRET_KEY }}{{ end }}"
PORT="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.PORT }}{{ end }}"
HOST="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.HOST }}{{ end }}"
DB_HOST="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DB_HOST }}{{ end }}"
DB_PORT="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DB_PORT }}{{ end }}"
DB_NAME="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DB_NAME }}{{ end }}"
DB_USER="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DB_USER }}{{ end }}"
DB_PASSWORD="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DB_PASSWORD }}{{ end }}"
DB_SCHEMA="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DB_SCHEMA }}{{ end }}"
DESTINATION__POSTGRES__CREDENTIALS__DATABASE="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DESTINATION__POSTGRES__CREDENTIALS__DATABASE }}{{ end }}"
DESTINATION__POSTGRES__CREDENTIALS__USERNAME="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DESTINATION__POSTGRES__CREDENTIALS__USERNAME }}{{ end }}"
DESTINATION__POSTGRES__CREDENTIALS__PASSWORD="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DESTINATION__POSTGRES__CREDENTIALS__PASSWORD }}{{ end }}"
DESTINATION__POSTGRES__CREDENTIALS__HOST="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DESTINATION__POSTGRES__CREDENTIALS__HOST }}{{ end }}"
DESTINATION__POSTGRES__CREDENTIALS__PORT="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DESTINATION__POSTGRES__CREDENTIALS__PORT }}{{ end }}"
EMONEY_API_BASE_URL="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.EMONEY_API_BASE_URL }}{{ end }}"
DLT_PIPELINE_NAME="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DLT_PIPELINE_NAME }}{{ end }}"
DLT_WORKING_DIR="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.DLT_WORKING_DIR }}{{ end }}"
EMONEY_API_TIMEOUT="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.EMONEY_API_TIMEOUT }}{{ end }}"
EMONEY_API_RATE_LIMIT="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.EMONEY_API_RATE_LIMIT }}{{ end }}"
MAX_CONCURRENT_SCANS="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.MAX_CONCURRENT_SCANS }}{{ end }}"
SCAN_TIMEOUT_HOURS="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.SCAN_TIMEOUT_HOURS }}{{ end }}"
CLEANUP_DAYS="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.CLEANUP_DAYS }}{{ end }}"
LOG_LEVEL="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.LOG_LEVEL }}{{ end }}"
LOKI_ENABLED="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.LOKI_ENABLED }}{{ end }}"
LOG_FORMAT="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.LOG_FORMAT }}{{ end }}"
KAFKA_BOOTSTRAP_SERVERS="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.KAFKA_BOOTSTRAP_SERVERS }}{{ end }}"
KAFKA_ENABLED="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.KAFKA_ENABLED }}{{ end }}"
KAFKA_TOPIC_1="{{ with secret "secrets/emoney/emoney-identity" }}{{ .Data.data.KAFKA_TOPIC_1 }}{{ end }}"
EOF
      }

      resources {
        cpu    = 200
        memory = 200
      }
    }
  }
}
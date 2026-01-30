job "Emoney_Advisor_Mock_Server-App" {
  datacenters = ["glynac-dc"] #disesuaikan
  type        = "service"
  namespace   = "extraction-service"

  update {
    max_parallel     = 1
    health_check     = "task_states"
    min_healthy_time = "30s"
  }

  group "emoney-advisor-mock-server" {
    count = 1

    network {
      port "http" {
        static       = 6820
        to           = 6820
        host_network = "private"
      }
    }

    service {
      name = "emoney-advisor-mock-server"
      tags = ["apps", "logs.promtail"]
      port = "http"
      check {
        name     = "api-health"
        type     = "http"
        path     = "/health"
        interval = "30s"
        timeout  = "10s"
      }
    }

    constraint {
      attribute = "${attr.unique.hostname}"
      value     = "Worker-02"
    }

    task "emoney-advisor-mock-server" {
      driver = "docker"

      config {

        image       = "harbor-registry.service.consul:8085/emoney-advisor/emoney-advisor-mock-server:IMAGE_TAG_PLACEHOLDER"
        ports       = ["http"]
        dns_servers = ["172.17.0.1", "172.18.0.1", "8.8.8.8", "8.8.4.4", "1.1.1.1"]
        auth {
          username       = "{{ with secret \"secrets/harbor/login\" }}{{ .Data.data.username }}{{ end }}"
          password       = "{{ with secret \"secrets/harbor/login\" }}{{ .Data.data.password }}{{ end }}"
          server_address = "{{ with secret \"secrets/harbor/login\" }}{{ .Data.data.server_address }}{{ end }}"
        }
      }

      vault {
        role = "emoney-advisor"
      }


      template {
        destination = "secrets/env"
        env         = true
        data        = <<EOF
    DATABASE_URL="{{ with secret "secrets/data/emoney/emoney-advisor-mock-server" }}{{ .Data.data.DATABASE_URL }}{{ end }}"
    ENVIRONMENT="{{ with secret "secrets/data/emoney/emoney-advisor-mock-server" }}{{ .Data.data.ENVIRONMENT }}{{ end }}"
    EOF
      }

      resources {
        cpu    = 200
        memory = 200
      }

    }

  }
}

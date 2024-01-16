terraform {
  required_providers {
    pulsar = {
      source  = "streamnative/pulsar"
      version = "0.2.0"
    }
  }
}

provider "pulsar" {
  web_service_url = var.pulsar_service_url
}

terraform {
  required_providers {
    pulsar = {
      source  = "streamnative/pulsar"
      version = "0.2.0"
    }
  }
}

provider "pulsar" {
  web_service_url = "http://127.0.0.1:8080"
}

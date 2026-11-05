terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.2"
    }
  }
}

provider "docker" {}

resource "docker_network" "app_network" {
  name = "lab3-network"
}

resource "docker_image" "demo_app" {
  name         = "demo-app:latest"
  keep_locally = true
}

resource "docker_container" "app_replicas" {
  count = var.replicas
  name  = "demo-app-${count.index + 1}"
  image = docker_image.demo_app.image_id

  networks_advanced {
    name = docker_network.app_network.name
  }

  ports {
    internal = 5000
    external = 5000 + count.index
  }

  env = [
    "ENVIRONMENT=production",
    "FEATURE_GREETING_V2=true"
  ]
}

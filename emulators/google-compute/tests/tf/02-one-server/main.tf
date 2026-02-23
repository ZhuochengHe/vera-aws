# Configure the Google provider
provider "google" {
  project              = "vera-project"
  region               = "us-central1"
  access_token         = "vera-local-token"
  user_project_override = false
}

# Create a Compute Engine instance with a tag
resource "google_compute_instance" "example" {
  name         = "vera-vm"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
  }

  tags = ["terraform-example"]
}

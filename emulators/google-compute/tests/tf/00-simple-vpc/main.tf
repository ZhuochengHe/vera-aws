provider "google" {
  project              = "vera-project"
  region               = "us-central1"
  access_token         = "vera-local-token"
  user_project_override = false
}

resource "google_compute_network" "test" {
  name                    = "vera-net"
  auto_create_subnetworks = false
}

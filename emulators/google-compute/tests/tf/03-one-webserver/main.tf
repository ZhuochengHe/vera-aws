# Configure the Google provider
provider "google" {
  project              = "vera-project"
  region               = "us-central1"
  access_token         = "vera-local-token"
  user_project_override = false
}

# Firewall rule to allow HTTP traffic on port 8080
resource "google_compute_firewall" "allow_http" {
  name    = "allow-http-8080"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web"]
}

# Create a Compute Engine instance running a simple web server
resource "google_compute_instance" "example" {
  name         = "vera-webserver"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    echo "Hello, World" > index.html
    nohup busybox httpd -f -p 8080 &
  EOF

  tags = ["web", "terraform-example"]
}

# Output: external IP
output "public_ip" {
  value = google_compute_instance.example.network_interface[0].access_config[0].nat_ip
}

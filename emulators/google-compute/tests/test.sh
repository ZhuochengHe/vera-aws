# Vera GCP — gcloud compute test suite
# Source: https://cloud.google.com/sdk/gcloud/reference/compute
# Run via: uv run eval_emulator.py test.sh --endpoint http://localhost:9100

# Zones & regions
gcpcli zones list
gcpcli regions list
gcpcli zones describe us-central1-a

# Machine types
gcpcli machine-types list --zones=us-central1-a
gcpcli machine-types describe n1-standard-1 --zone=us-central1-a

# Networks
gcpcli networks list
gcpcli networks create vera-net --subnet-mode=custom
gcpcli networks describe vera-net
gcpcli networks subnets create vera-subnet --network=vera-net --range=10.0.0.0/24 --region=us-central1
gcpcli networks subnets describe vera-subnet --region=us-central1

# Firewall rules
gcpcli firewall-rules list
gcpcli firewall-rules create allow-ssh --network=default --allow=tcp:22 --source-ranges=0.0.0.0/0
gcpcli firewall-rules create allow-http --network=default --allow=tcp:80

# Instances
gcpcli instances list
gcpcli instances create vera-vm --zone=us-central1-a --machine-type=n1-standard-1 --image-family=debian-11 --image-project=debian-cloud
gcpcli instances describe vera-vm --zone=us-central1-a
gcpcli instances stop vera-vm --zone=us-central1-a
gcpcli instances start vera-vm --zone=us-central1-a

# Disks
gcpcli disks list
gcpcli disks create vera-disk --size=50GB --zone=us-central1-a --type=pd-standard
gcpcli disks describe vera-disk --zone=us-central1-a
gcpcli disks snapshot vera-disk --snapshot-names=vera-snap --zone=us-central1-a
gcpcli snapshots describe vera-snap

# Addresses
gcpcli addresses list
gcpcli addresses create vera-ip --region=us-central1
gcpcli addresses describe vera-ip --region=us-central1

# Health checks & load balancing
gcpcli health-checks create http vera-hc --port=80
gcpcli backend-services create vera-backend --protocol=HTTP --health-checks=vera-hc --global
gcpcli url-maps create vera-url-map --default-service=vera-backend
gcpcli target-http-proxies create vera-proxy --url-map=vera-url-map
gcpcli forwarding-rules create vera-rule --global --target-http-proxy=vera-proxy --ports=80
gcpcli forwarding-rules describe vera-rule --global

# Instance templates
gcpcli instance-templates list
gcpcli instance-templates create vera-template --machine-type=n1-standard-1 --image-family=debian-11 --image-project=debian-cloud
gcpcli instance-templates describe vera-template

# Operations
gcpcli operations list --zones=us-central1-a
gcpcli operations list --global

# Cleanup
gcpcli forwarding-rules delete vera-rule --global
gcpcli target-http-proxies delete vera-proxy
gcpcli url-maps delete vera-url-map
gcpcli backend-services delete vera-backend --global
gcpcli health-checks delete vera-hc
gcpcli snapshots delete vera-snap
gcpcli instances delete vera-vm --zone=us-central1-a
gcpcli disks delete vera-disk --zone=us-central1-a
gcpcli addresses delete vera-ip --region=us-central1
gcpcli instance-templates delete vera-template
gcpcli firewall-rules delete allow-ssh
gcpcli firewall-rules delete allow-http
gcpcli networks subnets delete vera-subnet --region=us-central1
gcpcli networks delete vera-net

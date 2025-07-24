runtime: custom
env: flex

resources:
  cpu: 1
  memory_gb: 0.5
  disk_size_gb: 10

service_account: "{{SERVICE_ACCOUNT_EMAIL}}"

automatic_scaling:
  min_num_instances: 1
  max_num_instances: 10

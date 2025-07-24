runtime: custom
env: flex
beta_settings:
  cloud_build:
    # Construct the full Artifact Registry image path using repo secrets and IMAGE_TAG placeholder
    docker_image: "{{REGION}}-docker.pkg.dev/{{PROJECT_ID}}/{{REPOSITORY}}/{{IMAGE_NAME}}:latest"
service_account: "{{SERVICE_ACCOUNT_EMAIL}}"

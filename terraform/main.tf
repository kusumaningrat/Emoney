provider "nomad" {
  address   = var.nomad_addr
  secret_id = var.nomad_token
}

resource "nomad_job" "emoney_account" {
  jobspec = templatefile("${path.module}/jobs/emoney-account.hcl", {
    IMAGE_TAG = var.image_tag
  })
}
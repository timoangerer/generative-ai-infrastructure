# resource "pulsar_tenant" "tenant" {
#   tenant           = "rocky"
#   allowed_clusters = ["pulsar-mini"]
# }

# resource "pulsar_namespace" "gen" {
#   tenant    = pulsar_tenant.tenant.tenant
#   namespace = "gen"
# }

# variable "topics" {
#   description = "List of topic names"
#   type        = list(string)
#   default     = ["requested_txt2img_generation", "dlq_requested_txt2img_generation", "completed_txt2img_generation"]
# }

# resource "pulsar_topic" "topics" {
#   for_each   = toset(var.topics)
#   topic_name = each.value
#   tenant     = pulsar_tenant.tenant.tenant
#   namespace  = pulsar_namespace.gen.namespace
#   partitions = 0
#   topic_type = "persistent"
# }

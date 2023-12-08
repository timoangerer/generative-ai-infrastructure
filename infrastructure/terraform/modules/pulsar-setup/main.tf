resource "pulsar_tenant" "tenant" {
  tenant           = var.pulsar_tenant
  allowed_clusters = [var.pulsar_cluster]
}

resource "pulsar_namespace" "gen" {
  depends_on = [pulsar_tenant.tenant]
  tenant     = var.pulsar_tenant
  namespace  = var.pulsar_namespace
}

resource "pulsar_topic" "topics" {
  depends_on = [pulsar_namespace.gen]
  for_each   = toset(var.pulsar_topics)
  topic_name = each.value
  tenant     = var.pulsar_tenant
  namespace  = var.pulsar_namespace
  partitions = 1
  topic_type = "persistent"
}

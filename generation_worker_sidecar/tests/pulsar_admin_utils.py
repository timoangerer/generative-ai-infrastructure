import requests


def create_tenant(service_url: str, cluster: str, tenant: str):
    url = f"{service_url}/admin/v2/tenants/{tenant}"
    response = requests.put(
        url, json={'allowedClusters': [cluster]}, timeout=5)


def delete_tenant(service_url: str, tenant: str):
    url = f"{service_url}/admin/v2/tenants/{tenant}"
    response = requests.delete(url, json={'force': True}, timeout=5)


def create_namespace(service_url: str, tenant: str, namespace: str):
    url = f"{service_url}/admin/v2/namespaces/{tenant}/{namespace}"
    response = requests.put(url, timeout=5)


def delete_namespace(service_url: str, tenant: str, namespace: str):
    url = f"{service_url}/admin/v2/namespaces/{tenant}/{namespace}"
    response = requests.delete(url, timeout=5)


def create_topic(service_url: str, tenant: str, namespace: str, topic_name: str):
    url = f"{service_url}/admin/v2/persistent/{tenant}/{namespace}/{topic_name}"
    response = requests.put(url, timeout=5)


def delete_topic(service_url: str, tenant: str, namespace: str, topic_name: str):
    url = f"{service_url}/admin/v2/persistent/{tenant}/{namespace}/{topic_name}"
    response = requests.delete(url, timeout=5)


def create_tenant_namespace_topic(service_url: str, cluster: str, tenant: str, namespace: str, topic_name: str):
    tenant_res = create_tenant(service_url, cluster, tenant)
    create_namespace(service_url, tenant, namespace)
    create_topic(service_url, tenant, namespace, topic_name)


def delete_tenant_namespace_topic(service_url: str, tenant: str, namespace: str, topic_name: str):
    delete_topic(service_url, tenant, namespace, topic_name)
    delete_namespace(service_url, tenant, namespace)
    delete_tenant(service_url, tenant)

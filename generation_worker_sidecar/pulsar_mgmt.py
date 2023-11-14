

import sys
from src.config import get_config
from tests.pulsar_admin_utils import create_tenant_namespace_topics, delete_tenant_namespace_topics
from src.topics import Topics

config = get_config()


def create():
    create_tenant_namespace_topics(config.pulsar_service_url, config.pulsar_cluster,
                                   config.pulsar_tenant, config.pulsar_namespace, [topic.value for topic in Topics])
    print("Created tenant, namespace and topics")


def delete():
    delete_tenant_namespace_topics(config.pulsar_service_url, config.pulsar_tenant, config.pulsar_namespace, [
                                   topic.value for topic in Topics])
    print("Deleted tenant, namespace and topics")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "create":
            create()
        elif sys.argv[1] == "delete":
            delete()
        else:
            print("Invalid parameter")
    else:
        print("Missing parameter")

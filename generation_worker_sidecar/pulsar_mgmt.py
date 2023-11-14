

import argparse
from src.config import get_config
from tests.pulsar_admin_utils import create_tenant_namespace_topics, delete_tenant_namespace_topics
from src.topics import Topics

parser = argparse.ArgumentParser(
    description='Manage Pulsar tenants, namespaces and topics')
parser.add_argument('-e', '--env-file', type=str,
                    default='./dev.env', help='Path to .env file')
parser.add_argument('-o', '--operation', type=str,
                    choices=['create', 'delete'], required=True, help='Operation to perform')

args = parser.parse_args()

config = get_config(env_file=args.env_file)

if args.operation == 'create':
    create_tenant_namespace_topics(config.pulsar_service_url, config.pulsar_cluster,
                                   config.pulsar_tenant, config.pulsar_namespace, [topic.value for topic in Topics])
    print("Created tenant, namespace and topics")
elif args.operation == 'delete':
    delete_tenant_namespace_topics(config.pulsar_service_url, config.pulsar_tenant, config.pulsar_namespace, [
                                   topic.value for topic in Topics])
    print("Deleted tenant, namespace and topics")

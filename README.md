# generative-ai-infrastructure

### Start local services

```bash
# Local pulsar cluster with Zookeeper
PULSAR_STANDALONE_USE_ZOOKEEPER=1 ./local-services/apache-pulsar-3.1.0/bin/pulsar standalone

# Local Trino cluster
./local-services/apache-pulsar-3.1.0/bin/pulsar sql-worker run

# AUTO1111 Stable Diffusion API
cd local-services/stable-diffusion-webui && ./webui.sh --api
```
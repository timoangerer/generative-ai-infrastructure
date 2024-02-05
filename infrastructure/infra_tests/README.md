# Infrastructure Test

Run automated tests and load tests to verify the infrastructure is working correctly.

## Depdendecies

Install the depdencies and activate the python venv:
```bash
pdm install
```

## Automated tests

Make sure the infrastructure is deployed and running.

Forward the API service to your local machine:
```bash
kubectl port-forward $(kubectl get pods -l app=genai-api -o jsonpath='{.items[0].metadata.name}') 8000:8000
```

Run python pytest tests:
```bash
pytest
```

## Load tests

Make sure the infrastructure is deployed and running.

Forward the API service to your local machine:
```bash
kubectl port-forward $(kubectl get pods -l app=genai-api -o jsonpath='{.items[0].metadata.name}') 8000:8000
```

Run locust load tests:
```bash
locust -f locust/load_test.py
```

Visit the locust dashboard in your browser as instructed by the command output.
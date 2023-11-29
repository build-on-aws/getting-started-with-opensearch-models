import os
import boto3
import requests
import string
import random
import time

opensearch_url = "http://localhost:9200"

# Check if the AWS credentials are set

profile = os.getenv("AWS_PROFILE")
if profile is None:
    profile = "default"

session = boto3.Session(profile_name=profile)
credentials = session.get_credentials()
if credentials is None:
    print("AWS credentials are not set. Please set them up and try again.")
    exit(1)

aws_access_key = credentials.access_key
aws_secret_key = credentials.secret_key

# Check if OpenSearch is up and running

up_and_running = False
opensearch_conn_timeout = 60

try:
    response = requests.get(opensearch_url + "/_cluster/health")
    if response.status_code == 200 and response.json()["status"] == "green":
        up_and_running = True
except:
    if not up_and_running:
        count = 0
        while not up_and_running and count < opensearch_conn_timeout:
            print("⏰ Waiting for OpenSearch to start...")
            time.sleep(1)
            count += 1
            try:
                response = requests.get(opensearch_url + "/_cluster/health")
                if response.status_code == 200 and response.json()["status"] == "green":
                    up_and_running = True
            except:
                continue

if not up_and_running:
    print("OpenSearch is not running. Please start it up and try again.")
    exit(1)

# Wait until the ML plugin is initialized

ml_plugin_initialized = False
ml_plugin_timeout = 30

response = requests.head(opensearch_url + "/.plugins-ml-config")
if response.status_code == 200:
    ml_plugin_initialized = True
else:
    count = 0
    while not ml_plugin_initialized and count < ml_plugin_timeout:
        print("⏰ Waiting for the ML plugin to initialize...")
        time.sleep(1)
        count += 1
        try:
            response = requests.head(opensearch_url + "/.plugins-ml-config")
            if response.status_code == 200:
                ml_plugin_initialized = True
        except:
            continue

if not ml_plugin_initialized:
    print("OpenSearch ML plugin is not initialized. Please check the issue.")
    exit(1)

# Configure required persistent settings

persistent_settings = {
    "persistent": {
        "plugins.ml_commons.only_run_on_ml_node": 'false',
        "plugins.ml_commons.update_connector.enabled": 'true'
    }
}

requests.put(opensearch_url + "/_cluster/settings", json=persistent_settings)

# Create the remote model group

remote_model_group = os.getenv("REMOTE_MODEL_GROUP")
if remote_model_group is None:
    remote_model_group = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))

remote_model_group = {
    "name": remote_model_group,
    "description": "Description of the remote model group"
}

response = requests.post(opensearch_url + "/_plugins/_ml/model_groups/_register", json=remote_model_group)
if response.status_code == 400:
    print(response.json())
    exit(1)

model_group_id = response.json()["model_group_id"]

# Create the connector

connector_config = {
    "name": "Amazon Bedrock",
    "description": "Connector for Amazon Bedrock (AI21 Labs Jurassic)",
    "version": 1,
    "protocol": "aws_sigv4",
    "credential": {
        "access_key": aws_access_key,
        "secret_key": aws_secret_key
    },
    "parameters": {
        "region": "us-east-1",
        "service_name": "bedrock",
        "model_name": "ai21.j2-mid-v1"
    },
    "actions": [
        {
            "action_type": "predict",
            "method": "POST",
            "headers": {
                "content-type": "application/json"
            },
            "url": "https://bedrock-runtime.${parameters.region}.amazonaws.com/model/${parameters.model_name}/invoke",
            "request_body": "{\"prompt\":\"${parameters.inputs}\",\"maxTokens\":200,\"temperature\":0.7,\"topP\":1,\"stopSequences\":[],\"countPenalty\":{\"scale\":0},\"presencePenalty\":{\"scale\":0},\"frequencyPenalty\":{\"scale\":0}}",
            "post_process_function": "\n  return params['completions'][0].data.text; \n"
        }
    ]    
}

response = requests.post(opensearch_url + "/_plugins/_ml/connectors/_create", json=connector_config)
connector_id = response.json()["connector_id"]

# Register the model

model_config = {
    "name": "ai21.j2-mid-v1",
    "function_name": "remote",
    "model_group_id": model_group_id,
    "description": "AI21 Labs Model",
    "connector_id": connector_id
}

response = requests.post(opensearch_url + "/_plugins/_ml/models/_register", json=model_config)
model_id = response.json()["model_id"]

# Deploy the model

requests.post(opensearch_url + "/_plugins/_ml/models/" + model_id + "/_deploy")

### make sure to wait until the model is deployed ###

model_deployed = False
model_deploy_timeout = 30

response = requests.get(opensearch_url + "/_plugins/_ml/models/" + model_id)
if response.status_code == 200 and response.json()["model_state"] == "DEPLOYED":
   model_deployed = True
else:
    count = 0
    while not model_deployed and count < model_deploy_timeout:
        print("⏰ Waiting until the model is deployed...")
        time.sleep(1)
        count += 1
        try:
            response = requests.get(opensearch_url + "/_plugins/_ml/models/" + model_id)
            if response.status_code == 200 and response.json()["model_state"] == "DEPLOYED":
                model_deployed = True
        except:
            continue

# Testing the model

question = "What is the meaning of life?"
print("➡️ Testing the model with the question: " + question + "\n")
response = requests.post(opensearch_url + "/_plugins/_ml/models/" + model_id + "/_predict",
              json={
                  "parameters": {
                      "inputs": question
                    }})

if response.status_code != 200:
    print(response.json())
    exit(1)

print("Response:")
print(response.json()["inference_results"][0]["output"][0]["dataAsMap"]["response"])

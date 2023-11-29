## Getting Started with OpenSearch External Models

This repository contains the supporting code for this series, focused on introducing the concept of [external models](https://opensearch.org/docs/latest/ml-commons-plugin/remote-models/index/) from [OpenSearch](https://opensearch.org). External models allow ML developers to create integrations with models trained outside OpenSearch. Once these models are registered, they can be used along with the built-in features of OpenSearch.

## AI21 Labs Jurassic 2 as External Model

One way to explore the power of external models with OpenSearch is registering a model that points to a known service such as Amazon Bedrock. This repository contains one example, where a model based on AI21 Labs Jurassic 2 is used to run inferences. To test this, follow this instructions:

1. Start a local copy of OpenSearch

```bash
docker compose up -d
```

2. Deploy the external model

```bash
python deploy-external-model.py
```

Once the code finishes, you should see an output similar to this:

```bash
⏰ Waiting until the model is deployed...
➡️ Testing the model with the question: What is the meaning of life?

Response:

The meaning of life is a question that has been debated throughout history, and there is no single answer that is universally accepted. Some people believe that the meaning of life is to seek happiness, fulfillment, and personal growth, while others believe that it is to serve a higher power or to fulfill a specific purpose. Ultimately, the meaning of life is a personal belief that may vary from person to person.
```

💡 Make sure to register AWS credentials that have access to Amazon Bedrock.

## Deploying the Sample ML API

The third part of this series focus on showing how ML developers can author their own APIs and use them as external models. To illustrate how this is done, you can use the sample ML API implemented in this repository. This ML API is provisioned using the Cloud Development Kit (CDK). To install the CDK locally, follow the instructions in the [CDK documentation](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_install).

This will create an ECS Fargate service fronted by an Application Load Balancer. HTTPS will be configured on the application load balancer, so a custom Route53 domain and an ACM certificate will also be created.

Before deploying the example, update the 4 values in `app.py`, specifying an existing [Route53 Hosted Zone](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/CreatingHostedZone.html) and your desired subdomain for the API to run on:

```python
{
    "certificate_domain_name":"*.mydomain.com",
    "hosted_zone_name": "mydomain.com",
    "hosted_zone_id": "Z03957181ABCDEFGHI",
    "a_record_name": "api.mydomain.com"
}
```
Once updated, you can install the dependencies & deploy the CDK application:

```
cd custom-ml-api/cdk
pip install -r requirements.txt && cdk bootstrap
```

```
cdk deploy
```

This should take about 5 minutes to deploy. Once the deployment is complete, you will be able to access the API via the custom domain name you specified:

```
curl -H "authorization: Basic YWRtaW46c2VjcmV0" https://api.mydomain.com/weather -XPOST --data '{ "text_inputs": "London" }' -H "Content-Type: application/json"
```

```json
{
  "description": "cloudy",
  "humidity": 49,
  "location": "London",
  "temp": 29.36991312982127
}
```

Be sure to remove the application once you are done testing to avoid unexpected costs:

```
cdk destroy
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.

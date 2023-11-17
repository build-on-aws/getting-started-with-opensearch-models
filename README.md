## Getting Started with OpenSearch Remote Models


## Deploying the sample ML API

The example custom ML API is provisioned using the Cloud Development Kit (CDK). To install the CDK locally, follow the instructions in the [CDK documentation](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_install).

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
Once updated, you can deploy the CDK application:

```
cd custom-ml-api/cdk
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

This library is licensed under the MIT-0 License. See the LICENSE file.


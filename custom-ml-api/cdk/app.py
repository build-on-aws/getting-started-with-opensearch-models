#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import CdkStack


app = cdk.App()
CdkStack(app, "customMlApiStack", props={
    "certificate_domain_name":"*.mydomain.com",
    "hosted_zone_name": "mydomain.com",
    "hosted_zone_id": "Z03957181ABCDEFGHI",
    "a_record_name": "api.mydomain.com"})

app.synth()

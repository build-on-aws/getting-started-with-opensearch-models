from os import path
from aws_cdk import (
    Stack,
    Duration,
    aws_ec2 as ec2, 
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr_assets as ecr_assets
)
from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, props: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        public_zone = route53.HostedZone.from_hosted_zone_attributes(self, "mlApiHostedZone", 
            zone_name=props.get("hosted_zone_name"), 
            hosted_zone_id=props.get("hosted_zone_id"))

        cert = acm.Certificate(self, "mlApiCert", 
            domain_name=props.get("certificate_domain_name"), 
            validation=acm.CertificateValidation.from_dns(public_zone))

        vpc = ec2.Vpc(self, "mlApiVpc", max_azs=3)

        cluster = ecs.Cluster(self, "mlApiCluster", vpc=vpc)

        asset = ecr_assets.DockerImageAsset(self, 'mlApiImage',
            directory="../")

        service = ecs_patterns.ApplicationLoadBalancedFargateService(self, "mlApiService",
            certificate=cert,
            cluster=cluster,
            cpu=256,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_docker_image_asset(asset),
                container_port=5000),
            memory_limit_mib=512,
            protocol=elbv2.ApplicationProtocol.HTTPS,
            public_load_balancer=True,
            redirect_http=True)

        service.target_group.configure_health_check(
            path="/",
            healthy_threshold_count=2,
            unhealthy_threshold_count=2,
            timeout=Duration.seconds(3),
            interval=Duration.seconds(5),
            healthy_http_codes="200-499"
        )
        service.target_group.port = 5000

        route53.ARecord(self, "mlApiAliasRecord", 
            zone=public_zone, 
            target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(service.load_balancer)), 
            record_name=props.get("a_record_name"))
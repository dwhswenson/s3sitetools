import pathlib

import boto3
import click

def build_stack(stack_name, stack_file, parameters=None, region=None,
                capabilities=[]):
    if parameters is None:
        parameters = {}

    aws_params = [
        {"ParameterKey": key, "ParameterValue": value }
        for key, value in parameters.items()
    ]

    with open(stack_file, mode='r') as f:
        template_contents = f.read()

    if region:
        cf = boto3.client('cloudformation', region_name=region)
    else:
        cf = boto3.client('cloudformation')

    resp = cf.create_stack(
        StackName=stack_name,
        TemplateBody=template_contents,
        Parameters=aws_params,
        Capabilities=capabilities,
    )
    print(resp)

def get_oidc_provider_arn():
    iam = boto3.client('iam')
    resp = iam.list_open_id_connect_providers()
    arns = [p['Arn'] for p in resp['OpenIDConnectProviderList']]

    for arn in arns:
        prov = iam.get_open_id_connect_provider(OpenIDConnectProviderArn=arn)
        if (
            prov['Url'] == "token.actions.githubusercontent.com"
            and 'sts.amazonaws.com' in prov['ClientIDList']
        ):
            return arn
    return None


if __name__ == "__main__":
    import sys
    oidc_arn = get_oidc_provider_arn()
    params = {
        "BucketName": "hb-net-testbucket-186",
        "OIDCProviderArn": oidc_arn,
        "SubjectFilter": "repo:dwhswenson/hyperblazer-net/*",
    }
    print(params)
    cf_dir = pathlib.Path(__file__).parent / "cloudformation"
    template = cf_dir / "bucket-and-role.yaml"

    build_stack("hb-net-bucket-and-role", template, params,
                capabilities=['CAPABILITY_IAM'])

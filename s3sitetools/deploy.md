# Deploy order

Some notes to just to make sure I have this working correctly in my head.
Limiting this to the situation that we want to have an S3-hosted static site
that gets deployed from GitHub via OIDC.

Use matrix:

- WithDomain: [true, false]
- ExistingOIDCProvider: [true, false]

```
if WithDomain:
    build certificate.yaml in us-east-1

stack = [web-bucket.yaml, github-workflow-role.yaml]

if not ExistingOIDCProvider:
    stack += [github-oidc-provider.yaml]

if WithDomain:
    stack += [cloudfront.yaml]

build stack
```  

Test order for building:

1. github-oidc-provider
2. web-bucket
3. github-workflow-role
4. certificate
5. cloudfront

Consider lifecycles:

* *Once per account*: OIDC provider
* *Once per website*: Bucket
* *Once per domain*: certficate, cloudfront
* *Once per workflow*: role

NB: this means that we ALWAYS create the bucket with the workflow role already
attached. So that can be a single CloudFormation template.

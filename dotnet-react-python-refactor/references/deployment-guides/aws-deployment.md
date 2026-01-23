# AWS Deployment Guide

This guide covers deploying your React + Python application on AWS using various services including EC2, RDS, S3, CloudFront, and Elastic Beanstalk.

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Route 53 (DNS)                    │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│              CloudFront (CDN)                       │
└───────┬─────────────────────────────────┬───────────┘
        │                                 │
        │ Static Assets                   │ API Requests
        │                                 │
┌───────▼─────────┐            ┌──────────▼──────────┐
│  S3 Bucket      │            │  Application Load   │
│  (React Build)  │            │     Balancer        │
└─────────────────┘            └──────────┬──────────┘
                                          │
                        ┌─────────────────┴─────────────────┐
                        │                                   │
                ┌───────▼──────┐                  ┌─────────▼─────┐
                │   EC2/ECS    │                  │   EC2/ECS     │
                │   (FastAPI)  │                  │   (FastAPI)   │
                └───────┬──────┘                  └─────────┬─────┘
                        │                                   │
                        └───────────────┬───────────────────┘
                                        │
                        ┌───────────────▼───────────────┐
                        │                               │
                  ┌─────▼──────┐              ┌────────▼──────┐
                  │   RDS      │              │ ElastiCache   │
                  │ PostgreSQL │              │    (Redis)    │
                  └────────────┘              └───────────────┘
```

## Deployment Options

### Option 1: Elastic Beanstalk (Recommended for Quick Start)
- **Best for**: Quick deployment, managed platform
- **Complexity**: Low
- **Cost**: Medium
- **Flexibility**: Medium

### Option 2: EC2 + RDS + S3 (Full Control)
- **Best for**: Custom requirements, full control
- **Complexity**: High
- **Cost**: Low-Medium (reserved instances)
- **Flexibility**: High

### Option 3: ECS/Fargate (Container-Based)
- **Best for**: Microservices, scalability
- **Complexity**: Medium-High
- **Cost**: Medium-High
- **Flexibility**: High

## Option 1: Elastic Beanstalk Deployment

### Prerequisites

```bash
# Install AWS CLI
pip install awscli

# Install EB CLI
pip install awsebcli

# Configure AWS credentials
aws configure
```

### Step 1: Prepare Backend for Elastic Beanstalk

Create `.ebextensions/python.config` in backend directory:

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app.main:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:elasticbeanstalk:environment:proxy:
    ProxyServer: nginx

packages:
  yum:
    postgresql-devel: []
    gcc: []
```

Create `Procfile` in backend directory:

```
web: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 2: Initialize Elastic Beanstalk

```bash
cd backend

# Initialize EB application
eb init -p python-3.11 my-fastapi-app --region us-east-1

# Create environment
eb create production-env \
  --instance-type t3.medium \
  --database.engine postgres \
  --database.size 20 \
  --database.instance db.t3.micro \
  --envvars SECRET_KEY=your_secret_key,DATABASE_URL=will_be_set_by_eb

# Deploy
eb deploy

# Open in browser
eb open
```

### Step 3: Configure Environment Variables

```bash
# Set environment variables
eb setenv \
  SECRET_KEY=your_secret_key_here \
  ALGORITHM=HS256 \
  ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  BACKEND_CORS_ORIGINS='["https://yourdomain.com"]'

# Or via AWS Console: Elastic Beanstalk > Environment > Configuration > Software
```

### Step 4: Deploy Frontend to S3 + CloudFront

```bash
cd frontend

# Build production bundle
npm run build

# Create S3 bucket
aws s3 mb s3://my-react-app-bucket

# Configure bucket for static website hosting
aws s3 website s3://my-react-app-bucket \
  --index-document index.html \
  --error-document index.html

# Upload build files
aws s3 sync dist/ s3://my-react-app-bucket --delete

# Make bucket public
aws s3api put-bucket-policy \
  --bucket my-react-app-bucket \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-react-app-bucket/*"
    }]
  }'

# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name my-react-app-bucket.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html
```

### Step 5: Configure API Gateway (Optional)

For better API management:

```bash
# Create API Gateway
aws apigateway create-rest-api --name my-api

# Configure proxy to Elastic Beanstalk
# Use AWS Console for easier setup
```

## Option 2: EC2 + RDS + S3 Deployment

### Step 1: Launch RDS PostgreSQL

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name my-db-subnet \
  --db-subnet-group-description "My DB Subnet" \
  --subnet-ids subnet-12345 subnet-67890

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier myapp-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourSecurePassword \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-12345 \
  --db-subnet-group-name my-db-subnet \
  --backup-retention-period 7 \
  --publicly-accessible false
```

### Step 2: Launch ElastiCache Redis

```bash
# Create cache subnet group
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name my-cache-subnet \
  --cache-subnet-group-description "My Cache Subnet" \
  --subnet-ids subnet-12345 subnet-67890

# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id myapp-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --cache-subnet-group-name my-cache-subnet \
  --security-group-ids sg-12345
```

### Step 3: Launch EC2 Instance

```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name my-key-pair \
  --query 'KeyMaterial' \
  --output text > my-key-pair.pem

chmod 400 my-key-pair.pem

# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --count 1 \
  --instance-type t3.medium \
  --key-name my-key-pair \
  --security-group-ids sg-12345 \
  --subnet-id subnet-12345 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=MyAppServer}]' \
  --user-data file://user-data.sh
```

Create `user-data.sh`:

```bash
#!/bin/bash
# Update system
yum update -y

# Install Docker
yum install -y docker
service docker start
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository (or copy files)
cd /home/ec2-user
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# Set environment variables
cat > .env << EOF
DATABASE_URL=postgresql://admin:password@your-rds-endpoint:5432/myapp
REDIS_URL=redis://your-elasticache-endpoint:6379/0
SECRET_KEY=your_secret_key
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
EOF

# Start application
docker-compose up -d
```

### Step 4: Configure Application Load Balancer

```bash
# Create target group
aws elbv2 create-target-group \
  --name my-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-12345 \
  --health-check-path /api/health

# Create load balancer
aws elbv2 create-load-balancer \
  --name my-load-balancer \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-12345

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...

# Register targets
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --targets Id=i-1234567890abcdef0
```

### Step 5: Configure SSL/TLS with ACM

```bash
# Request certificate
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names www.yourdomain.com \
  --validation-method DNS

# Add HTTPS listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

## Option 3: ECS Fargate Deployment

### Step 1: Create ECR Repositories

```bash
# Create repository for backend
aws ecr create-repository --repository-name my-backend

# Create repository for frontend (optional)
aws ecr create-repository --repository-name my-frontend

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com
```

### Step 2: Build and Push Images

```bash
# Build and push backend
cd backend
docker build -t my-backend .
docker tag my-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-backend:latest
```

### Step 3: Create ECS Task Definition

Create `task-definition.json`:

```json
{
  "family": "my-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    }
  ]
}
```

Register task definition:

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

### Step 4: Create ECS Cluster and Service

```bash
# Create cluster
aws ecs create-cluster --cluster-name my-cluster

# Create service
aws ecs create-service \
  --cluster my-cluster \
  --service-name my-service \
  --task-definition my-app:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=backend,containerPort=8000"
```

## CI/CD with AWS CodePipeline

### Step 1: Create CodeBuild Project

Create `buildspec.yml`:

```yaml
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
  build:
    commands:
      - echo Build started on `date`
      - docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG backend/
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
  post_build:
    commands:
      - echo Build completed on `date`
      - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
```

### Step 2: Create CodePipeline

```bash
# Create pipeline using AWS Console or CLI
aws codepipeline create-pipeline --cli-input-json file://pipeline.json
```

## Monitoring and Logging

### CloudWatch Setup

```bash
# Create log group
aws logs create-log-group --log-group-name /aws/app/my-app

# Create metric alarm
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

### X-Ray for Tracing (Optional)

Add to FastAPI:

```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

xray_recorder.configure(service='my-backend')
XRayMiddleware(app, xray_recorder)
```

## Cost Optimization

### Reserved Instances

```bash
# Purchase reserved instance
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id offering-id \
  --instance-count 1
```

### Auto Scaling

```bash
# Create auto scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name my-asg \
  --launch-configuration-name my-launch-config \
  --min-size 1 \
  --max-size 5 \
  --desired-capacity 2 \
  --vpc-zone-identifier "subnet-12345,subnet-67890" \
  --target-group-arns arn:aws:elasticloadbalancing:...

# Create scaling policy
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name my-asg \
  --policy-name scale-up \
  --scaling-adjustment 1 \
  --adjustment-type ChangeInCapacity
```

## Security Best Practices

1. **Use IAM Roles** - Never hardcode credentials
2. **Enable VPC** - Keep resources in private subnets
3. **Security Groups** - Restrict access by IP/port
4. **Enable encryption** - RDS, S3, EBS encryption
5. **Use AWS WAF** - Protect against common attacks
6. **Enable CloudTrail** - Audit all API calls
7. **Regular updates** - Keep AMIs and containers updated
8. **Use Secrets Manager** - Store sensitive configuration
9. **Enable MFA** - Multi-factor authentication
10. **Regular backups** - Automated RDS snapshots

## Estimated Monthly Costs

### Small Application (Development/Staging)
- EC2 t3.medium: $30
- RDS db.t3.micro: $15
- ElastiCache t3.micro: $12
- S3 + CloudFront: $5
- Load Balancer: $16
- **Total: ~$78/month**

### Medium Application (Production)
- EC2 t3.large (2x): $120
- RDS db.t3.small: $30
- ElastiCache t3.small: $25
- S3 + CloudFront: $20
- Load Balancer: $16
- NAT Gateway: $32
- **Total: ~$243/month**

## Troubleshooting

### Check EC2 Instance Logs

```bash
# SSH into instance
ssh -i my-key-pair.pem ec2-user@ec2-ip-address

# Check Docker logs
docker-compose logs

# Check system logs
tail -f /var/log/messages
```

### RDS Connection Issues

```bash
# Test connection from EC2
psql -h rds-endpoint -U admin -d myapp

# Check security group rules
aws ec2 describe-security-groups --group-ids sg-12345
```

### Debug ECS Tasks

```bash
# List tasks
aws ecs list-tasks --cluster my-cluster

# Describe task
aws ecs describe-tasks --cluster my-cluster --tasks task-id

# View logs
aws logs tail /ecs/my-app --follow
```

## Additional Resources

- [AWS Documentation](https://docs.aws.amazon.com/)
- [Elastic Beanstalk Guide](https://docs.aws.amazon.com/elasticbeanstalk/)
- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)

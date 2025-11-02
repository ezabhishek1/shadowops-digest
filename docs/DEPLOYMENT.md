# Deployment Guide

This guide covers deploying ShadowOps Digest to various environments.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- PostgreSQL database (for production)
- Domain name (for production)
- SSL certificate (for production)

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Optional
ENVIRONMENT=production
LOG_LEVEL=INFO
REACT_APP_API_URL=https://api.yourdomain.com
```

## Local Development

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/shadowops-digest.git
cd shadowops-digest

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up --build

# Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Docker Deployment

### Single Server Deployment

1. **Prepare the server:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Deploy application:**
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/shadowops-digest.git
cd shadowops-digest

# Setup environment
cp .env.example .env
nano .env  # Edit with production values

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose ps
docker-compose logs -f
```

3. **Setup reverse proxy (Nginx):**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **Setup SSL with Let's Encrypt:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Cloud Deployments

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Build and push Docker images:**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and tag images
docker build -t shadowops-backend ./backend
docker tag shadowops-backend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/shadowops-backend:latest

docker build -t shadowops-frontend ./frontend
docker tag shadowops-frontend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/shadowops-frontend:latest

# Push images
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/shadowops-backend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/shadowops-frontend:latest
```

2. **Create ECS Task Definition:**
```json
{
  "family": "shadowops-digest",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/shadowops-backend:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"}
      ],
      "secrets": [
        {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
      ]
    }
  ]
}
```

3. **Setup RDS PostgreSQL:**
```bash
aws rds create-db-instance \
  --db-instance-identifier shadowops-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20
```

#### Using Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker shadowops-digest

# Create environment
eb create shadowops-prod

# Deploy
eb deploy

# Open application
eb open
```

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/shadowops-backend ./backend
gcloud builds submit --tag gcr.io/PROJECT_ID/shadowops-frontend ./frontend

# Deploy backend
gcloud run deploy shadowops-backend \
  --image gcr.io/PROJECT_ID/shadowops-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy frontend
gcloud run deploy shadowops-frontend \
  --image gcr.io/PROJECT_ID/shadowops-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name shadowops-rg --location eastus

# Create container registry
az acr create --resource-group shadowops-rg --name shadowopsacr --sku Basic

# Build and push images
az acr build --registry shadowopsacr --image shadowops-backend:latest ./backend
az acr build --registry shadowopsacr --image shadowops-frontend:latest ./frontend

# Deploy containers
az container create \
  --resource-group shadowops-rg \
  --name shadowops-backend \
  --image shadowopsacr.azurecr.io/shadowops-backend:latest \
  --dns-name-label shadowops-api \
  --ports 8000
```

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create shadowops-digest

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set OPENAI_API_KEY=your_key_here

# Deploy
git push heroku main

# Open app
heroku open
```

## Production Checklist

### Security
- [ ] Environment variables secured (not in code)
- [ ] SSL/TLS enabled
- [ ] CORS configured for specific origins
- [ ] Rate limiting implemented
- [ ] API authentication added
- [ ] Database credentials rotated
- [ ] Secrets management (AWS Secrets Manager, etc.)

### Performance
- [ ] CDN configured for frontend assets
- [ ] Database connection pooling enabled
- [ ] Caching layer added (Redis)
- [ ] Horizontal scaling configured
- [ ] Load balancer setup

### Monitoring
- [ ] Application logging configured
- [ ] Error tracking (Sentry, Rollbar)
- [ ] Performance monitoring (New Relic, Datadog)
- [ ] Uptime monitoring (Pingdom, UptimeRobot)
- [ ] Cost monitoring (AWS Cost Explorer)

### Backup & Recovery
- [ ] Database backups automated
- [ ] Disaster recovery plan documented
- [ ] Backup restoration tested
- [ ] Data retention policy defined

### Documentation
- [ ] API documentation published
- [ ] Deployment runbook created
- [ ] Incident response procedures documented
- [ ] Architecture diagrams updated

## Scaling Considerations

### Horizontal Scaling

**Backend:**
- Deploy multiple instances behind load balancer
- Use stateless design (no session storage)
- Implement distributed caching

**Frontend:**
- Serve from CDN
- Enable browser caching
- Optimize bundle size

### Vertical Scaling

**Backend:**
- Increase CPU/memory for compute-intensive tasks
- Optimize clustering algorithms
- Use async processing for long-running tasks

**Database:**
- Upgrade instance size
- Add read replicas
- Implement connection pooling

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend health
curl https://yourdomain.com

# Database health
psql $DATABASE_URL -c "SELECT 1"
```

### Log Monitoring

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# System logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Performance Metrics

Monitor:
- Response times (p50, p95, p99)
- Error rates
- Request throughput
- CPU and memory usage
- Database query performance
- OpenAI API latency and costs

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
docker-compose logs backend
docker-compose ps
docker-compose down -v && docker-compose up --build
```

**Database connection failed:**
```bash
# Check database is running
docker-compose ps postgres

# Test connection
psql $DATABASE_URL -c "SELECT version()"
```

**OpenAI API errors:**
- Verify API key is correct
- Check account has credits
- Review rate limits
- Check for service outages

## Rollback Procedure

```bash
# Docker deployment
docker-compose down
git checkout previous-version
docker-compose up -d

# Cloud deployment
# AWS ECS
aws ecs update-service --cluster shadowops --service backend --task-definition shadowops:PREVIOUS_VERSION

# Heroku
heroku releases:rollback v123
```

## Cost Optimization

1. **OpenAI API**: Monitor usage, implement caching
2. **Compute**: Right-size instances, use spot instances
3. **Database**: Use appropriate tier, enable auto-scaling
4. **Storage**: Implement lifecycle policies
5. **Network**: Use CDN, optimize data transfer

## Support

For deployment issues:
- Check [Troubleshooting Guide](TROUBLESHOOTING.md)
- Review [Architecture Documentation](ARCHITECTURE.md)
- Open [GitHub Issue](https://github.com/YOUR_USERNAME/shadowops-digest/issues)

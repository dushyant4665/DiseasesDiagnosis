# System Architecture - Disease Prediction Service

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USERS / CLIENTS                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CDN (CloudFlare / Akamai)                    │
│                  Static Assets Cache (HTML/CSS/JS)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx / ALB)                   │
│                      SSL Termination / HTTPS                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   API Gateway (Kong / AWS API GW)                │
│          Rate Limiting, Auth, Request Validation, CORS           │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   Inference Service      │    │    Cache Layer (Redis)    │
│   (Node.js / Python)     │◄───┤   Store: symptoms→results │
│   Stateless Pods x N     │    │   TTL: 5 minutes          │
└──────────┬───────────────┘    └──────────────────────────┘
           │
           │ Read
           ▼
┌──────────────────────────┐
│    Model Registry        │
│  (S3 / MinIO / GCS)      │
│  diseases.csv artifact   │
│  Version: v1.2.3         │
└──────────────────────────┘
           ▲
           │ Upload
┌──────────┴───────────────┐
│  Offline Training        │
│  Pipeline (Airflow)      │
│  Python Data Processing  │
│  ETL: Kaggle → CSV       │
│  Validation & Tests      │
└──────────┬───────────────┘
           │ Source
           ▼
┌──────────────────────────┐         ┌──────────────────────────┐
│   Data Lake (S3)         │         │  Application DB          │
│   Raw CSV files          │         │  (MongoDB / PostgreSQL)  │
│   Disease datasets       │         │  User logs, sessions     │
│   Historical data        │         │  Feedback, analytics     │
└──────────────────────────┘         └──────────┬───────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              Observability & Monitoring Stack                    │
│  Logs: ELK Stack (Elasticsearch, Logstash, Kibana)              │
│  Metrics: Prometheus + Grafana                                   │
│  Traces: Jaeger / OpenTelemetry                                  │
│  Alerts: PagerDuty / Slack                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      CI/CD Pipeline                              │
│  GitHub Actions / GitLab CI / Jenkins                            │
│  Build → Test → Security Scan → Docker Build → Deploy           │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Client Layer
- **Frontend**: Static HTML/CSS/JS served via CDN
- **Mobile Apps**: iOS/Android native apps hitting same API
- **Third-party integrations**: Partner systems via API keys

### Edge Layer
- **CDN**: CloudFlare or Akamai for global static asset distribution
- **DDoS Protection**: Cloud provider native or Cloudflare
- **WAF**: Web Application Firewall for security filtering

### Gateway Layer
- **API Gateway**: Kong, AWS API Gateway, or Nginx
  - Authentication: JWT tokens, OAuth2
  - Rate limiting: 100 req/min per user, 10k req/min global
  - Request validation and sanitization
  - CORS policy enforcement
  - API versioning (v1, v2)

### Application Layer
- **Inference Service**: Node.js or Python FastAPI
  - Horizontal scaling: 3-50 pods based on load
  - Auto-scaling: CPU > 70% or latency > 200ms
  - Health checks: /health endpoint
  - Graceful shutdown and startup
  - In-memory disease data loaded at boot
  - Stateless design for easy scaling

### Caching Layer
- **Redis Cluster**
  - Cache prediction results keyed by symptom hash
  - TTL: 5 minutes
  - Reduces database/compute load by 80%
  - Distributed cache across regions

### Data Layer
- **Model Registry**: S3, MinIO, or Google Cloud Storage
  - Versioned artifacts: diseases_v1.2.3.csv
  - Immutable storage
  - Access control via IAM
  
- **Application Database**: MongoDB or PostgreSQL
  - User profiles and sessions
  - Prediction history logs
  - Feedback and ratings
  - Analytics events
  - Encrypted at rest

- **Data Lake**: S3 or equivalent
  - Raw Kaggle datasets
  - Historical prediction logs
  - Data for offline analysis

### Training Pipeline (Offline)
- **Orchestration**: Apache Airflow or Prefect
- **Steps**:
  1. Fetch raw data from Kaggle API or manual upload
  2. Data validation and cleaning (Python pandas)
  3. Generate CSV artifact with schema validation
  4. Run integration tests
  5. Upload to model registry with version tag
  6. Trigger canary deployment
  7. Monitor metrics, rollback if needed
- **Schedule**: Weekly or on-demand
- **Language**: Python with pandas, scikit-learn

### Observability
- **Logging**: ELK Stack
  - Centralized logs from all services
  - Structured JSON logging
  - Log retention: 30 days hot, 1 year cold
  
- **Metrics**: Prometheus + Grafana
  - API latency (p50, p95, p99)
  - Error rates and status codes
  - Cache hit ratio
  - Throughput (requests per second)
  - Resource usage (CPU, memory, disk)
  
- **Tracing**: Jaeger or OpenTelemetry
  - End-to-end request tracing
  - Latency breakdown by service
  
- **Alerts**: PagerDuty or Slack
  - High error rate (> 5%)
  - High latency (> 500ms p95)
  - Service down
  - Cache failures

### CI/CD Pipeline
- **Source Control**: GitHub or GitLab
- **Pipeline Steps**:
  1. Code checkout
  2. Lint and format checks
  3. Unit tests (Jest, pytest)
  4. Integration tests
  5. Security scanning (Snyk, Trivy)
  6. Docker image build
  7. Push to container registry
  8. Deploy to staging
  9. Smoke tests
  10. Deploy to production (blue-green or canary)
- **Tools**: GitHub Actions, GitLab CI, Jenkins, ArgoCD

### Deployment
- **Kubernetes**: EKS, GKE, or AKS
  - Deployments with rolling updates
  - ConfigMaps for configuration
  - Secrets for sensitive data
  - Ingress controller (Nginx, Traefik)
  - Pod autoscaling (HPA)
  - Cluster autoscaling
  
- **Serverless Alternative**: AWS Lambda, Google Cloud Run, Azure Functions
  - Lower cost for low traffic
  - Cold start tradeoff
  - Simplified ops

## Data Flow

### Prediction Request Flow
1. User enters symptoms in web UI
2. Frontend sends POST to `/api/predict`
3. Request hits CDN (pass-through for API)
4. Load balancer distributes to API Gateway
5. API Gateway validates, authenticates, rate limits
6. Check Redis cache for symptom hash
7. If cache hit: return cached result (< 10ms)
8. If cache miss:
   - Forward to Inference Service
   - Load disease data from memory
   - Compute Jaccard similarity scores
   - Sort and return top 5
   - Store result in Redis cache
   - Log prediction to MongoDB
9. Response returns through gateway to client
10. Frontend renders results with confidence bars

### Model Update Flow
1. Data engineer downloads new Kaggle dataset
2. Upload to S3 data lake
3. Airflow DAG triggers on file arrival
4. Python script validates CSV schema
5. Data cleaning and normalization
6. Generate versioned artifact
7. Run automated tests against artifact
8. Upload to model registry (S3)
9. Update ConfigMap with new artifact version
10. Trigger rolling restart of Inference Service pods
11. Pods download new artifact on startup
12. Monitor metrics for anomalies
13. Rollback if error rate increases

## Non-Functional Requirements

### Scalability
- **Horizontal scaling**: Stateless services, add pods as needed
- **Database sharding**: Partition by user_id or region
- **Cache layer**: Redis for fast reads
- **CDN**: Offload static assets
- **Target**: Support 10k concurrent users, 100k requests/day

### Latency
- **Target**: p95 < 200ms, p99 < 500ms
- **Strategies**:
  - In-memory data loading
  - Redis caching (5min TTL)
  - CDN for static assets
  - Regional deployments (multi-region)
  - Async logging (don't block request)

### Availability
- **Target**: 99.9% uptime (43 minutes downtime/month)
- **Strategies**:
  - Multi-AZ deployment
  - Load balancing with health checks
  - Auto-restart on failure
  - Database replication
  - Chaos engineering tests

### Security
- **HTTPS only**: TLS 1.3
- **Input validation**: Sanitize all user input
- **Rate limiting**: Prevent abuse
- **Authentication**: JWT tokens for user actions
- **API keys**: For third-party access
- **Secrets management**: Vault or cloud KMS
- **SQL injection**: Parameterized queries
- **CORS**: Whitelist allowed origins
- **Regular security audits**: Quarterly penetration tests

### Privacy
- **Data anonymization**: Hash user identifiers
- **GDPR compliance**: User data deletion API
- **Logging**: No PII in logs
- **Encryption**: At rest (AES-256) and in transit (TLS)
- **Data retention**: 90 days, then archive or delete

### Testing
- **Unit tests**: 80% code coverage
- **Integration tests**: API endpoint testing
- **Load tests**: Simulate 10k concurrent users (k6, Locust)
- **Chaos tests**: Kill random pods, test resilience
- **Smoke tests**: Post-deployment validation
- **Canary deployments**: 5% traffic to new version, monitor, then full rollout

## Technology Stack

### Core Services
- **Inference Service**: Node.js (Express) or Python (FastAPI)
- **API Gateway**: Kong or AWS API Gateway
- **Load Balancer**: Nginx or cloud-native (ALB, GCP LB)

### Data & Storage
- **Database**: MongoDB (document store) or PostgreSQL (relational)
- **Cache**: Redis (single-threaded, fast)
- **Object Storage**: AWS S3, Google Cloud Storage, MinIO
- **Data Lake**: S3 with Athena for queries

### Orchestration & Deployment
- **Container Orchestration**: Kubernetes (EKS, GKE, AKS)
- **CI/CD**: GitHub Actions, GitLab CI, ArgoCD
- **Infrastructure as Code**: Terraform, Pulumi
- **Container Registry**: Docker Hub, ECR, GCR

### Observability
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana) or Loki
- **Metrics**: Prometheus + Grafana
- **Tracing**: Jaeger, OpenTelemetry
- **APM**: DataDog, New Relic (optional)

### Data Pipeline
- **Workflow Orchestration**: Apache Airflow, Prefect
- **Data Processing**: Python (pandas, scikit-learn)
- **Job Queue**: Celery + RabbitMQ or AWS SQS

### Frontend
- **Hosting**: Cloudflare Pages, Netlify, S3 + CloudFront
- **Framework**: Plain HTML/CSS/JS (or React/Vue for complex UI)

### Serverless Alternative
- **Compute**: AWS Lambda, Google Cloud Run, Azure Functions
- **API Gateway**: AWS API Gateway, Cloud Endpoints
- **Database**: DynamoDB, Firestore

## Next Steps to Production

### Pre-Launch Checklist
- [ ] Load testing with 10k concurrent users
- [ ] Security audit and penetration testing
- [ ] Set up monitoring dashboards (Grafana)
- [ ] Configure alerts (PagerDuty or Slack)
- [ ] Implement rate limiting and DDoS protection
- [ ] Set up database backups (daily snapshots)
- [ ] Document API (OpenAPI/Swagger spec)
- [ ] Create runbooks for common incidents
- [ ] Set up on-call rotation
- [ ] GDPR compliance review
- [ ] Implement user feedback collection
- [ ] A/B testing framework for model versions
- [ ] Canary deployment pipeline
- [ ] Multi-region deployment (US, EU, Asia)
- [ ] Cost monitoring and budgets
- [ ] Legal review (ToS, Privacy Policy)

### Post-Launch Improvements
- [ ] Machine learning model (replace Jaccard with trained classifier)
- [ ] User accounts and prediction history
- [ ] Mobile apps (iOS, Android)
- [ ] Symptom auto-complete and suggestions
- [ ] Multi-language support
- [ ] Doctor recommendations and telehealth integration
- [ ] User feedback loop (was prediction accurate?)
- [ ] Model retraining pipeline based on feedback
- [ ] Explainability (why this disease was predicted)
- [ ] Advanced analytics dashboard for internal users


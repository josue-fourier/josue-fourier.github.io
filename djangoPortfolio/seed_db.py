import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoPortfolio.settings')
django.setup()

from portfolio.models import LogEntry, Project, TechnicalStrength

print("Clearing database...")
LogEntry.objects.all().delete()
Project.objects.all().delete()
TechnicalStrength.objects.all().delete()

print("Generating Tech Stack...")
tech_names = [
    "Go", "Rust", "Python", "TypeScript", "React", "Vue", "Django", "FastAPI",
    "PostgreSQL", "Redis", "MongoDB", "Cassandra", "Kafka", "RabbitMQ",
    "Docker", "Kubernetes", "AWS", "GCP", "Terraform", "Ansible",
    "GraphQL", "gRPC", "WebSockets", "WebRTC", "Architecture", "CI/CD"
]
techs = []
for name in tech_names:
    tech = TechnicalStrength.objects.create(technology=name)
    techs.append(tech)

print("Generating Projects...")
project_data = [
    ("Telemetry Core", "Core telemetry ingest system for IoT devices"),
    ("Dashboard 2.0", "Realtime websocket analytics dashboard"),
    ("Storage Tier", "Distributed TimescaleDB storage cluster"),
    ("Design System", "React-based UI/UX component library"),
    ("Infrastructure", "Cloud provisioning and Kubernetes manifests"),
    ("Auth Service", "Centralized OAuth2 and JWT authentication provider"),
    ("Payment Gateway", "Stripe integration and billing microservice"),
    ("Recommendation Engine", "Collaborative filtering ML pipeline"),
    ("Search API", "Elasticsearch-powered full text search"),
    ("Mobile App API", "GraphQL backend for iOS and Android clients")
]
projects = []
for name, desc in project_data:
    p = Project.objects.create(name=name, active=True, description=desc)
    p.stack.set(random.sample(techs, random.randint(3, 5)))
    projects.append(p)

print("Generating 500 Logs...")
log_titles = [
    "Migrating to {tech}",
    "Optimizing {tech} performance",
    "Architecting the {project} backend",
    "Resolving bottlenecks in {tech}",
    "Deploying {project} to {tech}",
    "Stress testing the {project} cluster",
    "Implementing {tech} for {project}",
    "Post-mortem: {project} outage",
    "Refactoring {tech} modules in {project}",
    "Security audit results for {project}"
]

log_contents = [
    """
# Overview
We recently encountered scaling limits with the current architecture.

## The Solution
By integrating new strategies, we reduced latency by 45%.
```python
def optimize_query(data):
    return [x for x in data if x.is_valid()]
```

## Architecture Changes
```mermaid
graph TD
    A[Client] --> B(Load Balancer)
    B --> C{Cache Hit?}
    C -->|Yes| D[Redis]
    C -->|No| E[Primary DB]
```
    """,
    """
# Performance Review

During the load test, we observed the following percentiles:

| Service | p50 (ms) | p95 (ms) | p99 (ms) | Status |
|---------|----------|----------|----------|--------|
| API | 12 | 45 | 110 | 🟢 |
| Worker | 200 | 850 | 2100 | 🟡 |

> "Optimization is an ongoing battle, not a one-time fix."

We plan to implement connection pooling next week.
    """,
    """
# Deployment Successful

The new infrastructure has been fully provisioned.

### Checklist
- [x] VPC Peering
- [x] Database read replicas
- [x] Redis cluster scaling
- [x] IAM Role updates

System is nominal.
    """
]

logs_to_create = []
# Start from exactly 3 years ago
base_date = timezone.now() - timedelta(days=1095) 

for i in range(500):
    proj = random.choice(projects)
    tech = random.choice(techs)
    title_template = random.choice(log_titles)
    title = title_template.format(tech=tech.technology, project=proj.name)
    
    # Progress time forward randomly (between 12 hours and 3 days per log)
    base_date += timedelta(
        hours=random.randint(12, 72),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    
    log = LogEntry(
        title=title,
        project=proj,
        content=random.choice(log_contents)
    )
    # Bulk create bypasses auto_now_add, allowing us to spoof historical dates
    log.date = base_date
    logs_to_create.append(log)

# Insert all 500 rows in one query
LogEntry.objects.bulk_create(logs_to_create)

# Fetch them back to attach ManyToMany tags
saved_logs = LogEntry.objects.all()
for log in saved_logs:
    log.stack.set(random.sample(techs, random.randint(2, 4)))

print(f"Successfully generated {len(projects)} Projects, {len(techs)} Tech Strengths, and 500 Log Entries!")

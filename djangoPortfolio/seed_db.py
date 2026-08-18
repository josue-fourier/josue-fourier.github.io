import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoPortfolio.settings')
django.setup()

from portfolio.models import LogEntry, Project, TechnicalStrength

# Create some Tech Stack items
tech_go = TechnicalStrength.objects.get_or_create(technology="Go")[0]
tech_redis = TechnicalStrength.objects.get_or_create(technology="Redis")[0]
tech_arch = TechnicalStrength.objects.get_or_create(technology="Architecture")[0]
tech_python = TechnicalStrength.objects.get_or_create(technology="Python")[0]
tech_django = TechnicalStrength.objects.get_or_create(technology="Django")[0]
tech_ws = TechnicalStrength.objects.get_or_create(technology="WebSockets")[0]
tech_postgres = TechnicalStrength.objects.get_or_create(technology="PostgreSQL")[0]
tech_sql = TechnicalStrength.objects.get_or_create(technology="SQL")[0]
tech_md = TechnicalStrength.objects.get_or_create(technology="Markdown")[0]
tech_css = TechnicalStrength.objects.get_or_create(technology="CSS")[0]
tech_aws = TechnicalStrength.objects.get_or_create(technology="AWS")[0]
tech_tf = TechnicalStrength.objects.get_or_create(technology="Terraform")[0]

# Create Projects
p_telemetry = Project.objects.get_or_create(name="Telemetry Core", active=True, description="Core telemetry ingest system")[0]
p_telemetry.stack.add(tech_go, tech_redis, tech_arch)

p_dash = Project.objects.get_or_create(name="Dashboard 2.0", active=True, description="Realtime websocket dashboard")[0]
p_dash.stack.add(tech_python, tech_django, tech_ws)

p_storage = Project.objects.get_or_create(name="Storage Tier", active=True, description="TimescaleDB storage cluster")[0]
p_storage.stack.add(tech_postgres, tech_sql)

p_design = Project.objects.get_or_create(name="Design System", active=True, description="UI/UX component library")[0]
p_design.stack.add(tech_md, tech_css)

p_infra = Project.objects.get_or_create(name="Infrastructure", active=True, description="Cloud provisioning scripts")[0]
p_infra.stack.add(tech_aws, tech_tf)

# Delete existing logs to prevent duplicates
LogEntry.objects.all().delete()

# Create Logs (Using the exact data from our JS mockup)
logs_data = [
    {
        "title": "Architecting the Distributed Cache",
        "date": "2026-08-15",
        "project": p_telemetry,
        "tags": [tech_redis, tech_go, tech_arch],
        "content": """
# Architecting the Distributed Cache

To handle the 100k messages/sec throughput from the IoT sensors, a traditional relational database lookup was causing significant bottlenecking.

We migrated the hot-path state to a distributed Redis cluster.

## Architecture Flow
Below is the system overview:

```mermaid
graph TD
    A[IoT Sensors] -->|UDP Streams| B(Ingest Node)
    B -->|Parse & Validate| C{Cache Hit?}
    C -->|Yes| D[Redis Cluster]
    C -->|No| E[PostgreSQL DB]
    D --> F[Real-time Analytics HUD]
    E --> D
```

## Key Learnings
- **Connection Pooling**: Go's `go-redis` pool size had to be tuned to match our worker pool.
- **Eviction Strategy**: Switched to `allkeys-lru` to ensure we only keep the last 24hrs of telemetry in memory.
        """
    },
    {
        "title": "Migrating to WebSockets for Live Data",
        "date": "2026-07-22",
        "project": p_dash,
        "tags": [tech_python, tech_ws, tech_django],
        "content": """
# Migrating to WebSockets for Live Data

Polling the REST API every 2 seconds was melting the server. We shifted to Django Channels and WebSockets.

## Implementation Details

The transition allowed us to maintain persistent connections. Memory usage increased per client, but CPU dropped by 70%.

```mermaid
sequenceDiagram
    participant Client
    participant LoadBalancer
    participant DjangoChannels
    participant RedisPubSub
    
    Client->>LoadBalancer: Upgrade Request (WSS)
    LoadBalancer->>DjangoChannels: Forward
    DjangoChannels-->>Client: 101 Switching Protocols
    RedisPubSub->>DjangoChannels: Broadcast Telemetry Event
    DjangoChannels->>Client: Push Event JSON
```
        """
    },
    {
        "title": "Optimizing PostgreSQL TimescaleDB",
        "date": "2026-06-10",
        "project": p_storage,
        "tags": [tech_postgres, tech_sql],
        "content": """
# Optimizing PostgreSQL TimescaleDB

As our time-series data grew beyond 500GB, query performance degraded. 

## The Fix: Continuous Aggregates
By implementing TimescaleDB continuous aggregates, we pre-calculated the 5-minute and 1-hour rollups.

- Reduced dashboard load times from 8s to 200ms.
- Storage footprint increased by 15%, but entirely worth the tradeoff.
        """
    },
    {
        "title": "UI Component Stress Test & Guidelines",
        "date": "2026-08-10",
        "project": p_design,
        "tags": [tech_md, tech_css],
        "content": """
# Typography & Elements Stress Test

This log entry serves as a comprehensive test of all Markdown elements rendered via Marked.js to ensure our CSS styling remains consistent and premium across edge cases.

## 1. Blockquotes and Callouts

> "The hardest part of building a distributed system is figuring out what went wrong when it inevitably fails. Good logging is not a luxury; it's a lifeline."
> — *Senior Staff Engineer*

## 2. Tabular Data

When benchmarking the new message broker, we observed the following latency percentiles under a 50k RPS load:

| Service | p50 (ms) | p95 (ms) | p99 (ms) | Status |
|---------|----------|----------|----------|--------|
| Ingestion | 1.2 | 4.5 | 12.1 | 🟢 Healthy |
| Auth | 8.5 | 15.2 | 45.0 | 🟡 Warn |
| Storage | 45.1 | 120.5 | 350.2 | 🔴 Critical |

## 3. Lists and Nesting

### Unordered Features
- **Real-time processing**: Utilizes WebSockets for sub-100ms updates.
- **Resilience**:
  - Auto-reconnect with exponential backoff.
  - Circuit breakers on all external API calls.
- **Observability**: Prometheus metrics on every endpoint.

### Ordered Execution Plan
1. Drain traffic from `us-east-1`.
2. Upgrade PostgreSQL primary node.
3. Verify replication lag is < 1s.
4. Route traffic back.

## 4. Media & Code

Here is a mock placeholder image to test responsive image sizing:

![Mock Architecture Diagram](https://placehold.co/800x400/0d9488/ffffff?text=Architecture+Diagram+Placeholder)

And a quick snippet of the retry logic:

```python
def execute_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except NetworkException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```
        """
    },
    {
        "title": "Initial System Bootstrap",
        "date": "2026-01-12",
        "project": p_infra,
        "tags": [tech_tf, tech_aws],
        "content": """
# Initial System Bootstrap

The dawn of the project. Provisioned the VPC, subnets, and EKS clusters using Terraform. 

Infrastructure as code is officially online.
        """
    }
]

for item in logs_data:
    log = LogEntry.objects.create(
        title=item["title"],
        project=item["project"],
        content=item["content"]
    )
    # Since DateField has auto_now_add=True, we override it after creation to match our mock dates
    log.date = item["date"]
    log.save()
    
    log.stack.add(*item["tags"])

print("Successfully seeded the database with 5 LogEntries, 5 Projects, and 12 Technical Strengths!")

# Advanced Logging System

A comprehensive, production-ready logging system with structured logging, multiple outputs, AWS deployment, and monitoring capabilities.

## Features

### Core Logging Features
- **Structured JSON Logging**: Machine-readable logs for better analysis and monitoring
- **Multiple Output Channels**: Console (human-readable) and file (JSON structured)
- **Log Rotation**: Automatic rotation to prevent disk space issues
- **Context Management**: Correlation IDs for request tracking across services
- **Performance Timing**: Built-in timing context manager for operation monitoring
- **Exception Handling**: Comprehensive error logging with stack traces

### Production Features
- **AWS Deployment**: Complete Terraform infrastructure
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Alerting**: Automated alerts for errors and performance issues
- **Scalability**: Designed for containerized and distributed environments
- **Security**: Structured logging without sensitive data exposure

## Quick Start

### Basic Usage

```python
from logging_system import get_logger

# Initialize logger
logger = get_logger("my-app", log_level="INFO")

# Basic logging
logger.info("Application started", version="1.0.0")
logger.error("Database connection failed", database="primary")

# Context-based logging with correlation IDs
with logger.context(user_id="user123", session_id="sess456"):
    logger.info("User action", action="login")
    
    # Performance timing
    with logger.timer("database_query"):
        # Your database operation here
        result = perform_database_query()
        logger.info("Query completed", rows=len(result))
```

### Docker Usage

```bash
# Build the image
docker build -t logging-system .

# Run with environment variables
docker run -e LOG_LEVEL=DEBUG -e SERVICE_NAME=my-service logging-system
```

## Installation

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd logging-system

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run the example
python logging_system.py
```

### AWS Deployment

```bash
# Initialize Terraform
cd terraform
terraform init

# Plan deployment
terraform plan -var="environment=dev"

# Deploy infrastructure
terraform apply

# Deploy application
cd ../
docker build -t logging-system .
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-west-2.amazonaws.com
docker tag logging-system:latest <account-id>.dkr.ecr.us-west-2.amazonaws.com/logging-system:latest
docker push <account-id>.dkr.ecr.us-west-2.amazonaws.com/logging-system:latest
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| `SERVICE_NAME` | Service name for structured logs | logging-service |
| `LOG_DIR` | Directory for log files | logs |
| `MAX_FILE_SIZE` | Maximum log file size in bytes | 10485760 (10MB) |
| `BACKUP_COUNT` | Number of backup log files to keep | 5 |
| `METRICS_PORT` | Port for Prometheus metrics | 8080 |
| `AWS_REGION` | AWS region for CloudWatch integration | us-west-2 |

### Configuration File

Create a `logging_config.yaml` file:

```yaml
logging:
  level: INFO
  structured: true
  console_output: true
  file_output: true
  
handlers:
  file:
    max_size: 10MB
    backup_count: 5
    format: json
  console:
    format: colored
    
context:
  service_name: my-service
  version: 1.0.0
  environment: production
```

## Architecture

### Components

1. **AdvancedLogger**: Core logging class with structured output
2. **Formatters**: JSON and console formatters for different outputs
3. **Context Management**: Thread-safe correlation ID tracking
4. **Performance Monitoring**: Built-in timing and metrics
5. **AWS Integration**: CloudWatch logs and metrics
6. **Prometheus Metrics**: Application and system metrics
7. **Grafana Dashboards**: Visualization and alerting

### Log Structure

```json
{
  "timestamp": "2025-06-19T10:30:45.123Z",
  "level": "INFO",
  "logger": "my-app",
  "message": "User login successful",
  "module": "auth",
  "function": "login_user",
  "line": 42,
  "context": {
    "correlation_id": "abc123-def456-ghi789",
    "user_id": "user123",
    "session_id": "sess456",
    "service_name": "auth-service",
    "version": "1.0.0"
  },
  "duration_ms": 250.5,
  "action": "login",
  "user_agent": "Mozilla/5.0..."
}
```

## Monitoring and Alerting

### Prometheus Metrics

The system exposes the following metrics:

- `log_messages_total`: Counter of log messages by level
- `log_errors_total`: Counter of error messages by type
- `operation_duration_seconds`: Histogram of operation durations
- `active_contexts`: Gauge of active logging contexts

### Grafana Dashboards

Pre-configured dashboards include:

1. **Application Overview**: Error rates, response times, throughput
2. **Error Analysis**: Error breakdown by type and service
3. **Performance Monitoring**: Operation timing and bottlenecks
4. **Infrastructure**: System resources and container metrics

### Alerts

Automated alerts for:

- Error rate > 5% over 5 minutes
- Response time > 2 seconds for 95th percentile
- Critical errors (immediate notification)
- Disk space usage > 85%
- Memory usage > 90%

## AWS Infrastructure

### Services Used

- **ECS Fargate**: Containerized application hosting
- **CloudWatch Logs**: Centralized log aggregation
- **CloudWatch Metrics**: Custom metrics and alarms
- **Application Load Balancer**: Traffic distribution
- **ECR**: Container image registry
- **VPC**: Network isolation
- **IAM**: Security and permissions

### Cost Optimization

- **Log Retention**: Configurable retention periods
- **Compression**: Automatic log compression
- **Filtering**: Client-side filtering to reduce CloudWatch costs
- **Sampling**: Configurable sampling for high-volume logs
- **Spot Instances**: Optional spot instances for non-critical workloads

## Development

### Project Structure

```
logging-system/
├── logging_system.py          # Core logging implementation
├── metrics.py                 # Prometheus metrics
├── config.py                  # Configuration management
├── tests/                     # Test suite
│   ├── test_logging.py
│   ├── test_metrics.py
│   └── test_integration.py
├── terraform/                 # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       ├── dashboards/
│       └── provisioning/
├── requirements.txt
└── README.md
```

### Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=logging_system

# Run integration tests
python -m pytest tests/test_integration.py

# Performance tests
python -m pytest tests/test_performance.py -v
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`python -m pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Performance

### Benchmarks

- **Throughput**: 10,000+ log messages per second
- **Memory Usage**: <50MB for typical workloads
- **Latency**: <1ms for structured logging
- **File I/O**: Asynchronous with buffering

### Optimization Tips

1. Use appropriate log levels in production
2. Implement log sampling for high-volume scenarios
3. Configure log rotation to manage disk space
4. Use structured logging fields efficiently
5. Monitor and adjust buffer sizes based on load

## Security

### Best Practices

- Never log sensitive data (passwords, tokens, PII)
- Use correlation IDs instead of user identifiers when possible
- Implement log retention policies
- Secure log transport with TLS
- Regular security audits of log content

### Compliance

- **GDPR**: Configurable PII filtering
- **HIPAA**: Healthcare data handling guidelines
- **SOC 2**: Security and availability controls
- **PCI DSS**: Payment card data protection

## Troubleshooting

### Common Issues

1. **High Memory Usage**: Adjust buffer sizes and log levels
2. **Disk Space**: Configure log rotation and retention
3. **Performance**: Use sampling and async handlers
4. **Missing Logs**: Check file permissions and disk space
5. **Context Loss**: Verify thread-local storage usage

### Debug Mode

```python
# Enable debug mode for troubleshooting
logger = get_logger("debug", log_level="DEBUG")
logger.debug("Debug information", component="troubleshooting")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Wiki](../../wiki)
- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Email**: jasonboykin@gmail.com

## Roadmap

- [ ] OpenTelemetry integration
- [ ] Multi-region deployment
- [ ] Machine learning-based anomaly detection
- [ ] Real-time log streaming
- [ ] Enhanced security features
- [ ] Performance optimizations
- [ ] Additional output formats (Elasticsearch, Kafka)
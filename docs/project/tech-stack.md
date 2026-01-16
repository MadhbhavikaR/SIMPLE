# Tech Stack: SIMPLE

## Frontend

### Core Components
- **Language**: Python 3.13+
- **Framework**: Custom CLI framework
- **UI Library**: Questionary (interactive prompts)
- **State Management**: Context-based configuration

### Key Libraries
- **Questionary**: Interactive CLI prompts and user interfaces
- **Jinja2**: Template rendering for Docker Compose files
- **PyYAML**: YAML configuration parsing and generation
- **Cryptography**: Secure credential generation and management

## Backend

### Core Components
- **Language**: Python 3.13+
- **Framework**: Custom service orchestration framework
- **API Style**: CLI-based interface with structured configuration
- **Configuration**: YAML-based configuration management

### Key Libraries
- **Jinja2**: Template processing for infrastructure generation
- **PyYAML**: Configuration file parsing and generation
- **Cryptography**: Secure secret generation and management
- **Questionary**: Interactive user input handling

## Database

### Core Components
- **Configuration Storage**: YAML files
- **Secret Storage**: Encrypted files with Docker secrets
- **State Management**: Context-based in-memory storage

### Key Technologies
- **YAML**: Human-readable configuration format
- **Docker Secrets**: Secure credential management
- **File-based Storage**: Simple, portable configuration

## Infrastructure

### Core Components
- **Containerization**: Docker and Docker Compose
- **Orchestration**: Custom service selection and dependency resolution
- **Networking**: Isolated Docker networks with zero-trust principles

### Key Technologies
- **Docker**: Container runtime environment
- **Docker Compose**: Infrastructure-as-code deployment
- **Docker Secrets**: Secure credential management
- **Docker Networks**: Isolated service communication

## Third-Party Services

### Core Services
- **Authentication**: Authelia (optional)
- **Reverse Proxy**: SWAG (Secure Web Application Gateway)
- **Database**: MariaDB (optional)
- **Cloudflare Tunneling**: Cloudflared (optional)
- **Security Monitoring**: Crowdsec (optional)
- **Media Management**: Photoprism (optional)
- **Document Management**: Nextcloud (optional)
- **Ebook Management**: Calibre-Web (optional)
- **Notification System**: Diun (optional)

### Service Categories
- **Core Services**: Essential infrastructure components
- **Security Services**: Authentication, monitoring, and protection
- **Media Services**: Photo, video, and ebook management
- **Productivity Services**: Document management and collaboration
- **Network Services**: Reverse proxy and tunneling

## Development Tools

### Core Tools
- **IDE/Editor**: VSCode, PyCharm, or any Python IDE
- **Package Manager**: UV (recommended) or pip
- **Linting/Formatting**: Ruff, Black, MyPy
- **Testing**: Pytest with coverage
- **Version Control**: Git with GitHub

### Recommended Setup
```bash
# Install development dependencies
uv add --dev pytest pytest-cov mypy ruff black

# Run tests
uv run pytest --cov=src --cov-fail-under=100

# Run linting
uv run ruff check src
uv run black src

# Run type checking
uv run mypy src
```

## Decision Log

### Technology Choices

| Technology Choice | Alternatives Considered | Rationale |
|-------------------|-------------------------|-----------|
| **Python 3.13+** | Node.js, Go, Rust | Python's extensive ecosystem, ease of use, and strong community support for infrastructure tools |
| **Docker Compose** | Kubernetes, Podman, Nomad | Simplicity, wide adoption, and excellent integration with Docker ecosystem |
| **Jinja2 Templates** | Handlebars, Mustache, custom | Jinja2's powerful templating capabilities and Python integration |
| **Questionary** | Inquirer.py, PyInquirer | Active development, good documentation, and comprehensive feature set |
| **UV Package Manager** | pip, poetry, pdm | Performance, modern features, and excellent Python integration |
| **YAML Configuration** | JSON, TOML, HCL | Human-readable format with good support for complex nested structures |

### Architecture Decisions

| Decision | Alternatives | Rationale |
|----------|--------------|-----------|
| **CLI-First Approach** | Web UI, Desktop App | Better for automation, scripting, and remote management |
| **Modular Service Design** | Monolithic, Microservices | Balance between flexibility and complexity |
| **Template-Based Generation** | Code generation, DSL | Easier maintenance and customization |
| **Context-Based Configuration** | Global config, Environment variables | Better organization and scoping |
| **Dependency Resolution** | Manual specification, Automatic detection | Ensures proper service ordering and compatibility |

## Navigation

- 🏠 Home: [README](../../README.md)
- ⬅ Previous: [Project Overview](project-overview.md)
- ➡ Next: [Architecture](architecture.md)

## Traceability

- **Related ADRs**: architecture-decisions.md
- **Related Design Docs**: architecture.md
- **Related APIs**: None
- **Related Data Models**: None

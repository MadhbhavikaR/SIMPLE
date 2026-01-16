<p align="center">
  <img src="docs/assets/logo.png" width="300" />
</p>

<p align="center">
  Hardened Linux • Secure Docker • Zero Trust • One Command Deployments
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/MadhbhavikaR/SIMPLE" />
  <img src="https://img.shields.io/github/stars/MadhbhavikaR/SIMPLE" />
  <img src="https://img.shields.io/github/issues/MadhbhavikaR/SIMPLE" />
  <img src="https://img.shields.io/github/actions/workflow/status/MadhbhavikaR/SIMPLE/ci.yml" />
</p>

---

<h1 align="center">
  WORK IN PROGRESS
</h1>

---

## What is SIMPLE?

**SIMPLE** is an opinionated, security-first self-hosting framework for Linux.

It transforms a bare Linux machine into a hardened, production-grade self-hosting platform using:

- Secure OS baselines
- Zero-trust networking
- Hardened Docker runtime
- Isolated service stacks
- Encrypted secrets
- Automated audits
- One-command deployments

SIMPLE is designed for:
- Home labs
- VPS servers
- Edge servers
- Small businesses
- Makers and engineers

---

## Philosophy

SIMPLE follows three principles:

- **Secure by Default**
- **Composable by Design**
- **Auditable by Nature**

No Kubernetes.  
No YAML sprawl.  
No fragile bash scripts.  
No copy-paste infrastructure.

Just reproducible, hardened self-hosting.

---

## Quick Start

```sh
# 1. Clone & setup
git clone https://github.com/MadhbhavikaR/SIMPLE.git
cd SIMPLE
chmod +x scripts/setup.sh
./scripts/setup.sh

# 2. Activate & run wizard
source activate
sudo python src/main.py

python -m pytest tests/ -v
```

## 📚 Documentation

Comprehensive project documentation is available in the [docs/project/](docs/project/) directory:

- **[Project Overview](docs/project/project-overview.md)** - Goals, features, and vision
- **[Tech Stack](docs/project/tech-stack.md)** - Technology choices and tools
- **[Architecture](docs/project/architecture.md)** - System design and components
- **[Requirements](docs/project/requirements.md)** - Current and future requirements

For complete documentation, see the **[Project Documentation Hub](docs/project/README.md)**.

# AWKWARD LEGACY
## 🔍 Change the Past, Test the Present, Secure the Future

[![Language](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build](https://img.shields.io/badge/Build-Makefile-green.svg)](#compilation)
[![License](https://img.shields.io/badge/License-Legacy-orange.svg)](#license)
[![Coverage](https://img.shields.io/badge/Coverage-75.0%25-green.svg)](geneweb_python/htmlcov/index.html)
---

## 📋 Table of Contents
- [About](#about)
- [Project Context](#project-context)
- [Competencies](#competencies)
- [Installation](#installation)
- [Usage](#usage)
- [Quality Assurance](#quality-assurance)
- [Testing Policy](#testing-policy)
- [Security](#security)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Support](#support)

---

## 🎯 About

**AWKWARD LEGACY** is a restored software suite originally developed between 1995 and 2008 in OCaml, now modernized with a Python backend and Angular 17 frontend. This genealogical research tool is capable of revealing the origins of individuals and uncovering rightful heirs of powerful lineages.

Acquired by **CoinLegacy Inc.**, this legacy codebase has been carefully restored to meet current standards while preserving its historical core functionality.

### 🌟 Key Features

#### 🔐 Security & Authentication
- **JWT Authentication** with access & refresh tokens
- **Bcrypt password hashing** (cost factor 12)
- **Token blacklist** for revocation management
- **Session management** with audit logging
- **Rate limiting** and brute-force protection

#### 👥 Genealogical Management
- **Person Management**: Create, update, and track individuals
- **Family Trees**: Build and visualize family relationships
- **Sosa-Stradonitz Numbering**: Genealogical reference system
- **Multi-calendar Support**: Gregorian, Julian, French Republican, Hebrew
- **Event Timeline**: Track births, marriages, deaths, and custom events
- **Geographic Data**: Location management with historical places

#### 🌍 Frontend Features (Angular 17)
- **Multi-language Support**: French, English, Italian, Spanish
- **Authentication UI**: Login, register, password recovery
- **Database Management**: Multi-database switching
- **Family Editor**: Add and manage family relationships
- **GED2GWB Converter**: GEDCOM file import

#### 🔧 Technical Features
- **RESTful API** with FastAPI
- **OpenAPI/Swagger** documentation
- **SQLAlchemy ORM** for database operations
- **Server-Side Rendering** (SSR) with Angular Universal
- **Comprehensive Testing**: 280+ tests with 75% coverage
- **CI/CD Pipeline**: Automated deployment via GitHub Actions

### 🔗 Original Legacy
- **Original Repository**: [geneweb/geneweb](https://github.com/geneweb/geneweb)
- **Legacy Language**: OCaml
- **Current Implementation**: Python
- **Development Period**: 1995-2008

---

## 🏢 Project Context

### Mission Statement
Our team at CoinLegacy Inc. has been tasked with making this ancient code compliant with current standards. This is a piece of history that must be handled with extreme care - **rewriting or destroying it would result in immediate termination**.

### Objectives
- ✅ Restore legacy functionality
- ✅ Implement comprehensive testing
- ✅ Deploy securely
- ✅ Maintain historical integrity
- ✅ Meet modern quality standards

---

## 🎓 Competencies

### Quality Assurance & Project Management
- **Documented Testing Policy**: Implementation of comprehensive testing protocols
- **Standards Definition**: Quality processes throughout project lifecycle
- **Technical Deployment**: Expert-level deployment strategies
- **Documentation**: Complete deployment guidance

---

## 🛠️ Installation

### Prerequisites

#### Backend
- Python 3.8+
- pip
- virtualenv (recommended)

#### Frontend
- Node.js 18+
- npm 9+
- Angular CLI 17.2.0

#### Tools
- Make utility
- Git

### Quick Start

#### Backend Setup
```bash
cd geneweb_python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
make dev-setup

# Run tests
pytest

# Start API server
make run
# API available at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### Frontend Setup
```bash
cd front

# Install dependencies
npm install

# Start development server
npm start
# Application available at: http://localhost:2316
```

#### Full Stack Development
```bash
# Terminal 1 - Backend
cd geneweb_python && make run

# Terminal 2 - Frontend
cd front && npm start
```

### Compilation & Build

#### Backend
```bash
cd geneweb_python
make test          # Run all tests
make coverage      # Generate coverage report
make lint          # Check code quality
make format        # Format code with Black
```

#### Frontend
```bash
cd front
npm run build              # Build for development
npm run build:prod         # Build for production
npm test                   # Run unit tests
npm run testCypress        # Run E2E tests
```

#### Combined Backend & Frontend Test Pipeline
```bash
make test-bf
```
Runs backend coverage tests followed by frontend unit tests (with Angular coverage). The command prints a concise summary of failing suites or, on success, highlights the latest coverage metrics. Ensure backend dependencies (`make dev-setup` in `geneweb_python`) and frontend packages (`npm install` in `front`) are installed beforehand.

### Project Structure

```
G-ING-900-PAR-9-1-legacy-22/
├── geneweb_python/        # Backend - FastAPI Python
│   ├── src/geneweb/      # Source code
│   │   ├── api/          # REST API & authentication
│   │   ├── core/         # Domain models & business logic
│   │   └── db/           # Database layer
│   ├── tests/            # Test suite (280+ tests)
│   └── docs/             # Backend documentation
│
├── front/                # Frontend - Angular 17
│   ├── src/app/         # Application source
│   │   ├── pages/       # Page components
│   │   ├── components/  # Reusable components
│   │   ├── services/    # API & business services
│   │   └── guards/      # Route guards
│   └── cypress/         # E2E tests
│
├── docs/                # General documentation
│   ├── DEPLOYMENT.md    # Deployment guide
│   └── QUICK_DEPLOY.md  # Quick deploy reference
│
└── .github/workflows/   # CI/CD pipelines
```

---

---

## 📊 Quality Assurance

### Testing Metrics
- **Total Tests**: 280+ (Backend) + Cypress E2E (Frontend)
- **Code Coverage**: 75% (Backend)
- **Test Categories**: Unit, Integration, E2E, TDD
- **CI/CD**: Automated testing on every commit

### Testing Policy Integration
Our quality process is integrated throughout the entire project lifecycle:

#### 🧪 Test Protocols & Scenarios

**Backend (Python - pytest)**
```bash
# Run all tests
pytest

# With coverage report
pytest --cov=src --cov-report=html

# By category
pytest -m unit          # 220+ unit tests
pytest -m integration   # Integration tests
pytest -m tdd          # TDD cycle tests

# Parallel execution
pytest -n auto
```

**Frontend (Angular - Karma + Cypress)**
```bash
# Unit tests
npm test

# E2E tests
npm run testCypress

# Visual regression with Percy
npm run testPercy
```

#### 🔍 Error Detection & Handling
- **Comprehensive error logging** with structured JSON format
- **Malfunction detection systems** via health checks
- **Automated failure recovery** with retry mechanisms
- **Real-time monitoring** on Fly.io dashboard
- **Pre-commit hooks** for code quality enforcement
- **Linting & formatting** with Black, isort, flake8, mypy

#### 📈 Result Analysis & Reporting
- Automated test reporting
- Performance metrics tracking
- Quality gates implementation
- Continuous improvement feedback

---

## 🛡️ Security

### Authentication & Authorization
- **JWT Tokens**: Secure access & refresh token mechanism
- **Bcrypt Hashing**: Password encryption with cost factor 12
- **Token Blacklist**: Revocation management for logout/security
- **Session Management**: Audit logging of user activities
- **Rate Limiting**: Protection against brute-force attacks
- **CORS Configuration**: Strict origin control

### Security Auditing
- **Pre-commit Security Checks**: Automated vulnerability scanning
- **Dependency Scanning**: Regular updates and CVE monitoring
- **Penetration Testing**: Scheduled security assessments
- **Security Code Reviews**: Peer review process
- **Authentication Testing**: 280+ security-focused tests

### Security Best Practices
- ✅ **GDPR Compliance**: Privacy-first data handling
- ✅ **Data Encryption**: AES-256 at rest, TLS 1.3 in transit
- ✅ **Secure Password Management**: Bcrypt with salt
- ✅ **HTTPS Enforcement**: Forced HTTPS on production (Fly.io)
- ✅ **HSTS Headers**: HTTP Strict Transport Security
- ✅ **Security Headers**: CSP, X-Frame-Options, X-Content-Type-Options
- ✅ **Input Validation**: Pydantic models with strict validation
- ✅ **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
- ✅ **XSS Protection**: Angular sanitization + CSP headers

---

## 🚀 Deployment

### Quick Start - Backend Deployment

Le backend Python peut être déployé rapidement sur **Render.com** (gratuit) :

```bash
# 1. Générer les clés secrètes
cd geneweb_python
python generate_secrets.py

# 2. Suivre le guide de déploiement
# Voir : geneweb_python/DEPLOYMENT_RENDER.md
```

**📚 Guides de déploiement :**
- [Guide complet Render.com](geneweb_python/DEPLOYMENT_RENDER.md) - Déploiement backend (recommandé)
- [Étude comparative des plateformes](geneweb_python/docs/HOSTING_COMPARISON.md) - Comparaison des solutions d'hébergement

### Infrastructure Requirements
- **Servers**: Cloud-based or on-premise
- **Resources**: CPU, Memory, Storage specifications
- **Network**: Secure network configuration
- **Backup**: Automated backup solutions

### Best Practices Compliance
- ✅ System administration standards
- ✅ Network security protocols
- ✅ Encryption key management
- ✅ Password policy enforcement
- ✅ Vulnerability prevention measures

---

## 🚀 Deployment

### Production URLs
- **Frontend**: [https://geneweb.surge.sh](https://geneweb.surge.sh)
- **Backend API**: [https://geneweb-api.fly.dev](https://geneweb-api.fly.dev)
- **API Documentation**: [https://geneweb-api.fly.dev/docs](https://geneweb-api.fly.dev/docs)

### Quick Deploy

#### Frontend (Surge.sh)
```bash
cd front
npm install
npm run deploy
```

#### Backend (Fly.io)
```bash
cd geneweb_python
fly auth login
fly deploy
```

### Documentation
- 📖 [Guide de déploiement complet](./docs/DEPLOYMENT.md)
- ⚡ [Guide de déploiement rapide](./docs/QUICK_DEPLOY.md)

### Deployment Strategy
1. **Environment Setup**: Staging and production environments
2. **Resource Provisioning**: Cloud services configuration (Surge.sh + Fly.io)
3. **Security Hardening**: HTTPS, CORS, and authentication
4. **Monitoring Setup**: Health checks and logging
5. **Backup Configuration**: Data protection measures
6. **CI/CD**: Automatic deployment via GitHub Actions

---

## 📚 Documentation

### Project Documentation

#### General
- 📖 [Main README](./README.md) - Project overview and quick start
- 🚀 [Deployment Guide](./docs/DEPLOYMENT.md) - Complete deployment documentation
- ⚡ [Quick Deploy](./docs/QUICK_DEPLOY.md) - Fast deployment reference
- 📊 [Sequence Diagrams](./Sequence_diagram.md) - System architecture flows

#### Backend (Python/FastAPI)
- 🔐 [Authentication Guide](./geneweb_python/docs/AUTHENTICATION_GUIDE.md) - JWT auth implementation
- 🚀 [Quick Start Auth](./geneweb_python/QUICK_START_AUTH.md) - Auth quick reference
- 📡 [API Documentation](./geneweb_python/docs/API/API_DOCUMENTATION.md) - REST API endpoints
- 🔒 [Security Guide](./geneweb_python/docs/SECURITY.md) - Security best practices
- 🧪 [TDD Guide](./geneweb_python/docs/TDD_GUIDE.md) - Test-driven development
- 🗄️ [Database Integration](./geneweb_python/docs/DATABASE_API_INTEGRATION.md) - Database setup
- 🛡️ [GDPR Compliance](./geneweb_python/docs/GDPR_COMPLIANCE.md) - Privacy compliance
- 📚 [Developer Guide](./geneweb_python/docs/DEVELOPER_GUIDE.md) - Development guidelines

#### Frontend (Angular)
- 🌍 [Language Support](./front/doc/language.md) - Multi-language implementation
- 🔐 [Auth Integration](./front/AUTH_README.md) - Frontend authentication
- ⚙️ [API Configuration](./front/API_CONFIG.md) - Backend API setup

#### Live Documentation
- **Swagger UI**: https://geneweb-api.fly.dev/docs
- **ReDoc**: https://geneweb-api.fly.dev/redoc
- **Health Check**: https://geneweb-api.fly.dev/health

### Standards & Quality Processes
- **Documentation Standards**: Markdown with consistent formatting
- **Coding Conventions**:
  - Python: PEP 8, Black formatting, type hints
  - TypeScript: Angular style guide, ESLint
- **Commit Messages**: Conventional commits (feat, fix, docs, etc.)
- **Activity Reporting**: GitHub Projects and issue tracking
- **Accessibility**: WCAG 2.1 AA compliance

### Technical Communication
- **Deployment Guides**: Step-by-step installation instructions
- **API Documentation**: Comprehensive endpoint documentation
- **Troubleshooting**: Common issues and solutions
- **Best Practices**: Security and performance guidelines

### Stakeholder Communication
- **Sales Department**: Product capabilities and benefits
- **Marketing Team**: Feature highlights and use cases
- **Operations**: Deployment and maintenance procedures
- **Management**: Progress reports and milestones

---

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Setup** pre-commit hooks (`make dev-setup` for backend)
4. **Implement** changes following TDD methodology
5. **Test** your changes (`pytest` for backend, `npm test` for frontend)
6. **Commit** with conventional commits (`git commit -m 'feat: add amazing feature'`)
7. **Push** to your fork (`git push origin feature/amazing-feature`)
8. **Submit** a pull request

### Code Style

**Backend (Python)**
- Follow PEP 8 guidelines
- Use Black for formatting (`make format`)
- Sort imports with isort (`isort src tests`)
- Add type hints (checked by mypy)
- Write docstrings (Google style)
- Minimum 80% test coverage

**Frontend (TypeScript/Angular)**
- Follow Angular style guide
- Use ESLint for linting
- Write unit tests for components
- Use Cypress for E2E tests
- Follow component-based architecture

### Quality Gates
- ✅ All tests must pass (`pytest` + `npm test`)
- ✅ Code coverage > 80%
- ✅ No linting errors (`make lint` + `npm run lint`)
- ✅ Security scan approval (pre-commit hooks)
- ✅ Documentation updates (README, docs/)
- ✅ Peer review approval (1 reviewers minimum)
- ✅ Pre-commit hooks pass automatically

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality:
```bash
# Backend - runs automatically on commit
- YAML validation
- Large file detection
- Merge conflict detection
- Black formatting
- isort import sorting
- flake8 linting
- pytest test suite
```

### Branching Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

---

## 📞 Support

### Getting Help

#### Documentation
- 📖 [Complete Documentation](./docs/) - All guides and references
- 🔐 [Authentication Guide](./geneweb_python/docs/AUTHENTICATION_GUIDE.md) - Auth implementation
- 🚀 [Deployment Guide](./docs/DEPLOYMENT.md) - Deployment instructions
- 🐛 [Troubleshooting](./docs/DEPLOYMENT.md#dépannage) - Common issues

#### Live Resources
- **API Docs**: https://geneweb-api.fly.dev/docs
- **Health Check**: https://geneweb-api.fly.dev/health
- **Production App**: https://geneweb.surge.sh

#### Contact & Issues
- **GitHub Issues**: Report bugs and feature requests
- **Pull Requests**: Contribute improvements
- **Discussions**: Ask questions and share ideas

### Project Information
- **Organization**: CoinLegacy Inc.
- **Repository**: EpitechPGE45-2025/G-ING-900-PAR-9-1-legacy-22
- **License**: Legacy Project License
- **Development Period**: 2024-2025 (Restoration)
- **Original Project**: 1995-2008 (OCaml)

---

## 📊 Project Status

### Current Version
- **Backend API**: v0.1.0
- **Frontend App**: v0.0.0 (Angular 17.2.0)
- **Test Coverage**: 75% (Backend)
- **Total Tests**: 280+ (Backend) + E2E (Frontend)

### Technology Stack

**Backend**
- Python 3.11+
- FastAPI 0.109+
- SQLAlchemy 2.0+
- Pydantic v2
- pytest + coverage
- JWT Authentication
- Bcrypt password hashing

**Frontend**
- Angular 17.2.0
- TypeScript 5.3
- Tailwind CSS 3.4
- RxJS 7.8
- Cypress E2E testing
- Angular Universal SSR

**DevOps & Deployment**
- GitHub Actions (CI/CD)
- Fly.io (Backend hosting)
- Surge.sh (Frontend hosting)
- Docker (Backend containerization)
- Pre-commit hooks (Quality checks)

### Roadmap
- ✅ Core genealogical models
- ✅ JWT Authentication system
- ✅ RESTful API implementation
- ✅ Angular frontend with SSR
- ✅ Multi-language support
- ✅ Production deployment
- 🚧 Advanced search features
- 🚧 Relationship visualization
- 🚧 Export/Import enhancements
- 📋 Mobile application

### Defense Schedule
**Project Defense**: October 20-24, 2025
- Test policy presentation
- Standards and quality processes review
- Technical deployment demonstration
- Documentation walkthrough

---

**⚠️ CRITICAL WARNING**: This is a piece of history. Unauthorized modification or destruction of core functionality is strictly prohibited and will result in immediate termination.

---

## 🔄 Project Status

- ✅ Legacy code acquisition
- ✅ Initial assessment
- 🔄 Modernization in progress
- ⏳ Quality assurance implementation
- ⏳ Security hardening
- ✅ Deployment preparation
- ⏳ Documentation completion

---

*"With this program, we could uncover the rightful heirs of powerful lineages — and pocket a small fee for our efforts."*

**Stay vigilant. Stay sharp. Preserve the legacy.**

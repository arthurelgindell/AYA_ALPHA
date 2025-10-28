# GEMINI Analysis of the AYA Project

## Project Overview

This directory contains the **AYA AI Orchestration & Execution Platform**. It is a sophisticated system designed for managing and automating complex AI workflows.

The core components of the AYA platform are:

*   **Agent Turbo**: A multi-agent orchestration system for task planning, delegation, and auditing.
*   **PostgreSQL Backend (`aya_rag`)**: A centralized database for state management, audit trails, and knowledge storage.
*   **Self-Hosted GitHub Actions Runners**: The platform uses dedicated Mac Studio M3 Ultra machines (named ALPHA and BETA) for CI/CD and task execution.
*   **GLADIATOR**: A significant sub-project focused on building a "weapon-as-a-service" cyber defense platform using adversarial training techniques.

The system is designed with a clear separation of concerns, using different directories for the core agent system, specific projects, infrastructure automation, and data storage.

## Building and Running

The primary way to interact with the AYA platform is through its scripts and command-line tools.

### Prerequisites

*   macOS Sequoia 15.0+ (ARM64)
*   PostgreSQL 18+
*   Docker Desktop
*   GitHub account with repository access

### Initial Setup

To get started with the AYA platform, follow these steps:

```bash
# Clone the repository
git clone git@github.com:arthurelgindell/AYA.git
cd AYA

# Initialize Agent Turbo
cd Agent_Turbo/core
python3 agent_launcher.py

# Connect to the database
psql aya_rag
```

### Running Workflows

Workflows are primarily managed through GitHub Actions. You can trigger and monitor them from the project's [GitHub Actions page](https://github.com/arthurelgindell/AYA/actions).

Key workflows include:

*   **GLADIATOR Reality Check**: Validates the training approach for the GLADIATOR project.
*   **Runner Smoke Test**: Verifies the health and connectivity of the self-hosted runners.

## Development Conventions

*   **Branching**: Development follows a feature-branch workflow. Create a new branch for each feature, make changes, and then open a pull request for review.
*   **Code Style**: While not explicitly defined in the initial analysis, the presence of Python, SQL, and shell scripts suggests that standard best practices for each language should be followed.
*   **Testing**: The project uses smoke tests for its infrastructure (runners) and seems to have a validation process ("Reality Check") for its AI models.

## Key Directories

*   `Agent_Turbo/`: Contains the core multi-agent orchestration system.
*   `projects/GLADIATOR/`: The main cyber defense project, with its own documentation, scripts, and configurations.
*   `.github/workflows/`: Defines the CI/CD and automation pipelines using GitHub Actions.
*   `Databases/`: Holds knowledge bases and data for the AI agents.
*   `models/`: Stores local LLM models used by the platform.
*   `services/`: Contains supporting services for the platform.
*   `scripts/`: A variety of helper and automation scripts.
*   `archive_legacy_docs/`: Contains historical documentation for the project.

# Installation Guide

Follow these steps to set up the MCP Experto Filesystem server on your machine.

## Prerequisites

- **Python:** 3.12 or higher.
- **System:** Linux (preferred) or macOS.
- **Docker:** Required for local telemetry features.

## Automatic Installation

The project includes an installation script to automate the setup process:

```bash
bash install/install-mcp-experto-filesystem.sh
```

## Manual Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd mcp-experto-filesystem
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

## Configuration

The server can be configured via environment variables or a `.env` file. See the `src/server/config.py` for available options.

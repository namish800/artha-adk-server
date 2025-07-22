# Artha Agent

A FastAPI-based agent application using Google Cloud AI Platform and Agent Development Kit (ADK).

## Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account with appropriate permissions
- Git

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd artha-agent
```

### 2. Create and activate a virtual environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

The application uses centralized configuration via the `settings.py` file. All settings can be overridden using environment variables or a `.env` file.

Create a `.env` file in the root directory and configure your environment variables. Copy from `.env.example`

All settings have sensible defaults, so you only need to set the variables you want to override.

## Running the Server

To start the server, run:

```bash
python -m server
```

The server will start and be available at the configured host and port.

## Project Structure

```
artha-agent/
├── fi_mcp_agent/          # Main agent package
│   ├── agent.py           # Agent implementation
│   └── utils/             # Utility modules
├── requirements.txt       # Python dependencies
├── server.py             # FastAPI server entry point
├── settings.py           # Centralized configuration
└── README.md             # This file
```

## Development

Make sure your virtual environment is activated before working on the project:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Install any new dependencies and update `requirements.txt` as needed. 
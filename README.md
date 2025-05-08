# AI TechSpec Reviewer

A web-based application that allows users to upload technical specification documents, have an AI review and annotate them, and download annotated versions.

## Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Running with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd techSpecReviewer
```

2. Create and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

3. Build and run the application:
```bash
docker-compose up --build
```

The application will be available at http://localhost:8501

### Development with Docker

For development, you can use the following commands:

```bash
# Start the application
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Rebuild the application
docker-compose up --build
```

## Manual Setup

### Prerequisites
- Python 3.9+
- pip

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

4. Run the application:
```bash
streamlit run app/main.py
```

## Features

- Upload technical specification documents (PDF, DOCX, TXT)
- AI-powered document review and annotation
- Interactive document viewer
- Download annotated documents
- Modern, responsive UI

## Project Structure 
# Installation Guide

## Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning repository)

## Installation Methods

### Method 1: Git Clone

```bash
git clone https://github.com/WalkingDreams798/inf3rno.git
cd inf3rno
pip install -r requirements.txt
```

### Method 2: Direct Download

1. Download the latest release from GitHub
2. Extract the archive
3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Method 3: pip install

```bash
git clone https://github.com/WalkingDreams798/inf3rno.git
cd inf3rno
pip install -e .
```

### Method 4: Installer Script

```bash
git clone https://github.com/WalkingDreams798/inf3rno.git
cd inf3rno
chmod +x install.sh
./install.sh
```

### Method 5: Docker

```bash
git clone https://github.com/WalkingDreams798/inf3rno.git
cd inf3rno
docker build -t inf3rno .
docker run --rm inf3rno --help
```

## Verification

After installation, verify it works:

```bash
python3 inf3rno/cli.py --help
```

Or if installed via pip:

```bash
inf3rno --help
```

## Troubleshooting

### Permission Error

If you get a permission error, use `--break-system-packages`:

```bash
pip install --break-system-packages -r requirements.txt
```

Or use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Missing Dependencies

If you get import errors, install all dependencies:

```bash
pip install paramiko requests rich colorama tqdm pymysql pysocks psycopg2-binary fastapi uvicorn pydantic
```

### Python Version Error

Ensure you have Python 3.8+:

```bash
python3 --version
```

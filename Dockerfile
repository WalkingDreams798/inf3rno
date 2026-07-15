FROM python:3.12-slim

LABEL maintainer="WalkingDreams798"
LABEL description="Inf3rno - Multi-Protocol Brute-Force Tool"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x inf3rno-cli
RUN chmod +x install.sh

# Install the package
RUN pip install --no-cache-dir -e .

# Create output directory
RUN mkdir -p output

# Default entrypoint
ENTRYPOINT ["python3", "inf3rno/cli.py"]

# Default command (show help)
CMD ["--help"]

# Stage 1: Build stage
FROM python:3.10-alpine AS builder

# Install build dependencies
RUN apk add --no-cache build-base cargo

# Set working directory
WORKDIR /app

# Copy necessary files
COPY pyproject.toml requirements.lock requirements-dev.lock /app/

# Copy the README files
COPY README.md README_JA.md /app/

# Copy src directory
COPY src /app/src

# Install dependencies
RUN pip install --no-cache-dir -r requirements.lock

# Install additional dev dependencies
RUN pip install --no-cache-dir -r requirements-dev.lock


# Stage 2: Production stage
FROM python:3.10-alpine

# Set working directory
WORKDIR /app

# Copy the dependencies from the build stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the source code
COPY src /app/src

# Copy other necessary files
COPY .python-version .gitignore LICENSE README.md README_JA.md /app/

# Run the application
CMD ["python", "/app/src/paramit/cli/__init__.py"]

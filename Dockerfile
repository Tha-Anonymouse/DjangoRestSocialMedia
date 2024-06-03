# Use the official Python image from the Docker Hub for building dependencies
FROM python:3.9-slim as builder

# Set environment variable to ensure that the Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the Docker container
WORKDIR /social_network
# Copy the requirements.txt file into the container at /social_network/
COPY requirements.txt /social_network/
# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && pip install --user -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# Copy the entire social_network directory into the container at /social_network/
COPY /social_network /social_network/
# Copy the wait-for-it.sh script into the root directory of the container
COPY wait-for-it.sh /wait-for-it.sh
COPY start.sh /start.sh
# Make the wait-for-it.sh script executable
RUN chmod +x /wait-for-it.sh
RUN chmod +x /start.sh

# Final stage to create a lightweight image
FROM python:3.9-slim
# Set environment variable to ensure that the Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED=1
# Set the working directory inside the Docker container
WORKDIR /social_network
# Copy only the necessary files from the builder stage
COPY --from=builder /root/.local /root/.local
COPY --from=builder /social_network /social_network
COPY --from=builder /wait-for-it.sh /wait-for-it.sh
COPY --from=builder /start.sh /start.sh
# Ensure the local binaries are in PATH
ENV PATH=/root/.local/bin:$PATH


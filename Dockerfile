# Base image
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files to the container
COPY . .

# Expose the port the bot will listen to
EXPOSE 8443

# Run the bot when the container starts
CMD ["python", "src/app.py"]

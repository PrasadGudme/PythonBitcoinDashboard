# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /code

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files to the container
COPY . .

# Expose port 8000 for the Django app
EXPOSE 8000

# Default command to run the server
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "bitcoin_dashboard.asgi:application"]

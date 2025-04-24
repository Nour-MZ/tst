# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy project files into the container
COPY . .

RUN pip install -r requirements.txt

# Expose the port your app runs on
EXPOSE 3003

# Start the Flask app
CMD ["python", "cv_job.py"]

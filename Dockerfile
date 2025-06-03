# Use the official Python image as a base image
FROM python:3.12


# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install the required dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code into the container
COPY . /app/

# Expose port 8000 for FastAPI app (default Uvicorn port)
EXPOSE 8000

# Command to run the FastAPI app with Uvicorn
CMD ["python","main.py"]

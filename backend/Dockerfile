FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory to the container's working directory
COPY . .

# Install dependencies from the requirements file without using cache to reduce image size
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install --no-cache-dir gunicorn
RUN pip install joblib


# Option B: Or explicitly expose the venv bin path in $PATH
ENV PATH="/app/.venv/bin:$PATH"
# Define the command to start the application using Gunicorn with 4 worker processes
# - `-w 4`: Uses 4 worker processes for handling requests
# - `-b 0.0.0.0:7860`: Binds the server to port 7086 on all network interfaces
# - `app:superkart_api`: Runs the Flask app (Flask app instance is named `superkart_api` inside app.py)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]

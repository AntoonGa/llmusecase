# Dockerfile to build python image for CI environment.
# This image does not contain the project code, only the python env and tools requiered
# to run the project remotly.

# Use the Python 3.11 image as base. "slim" is a smaller image.
FROM python:3.11-slim

# set the working directory in the container
WORKDIR /code

# Copy the requirements files into the container. Both files are requiered.
COPY requirements.txt .
COPY requirements_dev.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install -r requirements_dev.txt

# Expose ports
EXPOSE 8080

# Specify the command to run on container start
CMD ["python3", "--version"]

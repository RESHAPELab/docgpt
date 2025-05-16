# Use an official Python image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set up the working directory
WORKDIR /app
ENV PYTHONPATH="/app"

# Copy project files
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the entire application
COPY config.yml main.py ./
COPY src ./src

# Run the application
ENTRYPOINT ["poetry", "run", "python", "main.py"]

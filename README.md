# My Data Transformation Project

A Python project performing data transformations using Pandas and NumPy, structured with industry-standard practices and a CI/CD pipeline using GitHub Actions.

## Features

-   Data transformation script in `src/main.py`.
-   Dependency management with `pyproject.toml`.
-   Linting and formatting with Ruff.
-   Static type checking with Mypy.
-   Security scanning with Bandit and Safety.
-   Unit testing with Pytest and code coverage.
-   Pre-commit hooks for local quality checks.
-   Automated CI/CD pipeline deploying and running the script on AWS EC2.

## Local Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd my_python_project
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies (including development tools):**
    The `-e .` part installs your project (`src/main.py` as the `main` module) in "editable" mode. `[dev]` installs all the tools listed under `optional-dependencies.dev` in `pyproject.toml`.
    ```bash
    pip install -e .[dev]
    ```

4.  **Install pre-commit hooks:**
    This enables the checks defined in `.pre-commit-config.yaml` to run before each `git commit`.
    ```bash
    pre-commit install
    ```

## Running the Script Locally

To execute the data transformation script:
```bash
python src/main.py

# veloxdf

`veloxdf` is a lightweight, modern Python project demonstrating the core components of a simple DataFrame library, including a parser, an abstract syntax tree (AST), and a rule-based optimizer. This project is built using `poetry` for dependency management and is compatible with Python 3.7.

## Features

-   A simple, fluent DataFrame API (`.filter()`, `.map()`).
-   SQL expression parsing using `sqlglot`.
-   A well-defined, immutable AST for expressions and logical plans.
-   An extensible, rule-based optimizer (RBO) with a `FilterPushdownRule` example.
-   Modern Python project structure with testing and code formatting.

## Getting Started

Follow these instructions to set up and run the project in a new environment.

### 1. Prerequisites

-   **Git**: For cloning the repository.
-   **Python 3.7**: You must have a Python 3.7 interpreter installed and accessible via the `python3.7` command in your terminal.
-   **curl**: For downloading the Poetry installation script.

### 2. Install a Python 3.7-Compatible Version of Poetry

The latest versions of Poetry are not compatible with Python 3.7. We must install a specific, compatible version, such as **Poetry 1.5.1**, using the official installation script.

**Run the following command in your terminal:**

```bash
curl -sSL https://install.python-poetry.org | python3.7 - --version 1.5.1
git clone git@github.com:duanmeng/veloxdf.git
cd veloxdf
poetry install
poetry run pytest -v
poetry run python main.py
```

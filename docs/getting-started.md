# Getting Started

Welcome to the Agentic Graph RAG project! This guide will walk you through
setting up your environment, configuring the application, and running the
end-to-end demo.

## Prerequisites

Before you begin, please ensure that you have the following installed:

- **Python 3.11+**
- **Git**
- **A Snowflake account**
- **A Neo4j database**
- **An OpenAI API key**

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/harshit-codes/lyzr-hackathon.git
    cd lyzr-hackathon
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application is configured using environment variables. To get started,
copy the `.env.example` file to a new file named `.env`:

```bash
cp .env.example .env
```

Now, open the `.env` file and fill in the following values:

| Variable                | Description                                      |
| ----------------------- | ------------------------------------------------ |
| `SNOWFLAKE_USER`        | Your Snowflake username.                         |
| `SNOWFLAKE_PASSWORD`    | Your Snowflake password.                         |
| `SNOWFLAKE_ACCOUNT`     | Your Snowflake account identifier.               |
| `SNOWFLAKE_WAREHOUSE`   | The Snowflake warehouse to use.                  |
| `SNOWFLAKE_DATABASE`    | The Snowflake database to use.                   |
| `SNOWFLAKE_SCHEMA`      | The Snowflake schema to use.                     |
| `NEO4J_URI`             | The connection URI for your Neo4j database.      |
| `NEO4J_USER`            | The username for your Neo4j database.            |
| `NEO4J_PASSWORD`        | The password for your Neo4j database.            |
| `OPENAI_API_KEY`        | Your OpenAI API key.                             |

> **Note:** For more information on setting up your Snowflake and Neo4j
> databases, please see the [**Database Setup**](database-setup.md) guide.

## Initialize the Database

Once you have configured your environment variables, you need to initialize
the database by running the following script:

```bash
python code/scripts/setup_snowflake.py
```

This will create all the necessary tables in your Snowflake database.

## Running the Demo

The project includes a Streamlit application that provides an interactive
demo of the end-to-end workflow. To run the demo, execute the following
command:

```bash
streamlit run code/streamlit_app.py
```

This will start the Streamlit application in your web browser. You can then
use the UI to:

-   Upload a PDF document.
-   Generate a schema proposal using SuperScan.
-   Build a knowledge base using SuperKB.
-   Ask questions to the SuperChat conversational AI.

## Next Steps

Now that you have the project up and running, here are a few things you can
do next:

-   **Explore the code:** Take a look at the different components of the
    system and how they interact with each other.
-   **Run the tests:** Run the test suite to ensure that everything is
    working as expected.
-   **Contribute to the project:** We welcome contributions! Please see our
    [**Contributing Guide**](contributing.md) for more information.
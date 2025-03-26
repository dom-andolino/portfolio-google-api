# Portfolio - Google API

This portfolio project explores the capabilities of the [Google Knowledge Graph API](https://developers.google.com/knowledge-graph) and implements an ELT process revolving around Persons of Influence (POI) data.

## Project Overview

The primary objective of this project is to:

- **Extract Data:** Utilize the Google Knowledge Graph API to fetch raw information about notable figures.
- **Load Data:** Use python to load the data into [DuckDB](https://duckdb.org/) (a free and portable DB solution, perfect for these kind of projects).
- **Transform Data:** Leverage [DBT-core](https://docs.getdbt.com/docs/core/installation-overview) to tranform the raw data into more fucntional tables.
- **Visualize Data:** (Work In Progress) Create a [Streamlit](https://streamlit.io/) app to present the findings through clear and informative visualizations.

## Repository Structure

- **data/**: Contains raw dataset obtained from the API and the DuckDB.
- **person_of_influence/**: DBT project folder.
    - scripts/: Python script to fetch raw API data.
    - models/: DBT SQL tranformations.
- **.github/workflows/**: YAML file defining the GitHub Actions automated workflow.
- **logs/**: Stores logs generated during data retrieval and processing.
- **scratchpad.ipynb**: Jupyter Notebook used for experimentation and preliminary analyses.


## Getting Started

To set up the project locally:

1. Clone the Repository:
   ```bash
   git clone https://github.com/dom-andolino/portfolio-google-api.git
2. Create a free [Google Cloud Console](https://console.cloud.google.com/) account.
    - Under "APIs & Services" enable the "Knowledge Graph Search API".
    - Under "APIs & Services" > "Credentials", create an "API Key".
3. Create a [GitHub Personal Access Token](https://github.com/settings/personal-access-tokens)
    - "Settings" > "Developer Settings" > "Personal Access Tokens" > "Fine Grained Tokens"
4. Configure Enviornment Variables
    - On GitHub, these will be entered in your repo settings under "Secrets and variables" > "Repository Secrets".
    - On Windows, these will be entered in your user enviornment variables. 
    - name = GOOGLE_API_KEY; value = API Key created from above
    - name = GH_ACTION_TOKEN; value = token created from above
5. Setup Python
    - Download and install python 3.13 [here](https://www.python.org/downloads/).
    - Create and activate a virtual environment
        ```bash 
        python -m venv .venv
        .venv\Scripts\activate
    - Upgrade pip
        ```bash
        python -m pip install --upgrade pip
    - Install python dependencies using the included requirements.txt
        ```bash
        pip install -r requirements.txt
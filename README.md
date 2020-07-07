# Gitlab tools


## Setup

    python3 -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt


## Collect comments in merge requests:

    python collect-comments.py <gitlab url> <project name> <access token>
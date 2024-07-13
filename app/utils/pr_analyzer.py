import os
import requests
import logging
import dotenv

dotenv.load_dotenv()
logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO
logger = logging.getLogger(__name__)

GIT_API_ADDRESS = "https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
DEFAULT_PR_URL= os.environ.get("DEFAULT_PR_URL", "")
PRODUCTION_MODE=os.environ.get("PRODUCTION_MODE",False)

def get_data(git_pr_url: str = DEFAULT_PR_URL) -> tuple[list, list]:
    """Get the added and removed lines from a GitHub PR URL through the GitHub API
    
    returns:
        tuple[list, list]: The added and removed lines
    """
    logger.info(f"Getting data from {git_pr_url}")
    headers = {
        "Accept": "application/vnd.github.diff+json", # This header is required to get the diff data
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "git-pr-data",
    }
    # Extract owener, repo and pull_number from the URL
    owner, repo, _, pull_number = git_pr_url.split("/")[-4:]
    logger.error(GIT_API_ADDRESS.format(owner=owner, repo=repo, pull_number=pull_number))
    if PRODUCTION_MODE:
        response = requests.get(GIT_API_ADDRESS.format(owner=owner, repo=repo, pull_number=pull_number), headers=headers)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        with open("diff.txt", "w") as f:
            f.write(response.text)
    else:
        class Response:
            def __init__(self):
                self.text = ""
        with open("diff.txt", "r") as f:
            response = Response()
            response.text = f.read()
    diff = response.text
    logger.info(f"Diff data: {diff}")
    lines = diff.split("\n") # Split the diff data into lines
    # We have to identify the added and removed lines
    # Plus we need the context (the unchanged lines)
    added_lines = [line for line in lines if line.startswith("+")] # Lines that start with "+"
    removed_lines = [line for line in lines if line.startswith("-")] # Lines that start with "-"
    return added_lines, removed_lines
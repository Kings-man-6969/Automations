import os
import random
import re
import requests

def get_slug_from_filename(filename):
    """
    Convert filename like '199-BinaryTreeRightSideView.cpp' 
    to slug like 'binary-tree-right-side-view'
    """
    match = re.match(r"^\d+-(.+)\.(cpp|py|java|.*)$", filename)
    if not match:
        return None
    raw_title = match.group(1)
    # Insert hyphen before uppercase letters preceded by lowercase letters, then lowercase all
    slug = re.sub(r"([a-z])([A-Z])", r"\1-\2", raw_title).lower()
    # Replace underscores or spaces with hyphens, just in case
    slug = slug.replace("_", "-").replace(" ", "-")
    return slug

def get_random_solution_file(root="leetcode-solutions"):
    cpp_files = []
    for dirpath, _, filenames in os.walk(root):
        for file in filenames:
            if file.endswith(".cpp"):
                cpp_files.append(os.path.join(dirpath, file))
    if not cpp_files:
        raise Exception(f"No .cpp files found in {root}")
    return random.choice(cpp_files)

def submit_solution(session_token, csrf_token, slug, code, language="cpp"):
    url = "https://leetcode.com/graphql/"

    headers = {
        "Content-Type": "application/json",
        "Cookie": f"LEETCODE_SESSION={session_token}; csrftoken={csrf_token}",
        "x-csrftoken": csrf_token,
        "Referer": f"https://leetcode.com/problems/{slug}/",
        "User-Agent": "Mozilla/5.0"
    }

    graphql_query = {
        "operationName": "submitSolution",
        "variables": {
            "input": {
                "questionSlug": slug,
                "language": language,
                "typedCode": code
            }
        },
        "query": """
        mutation submitSolution($input: SubmitSolutionInput!) {
          submitSolution(input: $input) {
            submission {
              id
              status {
                id
                status
                __typename
              }
              __typename
            }
            __typename
          }
        }
        """
    }

    response = requests.post(url, json=graphql_query, headers=headers)
    data = response.json()

    if response.status_code == 200 and "errors" not in data:
        submission_status = data["data"]["submitSolution"]["submission"]["status"]["status"]
        print(f"✅ Submitted '{slug}' with status: {submission_status}")
        return submission_status
    else:
        print("❌ Submission failed:", data)
        return None


if __name__ == "__main__":
    LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
    CSRFTOKEN = os.getenv("CSRFTOKEN")
    ROOT_DIR = "leetcode-solutions"  # Your solutions folder

    if not LEETCODE_SESSION or not CSRFTOKEN:
        raise Exception("Set LEETCODE_SESSION and CSRFTOKEN environment variables.")

    file_path = get_random_solution_file(ROOT_DIR)
    filename = os.path.basename(file_path)
    slug = get_slug_from_filename(filename)

    if not slug:
        raise Exception(f"Filename '{filename}' does not match expected format.")

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    submit_solution(LEETCODE_SESSION, CSRFTOKEN, slug, code)

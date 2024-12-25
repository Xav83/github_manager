import argparse
import sys

from gh_cli_adapter import GhCliAdapter

EXPECTED_LABELS_INFO = [
    {"name":"bug", "color":"d73a4a", "description": "Something isn't working"},
    {"name":"dependencies", "color":"006b75", "description": "Updates ar least one external dependency"},
    {"name":"documentation", "color":"0075ca", "description": "Improvements or additions to documentation"},
    {"name":"duplicate", "color":"cfd3d7", "description": "This issue or pull request already exists"},
    {"name":"enhancement", "color":"a2eeef", "description": "New feature or request"},
    {"name":"good first issue", "color":"7057ff", "description": "Good for newcomers"},
    {"name":"help wanted", "color":"008672", "description": "Extra attention is needed"},
    {"name":"invalid", "color":"e4e669", "description": "This doesn't seem right"},
    {"name":"python", "color":"2b67c6", "description": "This issue or pull request is related to Python code"},
    {"name":"question", "color":"d876e3", "description": "Further information is requested"},
    {"name":"wontfix", "color":"ffffff", "description": "This will not be worked on"},
]

def get_label_info_in_list(label_name, label_list):
    matching_labels = list(filter(lambda label, label_name=label_name: label_name == label["name"], label_list))
    if len(matching_labels) == 1:
        return matching_labels[-1]
    elif len(matching_labels) == 0:
        return {}
    else:
        print(f"Error: several matching labels for the label '{label_name}' in {label_list}: {matching_labels}")
        sys.exit(1)

def is_label_in_list(label_name, label_list):
    return bool(get_label_info_in_list(label_name, label_list))


parser = argparse.ArgumentParser()
parser.add_argument("--owner", required=True)

args = parser.parse_args()

repos_list = GhCliAdapter.get_repos_list(args.owner)
for repo in repos_list:
    print(f"Analysing the repo {repo['name']}...")
    repo_labels_info = GhCliAdapter.get_labels_info_of(args.owner, repo["name"])
    for repo_label in repo_labels_info:
        if not is_label_in_list(repo_label["name"], EXPECTED_LABELS_INFO):
            print("🤔 Should we add the following label in the 'EXPECTED_LABELS_INFO' ?")
            print(repo_label)
            continue
        matching_label_info_expected = get_label_info_in_list(repo_label["name"], EXPECTED_LABELS_INFO) 
        if matching_label_info_expected["color"] != repo_label["color"]:
            print(f"🛠 Fixing the color of the label '{repo_label['name']}' in the repo {repo['name']}")
            GhCliAdapter.set_label_color(args.owner, repo["name"], repo_label["name"], matching_label_info_expected["color"])
        if matching_label_info_expected["description"] != repo_label["description"]:
            print(f"🛠 Fixing the description of the label '{repo_label['name']}' in the repo {repo['name']}")
            GhCliAdapter.set_label_description(args.owner, repo["name"], repo_label["name"], matching_label_info_expected["description"])

    for expected_label_info in EXPECTED_LABELS_INFO:
        if not is_label_in_list(expected_label_info["name"], repo_labels_info):
            print(f"🛠 Adding the label '{expected_label_info['name']}' in the repo {repo['name']}")
            GhCliAdapter.add_label(args.owner, repo["name"], expected_label_info)


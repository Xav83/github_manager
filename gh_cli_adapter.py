import json
import os
import shlex
import subprocess  # nosec B404
import time


class GhCliAdapter:
    @staticmethod
    def get_rate_limit_info():
        cmd = "gh api rate_limit"
        return json.loads(
            subprocess.run(  # nosec B603
                shlex.split(cmd), capture_output=True, text=True, check=True
            ).stdout
        )

    @staticmethod
    def get_remaining_code_search():
        rate_limit = GhCliAdapter.get_rate_limit_info()
        return rate_limit["resources"]["code_search"]["remaining"]

    @staticmethod
    def get_max_code_search():
        rate_limit = GhCliAdapter.get_rate_limit_info()
        return rate_limit["resources"]["code_search"]["limit"]

    @staticmethod
    def search_code(
        code_to_search, owner, repository=None, matching_filename=True, filename=None
    ):
        if GhCliAdapter.get_remaining_code_search() <= 1:
            while (
                GhCliAdapter.get_remaining_code_search()
                != GhCliAdapter.get_max_code_search()
            ):
                time.sleep(1)
        cmd = f"gh search code {code_to_search} {f'--repo {owner}/{repository}' if repository is not None else f'--owner {owner}'} {f'--filename {filename}' if filename is not None else ''} --match {'path' if matching_filename else 'file'} --json path,repository,textMatches --limit 999"
        return json.loads(
            subprocess.run(  # nosec B603
                shlex.split(cmd), capture_output=True, text=True, check=True
            ).stdout
        )

    @staticmethod
    def search_prs(repository_owner, branch_name, pr_state="open"):
        if GhCliAdapter.get_remaining_code_search() <= 1:
            while (
                GhCliAdapter.get_remaining_code_search()
                != GhCliAdapter.get_max_code_search()
            ):
                time.sleep(1)
        cmd = f"gh search prs --owner {repository_owner} --state {pr_state} --head {branch_name} --archived=false --json number,repository --limit 999"
        return json.loads(
            subprocess.run(  # nosec B603
                shlex.split(cmd), capture_output=True, text=True, check=True
            ).stdout
        )

    @staticmethod
    def search_prs_from(repository_owner, author, pr_state="open"):
        if GhCliAdapter.get_remaining_code_search() <= 1:
            while (
                GhCliAdapter.get_remaining_code_search()
                != GhCliAdapter.get_max_code_search()
            ):
                time.sleep(1)
        cmd = f"gh search prs --owner {repository_owner} --state {pr_state} --author {author} --archived=false --json number,repository --limit 999"
        return json.loads(
            subprocess.run(  # nosec B603
                shlex.split(cmd), capture_output=True, text=True, check=True
            ).stdout
        )

    @staticmethod
    def pr_new_comment(pull_request_number_or_branch, owner, repository, comment_message):
        cmd = f"gh pr comment {pull_request_number_or_branch} -b '{comment_message}' -R {owner}/{repository}"
        subprocess.run(shlex.split(cmd), check=True)  # nosec B603

    @staticmethod
    def pr_approve(pull_request_number, owner, repository):
        cmd = (
            f"gh pr review {pull_request_number} --approve --repo {owner}/{repository}"
        )
        subprocess.run(shlex.split(cmd), check=True)  # nosec B603

    @staticmethod
    def pr_merge(pull_request_number, owner, repository):
        cmd = f"gh pr merge {pull_request_number} --merge --delete-branch --repo {owner}/{repository}"
        subprocess.run(shlex.split(cmd), check=True)  # nosec B603

    @staticmethod
    def pr_view(pull_request_number_or_branch, owner, repository):
        cmd = f"gh pr view {pull_request_number_or_branch} --json author,baseRefName,comments,commits,headRefName,headRepository,mergeable,mergeStateStatus,number,reviewDecision,reviews,state,statusCheckRollup,url -R {owner}/{repository}"
        return json.loads(
            subprocess.run(  # nosec B603
                shlex.split(cmd), capture_output=True, text=True, check=True
            ).stdout
        )

    @staticmethod
    def pr_rebase(pull_request_number, owner, repository):
        cmd = f"gh pr update-branch {pull_request_number} --rebase -R {owner}/{repository}"
        subprocess.run(shlex.split(cmd), check=True)  # nosec B603

    @staticmethod
    def pr_checkout(pull_request_number, repository_location):
        if not os.path.exists(repository_location):
            raise OSError(f"No git repository found in {repository_location}")
        cmd = f"gh pr checkout {pull_request_number}"
        subprocess.run(  # nosec B603
            shlex.split(cmd),
            cwd=repository_location,
            stdout=subprocess.DEVNULL,
            check=True,
        )

    @staticmethod
    def pr_create(repository_location, pull_request_title, pull_request_description):
        if not os.path.exists(repository_location):
            raise OSError(f"No git repository found in {repository_location}")
        cmd = f"gh pr create --title \"{pull_request_title}\" --body \"{pull_request_description}\""
        return subprocess.run(  # nosec B603
            shlex.split(cmd),
            cwd=repository_location,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()[-1]

    @staticmethod
    def repo_clone(owner, repository):
        if os.path.exists(repository):
            raise OSError(f"Git repository ' {repository}' already existing.")
        cmd = f"gh repo clone {owner}/{repository}"
        subprocess.run(
            shlex.split(cmd), stdout=subprocess.DEVNULL, check=True
        )  # nosec B603

    @staticmethod
    def get_repos_list(owner):
        cmd = f"gh repo list {owner} --source --no-archived --limit 999 --json name"
        return json.loads(subprocess.run(  # nosec B603
                shlex.split(cmd),
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        )

    @staticmethod
    def get_labels_info_of(owner, repository):
        cmd = f"gh label list --repo {owner}/{repository} --json color,description,name"
        output = subprocess.run(  # nosec B603
                shlex.split(cmd),
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        if not output:
            return json.loads("[]")
        else:
            return json.loads(output)

    @staticmethod
    def set_label_color(owner, repository, label, new_color):
        cmd = f"gh label edit \"{label}\" --color {new_color} --repo {owner}/{repository}"
        subprocess.run(
            shlex.split(cmd), stdout=subprocess.DEVNULL, check=True
        )  # nosec B603

    @staticmethod
    def set_label_description(owner, repository, label, new_description):
        cmd = f"gh label edit \"{label}\" --description \"{new_description}\" --repo {owner}/{repository}"
        subprocess.run(
            shlex.split(cmd), stdout=subprocess.DEVNULL, check=True
        )  # nosec B603

    @staticmethod
    def add_label(owner, repository, label):
        cmd = f"gh label create \"{label['name']}\" --description \"{label['description']}\" --color {label['color']} --repo {owner}/{repository}"
        subprocess.run(
            shlex.split(cmd), stdout=subprocess.DEVNULL, check=True
        )  # nosec B603

    # https://github.com/mislav/gh-cp
    @staticmethod
    def download_file(owner, repository, file, file_destination="."):
        cmd = f"gh cp {owner}/{repository} {file} {file_destination}"
        subprocess.run(
            shlex.split(cmd), stdout=subprocess.DEVNULL, check=True
        )  # nosec B603

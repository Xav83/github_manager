import argparse

from gh_cli_adapter import GhCliAdapter

EXPECTED_CONFIGURATION = {
    "defaultBranchRef": {"name": "main"},
    "deleteBranchOnMerge": True,
    "hasDiscussionsEnabled": True,
    "hasIssuesEnabled": True,
    "hasProjectsEnabled": True,
    "hasWikiEnabled": True,
    "isBlankIssuesEnabled": True,
    "isEmpty": False,
    "isSecurityPolicyEnabled": False,
    "isUserConfigurationRepository": False,
    "mergeCommitAllowed": True,
    "rebaseMergeAllowed": False,
    "squashMergeAllowed": False,
}

parser = argparse.ArgumentParser()
parser.add_argument("--owner", required=True)

args = parser.parse_args()

repos_list = GhCliAdapter.get_repos_list(args.owner)
for repo in repos_list:
    print(f"Analysing the repo {repo['name']}...")
    repo_view = GhCliAdapter.repo_view(args.owner, repo["name"])
    if (
        EXPECTED_CONFIGURATION["deleteBranchOnMerge"]
        != repo_view["deleteBranchOnMerge"]
    ):
        print(f"🛠 Fixing the 'deleteBranchOnMerge' flag in the repo {repo['name']}")
        GhCliAdapter.repo_edit(
            args.owner,
            repo["name"],
            f"--delete-branch-on-merge={EXPECTED_CONFIGURATION['deleteBranchOnMerge']}",
        )
    if (
        EXPECTED_CONFIGURATION["hasDiscussionsEnabled"]
        != repo_view["hasDiscussionsEnabled"]
    ):
        print(f"🛠 Fixing the 'hasDiscussionsEnabled' flag in the repo {repo['name']}")
        GhCliAdapter.repo_edit(
            args.owner,
            repo["name"],
            f"--enable-discussions={EXPECTED_CONFIGURATION['hasDiscussionsEnabled']}",
        )
    if EXPECTED_CONFIGURATION["hasProjectsEnabled"] != repo_view["hasProjectsEnabled"]:
        print(f"🛠 Fixing the 'hasProjectsEnabled' flag in the repo {repo['name']}")
        GhCliAdapter.repo_edit(
            args.owner,
            repo["name"],
            f"--enable-projects={EXPECTED_CONFIGURATION['hasProjectsEnabled']}",
        )
    if EXPECTED_CONFIGURATION["mergeCommitAllowed"] != repo_view["mergeCommitAllowed"]:
        print(f"🛠 Fixing the 'mergeCommitAllowed' flag in the repo {repo['name']}")
        GhCliAdapter.repo_edit(
            args.owner,
            repo["name"],
            f"--enable-merge-commit={EXPECTED_CONFIGURATION['mergeCommitAllowed']}",
        )
    if EXPECTED_CONFIGURATION["rebaseMergeAllowed"] != repo_view["rebaseMergeAllowed"]:
        print(f"🛠 Fixing the 'rebaseMergeAllowed' flag in the repo {repo['name']}")
        GhCliAdapter.repo_edit(
            args.owner,
            repo["name"],
            f"--enable-rebase-merge={EXPECTED_CONFIGURATION['rebaseMergeAllowed']}",
        )
    if EXPECTED_CONFIGURATION["squashMergeAllowed"] != repo_view["squashMergeAllowed"]:
        print(f"🛠 Fixing the 'squashMergeAllowed' flag in the repo {repo['name']}")
        GhCliAdapter.repo_edit(
            args.owner,
            repo["name"],
            f"--enable-squash-merge={EXPECTED_CONFIGURATION['squashMergeAllowed']}",
        )

    if repo_view["issueTemplates"] == []:
        print(f"🚧 No Issue template found in {repo['name']}")
    if repo_view["pullRequestTemplates"] == []:
        print(f"🚧 No Pull Request template found in {repo['name']}")

    repo_view = GhCliAdapter.repo_view(args.owner, repo["name"])
    for repo_parameter_name in EXPECTED_CONFIGURATION:
        if (
            EXPECTED_CONFIGURATION[repo_parameter_name]
            != repo_view[repo_parameter_name]
        ):
            print(
                f"🚧 Mismatching parameter '{repo_parameter_name}' in {repo['name']}: {EXPECTED_CONFIGURATION[repo_parameter_name]} != {repo_view[repo_parameter_name]}"
            )

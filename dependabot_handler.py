import argparse

from gh_cli_adapter import GhCliAdapter

TOOLS_AUTO_APPROUVED = ["clang-format", "cmake", "conan", "ninja", "pytest"]


def get_dependabot_pr(owner):
    return GhCliAdapter.search_prs_from(owner, "app/dependabot")


def has_been_reviewed_by(pr_view, author):
    return bool(
        list(
            filter(
                lambda review, author=author: author == review["author"]["login"],
                pr_view["reviews"],
            )
        )
    )


def handling_pr_approbation(pr_view, owner, github_id):
    matching_tool = list(
        filter(
            lambda tool_name, pr_view=pr_view: pr_view["headRefName"].startswith(
                f"dependabot/pip/{tool_name}"
            ),
            TOOLS_AUTO_APPROUVED,
        )
    )
    if len(matching_tool) == 1:
        if not has_been_reviewed_by(pr_view, github_id):
            print(
                f"🤝 Approving the PR #{pr_view['number']} (`{matching_tool[0]}` update) of the repo {pr_view['headRepository']['name']}"
            )
            GhCliAdapter.pr_approve(pr_view["number"], owner, pr["repository"]["name"])
        else:
            print(
                f"🙌 The PR #{pr_view['number']} (`{matching_tool[0]}` update) of the repo {pr_view['headRepository']['name']} has already been approved by myself."
            )
    elif len(matching_tool) == 0:
        print(
            f"🤔 Should we auto-approuve the branch `{pr_view['headRefName']}` by the PR #{pr_view['number']} in the repo {pr_view['headRepository']['name']} ?"
        )


def has_running_checks(pr_view):
    return bool(
        list(
            filter(
                lambda check: check["status"] == "IN_PROGRESS"
                or check["status"] == "QUEUED",
                pr_view["statusCheckRollup"],
            )
        )
    )


parser = argparse.ArgumentParser()
parser.add_argument("--owner", required=True)
parser.add_argument("--github-id", required=True)
parser.add_argument("--with-azure", action="store_true")

args = parser.parse_args()

prs_list = get_dependabot_pr(args.owner)

for pr in prs_list:
    pr_view = GhCliAdapter.pr_view(pr["number"], args.owner, pr["repository"]["name"])
    if pr_view["mergeStateStatus"] == "BEHIND":
        print(
            f"🔄 Updating the PR #{pr_view['number']} of the repo {pr_view['headRepository']['name']} to date."
        )
        GhCliAdapter.pr_new_comment(
            pr_view["number"],
            args.owner,
            pr_view["headRepository"]["name"],
            "@dependabot rebase",
        )
    elif pr_view["mergeable"] == "CONFLICTING":
        print(
            f"🔄 Updating the PR #{pr_view['number']} of the repo {pr_view['headRepository']['name']} to date."
        )
        GhCliAdapter.pr_new_comment(
            pr_view["number"],
            args.owner,
            pr_view["headRepository"]["name"],
            "@dependabot recreate",
        )
    elif pr_view["reviewDecision"] == "REVIEW_REQUIRED":
        handling_pr_approbation(pr_view, args.owner, args.github_id)
    elif (
        pr_view["reviewDecision"] == "APPROVED"
        and pr_view["mergeStateStatus"] == "CLEAN"
    ):
        print(
            f"✅ The PR #{pr_view['number']} of the repo {pr_view['headRepository']['name']} can be merged."
        )
        GhCliAdapter.pr_new_comment(
            pr_view["number"],
            args.owner,
            pr_view["headRepository"]["name"],
            "@dependabot merge",
        )
    elif (
        pr_view["reviewDecision"] == "APPROVED"
        and pr_view["mergeStateStatus"] == "BLOCKED"
    ):
        if not (has_running_checks(pr_view)):
            if args.with_azure:
                print(
                    f"🛠 Launching Azure Pipelines on the PR #{pr_view['number']} of the repo {pr_view['headRepository']['name']}."
                )
                GhCliAdapter.pr_new_comment(
                    pr_view["number"],
                    args.owner,
                    pr_view["headRepository"]["name"],
                    "/azp run",
                )
            else:
                print(
                    f"🕰️😴 The PR #{pr_view['number']} of the repo {pr_view['headRepository']['name']} waits for checks to be triggered."
                )
        else:
            print(
                f"⏳ Waiting for Azure Pipelines on the PR #{pr_view['number']} of the repo {pr_view['headRepository']['name']}."
            )
    elif pr_view["mergeStateStatus"] == "UNSTABLE":
        print(
            f"🔴 The PR #{pr_view['number']} of the repo {pr_view['headRepository']['name']} has some failing checks."
        )
    elif pr_view["mergeStateStatus"] == "UNKNOWN":
        print(
            f"⚪ The PR #{pr_view['number']} of the repo {pr_view['headRepository']['name']} is in an unkown state.\n-- You should probable wait for GitHub to update the state of the PR."
        )
    elif (
        pr_view["reviewDecision"] == "APPROVED"
        and pr_view["mergeStateStatus"] != "CLEAN"
        and pr_view["mergeStateStatus"] != "BEHIND"
        and pr_view["mergeStateStatus"] != "BLOCKED"
    ):
        print(pr_view)
        input()

import os

from github import Github, Auth, GithubException
from jinja2 import Template

template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GitHub Branch Protection Status</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            margin: 0;
            padding: 2em;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            background: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        th, td {
            text-align: left;
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #24292e;
            color: #fff;
            position: sticky;
            top: 0;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .yes {
            color: green;
            font-weight: bold;
        }
        .no {
            color: red;
            font-weight: bold;
        }
        .not-protected {
            color: red;
            font-weight: bold;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>GitHub Branch Protection Status</h1>
    <table>
        <thead>
            <tr>
                <th>Repository</th>
                <th>Branch</th>
                <th>Allow deletions</th>
                <th>Allow force pushes</th>
                <th>Enforce admins</th>
                <th>Require linear history</th>
                <th>Require signatures</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
                {% if item.unprotected %}
                    <tr>
                        <td colspan="8" class="not-protected">
                            {{ item.repository }} / {{ item.branch }} — Not Protected
                        </td>
                    </tr>
                {% else %}
                    <tr>
                        <td>{{ item.repository }}</td>
                        <td>{{ item.branch }}</td>
                        <td class="{{ 'no' if item.allow_deletions else 'yes' }}">
                            {{ 'Yes' if item.allow_deletions else 'No' }}
                        </td>
                        <td class="{{ 'no' if item.allow_force_pushes else 'yes' }}">
                            {{ 'Yes' if item.allow_force_pushes else 'No' }}
                        </td>
                        <td class="{{ 'yes' if item.enforce_admins else 'no' }}">
                            {{ 'Yes' if item.enforce_admins else 'No' }}
                        </td>
                        <td class="{{ 'yes' if item.require_linear_history else 'no' }}">
                            {{ 'Yes' if item.require_linear_history else 'No' }}
                        </td>
                        <td class="{{ 'yes' if item.require_signatures else 'no' }}">
                            {{ 'Yes' if item.require_signatures else 'No' }}
                        </td>
                    </tr>
                {% endif %}
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""


def render_branch_protection_report(items, template_str: str) -> None:
    """
    Renders a GitHub branch protection status HTML report to 'index.html'.

    Parameters:
        items (List[Dict]): A list of dictionaries with branch protection data.
        template_str (str): A Jinja2/Ninja template string for rendering the HTML.
    """
    template = Template(template_str)
    rendered_html = template.render(items=items)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(rendered_html)


def main():
    branch_names = ["main", "master", "develop"]
    
    auth = Auth.Token(os.environ["GH_TOKEN"])
    g = Github(auth=auth)
    ecmwf_org = g.get_organization("ecmwf")
    items = []
    for repo in ecmwf_org.get_repos():
        for branch_name in branch_names:
            print(f"Cheking {repo.name}@{branch_name}")
            try:
                b = repo.get_branch(branch_name)
            except GithubException as _:
                continue
            try:
                prot = b.get_protection()
                items.append(
                    {
                        "repository": repo.name,
                        "branch": branch_name,
                        "allow_deletions": prot.allow_deletions,
                        "allow_force_pushes": prot.allow_force_pushes,
                        "enforce_admins": prot.enforce_admins,
                        "required_linear_history": prot.required_linear_history,
                        "required_signatures": prot.required_signatures,
                    }
                )
            except GithubException as _:
                items.append(
                    {
                        "repository": repo.name,
                        "branch": branch_name,
                        "unprotected": True,
                    }
                )
                
    render_branch_protection_report(items, template)


if __name__ == "__main__":
    main()

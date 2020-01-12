import re
import json as json_module
import asyncio
import httpx

from urllib.parse import parse_qs, urlparse

from sanic import Blueprint
from sanic.response import json


github_app = Blueprint("repo")


@github_app.route("/github/<repo_path:path>")
async def fetch_repo(request, repo_path):
    commits = []

    cache_key = f"repo_{repo_path}"
    cached_commits = await request.ctx.redis.get(cache_key)

    if cached_commits:
        commits = json_module.loads(cached_commits)
    else:
        commits = await get_all_commits(repo_path, request.app.config["GITHUB_TOKEN"])
        await request.ctx.redis.set(cache_key, json_module.dumps(commits))

    return json(commits, headers={"Access-Control-Allow-Origin": request.app.config['REPOSURF_URL']})


def map_commit(c, i = 0):
    commit = {
        "authorDate": c["commit"]["author"]["date"],
        "date": c["commit"]["committer"]["date"],
        "message": c["commit"]["message"],
        "url": c["commit"]["url"],
        "commentCount": c["commit"]["comment_count"]
    }
    author = None
    if c["author"]:
        author = {
            "name": c["commit"]["author"]["name"],
            "username": c["author"]["login"],
            "picture": c["author"]["avatar_url"],
            "url": c["author"]["url"],
            "htmlUrl": c["author"]["html_url"]
        }
    committer = None
    if c["committer"]:
        committer = {
            "name": c["commit"]["committer"]["name"],
            "username": c["committer"]["login"],
            "picture": c["committer"]["avatar_url"],
            "url": c["committer"]["url"],
            "htmlUrl": c["committer"]["html_url"]
        },

    return {
        "sha": c["sha"],
        "index": i,
        "url": c["url"],
        "htmlUrl": c["html_url"],
        "commit": commit,
        "author": author,
        "committer": committer,
        "parents": [p["sha"] for p in c["parents"]],
    }

async def get_all_commits(repo_path, github_token):
    headers = {"Authorization": f"token {github_token}"}

    initial_page = (
        f"https://api.github.com/repos/{repo_path}/commits?sha=master&per_page=100"
    )
    initial_request = await httpx.get(initial_page, headers=headers)

    link_header = initial_request.headers.get("link")

    if not link_header:
        commits = initial_request.json()
    else:
        parsed_header = parse_header_links(link_header)
        concurrent_pages = 10
        total_pages = int(parsed_header["last"]["qs"]["page"])

        commits = []

        current_page = 1

        while current_page <= total_pages:
            requests = []

            for i in range(0, concurrent_pages):
                request = httpx.get(
                    f"https://api.github.com/repos/{repo_path}/commits?sha=master&per_page=100&page={current_page}",
                    headers=headers,
                )

                requests.append(request)
                current_page = current_page + 1

                if current_page > total_pages:
                    break

            responses = await asyncio.gather(*requests)

            for response in responses:
                response.raise_for_status()

                request_commits = response.json()
                commits.extend(request_commits)

    commits = [map_commit(c, len(commits) - i - 1) for i, c in enumerate(commits)]

    return commits


def parse_header_links(value):
    links = []

    replace_chars = " '\""

    for val in re.split(", *<", value):
        try:
            url, params = val.split(";", 1)
        except ValueError:
            url, params = val, ""

        link = {}

        link["url"] = url.strip("<> '\"")

        parsed_url = urlparse(link["url"])

        link[
            "url_without_qs"
        ] = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        querystring = parsed_url.query
        parsed_qs = parse_qs(querystring)

        link["qs"] = {key: value[0] for key, value in parsed_qs.items()}

        for param in params.split(";"):
            try:
                key, value = param.split("=")
            except ValueError:
                break

            link[key.strip(replace_chars)] = value.strip(replace_chars)

        links.append(link)

    return {link["rel"]: link for link in links}

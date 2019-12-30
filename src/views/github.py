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
        return json(json_module.loads(cached_commits))

    commits = await get_all_commits(repo_path, request.app.config["GITHUB_TOKEN"])

    await request.ctx.redis.set(cache_key, json_module.dumps(commits))
    return json(commits)


async def get_all_commits(repo_path, github_token):
    headers = {"Authorization": f"token {github_token}"}

    initial_page = (
        f"https://api.github.com/repos/{repo_path}/commits?sha=master&per_page=100"
    )
    initial_request = await httpx.get(initial_page, headers=headers)

    link_header = initial_request.headers.get("link")

    if not link_header:
        commits = initial_request.json()
        commits.reverse()
        return commits

    parsed_header = parse_header_links(link_header)
    concurrent_pages = 10
    total_pages = int(parsed_header["last"]["qs"]["page"])

    commits = []

    remaining_pages = total_pages

    while remaining_pages > 0:
        requests = []

        for i in range(0, concurrent_pages):
            request = httpx.get(
                f"https://api.github.com/repos/{repo_path}/commits?sha=master&per_page=100&page={remaining_pages}",
                headers=headers,
            )

            requests.append(request)
            remaining_pages = remaining_pages - 1

            if remaining_pages <= 0:
                break

        responses = await asyncio.gather(*requests)

        for response in responses:
            response.raise_for_status()

            request_commits = response.json()
            request_commits.reverse()
            commits.extend(request_commits)

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

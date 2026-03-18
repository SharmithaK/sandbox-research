#!/usr/bin/env python3
"""Owl Bot — responds to @how-to <query> in GitHub Discussions."""

import json
import os
import re
import sys

import requests

# ---------------------------------------------------------------------------
# Config / env
# ---------------------------------------------------------------------------

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
COMMENT_BODY = os.environ.get("COMMENT_BODY", "")
COMMENT_ID = os.environ.get("COMMENT_ID", "")       # node_id (GraphQL)
COMMENT_AUTHOR = os.environ.get("COMMENT_AUTHOR", "")
DISCUSSION_ID = os.environ.get("DISCUSSION_ID", "")  # node_id (GraphQL)
DISCUSSION_NUMBER = os.environ.get("DISCUSSION_NUMBER", "")
REPO = os.environ.get("REPO", "")                   # owner/repo

GRAPHQL_URL = "https://api.github.com/graphql"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/vnd.github+json",
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_INDEX_PATH = os.path.join(SCRIPT_DIR, "docs_index.json")

FOOTER = (
    "\n\n*still stuck? here's how to ask so someone can help:*\n"
    "*• what exactly are you trying to do?*\n"
    "*• what did you try?*\n"
    "*• what happened / what's the error message?*\n"
    "*• what have you already looked up or attempted to fix it?*\n\n"
    "*drop that in the thread and someone from the community might jump in! "
    "you can also try googling it or asking an AI in the meantime 🐿️*"
)

# ---------------------------------------------------------------------------
# GraphQL helpers
# ---------------------------------------------------------------------------


def gql(query: str, variables: dict = None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    r = requests.post(GRAPHQL_URL, headers=HEADERS, json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}", file=sys.stderr)
    return data


# ---------------------------------------------------------------------------
# Bot self-check
# ---------------------------------------------------------------------------


def get_bot_login() -> str:
    data = gql("{ viewer { login } }")
    return data.get("data", {}).get("viewer", {}).get("login", "")


# ---------------------------------------------------------------------------
# Reactions
# ---------------------------------------------------------------------------


def add_reaction(comment_node_id: str, content: str):
    """content: THUMBS_UP | HOORAY | CONFUSED | HEART | ROCKET | EYES"""
    mutation = """
    mutation($subjectId: ID!, $content: ReactionContent!) {
      addReaction(input: {subjectId: $subjectId, content: $content}) {
        reaction { content }
      }
    }
    """
    gql(mutation, {"subjectId": comment_node_id, "content": content})


# ---------------------------------------------------------------------------
# Discussion label helpers
# ---------------------------------------------------------------------------


def get_label_node_id(label_name: str) -> str:
    owner, name = REPO.split("/", 1)
    query = """
    query($owner: String!, $name: String!, $labelName: String!) {
      repository(owner: $owner, name: $name) {
        label(name: $labelName) { id }
      }
    }
    """
    data = gql(query, {"owner": owner, "name": name, "labelName": label_name})
    label = data.get("data", {}).get("repository", {}).get("label")
    return label["id"] if label else ""


def discussion_has_label(label_name: str) -> bool:
    query = """
    query($id: ID!) {
      node(id: $id) {
        ... on Discussion {
          labels(first: 20) {
            nodes { name }
          }
        }
      }
    }
    """
    data = gql(query, {"id": DISCUSSION_ID})
    labels = (
        data.get("data", {})
        .get("node", {})
        .get("labels", {})
        .get("nodes", [])
    )
    return any(l["name"] == label_name for l in labels)


def add_label_to_discussion(label_name: str):
    label_id = get_label_node_id(label_name)
    if not label_id:
        print(f"Label '{label_name}' not found in repo — skipping.", file=sys.stderr)
        return
    mutation = """
    mutation($labelableId: ID!, $labelIds: [ID!]!) {
      addLabelsToLabelable(input: {labelableId: $labelableId, labelIds: $labelIds}) {
        labelable { ... on Discussion { id } }
      }
    }
    """
    gql(mutation, {"labelableId": DISCUSSION_ID, "labelIds": [label_id]})


def remove_label_from_discussion(label_name: str):
    label_id = get_label_node_id(label_name)
    if not label_id:
        print(f"Label '{label_name}' not found in repo — skipping.", file=sys.stderr)
        return
    mutation = """
    mutation($labelableId: ID!, $labelIds: [ID!]!) {
      removeLabelsFromLabelable(input: {labelableId: $labelableId, labelIds: $labelIds}) {
        labelable { ... on Discussion { id } }
      }
    }
    """
    gql(mutation, {"labelableId": DISCUSSION_ID, "labelIds": [label_id]})


# ---------------------------------------------------------------------------
# Post reply to discussion
# ---------------------------------------------------------------------------


def post_reply(body: str):
    mutation = """
    mutation($discussionId: ID!, $body: String!) {
      addDiscussionComment(input: {discussionId: $discussionId, body: $body}) {
        comment { id url }
      }
    }
    """
    data = gql(mutation, {"discussionId": DISCUSSION_ID, "body": body})
    comment = data.get("data", {}).get("addDiscussionComment", {}).get("comment", {})
    print(f"Posted reply: {comment.get('url', '(no url)')}")


# ---------------------------------------------------------------------------
# Docs keyword lookup
# ---------------------------------------------------------------------------


def load_docs_index() -> dict:
    with open(DOCS_INDEX_PATH, encoding="utf-8") as f:
        return json.load(f)


def fuzzy_docs_lookup(query: str) -> tuple | None:
    """Return (matched_key, url, desc) for the best (longest) partial keyword match."""
    index = load_docs_index()
    q = query.lower()
    best_key = None
    best_url = None
    best_desc = None
    for key, entry in index.items():
        k = key.lower()
        if q in k or k in q:
            if best_key is None or len(k) > len(best_key):
                best_key = k
                best_url = entry["url"]
                best_desc = entry["desc"]
    return (best_key, best_url, best_desc) if best_key else None


# ---------------------------------------------------------------------------
# Discussion search via GraphQL
# ---------------------------------------------------------------------------


def strip_markdown(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`#>~]", "", text)
    return text.strip()


def search_discussions(query: str) -> list:
    """Return up to 3 discussion comment matches: [{preview, url}]."""
    owner, repo_name = REPO.split("/", 1)
    search_query = f"{query} repo:{owner}/{repo_name}"
    gql_query = """
    query($q: String!) {
      search(query: $q, type: DISCUSSION, first: 5) {
        nodes {
          ... on Discussion {
            comments(first: 10) {
              nodes {
                body
                url
              }
            }
          }
        }
      }
    }
    """
    data = gql(gql_query, {"q": search_query})
    results = []
    q_lower = query.lower()
    nodes = data.get("data", {}).get("search", {}).get("nodes", [])
    for discussion in nodes:
        for comment in discussion.get("comments", {}).get("nodes", []):
            body = comment.get("body", "")
            if q_lower in body.lower():
                preview = strip_markdown(body)[:80]
                results.append({"preview": preview, "url": comment.get("url", "")})
            if len(results) >= 3:
                break
        if len(results) >= 3:
            break
    return results


# ---------------------------------------------------------------------------
# Reply builders
# ---------------------------------------------------------------------------


def build_docs_reply(query: str, url: str, desc: str, author: str) -> str:
    mention = f"@{author} " if author else ""
    return (
        f'{mention}🦉 hoot hoot! here\'s what I found for "**{query}**":\n\n'
        f"📖 **from the docs:**\n"
        f"→ *{desc}*\n"
        f"  {url}"
        + FOOTER
    )


def build_discussion_reply(query: str, matches: list, author: str) -> str:
    mention = f"@{author} " if author else ""
    lines = [
        f'{mention}🦉 hoot hoot! "**{query}**" isn\'t in my docs index but found these in our discussions:\n',
        "💬 **from the discussions:**",
    ]
    for m in matches:
        lines.append(f"→ {m['preview']} — {m['url']}")
    return "\n".join(lines) + FOOTER


def build_nothing_reply(query: str, author: str) -> str:
    mention = f"@{author} " if author else ""
    return (
        f'{mention}🦉 hoot... I looked everywhere and couldn\'t find anything for "**{query}**".\n\n'
        "*here's how to ask so someone can actually help:*\n"
        "*• what exactly are you trying to do?*\n"
        "*• what did you try?*\n"
        "*• what happened — paste the exact error message if there is one*\n"
        "*• what have you already looked up or tried to fix it?*\n\n"
        "*drop that in the thread and someone from the community might jump in! "
        "you can also try googling it or asking an AI in the meantime 🐿️*"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_owl_comment(body: str):
    """
    Match any natural 'owl' invocation and return (command, query_or_None).

    Trigger examples:
        owl, how do I fork a repo?
        dear owl, what is a PR?
        oh wise owl — how does markdown work?
        hey owl! zenodo
        owl off / owl on

    Returns:
        ('off', None)       — silence command
        ('on', None)        — resume command
        ('query', str)      — query text (original case)
        None                — not an owl comment
    """
    # Pattern: optional preamble ("dear", "oh wise", "hey", etc.), then "owl",
    # then an optional separator (comma / dash / colon / !? / whitespace),
    # then the rest.
    m = re.match(
        r"^(?:[\w\s]*?\b)?owl\b[,\-:!?\s]+(.+)$",
        body.strip(),
        re.IGNORECASE | re.DOTALL,
    )
    if not m:
        # bare "owl off" / "owl on" with no separator
        bare = re.match(r"^(?:[\w\s]*?\b)?owl\s+(off|on)\s*$", body.strip(), re.IGNORECASE)
        if bare:
            return (bare.group(1).lower(), None)
        return None

    rest = m.group(1).strip()
    if re.match(r"^off\s*$", rest, re.IGNORECASE):
        return ("off", None)
    if re.match(r"^on\s*$", rest, re.IGNORECASE):
        return ("on", None)
    return ("query", rest)


def main():
    body = COMMENT_BODY.strip()

    parsed = parse_owl_comment(body)
    if parsed is None:
        print("Not an owl comment — exiting.")
        return

    command, query = parsed

    # owl off
    if command == "off":
        add_reaction(COMMENT_ID, "CONFUSED")
        add_label_to_discussion("owl-silenced")
        print("Owl silenced.")
        return

    # owl on
    if command == "on":
        remove_label_from_discussion("owl-silenced")
        add_reaction(COMMENT_ID, "HOORAY")
        print("Owl re-enabled.")
        return

    # Check silenced
    if discussion_has_label("owl-silenced"):
        print("Discussion is silenced — exiting.")
        return

    # Avoid self-reply
    bot_login = get_bot_login()
    if COMMENT_AUTHOR and bot_login and COMMENT_AUTHOR.lower() == bot_login.lower():
        print("Comment is from the bot itself — exiting.")
        return

    if not query:
        print("Empty query — exiting.")
        return

    print(f"Query: {query!r}")

    # Step 1: docs lookup
    match = fuzzy_docs_lookup(query)
    if match:
        _, url, desc = match
        post_reply(build_docs_reply(query, url, desc, COMMENT_AUTHOR))
        return

    # Step 2: discussion search
    matches = search_discussions(query)
    if matches:
        post_reply(build_discussion_reply(query, matches, COMMENT_AUTHOR))
        return

    # Step 3: nothing found
    post_reply(build_nothing_reply(query, COMMENT_AUTHOR))


if __name__ == "__main__":
    main()

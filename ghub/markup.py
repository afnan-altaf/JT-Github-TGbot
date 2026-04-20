import html as _html


def _esc(s: str) -> str:
    return _html.escape(str(s or ""))


def format_push(p: dict) -> str:
    repo = (p.get("repository") or {}).get("full_name", "?")
    ref = p.get("ref", "").replace("refs/heads/", "")
    pusher = (p.get("pusher") or {}).get("name", "?")
    commits = p.get("commits") or []
    count = len(commits)
    lines = [
        f"<b>📦 Push to <code>{_esc(repo)}</code></b>",
        f"<b>Branch:</b> <code>{_esc(ref)}</code>  |  <b>By:</b> {_esc(pusher)}  |  <b>Commits:</b> {count}",
    ]
    for c in commits[:5]:
        msg = (c.get("message") or "").split("\n")[0]
        sha = (c.get("id") or "")[:7]
        url = c.get("url", "")
        lines.append(f'  • <a href="{_esc(url)}"><code>{_esc(sha)}</code></a> {_esc(msg)}')
    if count > 5:
        lines.append(f"  … and {count - 5} more commits")
    return "\n".join(lines)


def format_issue(p: dict) -> str:
    action = p.get("action", "?")
    issue = p.get("issue") or {}
    repo = (p.get("repository") or {}).get("full_name", "?")
    title = issue.get("title", "?")
    url = issue.get("html_url", "")
    num = issue.get("number", "?")
    user = (issue.get("user") or {}).get("login", "?")
    return (
        f"<b>🐛 Issue #{num} {_esc(action)}</b> in <code>{_esc(repo)}</code>\n"
        f"<b>Title:</b> {_esc(title)}\n"
        f"<b>By:</b> {_esc(user)}\n"
        f'<a href="{_esc(url)}">View Issue</a>'
    )


def format_pr(p: dict) -> str:
    action = p.get("action", "?")
    pr = p.get("pull_request") or {}
    repo = (p.get("repository") or {}).get("full_name", "?")
    title = pr.get("title", "?")
    url = pr.get("html_url", "")
    num = pr.get("number", "?")
    user = (pr.get("user") or {}).get("login", "?")
    return (
        f"<b>🔀 PR #{num} {_esc(action)}</b> in <code>{_esc(repo)}</code>\n"
        f"<b>Title:</b> {_esc(title)}\n"
        f"<b>By:</b> {_esc(user)}\n"
        f'<a href="{_esc(url)}">View PR</a>'
    )


def format_fork(p: dict) -> str:
    repo = (p.get("repository") or {}).get("full_name", "?")
    forkee = (p.get("forkee") or {}).get("full_name", "?")
    user = (p.get("sender") or {}).get("login", "?")
    return (
        f"<b>🍴 Fork</b> of <code>{_esc(repo)}</code>\n"
        f"<b>New fork:</b> <code>{_esc(forkee)}</code>\n"
        f"<b>By:</b> {_esc(user)}"
    )


def format_star(p: dict) -> str:
    action = p.get("action", "starred")
    repo = (p.get("repository") or {}).get("full_name", "?")
    stars = (p.get("repository") or {}).get("stargazers_count", "?")
    user = (p.get("sender") or {}).get("login", "?")
    return (
        f"<b>⭐ Star {_esc(action)}</b> on <code>{_esc(repo)}</code>\n"
        f"<b>By:</b> {_esc(user)}  |  <b>Total stars:</b> {stars}"
    )


def format_release(p: dict) -> str:
    action = p.get("action", "?")
    release = p.get("release") or {}
    repo = (p.get("repository") or {}).get("full_name", "?")
    name = release.get("name") or release.get("tag_name", "?")
    url = release.get("html_url", "")
    user = (release.get("author") or {}).get("login", "?")
    return (
        f"<b>🚀 Release {_esc(action)}</b> in <code>{_esc(repo)}</code>\n"
        f"<b>Name:</b> {_esc(name)}\n"
        f"<b>By:</b> {_esc(user)}\n"
        f'<a href="{_esc(url)}">View Release</a>'
    )


def format_ping(p: dict) -> str:
    repo = (p.get("repository") or {}).get("full_name", "?")
    hook_id = (p.get("hook") or {}).get("id", "?")
    return (
        f"<b>🏓 Webhook ping</b> from <code>{_esc(repo)}</code>\n"
        f"<b>Hook ID:</b> <code>{hook_id}</code>\n"
        "Webhook is active and working!"
    )


def format_generic(event: str, p: dict) -> str:
    repo = (p.get("repository") or {}).get("full_name", "?")
    action = p.get("action", "")
    return (
        f"<b>📡 GitHub event: <code>{_esc(event)}</code></b>"
        + (f" ({_esc(action)})" if action else "")
        + f"\n<b>Repo:</b> <code>{_esc(repo)}</code>"
    )

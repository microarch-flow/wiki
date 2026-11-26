"""Attach Giscus to published article pages, without altering Markdown or search."""

from html import escape
from pathlib import PurePosixPath
import re
from urllib.parse import unquote, urlsplit

# The main navigation is the source of truth for published articles. Most
# guides are index pages. Several retained public URLs use non-index files.
LANDINGS = frozenset({
    "README.md", "microarchitecture.md", "storage.md", "interconnect.md",
    "articles.md", "visuals.md",
})
GUIDE_FILES = frozenset({
    "SUMMARY.md", "learning-roadmap.md", "reading-roadmap-by-goal.md",
    "study-navigation.md", "taxonomy-and-roadmap.md", "wiki-roadmap.md",
    "self-test-questions.md",
})


def comment_settings(config):
    """The feature is opt-in and fails the build if activation is incomplete."""
    settings = config.extra.get("comments", {})
    if not isinstance(settings, dict):
        raise ValueError("extra.comments must be a mapping")
    enabled = settings.get("enabled", False)
    if not isinstance(enabled, bool):
        raise ValueError("extra.comments.enabled must be true or false")
    if not enabled:
        return None
    required = ("repo", "repo_id", "category", "category_id")
    missing = [key for key in required if not isinstance(settings.get(key), str) or not settings[key].strip()]
    if missing:
        raise ValueError(f"Giscus requires extra.comments fields: {', '.join(missing)}")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", settings["repo"]):
        raise ValueError("extra.comments.repo must be an owner/repository name")
    if not config.site_url:
        raise ValueError("Giscus requires site_url for stable article mappings")
    return {key: settings[key].strip() for key in required}


def is_concrete_article(page):
    """Honor MkDocs' index role, including the custom readme article role."""
    path = page.file.src_uri
    parts = PurePosixPath(path).parts
    return (not page.is_index and path not in LANDINGS
            and parts[-1] not in GUIDE_FILES
            and not any(part in {"reviews", "archive", "wiki.old"} for part in parts))


def on_config(config, **kwargs):
    comment_settings(config)
    return config


def on_nav(nav, config, **kwargs):
    # Unlisted redirect/archived pages are not nav.pages. The primary navigation
    # already distinguishes foundation and chip-case README articles from guides.
    config.extra["comment_article_paths"] = {
        page.file.src_uri for page in nav.pages if is_concrete_article(page)
    } if comment_settings(config) else set()
    return nav


def comment_term(page):
    """Use a canonical published URL path, not titles or the local source path."""
    if not page.canonical_url:
        raise ValueError(f"Article has no canonical URL: {page.file.src_uri}")
    return unquote(urlsplit(page.canonical_url).path)


def render_comments(page, settings):
    attrs = {
        "src": "https://giscus.app/client.js",
        "data-repo": settings["repo"],
        "data-repo-id": settings["repo_id"],
        "data-category": settings["category"],
        "data-category-id": settings["category_id"],
        "data-mapping": "specific",
        "data-term": comment_term(page),
        "data-strict": "1",
        "data-reactions-enabled": "1",
        "data-emit-metadata": "0",
        "data-input-position": "top",
        "data-theme": "noborder_light",
        "data-lang": "zh-CN",
        "data-loading": "lazy",
        "crossorigin": "anonymous",
    }
    script_attrs = " ".join(f'{key}="{escape(value, quote=True)}"' for key, value in attrs.items())
    repo_url = "https://github.com/" + settings["repo"]
    return (
        '\n<section class="site-comments" aria-labelledby="site-comments-heading">\n'
        '<h2 id="site-comments-heading">讨论与评论</h2>\n'
        '<p class="site-comments-intro">欢迎交流技术问题、不同观点和勘误。评论公开保存在 GitHub Discussions，发表评论需要 GitHub 账号。'
        f'如果评论区无法加载，可以前往 <a href="{repo_url}/discussions">GitHub Discussions</a> 交流；'
        f'明确的技术错误、失效链接或网站问题也可以通过 <a href="{repo_url}/issues">GitHub Issues</a> 反馈。</p>\n'
        '<div class="giscus"></div>\n'
        f'<script {script_attrs} async></script>\n'
        '</section>\n'
    )


def on_post_page(output, page, config, **kwargs):
    # Insert after Markdown, TOC and search index have already been generated,
    # so the shared comments introduction doesn't pollute the search corpus.
    settings = comment_settings(config)
    if not settings or page.file.src_uri not in config.extra.get("comment_article_paths", set()):
        return output
    if page.meta.get("comments") is False:
        return output
    if "</article>" not in output or "</head>" not in output:
        raise ValueError(f"Article or head container not found: {page.file.src_uri}")
    before, after = output.rsplit("</article>", 1)
    output = before + render_comments(page, settings) + "</article>" + after
    # Giscus creates the discussion backlink from this canonical URL rather
    # than a reader's fragment, query string, or alternate access address.
    backlink = f'<meta name="giscus:backlink" content="{escape(page.canonical_url, quote=True)}">\n'
    return output.replace("</head>", backlink + "</head>", 1)

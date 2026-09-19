"""SEO structured data template tags

  - BreadcrumbList  (https://developers.google.com/search/docs/appearance/structured-data/breadcrumb)
  - NewsArticle     (https://developers.google.com/search/docs/appearance/structured-data/article)
  - VideoObject     (https://developers.google.com/search/docs/appearance/structured-data/video)
  - Organization    (used site-wide and as the NewsArticle/VideoObject publisher)

All tags take the template context so they can resolve absolute URLs from the
current request. JSON is escaped so it can never break out of the <script> block.
"""

import json

from django import template
from django.templatetags.static import static
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from newsroom import settings as newsroom_settings

register = template.Library()

# org details; reused as NewsArticle publisher.
ORG_NAME = "GroundUp"
ORG_LOGO = "newsroom/images/LogoFiles/Logos20180905/MasterLogo.png"
ORG_LOGO_WIDTH = 2000
ORG_LOGO_HEIGHT = 403
ORG_SAME_AS = [
    "https://twitter.com/GroundUp_News",
    "https://www.facebook.com/GroundUpNews",
    "https://www.instagram.com/groundup_news/",
    "https://www.tiktok.com/@groundup_news",
]
ORG_PUBLISHING_PRINCIPLES = "https://groundup.org.za/about/"
ORG_ETHICS_POLICY = "https://groundup.org.za/ethics_and_style/"
ORG_CORRECTIONS_POLICY = "https://groundup.org.za/correction/list/"
ORG_MASTHEAD = "https://groundup.org.za/journalists/"


def _ld_script(data):
    """dict -> a safe <script type="application/ld+json"> block"""
    payload = json.dumps(data, ensure_ascii=False)
    # Prevent the JSON from terminating the <script> element or being parsed as html
    payload = (
        payload.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    return mark_safe(
        '<script type="application/ld+json">' + payload + "</script>"
    )


def _abs(request, url):
    """Make a relative path/URL absolute using current request"""
    if not url:
        return url
    return request.build_absolute_uri(url)


def _org_id(request):
    return _abs(request, "/").rstrip("/") + "#publisher"


def _publisher_ref(request):
    return {"@id": _org_id(request), "name": ORG_NAME}


def _organization_full(request):
    """Full NewsMediaOrganization object for the standalone JSON-LD block."""
    logo_url = _abs(request, static(ORG_LOGO))
    return {
        "@type": "NewsMediaOrganization",
        "@id": _org_id(request),
        "name": ORG_NAME,
        "url": _abs(request, "/"),
        "logo": {
            "@type": "ImageObject",
            "url": logo_url,
            "contentUrl": logo_url,
            "width": ORG_LOGO_WIDTH,
            "height": ORG_LOGO_HEIGHT,
        },
        "sameAs": ORG_SAME_AS,
        "publishingPrinciples": ORG_PUBLISHING_PRINCIPLES,
        "ethicsPolicy": ORG_ETHICS_POLICY,
        "correctionsPolicy": ORG_CORRECTIONS_POLICY,
        "masthead": ORG_MASTHEAD,
        "ownershipFundingInfo": _abs(request, "/funders"),
    }


@register.simple_tag(takes_context=True)
def organization_jsonld(context):
    request = context.get("request")
    if request is None:
        return ""
    data = {"@context": "https://schema.org"}
    data.update(_organization_full(request))
    return _ld_script(data)


@register.simple_tag(takes_context=True)
def breadcrumb_jsonld(context, breadcrumbs):
    """Render a BreadcrumbList from a list of {"name", "url"} dicts"""
    request = context.get("request")
    if not breadcrumbs or request is None:
        return ""
    items = []
    for position, crumb in enumerate(breadcrumbs, start=1):
        item = {
            "@type": "ListItem",
            "position": position,
            "name": crumb["name"],
        }
        if crumb.get("url"):
            item["item"] = _abs(request, crumb["url"])
        items.append(item)
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }
    return _ld_script(data)


@register.simple_tag(takes_context=True)
def news_article_jsonld(context, article):
    request = context.get("request")
    if request is None or article is None:
        return ""

    # Images (absolute, de-duplicated, blanks skipped)
    images = []
    for img in (article.cached_primary_image, article.cached_summary_image):
        if img:
            url = _abs(request, img)
            if url not in images:
                images.append(url)

    # Authors: we pref real Person objects with profile pages
    authors = [
        {
            "@type": "Person",
            "name": str(author),
            "url": _abs(request, author.get_absolute_url()),
        }
        for author in article.get_authors()
    ]
    if not authors and article.cached_byline_no_links:
        name = article.cached_byline_no_links
        if name.startswith("By "):
            name = name[3:]
        authors = [{"@type": "Person", "name": name}]

    data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": _abs(request, article.get_absolute_url()),
        },
        "headline": strip_tags(article.title),
        "publisher": _publisher_ref(request),
    }
    if article.cached_summary_text_no_html:
        data["description"] = article.cached_summary_text_no_html
    if images:
        data["image"] = images
    if article.published:
        data["datePublished"] = article.published.isoformat()
    if article.modified:
        data["dateModified"] = article.modified.isoformat()
    if authors:
        data["author"] = authors
    if article.category_id:
        data["articleSection"] = article.category.name

    return _ld_script(data)


def _video_object(context, video, include_context=True):
    """VideoObject for one video. Chapters become Clip parts, which is what
    Google reads for key moments in search results."""
    request = context.get("request")
    data = {}
    if include_context:
        data["@context"] = "https://schema.org"
    page_url = _abs(request, video.get_absolute_url())
    data.update(
        {
            "@type": "VideoObject",
            "@id": page_url + "#video",
            "name": strip_tags(video.title),
            "url": page_url,
            "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
            "thumbnailUrl": _abs(request, video.thumbnail_url()),
            "embedUrl": video.embed_url(),
            "contentUrl": video.watch_url(),
            "publisher": _publisher_ref(request),
            "isFamilyFriendly": True,
            "inLanguage": "en",
        }
    )
    if video.summary:
        data["description"] = strip_tags(video.summary)
    if video.published:
        data["uploadDate"] = video.published.isoformat()
    if video.modified:
        data["dateModified"] = video.modified.isoformat()
    if video.duration_iso():
        data["duration"] = video.duration_iso()
    if video.author_id:
        data["author"] = {
            "@type": "Person",
            "name": str(video.author),
            "url": _abs(request, video.author.get_absolute_url()),
        }
    elif video.byline:
        data["author"] = {"@type": "Person", "name": video.byline}
    contributors = list(video.contributors.all())
    if contributors:
        if "author" not in data:
            reporters = [c for c in contributors if c.role == "reporting"]
            if reporters:
                data["author"] = [
                    {
                        "@type": "Person",
                        "name": str(contributor.author),
                        "url": _abs(
                            request, contributor.author.get_absolute_url()
                        ),
                    }
                    for contributor in reporters
                ]
        data["contributor"] = [
            {"@type": "Person", "name": str(contributor.author)}
            for contributor in contributors
        ]
    data["license"] = newsroom_settings.VIDEO_LICENCE_URL
    if video.category_id:
        data["genre"] = video.category.name
    topics = [topic.name for topic in video.topics.all()]
    if topics:
        data["keywords"] = ", ".join(topics)

    chapters = list(video.chapters.all())
    total = video.duration_seconds()
    clips = []
    for position, chapter in enumerate(chapters):
        start = chapter.seconds()
        if position + 1 < len(chapters):
            end = chapters[position + 1].seconds()
        else:
            end = total
        if end is None or end <= start:
            continue
        clips.append(
            {
                "@type": "Clip",
                "name": chapter.description,
                "startOffset": start,
                "endOffset": end,
                "url": _abs(request, video.get_absolute_url()) + "#t=" + str(start),
            }
        )
    if clips:
        data["hasPart"] = clips
    return data


@register.simple_tag(takes_context=True)
def video_jsonld(context, video):
    request = context.get("request")
    if request is None or video is None:
        return ""
    return _ld_script(_video_object(context, video))


@register.simple_tag(takes_context=True)
def video_list_jsonld(context, videos, hero=None):
    """ItemList for a videos index page, so each entry can surface on its own."""
    request = context.get("request")
    if request is None:
        return ""
    ordered = ([hero] if hero else []) + list(videos or [])
    if not ordered:
        return ""
    items = [
        {
            "@type": "ListItem",
            "position": position,
            "item": _video_object(context, video, include_context=False),
        }
        for position, video in enumerate(ordered, start=1)
    ]
    return _ld_script(
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "itemListElement": items,
        }
    )

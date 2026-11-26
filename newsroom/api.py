from django.http import JsonResponse
from django.urls import reverse

from . import models


def _serialise(rows, request):
    """Turn [[slug, title], ...] into a list of JSON-ready dicts."""
    articles = []
    for row in rows or []:
        if len(row) < 2:
            continue
        slug = row[0].strip()
        # Rejoin: titles may legitimately contain a pipe.
        title = "|".join(row[1:]).strip()
        if not slug or not title:
            continue
        articles.append(
            {
                "slug": slug,
                "title": title,
                "url": request.build_absolute_uri(
                    reverse("newsroom:article.detail", args=[slug])
                ),
            }
        )
    return articles


def most_popular(request):
    """Public, unauthenticated JSON feed of the current most-popular list."""
    articles = _serialise(models.MostPopular.get_most_popular_list(), request)
    return JsonResponse({"count": len(articles), "articles": articles})


def most_deeply_read(request):
    """Public, unauthenticated JSON feed of the current most-deeply-read list."""
    articles = _serialise(models.MostDeeplyRead.get_list(), request)
    return JsonResponse({"count": len(articles), "articles": articles})


def articles_by_month(request, year, month):
    """Public, unauthenticated JSON list of the articles published in the given
    month (in the site's time zone), oldest first."""
    if not 1 <= month <= 12:
        return JsonResponse({"error": "month must be between 1 and 12"}, status=400)
    rows = (
        models.Article.objects.published()
        .filter(published__year=year, published__month=month)
        .order_by("published", "pk")
        .values_list("pk", "slug", "published")
    )
    articles = [
        {
            "pk": pk,
            "url": request.build_absolute_uri(
                reverse("newsroom:article.detail", args=[slug])
            ),
            "published": published.isoformat(),
        }
        for pk, slug, published in rows
    ]
    return JsonResponse({"count": len(articles), "articles": articles})

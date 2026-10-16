"""Target has moved to puzzles.groundup.org.za.

Every old Target address on the news site now permanently redirects to the
same page on the puzzles site. The URL names are kept so anything still
calling reverse("target:...") (the menu, Target.get_absolute_url, the
admin's "View on site", the tweettarget command) keeps working and simply
lands on a redirect.
"""

from django.conf import settings
from django.urls import path, re_path
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.base import RedirectView, TemplateView

app_name = "target"

PUZZLES_SITE_URL = getattr(
    settings, "PUZZLES_SITE_URL", "https://puzzles.groundup.org.za"
).rstrip("/")


def moved(new_path):
    return RedirectView.as_view(
        url=PUZZLES_SITE_URL + new_path, permanent=True, query_string=True
    )


@xframe_options_exempt
def export(request):
    """Hand the visitor's saved Target words to the puzzles site.

    Players' progress was stored in localStorage under this origin before
    Target moved. The puzzles site frames this page (see the template) and
    receives the words by postMessage. Remove once the migration is over.
    """
    response = TemplateView.as_view(
        template_name="target/target_export.html",
        extra_context={"PUZZLES_SITE_URL": PUZZLES_SITE_URL},
    )(request)
    response["Content-Security-Policy"] = (
        "frame-ancestors " + PUZZLES_SITE_URL
    )
    return response


urlpatterns = [
    path("target/export/", export, name="export"),
    # The archive is the only address whose path changed on the new site.
    path("targets/", moved("/target/archive/"), name="list"),
    path("target/", moved("/target/"), name="latest"),
    path("target/<int:pk>", moved("/target/%(pk)s"), name="detail"),
    path("target/create/", moved("/target/create/"), name="create"),
    path("target/create/<str:letters>",
         moved("/target/create/%(letters)s"), name="create_letters"),
    path("target/update/<int:pk>", moved("/target/update/%(pk)s"), name="update"),
    path("target/delete/<int:pk>", moved("/target/delete/%(pk)s"), name="delete"),
    # Anything else under /target/ goes to the same path on the puzzles site.
    re_path(r"^target/(?P<rest>.+)$", moved("/target/%(rest)s")),
]

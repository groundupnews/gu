from django.db import migrations


# video filter bar; Editors can rename / reorder / add
CATEGORIES = [
    ("Explainers", "explainers", "Explainer", 10),
    ("Investigations", "investigations", "Investigation", 20),
    ("Documentaries", "documentaries", "Documentary", 30),
    ("Court cases", "court-cases", "Court case", 40),
    ("Features", "features", "Feature", 50),
]


def add_categories(apps, schema_editor):
    VideoCategory = apps.get_model("newsroom", "VideoCategory")
    for name, slug, label, position in CATEGORIES:
        VideoCategory.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "label": label, "position": position},
        )


def remove_categories(apps, schema_editor):
    VideoCategory = apps.get_model("newsroom", "VideoCategory")
    VideoCategory.objects.filter(
        slug__in=[slug for _, slug, _, _ in CATEGORIES], videos__isnull=True
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("newsroom", "0052_videocategory_video_videochapter_and_more"),
    ]

    operations = [
        migrations.RunPython(add_categories, remove_categories),
    ]

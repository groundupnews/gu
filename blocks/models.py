from django.db import models

# Create your models here.

BLOCK_TYPES = (
    ("standard", "Standard HTML"),
    ("topic", "Topic"),
    ("category", "Category"),
    ("chart_of_the_week", "Chart of the Week"),
    ("creative_commons_gallery", "Creative Commons Gallery"),
)


class Block(models.Model):
    name = models.CharField(max_length=200, unique=True)
    block_type = models.CharField(
        max_length=50, choices=BLOCK_TYPES, default="standard"
    )
    custom_title = models.CharField(
        max_length=200, blank=True, help_text="Override the default title"
    )

    selected_topic = models.ForeignKey(
        "newsroom.Topic", on_delete=models.SET_NULL, null=True, blank=True
    )
    selected_category = models.ForeignKey(
        "newsroom.Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    num_articles = models.PositiveIntegerField(default=5, blank=True, null=True)
    feature_first_article = models.BooleanField(
        default=True,
        help_text="If checked, the first article will be styled as a featured article.",
    )
    show_summary_featured = models.BooleanField(
        default=True, verbose_name="Show summary for featured article"
    )
    show_summary_standard = models.BooleanField(
        default=True, verbose_name="Show summary for standard articles"
    )
    show_title_featured = models.BooleanField(
        default=True, verbose_name="Show title for featured article"
    )
    show_title_standard = models.BooleanField(
        default=True, verbose_name="Show title for standard articles"
    )

    show_byline_featured = models.BooleanField(
        default=True, verbose_name="Show byline for featured article"
    )
    show_byline_standard = models.BooleanField(
        default=True, verbose_name="Show byline for standard articles"
    )
    show_date_featured = models.BooleanField(
        default=True, verbose_name="Show date for featured article"
    )
    show_date_standard = models.BooleanField(
        default=True, verbose_name="Show date for standard articles"
    )
    show_category_featured = models.BooleanField(
        default=True, verbose_name="Show category for featured article"
    )
    show_category_standard = models.BooleanField(
        default=True, verbose_name="Show category for standard articles"
    )

    exclude_duplicates = models.BooleanField(
        default=False,
        verbose_name="Exclude duplicates",
        help_text="If checked, articles already displayed on the page will be excluded.",
    )

    html = models.TextField(blank=True)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def save(self, *args, **kwargs):
        feat = "1" if self.feature_first_article else "0"
        sum_feat = "1" if self.show_summary_featured else "0"
        sum_std = "1" if self.show_summary_standard else "0"
        title_feat = "1" if self.show_title_featured else "0"
        title_std = "1" if self.show_title_standard else "0"
        byline_feat = "1" if self.show_byline_featured else "0"
        byline_std = "1" if self.show_byline_standard else "0"
        date_feat = "1" if self.show_date_featured else "0"
        date_std = "1" if self.show_date_standard else "0"
        cat_feat = "1" if self.show_category_featured else "0"
        cat_std = "1" if self.show_category_standard else "0"
        exclude_duplicates = "1" if self.exclude_duplicates else "0"

        title = self.custom_title.replace(":", "") if self.custom_title else ""

        flags = f"{feat}:{sum_feat}:{sum_std}:{title}:{title_feat}:{title_std}:{byline_feat}:{byline_std}:{date_feat}:{date_std}:{cat_feat}:{cat_std}:{exclude_duplicates}"

        if self.block_type == "topic" and self.selected_topic:
            self.html = f"{{{{topic:{self.selected_topic.slug}:{self.num_articles}:{flags}}}}}"
        elif self.block_type == "category" and self.selected_category:
            self.html = f"{{{{category:{self.selected_category.slug}:{self.num_articles}:{flags}}}}}"
        elif self.block_type == "chart_of_the_week":
            self.html = f"{{{{chart_of_the_week:{self.num_articles}:{flags}}}}}"
        elif self.block_type == "creative_commons_gallery":
            self.html = "{{creative_commons_gallery}}"

        super(Block, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = [
            "name",
        ]


class Group(models.Model):
    name = models.CharField(max_length=200, unique=True)
    pages_include = models.TextField(blank=True)
    pages_exclude = models.TextField(blank=True)
    blocks = models.ManyToManyField(Block, through="BlockGroup", blank=True)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def block_list(self):
        return ", ".join([str(block) for block in self.blocks.all()])

    def get_blocks(self):
        return self.blocks.order_by("link_to_group")

    def __str__(self):
        return self.name

    class Meta:
        ordering = [
            "name",
        ]


class BlockGroup(models.Model):
    block = models.ForeignKey(
        Block, on_delete=models.CASCADE, related_name="link_to_group"
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField("position", null=True)

    def __str__(self):
        return str(self.group) + ":" + str(self.block)

    class Meta:
        ordering = [
            "position",
        ]

from django.db import models

# Create your models here.

BLOCK_TYPES = (
    ('standard', 'Standard HTML'),
    ('topic', 'Topic'),
    ('category', 'Category'),
)


class Block(models.Model):
    name = models.CharField(max_length=200, unique=True)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES, default='standard')

    selected_topic = models.ForeignKey('newsroom.Topic', on_delete=models.SET_NULL, null=True, blank=True)
    selected_category = models.ForeignKey('newsroom.Category', on_delete=models.SET_NULL, null=True, blank=True)
    num_articles = models.PositiveIntegerField(default=5, blank=True, null=True)
    feature_first_article = models.BooleanField(default=True, help_text="If checked, the first article will be styled as a featured article.")

    html = models.TextField(blank=True)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def save(self, *args, **kwargs):
        feat = "1" if self.feature_first_article else "0"
        if self.block_type == 'topic' and self.selected_topic:
            self.html = f"{{{{topic:{self.selected_topic.slug}:{self.num_articles}:{feat}}}}}"
        elif self.block_type == 'category' and self.selected_category:
            self.html = f"{{{{category:{self.selected_category.slug}:{self.num_articles}:{feat}}}}}"
        super(Block, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]


class Group(models.Model):
    name = models.CharField(max_length=200, unique=True)
    pages_include = models.TextField(blank=True)
    pages_exclude = models.TextField(blank=True)
    blocks = models.ManyToManyField(Block, through="BlockGroup",
                                    blank=True)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def block_list(self):
        return ", ".join([str(block) for block in self.blocks.all()])

    def get_blocks(self):
        return self.blocks.order_by('link_to_group')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]


class BlockGroup(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE,
                              related_name='link_to_group')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField("position", null=True)

    def __str__(self):
        return str(self.group) + ":" + str(self.block)

    class Meta:
        ordering = ['position', ]

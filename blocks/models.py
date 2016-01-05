from django.db import models

# Create your models here.

class Block(models.Model):
    name = models.CharField(max_length=200, unique=True)
    html = models.TextField(blank=True)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name',]


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
        ordering = ['name',]

class BlockGroup(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE,
                              related_name='link_to_group')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField("position", null=True)

    def __str__(self):
        return str(self.group) + ":" + str(self.block)

    class Meta:
        ordering = ['position',]

from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class SudokuQuerySet(models.QuerySet):

    def published(self):
        return self.filter(published__lte=timezone.now())

class Sudoku(models.Model):

    class Difficulty(models.TextChoices):
        UNKNOWN = '0', _('Unknown')
        VERY_EASY = '1', _('Very easy')
        EASY = '2', _('Easy')
        MEDIUM = '3', _('Medium')
        HARD = '4', _('Hard')
        VERY_HARD = '5', _('Very hard')
        EXTREMELY_HARD = '6', _('Extremely hard')

    puzzle = models.CharField(max_length=81, unique=True)
    solution = models.CharField(max_length=81, blank=True)
    number = models.IntegerField(null=True)
    published = models.DateTimeField(blank=True, null=True,
                                     verbose_name=_('publish time'))
    difficulty = models.CharField(max_length=1,
                                  choices=Difficulty.choices,
                                  default=Difficulty.UNKNOWN)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    objects = SudokuQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('sudoku:detail', args=[self.pk, ])

    def is_published(self):
        return (self.published is not None) and \
            (self.published <= timezone.now())

    def publish_now(self):
        if self.is_published() is False:
            self.published = timezone.now()
            self.save()

    is_published.boolean = True
    is_published.short_description = 'published'

    def __str__(self):
        return str(self.pk) + ': ' + str(self.published) + ' - ' + \
            self.difficulty + ' - ' + self.puzzle

    class Meta:
        ordering = ['-published', ]

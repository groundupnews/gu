from django.db import models
from django.urls import reverse
from target import target
from django.utils import timezone

class TargetQuerySet(models.QuerySet):

    def published(self):
        return self.filter(published__lte=timezone.now())

class Target(models.Model):
    letters = models.CharField(max_length=9, unique=True)
    words = models.TextField(blank=True)
    bullseye = models.CharField(max_length=1)
    published = models.DateTimeField(blank=True, null=True)
    public_solution = models.BooleanField(default=False)
    number = models.PositiveSmallIntegerField(default=0, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    objects = TargetQuerySet.as_manager()

    def is_published(self):
        return (self.published is not None) and \
            (self.published <= timezone.now())

    def splitWords(self):
        return self.words.split("\r\n")

    def wordCount(self):
        return len(self.splitWords())

    def lettersJson(self):
        letterArray = ["'" + l + "'" for l in self.letters]
        return  "[" + ",".join(letterArray) + "]"

    def hashedWords(self):
        hashed_words = [target.hashCode(w) for w in self.splitWords()]
        return hashed_words

    def nineLetterWord(self):
        return [w for w in self.splitWords() if len(w) == 9][0]

    def hashedNineLetterWord(self):
        return target.hashCode(self.nineLetterWord())

    def wordsWithoutNineLetter(self):
        return ' '.join([w for w in self.splitWords() if len(w) != 9])

    def __str__(self):
        return str(self.pk) + "-" + str(self.number) + ":" + self.letters

    def save(self, *args, **kwargs):
        if self.published and self.number == 0:
            objects = Target.objects.order_by("-number")
            if objects:
                latest = objects[0]
                number = latest.number + 1
            else:
                number = 1
            self.number = number
        super(Target, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('target:detail', args=[self.pk, ])

    class Meta:
        ordering = ['-number']

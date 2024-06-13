from django.db import models
from django.urls import reverse
from target import target
from django.utils import timezone

DEFAULT_RULES = """
PLEASE NOTE: THE RULES CHANGED ON 14 JUNE 2024.

Make words of at least four letters using the grid letters at most once.
The centre letter must be in every word.
There's one nine-letter word.

Except possibly for the nine-letter word:
- There are no plurals ending in s. (But geese would be allowed.)
- There are no third-person singular verbs ending in s (e.g. cooks in ‘He cooks bread’).
- There are no proper nouns.

The nine-letter word often has a South African flavour.

Words are drawn from our dictionary which has about 100,000 words.
You can either type the letters or click on them.
To delete a letter use the backspace key or click it again."""

class TargetQuerySet(models.QuerySet):

    def published(self):
        return self.filter(published__lte=timezone.now())

class Target(models.Model):
    letters = models.CharField(max_length=9, unique=True)
    words = models.TextField(blank=True)
    published = models.DateTimeField(blank=True, null=True)
    public_solution = models.BooleanField(default=False)
    publish_solution_after = models.SmallIntegerField(
        default=24, null=True,
        verbose_name="solution time",
        help_text="Make solution available after this many hours")
    clue = models.CharField(
        max_length=150, blank=True, help_text="Leave blank if no clue.")
    tweet_text = models.CharField(
        max_length=180,
        default="Try the latest GroundUp Target.",
        help_text="Blank for no tweet")
    tweet_solution_text = models.CharField(
        max_length=180,
        default="The solution for this GroundUp Target is now available.")

    tweeted = models.BooleanField(default=False, editable=False)
    tweeted_solution = models.BooleanField(default=False, editable=False)

    rules = models.TextField(default=DEFAULT_RULES, blank=True)
    number = models.PositiveSmallIntegerField(default=0, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    objects = TargetQuerySet.as_manager()

    def is_published(self):
        return (self.published is not None) and \
            (self.published <= timezone.now())

    def is_solution_public(self):
        if self.public_solution or \
           (self.is_published() and \
           self.published + timezone.timedelta(hours=self.publish_solution_after) \
            < timezone.now()):
           return True
        return False

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
        try:
            return [w for w in self.splitWords() if len(w) == 9][0]
        except:
            return ""

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
        ordering = ['-number', '-modified', ]

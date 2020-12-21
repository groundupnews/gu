from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from django.utils import timezone
from sudoku.models import Sudoku

class Command(BaseCommand):
    help = 'Load Sudoku puzzles from a file'

    def add_arguments(self, parser):
        parser.add_argument('file',  type=str)
        parser.add_argument('--start_date', type=str, default='0')
        parser.add_argument('--skip', type=int, default=7)

    def handle(self, *args, **options):

        skip = options['skip']
        if options['start_date'] == '0':
            start_date = timezone.now()
        else:
            s = options['start_date']
            start_date = timezone.datetime(int(s[0:4]), int(s[4:6]), int(s[6:8]),
                                           int(s[8:10]), int(s[10:12]), int(s[12:]))
        with open(options['file']) as f:
            lines = f.readlines()
            try:
                with transaction.atomic():
                    for line in lines:
                        line = line.strip()
                        puzzle, difficulty = line.split(" ")
                        if len(puzzle) != 81:
                            print("Puzzle length is incorrect", puzzle)
                            continue
                        for c in puzzle:
                            if c < '0' or c > '9':
                                print("Puzzle has invalid characters", puzzle)
                        try:
                            p = None
                            p = Sudoku.objects.get(puzzle=puzzle)
                            print("Puzzle exists (skipping):", p.pk, p.puzzle)
                        except Sudoku.DoesNotExist:
                            pass
                        if p is None:
                            s = Sudoku()
                            s.puzzle = puzzle
                            s.difficulty = difficulty
                            s.published = start_date
                            s.save()
                            start_date += timezone.timedelta(skip)
            except IntegrityError:
                print("Database integrity error. Transaction cancelled.")

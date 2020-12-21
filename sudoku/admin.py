from django.contrib import admin

from .models import Sudoku

class SudokuAdmin(admin.ModelAdmin):
    list_display = ('pk', 'puzzle', 'difficulty',
                    'modified', 'published', 'is_published')
    list_editable = ('puzzle', 'difficulty', )
    search_fields = ('puzzle', 'pk',)
    date_hierarchy = 'modified'
    ordering = ['-modified',]
    readonly_fields = ['created', 'modified', ]
    actions_on_bottom = True
    actions_on_top = True
    save_on_top = True

admin.site.register(Sudoku, SudokuAdmin)

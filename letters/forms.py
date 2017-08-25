from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.forms import ModelForm
from captcha.fields import ReCaptchaField
from .models import Letter


class LetterForm(ModelForm):
    captcha = ReCaptchaField()
    title = forms.CharField(min_length=5, max_length=55,
                            label='Title of your letter',
                            help_text='At least 5 and no more than 55 '
                            'characters.')
    text = forms.CharField(min_length=140, max_length=2100,
                           label='Text of your letter',
                           help_text='Blank lines separate paragraphs. '
                           'You can use URLs but not HTML. At '
                           'least 140 and no more than 2,100 characters '
                           '(about 340 words).',
                           widget=forms.Textarea(attrs={'rows': '10'}))
    byline = forms.CharField(min_length=5, max_length=200,
                             label='Yours sincerely',
                             help_text='Your real name(s) and, if you wish, '
                             'title(s) and designation(s). At least 5 and '
                             'no more than 200 characters.')
    email = forms.EmailField(label='Your email address',
                             max_length=200,
                             help_text='This will neither be displayed nor '
                             'shared with any third party.')
    check_this_1 = forms.CharField(max_length=10,
                                   widget=forms.HiddenInput,
                                   validators=[MaxLengthValidator(0)],
                                   required=False)
    check_this_2 = forms.CharField(max_length=10,
                                   initial="Pot",
                                   widget=forms.HiddenInput,
                                   validators=[MinLengthValidator(3),
                                               MaxLengthValidator(3)],
                                   required=True)

    class Meta:
        model = Letter
        fields = ['title', 'text', 'byline', 'email',
                  'check_this_1', 'check_this_2']

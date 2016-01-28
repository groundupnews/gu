from django.test import TestCase
from newsroom.models import Article
from newsroom import utils

class HtmlCleanUp(TestCase):

    def test_html_cleaners(self):
        """HTML is correctly cleaned"""

        html = "<p class='plod'></p><p>Hello</p><p class=''> &nbsp; </p><p class='test'> Good bye </p>"
        self.assertEqual(utils.remove_blank_paras(html),
                         "<p>Hello</p><p class='test'> Good bye </p>")

        html = '<img height="200px" width="100px" alt="Bla bla 1" src="/media/blabla1.jpg" /><img height="200px" width="100px" src="/media/blabla2.jpg" alt="Bla bla 2" />'

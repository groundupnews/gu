from django.test import TestCase, Client 
from django.contrib.auth.models import User
from newsroom.models import Article, Category
from django.utils import timezone
from .utils import parseSearchString

class TextSearch(TestCase):

    def test_search_strings(self):
        """Test parsing quoted and unquoted search strings
        
        Expected output:
        - Should split unquoted text into individual words
        - Should keep quoted text together as one term
        - Should handle mixed quoted and unquoted text correctly
        """
        s = 'The quick, "brown fox, jumps" over the lazy dog.'
        result = parseSearchString(s)
        comparator = ['The', 'quick', 'brown fox jumps',
                      'over', 'the', 'lazy', 'dog']
        self.assertEqual(result, comparator)

class SearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test articles
        category = Category.objects.create(name="News", slug="news")
        
        cls.article1 = Article.objects.create(
            title="Test search article one",
            slug="test-search-1",
            body="The quick brown fox jumps over lazy dogs",
            category=category
        )
        cls.article1.publish_now()

        cls.article2 = Article.objects.create(
            title="Another test article two", 
            slug="test-search-2",
            body="The lazy cat sleeps all day",
            category=category
        )
        cls.article2.publish_now()

    def test_basic_search(self):
        """Test basic search functionality
        
        Expected output:
        - Single word 'fox' should find 1 article
        - Word 'lazy' should find 2 articles
        """
        from .utils import searchArticlesAndPhotos
        
        # Test single word search
        results = searchArticlesAndPhotos("fox")
        self.assertEqual(len(results), 1, "Expected 1 result for search term 'fox'")
        self.assertEqual(results[0]['pk'], self.article1.pk, 
                        "Expected to find article1 with 'fox' in content")

        # Test multiple word search
        results = searchArticlesAndPhotos("lazy")
        self.assertEqual(len(results), 2, "Expected 2 results for search term 'lazy'")

    def test_search_view(self):
        """Test the advanced search view
        
        Expected output:
        - Search for 'fox' should return article with 'fox' in content
        - Search for 'missing' should return no articles
        - View should use correct /advanced_search/ URL
        - View should accept search parameters and return 200 status
        """
        c = Client()
        # Add required parameters for AdvancedSearchForm with correct URL path
        params = {
            'adv_search': 'fox',
            'search_type': 'article',
            'is_simple': 'true'
        }
        response = c.get('/advanced_search/', params)
        self.assertEqual(response.status_code, 200, 
                        "Expected 200 OK response from search view")
        self.assertContains(response, "Test search article one",
                           msg_prefix="Expected to find article with 'fox' in search results")
        
        params['adv_search'] = 'missing'
        response = c.get('/advanced_search/', params)
        self.assertEqual(response.status_code, 200,
                        "Expected 200 OK response for search with no results")
        self.assertNotContains(response, "Test search article",
                             msg_prefix="Expected no articles for term 'missing'")

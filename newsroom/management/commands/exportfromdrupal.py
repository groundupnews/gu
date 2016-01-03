from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from newsroom.models import Article
import logging

from bs4 import BeautifulSoup

def process(start, finish, html_file):
    soup = BeautifulSoup(open(html_file), "lxml")
    articles = soup.find_all("div")
    print("Number of articles", len(articles))
    if finish > len(articles):
        print("Truncating finish to ", len(articles))
        finish = len(articles)
    if start > finish:
        print("Start > finish")
        return

    articles = articles[start:finish]
    for idx,article in enumerate(articles):
        # Title, Link and date published
        link = article.find("a")["href"]
        link = 'http://gutest.nathangeffen.webfactional.com' + str(link)
        if link.find("/gallery/") == -1:
            print("Processing: ", idx + start, link)
        else:
            print("Ignoring: ", idx + start, link)
            continue

        newarticle = Article()
        newarticle.title = article.find("p",
                                        attrs={'class' : 'title'}).get_text(). \
            replace("â€™", "'").replace("â€œ",'"').replace("â€",'"')
        newarticle.slug = slugify(str(link).rpartition("/")[2])
        import datetime
        published = article.find('p', attrs={'class' : 'date'}).get_text()[2:] \
                    + " +0200"
        published_conv = datetime.datetime.strptime(published,
                                                    "%d/%m/%Y - %H:%M %z")
        newarticle.published = published_conv

        # Fetch article from web
        import urllib.request
        with urllib.request.urlopen(link) as response:
            html = response.read()
        soup = BeautifulSoup(html, "lxml")

        # Byline
        try:
            newarticle.byline = soup.find \
            ("div", { "class" : "article-author" }).get_text()
        except:
            print("Byline not found")

        # Intro
        try:
            intro = soup.find("div", {"class" : "article-intro"})
            intro = intro.find("p")
            intro["class"] = "intro"
            newarticle.summary_text = str(intro)
        except:
            print("Intro not found")

        try:
            primary_image = soup.find("div", {"class" : "article-image"}). \
                            find("img")
            link = primary_image["src"]
            link = link.replace("http://gutest.nathangeffen.webfactional.com",
                                "http://groundup.org.za")
            newarticle.external_primary_image = link.replace("/column_width/",
                                                             "/article_image/")
            newarticle.primary_image_size = "LEAVE"
        except:
            print("Primary image not found")

        try:
            newarticle.primary_image_caption = primary_image["alt"]
        except:
            print("Primary image caption not found")

        # Body

        try:
            text = soup.find("div", {"class":"article-body"}). \
                   find("div", {"class":"field-item"})
        except:
            print("No text")
            text = ""

        body = str(intro) + str(text) # "".join([str(item) for item in text])
        newarticle.body = body

        # category

        try:
            category = soup.find("div", attrs={'class' :
                                               'article-category'}).get_text()

            if category.lower() == "news":
                newarticle.category = "news"
            elif category.lower() == "featured story":
                newarticle.category = "featured story"
            elif category.lower() == "photo essay":
                newarticle.category = "photo essay"
            elif category.lower() == "photo":
                newarticle.category = "photo"
            elif category.lower() == "opinion":
                newarticle.category = "opinion"
            elif category.lower() == "brief":
                newarticle.category = "brief"
            elif category.lower() == "analysis":
                newarticle.category = "analysis"
            else:
                print("Unknown category: ", category)
        except:
            print("No category")

        # Topics
        try:
            topics = soup.find("div", {"class":"article-subject"}). \
                     get_text(", ")
        except:
            print("No topics")
            topics = ""
        try:
            tags = soup.find("div", {"class":"article-tags"}).get_text(", ")
        except:
            tags = ""

        if tags:
            if topics:
                topics += ", " + tags
            else:
                topics = tags

        topics_split = topics.split(",")
        if len(topics_split) > 8:
            topics = ", ".join(topics_split[0:8])
        newarticle.topics = topics

        # Saving
        try:
            article_to_replace = Article.objects.get(slug=newarticle.slug)
        except Article.DoesNotExist:
            print("Saving as new article")
            newarticle.save()
        else:
            print("Updating existing article")
            newarticle.pk = article_to_replace.pk
            newarticle.created = article_to_replace.created
            newarticle.save()


class Command(BaseCommand):
    help = 'Exports from the Drupal production GroundUp site to the new one'

    def add_arguments(self, parser):
        parser.add_argument('start', type=int)
        parser.add_argument('finish', type=int)
        parser.add_argument('html_file')


    def handle(self, *args, **options):
        start = options["start"]
        finish = options["finish"]
        html_file = options["html_file"]
        print("Processing with", start, finish, html_file)
        process(start, finish, html_file)

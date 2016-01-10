from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from newsroom.models import Article
import logging
import urllib.request

from bs4 import BeautifulSoup

def process(start, finish, html_file):
    soup = BeautifulSoup(open(html_file), "lxml")

    articles = soup.find_all("div")
    # for article in articles:
    #     url = article.find("a")["href"]
    #     title = article.find("p", attrs={'class' : 'title'}).get_text()
    #     article_date = article.find("p", attrs={'class' : 'date'}).get_text()
    #     title = title.replace('\n', ' ').replace('\r', '')
    #     article_date = article_date.replace('\n', ' ').replace('\r', '')
    #     print( (url + " @ " + title + " | " + article_date).strip() )
    # return

    with open(html_file) as f:
        articles = f.readlines()
    print("Number of articles", len(articles))
    if finish > len(articles):
        print("Truncating finish to ", len(articles))
        finish = len(articles)
    if start > finish:
        print("Start > finish")
        return

    articles = articles[start:finish]

    for idx,line in enumerate(articles):
        link = line.partition(" @ ")[0]
        title = line.partition(" @ ")[2].partition(" | ")[0].strip()
        if len(title) > 200:
            title = title[0:200]
        date_time = line.partition(" | ")[2].strip() + " +0200"
        slug = slugify(link.rpartition("/")[2])
        new_link = "http://groundup.org.za/article/" + slug
        old_link = "http://gutest.nathangeffen.webfactional.com" + link

        html = ""

        newarticle = Article()
        newarticle.title = title
        newarticle.slug = slug
        import datetime
        newarticle.published = datetime.datetime.strptime(date_time,
                                                    "%d/%m/%Y - %H:%M %z")
        html = ""
        try:
            with urllib.request.urlopen(old_link) as response:
                html = response.read()
        except:
            print("CRITICAL: Can't find old link", old_link)
            continue
        html = str(html)
        pos = html.find('<div class="field field-name-field-where field-type-text field-label-above"><div class="field-label">Where is the event:&nbsp;</div>')

        if pos == -1:
            print("PROCESSING:", str(idx + start) + " " + link)
        else:
            print("IGNORING:", link)
            continue

        soup = BeautifulSoup(html, "lxml")

        # Byline
        try:
            newarticle.byline = soup.find \
            ("div", { "class" : "article-author" }).get_text()
        except:
            newarticle.byline = ""
            print("Byline not found")

        # Intro
        intro = ""
        try:
            intro = soup.find("div", {"class" : "article-intro"})
            intro = intro.find("p")
            intro["class"] = "intro"
            newarticle.summary_text = str(intro)
        except:
            intro = ""
            print("Intro not found")

        primary_image = ""
        try:
            primary_image = soup.find("div", {"class" : "article-image"}). \
                            find("img")
            link = primary_image["src"]
            link = link.replace("http://gutest.nathangeffen.webfactional.com",
                                "http://groundup.org.za")
            newarticle.external_primary_image = link.replace("/column_width/",
                                                             "/article_image/")
            newarticle.primary_image_size = "LEAVE"
            primary_image_found = True
        except:
            print("Primary image not found")
            primary_image_found = False

        try:
            newarticle.primary_image_caption = primary_image["alt"]
        except:
            try:
                newarticle.primary_image_caption = str(soup.find("div", \
                    {"class": "field-name-field-image-description"})).\
                    replace("\\n","").replace("\\'","'")
            except:
                newarticle.primary_image_caption = ""
                print("Primary image caption not found")

        if newarticle.summary_text == "" and primary_image_found == False:
            intro = newarticle.primary_image_caption
            newarticle.primary_image_caption = ""
            print("Swapping caption and intro")

        try:
            text = soup.find("div", {"class":"article-body"}). \
                   find("div", {"class":"field-item"})
        except:
            try:
                text = soup.find("div", {"class":"content"}). \
                       find("div", {"class":"field-item"})
            except:
                print("No text")
                text = ""

        if str(intro) != "None":
            body = str(intro) + str(text) # "".join([str(item) for item in text])
        else:
            body = str(text)

        newarticle.body = body.replace("\\n"," ")

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
            elif category.lower() == "photo story":
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

        # # Topics
        # try:
        #     topics = soup.find("div", {"class":"article-subject"}). \
        #              get_text(", ")
        # except:
        #     print("No topics")
        #     topics = ""
        # try:
        #     tags = soup.find("div", {"class":"article-tags"}).get_text(", ")
        # except:
        #     tags = ""

        # if tags:
        #     if topics:
        #         topics += ", " + tags
        #     else:
        #         topics = tags

        # topics_split = topics.split(",")
        # if len(topics_split) > 8:
        #     topics = ", ".join(topics_split[0:8])
        # newarticle.topics = topics

        # Disqus
        newarticle.disqus_id = "node/"
        id = html.partition("/node/")[2][0:4]
        digits = [str(x) for x in list(range(10))]
        if id[0] in digits:
            newarticle.disqus_id = newarticle.disqus_id + id[0]
        if id[1] in digits:
            newarticle.disqus_id = newarticle.disqus_id + id[1]
        if id[2] in digits:
            newarticle.disqus_id = newarticle.disqus_id + id[2]
        if id[3] in digits:
            newarticle.disqus_id = newarticle.disqus_id + id[3]


        newarticle.include_in_rss = False
        newarticle.exclude_from_list_views = True

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
    return


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

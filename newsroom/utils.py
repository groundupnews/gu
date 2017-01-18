import re
import html
import string
import random
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from random import randint

from django.test import TestCase
from newsroom.settings import SUPPORT_US_IMAGES, ADVERT_CODE
from django.conf import settings

''' Can be used to prevent staff from getting cached pages.
'''

def cache_except_staff(decorator):
    """ Returns decorated view if user is not staff. Un-decorated otherwise """

    def _decorator(view):
        decorated_view = decorator(view)

        def _view(request, *args, **kwargs):

            if request.user.is_staff:
                # view without @cache
                return view(request, *args, **kwargs)
            else:
                # view with @cache
                return decorated_view(request, *args, **kwargs)

        return _view

    return _decorator

'''Used to find visible text in html.
Courtesy of: http://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
'''
def visible_text_in_html(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True

'''Replace bad html with good. Not foolproof, but should cover most cases
that arise in the editor.
'''

blankpara_regex = re.compile(r'<p[^>]*?>\s*?</p>|<p[^>]*?>\s*?&nbsp;\s*?</p>')

img_regex = re.compile(r'(<img(.*?))(height="(.*?)")(.*?)(width="(.*?)")(.*?)(>)')

figure_regex = re.compile(r'(<p>)(.*?)(<img)(.*?)(/>)(.*?)(</p>)(.*?)\r\n(<p) (class="caption")(.*?)>(.*?)(</p>)')

def remove_blank_paras(html):
    return blankpara_regex.sub(r'', html)

def replaceImgHeightWidthWithClass(soup):
    try:
        for tag in soup.find_all("img"):
            # This deals with CKEditor's image insertion
            if tag.has_attr("style"):
                # Don't do anything if class is leave
                if tag.has_attr("class"):
                    if "leave" in tag["class"]:
                        continue
                del tag["style"]
            # This deals with TinyMCE's image insertion
            if tag.has_attr("height") and tag.has_attr("width"):
                # Don't do anything if class is leave
                if tag.has_attr("class"):
                    if "leave" in tag["class"]:
                        continue
                del tag["height"]
                del tag["width"]
        return soup
    except:
        return soup

def replacePImgWithFigureImg(soup):
    images = soup.find_all("img")
    for image in images:
        parent = image.find_parent()
        if parent and parent.name == "p":
            parent.name = "figure"
    captions = soup.find_all("p", "caption")

    for caption in captions:
        if caption.find_parent().name != "figure":
            sibling = caption.find_previous_sibling()
            if sibling.name == "figure":
                del caption["class"]
                caption.name = "figcaption"
                sibling.append(caption)
    return soup

def fixEditorSummary(soup):
    uls = list(set([item.parent for item in \
                    [tag.parent for tag in \
                     soup.find_all("div","editor-summary")] \
                    if item.parent is not None]))
    for ul in uls:
        divs = ul.find_all("div", "editor-summary")
        for div in divs:
            del div["class"]
        d = soup.new_tag("div")
        d["class"] = "editor-summary"
        ul.wrap(d)
    return soup

def removeGoogleDocsSpans(soup):
    spans = soup.find_all("span")
    deletes_exist = False
    for span in spans:
        if span.has_attr("id"):
            if span["id"][0:18] == 'docs-internal-guid':
                span.name = "_delete_me_"
                p = span.parent
                if p:
                    p._delete_me_.unwrap()

    return soup

# <div class="embed-responsive embed-responsive-16by9"><iframe allowfullscreen="" frameborder="0" height="315" src="https://www.youtube.com/embed/WsAn5AgAF0I" width="560"></iframe></div>

def processYouTubeDivs(soup):
    youtubedivs = soup.find_all('div', {'class':"youtube"})
    for div in youtubedivs:
        div["class"] = "embed-responsive embed-responsive-16by9"
        d = BeautifulSoup(div.string, "html.parser")
        div.string = ""
        div.append(d)
    return soup

def processSoundCloudDivs(soup):
    soundclouddivs = soup.find_all('div', {'class':"soundcloud"})
    for div in soundclouddivs:
        div["class"] = ""
        sc = BeautifulSoup(div.string, "html.parser")
        iframe = sc.find("iframe")
        iframe["height"] = 100
        div.string = ""
        div.append(sc)
    return soup

def processSupportUs(soup):
    asides = soup.find_all('aside', {'class':"supportus-edit"})
    for aside in asides:
        aside['class'] = "supportus"
        aside.string = ""
        ad_to_run = randint(0, len(SUPPORT_US_IMAGES) - 1)
        image_url = SUPPORT_US_IMAGES[ad_to_run]
        supportimage = soup.new_tag('img', src=settings.STATIC_URL + image_url)
        aside.append(supportimage)
    return soup

def processAdverts(soup):
    asides = soup.find_all('aside', {'class':"article-advert-edit"})
    for aside in asides:
        aside['class'] = "article-advert"
        aside.string = ""
        print("DO:", ADVERT_CODE)
        advert = BeautifulSoup(ADVERT_CODE, "html.parser")
        print("D1:", advert)
        aside.append(advert)
    return soup


def replaceBadHtmlWithGood(html):
    html = html.replace('dir="ltr"',"")
    html = remove_blank_paras(html)
    soup = BeautifulSoup(html, "html.parser")
    soup = replaceImgHeightWidthWithClass(soup)
    soup = replacePImgWithFigureImg(soup)
    soup = fixEditorSummary(soup)
    soup = removeGoogleDocsSpans(soup)
    soup = processYouTubeDivs(soup)
    soup = processSoundCloudDivs(soup)
    soup = processSupportUs(soup)
    soup = processAdverts(soup)
    return str(soup)

def get_edit_lock_msg(user):
    message = \
    "Changes not saved. User " + str(user) + " edited the article " \
    "after you opened this page. Copy and paste your changes somewhere " \
    "safe (like a text editor). Then open this page again."
    return message


# Used to generate random passwords
# Source: http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python

def generate_pwd(size=12, chars=string.ascii_letters + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

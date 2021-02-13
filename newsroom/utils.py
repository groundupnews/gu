import random
import re
import string
from random import randint
import os
from urllib.parse import unquote

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.sites.models import Site

# from newsroom.settings import ADVERT_CODE
from newsroom.settings import SUPPORT_US_IMAGES


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


'''Replace bad html with good. Not foolproof, but should cover most cases
that arise in the editor.
'''

blankpara_regex = re.compile(r'<p[^>]*?>\s*?</p>|<p[^>]*?>\s*?&nbsp;\s*?</p>')


def remove_unnecessary_white_space(html):
    html = re.sub('&nbsp;', ' ', html)
    html = re.sub(' +', ' ', html)
    return blankpara_regex.sub(r'', html)


def replaceImgHeightWidthWithClass(soup):
    try:
        for tag in soup.find_all("img"):
            # This deals with CKEditor's image insertion
            if tag.has_attr("style"):
                # Don't do anything if class is leave or this is the counter
                if tag.has_attr("class"):
                    if "leave" in tag["class"]:
                        continue
                if tag.has_attr("id"):
                    if tag["id"] == "gu_counter":
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
            if sibling and sibling.name == "figure":
                del caption["class"]
                caption.name = "figcaption"
                sibling.append(caption)
    return soup


def fixEditorSummary(soup):
    uls = list(set([item.parent for item in
                    [tag.parent for tag in
                     soup.find_all("div", "editor-summary")]
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
    for span in spans:
        if span.has_attr("id"):
            if span["id"][0:18] == 'docs-internal-guid':
                span.name = "_delete_me_"
                p = span.parent
                if p:
                    p._delete_me_.unwrap()

    return soup


def processDashes(soup):
    # em-dash
    target = soup.find_all(text=re.compile(r' --- '))
    for dashes in target:
        dashes.replace_with(dashes.replace('---', "\u2014"))
    # en-dash
    target = soup.find_all(text=re.compile(r' -- '))
    for dashes in target:
        dashes.replace_with(dashes.replace('--', "\u2013"))
    return soup


def processYouTubeDivs(soup):
    youtubedivs = soup.find_all('div', {'class': "youtube"})
    for div in youtubedivs:
        div["class"] = "embed-responsive embed-responsive-16by9"
        d = BeautifulSoup(div.string, "html.parser")
        div.string = ""
        div.append(d)
    return soup


def processSoundCloudDivs(soup):
    soundclouddivs = soup.find_all('div', {'class': "soundcloud"})
    for div in soundclouddivs:
        div["class"] = ""
        sc = BeautifulSoup(div.string, "html.parser")
        iframe = sc.find("iframe")
        iframe["height"] = 100
        div.string = ""
        div.append(sc)
    return soup


def processSupportUs(soup):
    asides = soup.find_all('aside', {'class': "supportus-edit"})
    for aside in asides:
        aside['class'] = "supportus"
        aside.string = ""
        ad_to_run = randint(0, len(SUPPORT_US_IMAGES) - 1)
        image_url = SUPPORT_US_IMAGES[ad_to_run]
        supporta = soup.new_tag('a', href=settings.DONATE_PAGE)
        supportimage = soup.new_tag('img',
                                    src=settings.STATIC_URL + image_url,
                                    alt="Support GroundUp image")
        supporta.append(supportimage)
        aside.append(supporta)
    return soup


def processAdverts(soup):
    asides = soup.find_all('aside', {'class': "article-advert-edit"})
    for aside in asides:
        aside['class'] = ""
        aside.string = ""
        advert = BeautifulSoup("", "html.parser")
        aside.append(advert)
    # for aside in asides:
    #     aside['class'] = "article-advert"
    #     aside.string = ""
    #     if settings.AB_TEST_ADS is True:
    #         r = randint(0, 1)
    #         if r == 0:
    #             advert = BeautifulSoup(settings.ADVERT_CODE_GOOGLE,
    #                                    "html.parser")
    #         else:
    #             advert = BeautifulSoup(settings.ADVERT_CODE_AMAZON,
    #                                    "html.parser")
    #     else:
    #         advert = BeautifulSoup(ADVERT_CODE, "html.parser")
    #     aside.append(advert)
    return soup

def linkImages(soup):
    soup_copy = soup
    try:
        images = soup.find_all('img')
        # Exclude images with class leave
        images = [i for i in images if not (i.has_attr("class") and
                                            "leave" in i["class"])]
        # Exclude if not a versioned image
        images = [i for i in images if i.has_attr("src") and
                  ("_versions" in i["src"] and
                  ("_extra_large" in i["src"] or "_huge" in i["src"]))]
        lenVersions = len("_versions/")
        extra_large_len = len("_extra_large")
        huge_len = len("_huge")
        for img in images:
            url = img["src"]
            vBegin = url.find("_versions/")
            vEnd = vBegin + lenVersions

            eBegin = url.find("_extra_large")
            if eBegin > -1:
                eEnd = eBegin + extra_large_len
            else:
                eBegin = url.find("_huge")
                eEnd = eBegin + huge_len

            urlnew = url[:vBegin] + "uploads/" + url[vEnd:eBegin] + url[eEnd:]
            if img.parent.name == 'a':
                img.parent["href"] = urlnew
                img.parent["class"] = "bigger-image"
                img.parent["target"] = "_blank"
            else:
                link = soup.new_tag("a")
                link["href"] = urlnew
                link["target"] = "_blank"
                link["class"] = "bigger-image"
                img.wrap(link)
        return soup
    # This code is not important enough to be worth crashing the site on
    # an exception
    except:
        return soup_copy

def warnImageTooBig(soup):
    base_https_url = "https://" + Site.objects.get_current().domain
    base_http_url = "http://" + Site.objects.get_current().domain
    images = soup.find_all('img')
    for img in images:
        try:
            if base_https_url == img['src'][:len(base_https_url)]:
                img['src'] = img['src'][len(base_https_url):]
            if base_http_url == img['src'][:len(base_http_url)]:
                img['src'] = img['src'][len(base_http_url):]

            filename = settings.MEDIA_ROOT + \
                       unquote(img['src'][len(settings.MEDIA_URL):])

            size = os.stat(filename).st_size
            if 'warn_big' in img.get('class', []):
                img.get('class').remove('warn_big')
            if 'too_big' in img.get('class', []):
                img.get('class').remove('too_big')
            if size > 250000:
                img['class'] = img.get('class', []) + ['too_big']
            elif size > 150000:
                img['class'] = img.get('class', []) + ['warn_big']
        except:
            pass

def replaceBadHtmlWithGood(html):
    html = html.replace('dir="ltr"', "")
    html = remove_unnecessary_white_space(html)
    soup = BeautifulSoup(html, "html.parser")
    soup = replaceImgHeightWidthWithClass(soup)
    # While nice to make images into figures, it is a real struggle for
    # users of CKEditor.
    # soup = replacePImgWithFigureImg(soup)
    soup = fixEditorSummary(soup)
    soup = removeGoogleDocsSpans(soup)
    soup = processDashes(soup)
    soup = processYouTubeDivs(soup)
    soup = processSoundCloudDivs(soup)
    soup = linkImages(soup)
    warnImageTooBig(soup)

    return str(soup)


def get_edit_lock_msg(user):
    message = \
              "Changes not saved. User " + str(user) + " edited the article " \
              "after you opened this page. Copy and paste your changes " \
              "somewhere safe (like a text editor). Then open this page again."
    return message

# Used to generate random passwords. Source:
# http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python


def generate_pwd(size=12, chars=string.ascii_letters + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

def get_first_image(html):
    soup = BeautifulSoup(html, "html.parser")
    img = soup.find('img')

    if img:
        if 'src' in img.attrs:
            return img.attrs['src']
        else:
            return ""
    else:
        return ""

def insertPixel(html, pk, slug):
    # Not worth crashing for
    soup = BeautifulSoup(html, "html.parser")
    style = "height:1px; width:1px; visibility:none;"
    img = soup.find('img', id='gu_counter')
    if img is None:
        paras = soup.find_all('p')
        if len(paras) > 2:
            url = 'https://republish.groundup.org.za/counter/hit/' + \
                str(pk) +  '/' + slug
            img = soup.new_tag('img',
                               src=url,
                               id="gu_counter",
                               alt="",
                               height="1",
                               width="1",
                               style=style)
            img['class'] = 'leave'
            paras[2].append(img)
    else:
        img['height'] = "1"
        img["width"] = "1"
        img["style"] = style
        img['class'] = "leave"
        img['alt'] = ""
    html = str(soup)


    return html


def get_first_caption(html):
    soup = BeautifulSoup(html, "html.parser")
    p = soup.find('p', class_='caption')

    if p:
        return p.text
    else:
        return ""

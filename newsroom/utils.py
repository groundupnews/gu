import re
from bs4 import BeautifulSoup

from django.test import TestCase

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

def replaceImgHeightWidthWithClass(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
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
        return str(soup)
    except:
        return html

def replacePImgWithFigureImg(html):
    soup = BeautifulSoup(html, "html.parser")
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
    return str(soup)


def replaceBadHtmlWithGood(html):
    html = html.replace('dir="ltr"',"")
    html = remove_blank_paras(html)
    html = replaceImgHeightWidthWithClass(html)
    html = replacePImgWithFigureImg(html)
    return html

import re

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

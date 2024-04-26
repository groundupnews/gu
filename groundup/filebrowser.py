import os
import re

from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.shortcuts import HttpResponse, render
from django.core.files.storage import (DefaultStorage, FileSystemStorage,
                                       default_storage)
from django.utils.translation import gettext as _

from filebrowser.sites import FileBrowserSite, get_breadcrumbs, get_filterdate, get_settings_var
from filebrowser.base import FileListing
from filebrowser.settings import (ADMIN_THUMBNAIL, ADMIN_VERSIONS,
                                  CONVERT_FILENAME, DEFAULT_PERMISSIONS,
                                  DEFAULT_SORTING_BY, DEFAULT_SORTING_ORDER,
                                  DIRECTORY, EXCLUDE, EXTENSION_LIST,
                                  EXTENSIONS, LIST_PER_PAGE, MAX_UPLOAD_SIZE,
                                  NORMALIZE_FILENAME, OVERWRITE_EXISTING,
                                  SEARCH_TRAVERSE, SELECT_FORMATS,
                                  UPLOAD_TEMPDIR, VERSIONS, VERSIONS_BASEDIR)
from filebrowser.actions import (flip_horizontal, flip_vertical,
                                 rotate_90_clockwise,
                                 rotate_90_counterclockwise, rotate_180)


class CustomFileBrowserSite(FileBrowserSite):

    def browse(self, request):
        "Browse Files/Directories."
        filter_re = []
        for exp in EXCLUDE:
            filter_re.append(re.compile(exp))

        # do not filter if VERSIONS_BASEDIR is being used
        if not VERSIONS_BASEDIR:
            for k, v in VERSIONS.items():
                exp = (r'_%s(%s)$') % (k, '|'.join(EXTENSION_LIST))
                filter_re.append(re.compile(exp, re.IGNORECASE))

        def filter_browse(item):
            "Defining a browse filter"
            filtered = item.filename.startswith('.')
            for re_prefix in filter_re:
                if re_prefix.search(item.filename):
                    filtered = True
            if filtered:
                return False
            return True

        query = request.GET.copy()
        path = u'%s' % os.path.join(self.directory, query.get('dir', ''))

        filelisting = self.filelisting_class(
            path,
            filter_func=filter_browse,
            sorting_by=query.get('o', DEFAULT_SORTING_BY),
            sorting_order=query.get('ot', DEFAULT_SORTING_ORDER),
            site=self)

        files = []
        if SEARCH_TRAVERSE and query.get("q"):
            listing = filelisting.files_walk_filtered()
        else:
            listing = filelisting.files_listing_filtered()

        # If we do a search, precompile the search pattern now
        do_search = query.get("q")
        if do_search:
            re_q = re.compile(query.get("q").lower(), re.M)

        filter_type = query.get('filter_type')
        filter_date = query.get('filter_date')
        filter_format = query.get('type')

        for fileobject in listing:
            # date/type filter, format filter
            append = False
            if (not filter_type or fileobject.filetype == filter_type) and \
                    (not filter_date or get_filterdate(filter_date, fileobject.date or 0)) and \
                    (not filter_format or filter_format in fileobject.format):
                append = True
            # search
            if do_search and not re_q.search(fileobject.filename.lower()):
                append = False
            # always show folders with popups
            # otherwise, one is not able to select/filter files within subfolders
            # if fileobject.filetype == "Folder":
            #     append = True
            # append
            if append:
                files.append(fileobject)

        filelisting.results_total = len(listing)
        filelisting.results_current = len(files)

        p = Paginator(files, LIST_PER_PAGE)
        page_nr = request.GET.get('p', '1')
        try:
            page = p.page(page_nr)
        except (EmptyPage, InvalidPage):
            page = p.page(p.num_pages)

        request.current_app = self.name
        return render(request, 'filebrowser/index.html', {
            'p': p,
            'page': page,
            'filelisting': filelisting,
            'query': query,
            'title': _(u'FileBrowser'),
            'settings_var': get_settings_var(directory=self.directory),
            'breadcrumbs': get_breadcrumbs(query, query.get('dir', '')),
            'breadcrumbs_title': "",
            'filebrowser_site': self
        })

storage = DefaultStorage()
# Default FileBrowser site
site = CustomFileBrowserSite(name='filebrowser', storage=storage)

site.add_action(flip_horizontal)
site.add_action(flip_vertical)
site.add_action(rotate_90_clockwise)
site.add_action(rotate_90_counterclockwise)
site.add_action(rotate_180)

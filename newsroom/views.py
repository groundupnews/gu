from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.views import generic
from django.views.generic import View
from django.db.models import Q
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import Site
from django.utils.html import strip_tags
from django.http import HttpResponseForbidden
from django.views.decorators.http import last_modified
from django.utils import timezone
from django.http import JsonResponse
from pgsearch.utils import searchPostgresDB
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from bs4 import BeautifulSoup

import datetime
import logging

from . import models
from . import settings
from letters.settings import DAYS_AGO
from . import utils
from .forms import ArticleListForm, ArticleForm

from letters.models import Letter
from blocks.models import Group

logger = logging.getLogger(__name__)


def get_blocks(group_name="Home"):
    try:
        return Group.objects.get(name=group_name).get_blocks()
    except:
        return []


def get_blocks_in_context(context, group_name="Home", context_key="blocks"):
    context[context_key] = get_blocks(group_name)
    return context


class ArticleList(generic.ListView):
    context_object_name = 'article_list'
    template_name = "newsroom/article_list.html"
    paginate_by = settings.ARTICLES_PER_PAGE

    def get_queryset(self):
        return models.Article.objects.list_view()

    def get_context_data(self, **kwargs):
        context = super(ArticleList, self).get_context_data(**kwargs)
        context = get_blocks_in_context(context)
        context['most_popular_html'] = \
            models.MostPopular.get_most_popular_html()
        date_from = timezone.now() - datetime.timedelta(days=DAYS_AGO)
        context['letters'] = Letter.objects.published().\
            filter(published__gte=date_from).order_by('-published')
        return context


def last_article_modified(request):
    return models.Article.objects.published().latest("modified").modified


class HomePage(ArticleList):
    template_name = "newsroom/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context = get_blocks_in_context(context, "Home_Top", "topblocks")
        return context

    # LEAVE THIS COMMENTED OUT CODE IN CASE OF EMERGENCY IN
    # WHICH CODE NEEDS TO CHANGE URGENTLY.

    # def get(self, request, *args, **kwargs):
    # Add messages here. E.g.
    # messages.add_message(request, messages.INFO,
    #                      "We're only publishing urgent "
    #                      "news until 10 January. Have a "
    #                      "safe holiday season.")
    # request = super(HomePage, self).get(request, args, kwargs)
    # return request


home_page_view = HomePage.as_view()
home_page_view = last_modified(last_article_modified)(home_page_view)


class OpinionAnalysisList(ArticleList):

    def get_queryset(self):
        return models.Article.objects.list_view().filter(
            Q(category__name="Opinion") |
            Q(category__name="Analysis"))

    def get_context_data(self, **kwargs):
        context = super(OpinionAnalysisList, self).get_context_data(**kwargs)
        context['heading'] = "Opinion and Analysis"
        return context


class AuthorList(generic.ListView):
    model = models.Author


class AuthorDetail(ArticleList):

    def get_queryset(self):
        self.author = get_object_or_404(models.Author, pk=self.args[0])
        return models.Article.objects.list_view().filter(
            Q(author_01=self.author) | Q(author_02=self.author) |
            Q(author_03=self.author) | Q(author_04=self.author) |
            Q(author_05=self.author) |
            Q(cached_byline_no_links__icontains=str(self.author)))

    def get_context_data(self, **kwargs):
        context = super(AuthorDetail, self).get_context_data(**kwargs)
        context['heading'] = "Articles by " + str(self.author)
        context['image'] = self.author.photo
        context['description'] = self.author.description
        return context


class CategoryList(generic.ListView):
    model = models.Category


class CategoryDetail(ArticleList):

    def get_queryset(self):
        self.category = get_object_or_404(models.Category,
                                          name__iexact=self.args[0])
        return models.Article.objects.list_view(). \
            filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super(CategoryDetail, self).get_context_data(**kwargs)
        context['heading'] = self.category.name
        return context


class RegionList(generic.ListView):
    model = models.Region


class RegionDetail(ArticleList):

    def get_queryset(self):
        self.region = get_object_or_404(models.Region, name=self.args[0])
        return models.Article.objects.list_view(). \
            filter(Q(region__in=self.region.get_descendants()) |
                   Q(region=self.region))

    def get_context_data(self, **kwargs):
        context = super(RegionDetail, self).get_context_data(**kwargs)
        query = Q(name=self.region.name)
        region_name = str(self.region)
        while region_name:
            region_name = region_name.rpartition("/")[0]
            query = query | Q(name=region_name)
        regions = models.Region.objects.filter(query)
        regions = ["<a href='" + reverse("region.detail",
                                         args=(region.name, )) + "'>"
                   + region.name.rpartition("/")[2] + "</a>"
                   for region in regions]
        context['title'] = str(self.region).rpartition("/")[2]
        context['heading'] = "|".join(regions)
        return context


class TopicList(generic.ListView):
    model = models.Topic


class TopicDetail(ArticleList):

    def get_queryset(self):
        self.topic = get_object_or_404(models.Topic, slug=self.args[0])
        if self.topic.newest_first is True:
            return models.Article.objects.published(). \
                filter(topics=self.topic)
        else:
            return models.Article.objects.published(). \
                filter(topics=self.topic).order_by("published")

    def get_context_data(self, **kwargs):
        context = super(TopicDetail, self).get_context_data(**kwargs)
        context['heading'] = self.topic.name.upper()
        context['topic'] = self.topic
        return context

    def get_template_names(self):
        return (self.topic.template,)


# Support functions for article editing

def check_concurrent_edit(request):
    '''This is an Ajax callback on article update pages to
    check if another user has updated the article.
    '''
    if request.method == "POST" and \
       request.is_ajax and \
       request.user.has_perm("newsroom.change_article"):
        pk = int(request.POST["pk"])
        version = int(request.POST["version"])
        if request.POST["changed"] == "true":
            changed = True
        else:
            changed = False
        article = get_object_or_404(models.Article, pk=pk)
        if article.version > version:
            edited_by = str(article.user)
        else:
            edited_by = "(None)"
        try:
            user_edit = models.UserEdit.objects.get(
                article__pk=article.pk,
                user=request.user)
            user_edit.changed = changed
        except models.UserEdit.DoesNotExist:
            user_edit = models.UserEdit()
            user_edit.article = article
            user_edit.changed = changed
            user_edit.user = request.user
        finally:
            user_edit.save()
        cutoff = timezone.now() - datetime.timedelta(seconds=30)
        user_edits = models.UserEdit.objects. \
            filter(article=article). \
            exclude(user=request.user). \
            filter(edit_time__gte=cutoff)
        users = [obj.editStatusPlusName() for obj in user_edits]
        return JsonResponse({
            'edited_by': edited_by,
            'users': users
        }, safe=False)
    else:
        raise Http404


'''These functions were originally two generic Django class views (DetailView
and UpdateView). But the logic was hidden behind Django's opaque and not very
well documented system. This might seem complex with lots of coding that Django
could take care of, but at least I can understand what's going on here without
having to search reams of documentation and StackOverview questions.
Nevertheless, some refactoring needed here.

'''


def article_post(request, slug):
    form = ArticleForm(request.POST)
    if form.is_valid():
        if request.user.has_perm("newsroom.change_article"):
            article = get_object_or_404(models.Article, slug=slug)
            if article.version > form.cleaned_data["version"]:
                messages.add_message(request, messages.ERROR,
                                     utils.get_edit_lock_msg(article.user))
                for field in form.changed_data:
                    setattr(article, field,
                            form.cleaned_data[field])
                    return render(request, article.template,
                                  {'article': article,
                                   'display_region': None,
                                   'blocks': get_blocks('Article'),
                                   'can_edit': False,
                                   'article_letters': None,
                                   'most_popular_html': None,
                                   'form': form})
            for field in form.cleaned_data:
                setattr(article, field, form.cleaned_data[field])
            article.user = request.user
            article.save()
            # Check if user clicked "Publish" button
            if request.POST["is_published"] == "Now":
                article.publish_now()
                messages.add_message(request, messages.INFO,
                                     "Article published.")
            elif request.POST["input_top_story"] == "YES":
                article.make_top_story()
                messages.add_message(request, messages.INFO,
                                     "This is the top article.")
            elif request.POST["input_unsticky"] == "YES":
                messages.add_message(request, messages.INFO,
                                     "This article is no longer sticky.")
                article.unsticky()
            else:
                messages.add_message(request, messages.INFO,
                                     "Changes saved.")
            return HttpResponseRedirect(reverse('article.detail',
                                                args=(slug,)))
        else:
            return HttpResponseForbidden()
    else:
        if form.data["title"] == "":
            messages.add_message(request, messages.ERROR,
                                 "Title can't be blank.")
        else:
            messages.add_message(request, messages.ERROR,
                                 "Something went wrong.")
        return HttpResponseRedirect(reverse('article.detail',
                                            args=(slug,)))


def article_detail(request, slug):
    if request.method == 'POST':
        return article_post(request, slug)
    else:  # GET
        article = get_object_or_404(models.Article, slug=slug)
        if request.user.has_perm('newsroom.change_article'):
            form = ArticleForm(instance=article)
        else:
            form = None
        if article.is_published() or request.user.is_staff:
            if request.user.is_staff and not article.is_published():
                messages.add_message(request, messages.INFO,
                                     "This article is not published.")

            if article.region and (article.region.name not in
                                   ["None", "", "(None)", ]):
                display_region = article.region.name.rpartition("/")[2]
            else:
                display_region = ""

            can_edit = False
            if request.user.is_staff and \
               request.user.has_perm("newsroom.change_article"):
                can_edit = True
                query_edit = request.GET.get('edit', "true")
                if query_edit.lower() == "no" or \
                   query_edit.lower() == "false":
                    can_edit = False

            article_body = article.body
            if can_edit is False:
                try:
                    soup = BeautifulSoup(article_body, "html.parser")
                    soup = utils.processSupportUs(soup)
                    soup = utils.processAdverts(soup)
                    article_body = str(soup)
                except:
                    article_body = article_body.replace(
                        '<aside class="article-advert-edit">',
                        '<aside class="article-advert" style="display:none;">')
                    article_body = article_body.replace(
                        '<aside class="supportus-edit">',
                        '<aside class="supportus" style="display:none;">')

            date_from = timezone.now() - datetime.timedelta(days=DAYS_AGO)
            # most_popular = models.MostPopular.get_most_popular_html()
            return render(request, article.template,
                          {'article': article,
                           'display_region': display_region,
                           'recommended': article.get_recommended(),
                           'related': article.get_related,
                           'blocks': get_blocks('Article'),
                           'can_edit': can_edit,
                           'article_body': article_body,
                           'article_letters': article.letter_set.published(),
                           'letters': Letter.objects.published().
                           filter(published__gte=date_from).
                           order_by('-published'),
                           'content_type': 'article',
                           'form': form})
        else:
            raise Http404


def copy_article(request, slug):
    article = get_object_or_404(models.Article, slug=slug)
    if (article.is_published() or request.user.is_staff) and \
       article.encourage_republish:
        if request.user.is_staff and not article.is_published():
            messages.add_message(request, messages.INFO,
                                 "This article is not published.")
        return render(request, "newsroom/copy_article.html",
                      {'article': article})
    else:
        raise Http404


####################################################

''' Redirect images on old Drupal site
'''


class RedirectOldImages(View):

    def get(self, request, path):
        url = "/media/old/" + path
        return redirect(url)


'''Redirect hand constructed features (mainly an old site phenomenon

'''


class RedirectHandConstructedFeatures(View):

    def get(self, request, path):
        url = "/media/features/" + path
        return redirect(url)


'''Redirect old /content/ articles to new /article/

'''


class RedirectContentToArticle(View):

    def get(self, request, path):
        url = "/article/" + path
        return redirect(url)


'''newsletter generator form
'''


@staff_member_required
def generate_article_list(request):
    output = []
    articles = []
    if request.method == "POST":
        form = ArticleListForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data["date_from"]
            date_to = form.cleaned_data["date_to"]
            if date_to:
                articles = models.Article.objects.published(). \
                    filter(published__gte=date_from). \
                    filter(published__lte=date_to)
            else:
                articles = models.Article.objects.published(). \
                    filter(published__gte=date_from)
            site_url = 'http://' + Site.objects.get_current().domain
            for article in articles:
                output.append("<h3><a href='" + site_url +
                              article.get_absolute_url() +
                              "'>" + article.title + "</a></h3>")
                output.append(
                    "<p>" + strip_tags(article.cached_summary_text) + "</p>")
                output.append("<p style='font-style:italic;'>" +
                              article.cached_byline_no_links + "</p>\n")
    else:
        form = ArticleListForm()

    return render(request, "newsroom/article_list_form.html",
                  {'form': form,
                   'output': output,
                   'len_articles': len(articles)})


def has_author(user):
    has_author = False
    try:
        has_author = (user.author is not None)
    except models.Author.DoesNotExist:
        pass
    return has_author


def account_profile(request):
    if request.user.is_authenticated() is True:
        if has_author(request.user):
            if request.user.author.password_changed is False:
                messages.add_message(request, messages.WARNING,
                                     "Please change your password.")
    return render(request, "newsroom/account_profile.html")


def search(request):
    query = request.GET.get('q')
    method = request.GET.get('method')
    if method is None:
        method = "DATE"
    if query:
        if method == "DATE":
            article_list = searchPostgresDB(query,
                                            models.Article,
                                            settings.SEARCH_CONFIG, False,
                                            "title", "subtitle",
                                            "cached_byline_no_links",
                                            "body").published() \
                                            [:settings.MAX_SEARCH_RESULTS]
        else:
            article_list = searchPostgresDB(query,
                                            models.Article,
                                            settings.SEARCH_CONFIG, True,
                                            "title", "subtitle",
                                            "cached_byline_no_links",
                                            "body").published() \
                                            [:settings.MAX_SEARCH_RESULTS]
        paginator = Paginator(article_list, settings.SEARCH_RESULTS_PER_PAGE)
        page_num = request.GET.get('page')
        if page_num is None:
            page_num = 1
        try:
            page = paginator.page(page_num)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
    else:
        query = ""
        page = None
        method = None
    return render(request, 'search/search.html', {'method': method,
                                                  'page': page,
                                                  'query': query})


''' Used to test logging
'''


def testLoggingDebug():
    logger.debug("Debug logging test")


def testLoggingInfo():
    logger.debug("Info logging test")


def testLoggingWarning():
    logger.debug("Warning logging test")


def testLoggingError():
    logger.error("Error logging test")


def testLoggingCritical():
    logger.critical("Critical logging test")


def testLoggingAll():
    testLoggingDebug()
    testLoggingInfo()
    testLoggingWarning()
    testLoggingError()
    testLoggingCritical()

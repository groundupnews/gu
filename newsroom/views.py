import datetime
import logging
import json
import re

from blocks.models import Group
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import Site
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import (
    Http404,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.template import Template, Context
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.views import generic
from django.views.decorators.http import last_modified
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.forms import inlineformset_factory
from django.conf import settings as django_settings

from letters.models import Letter
from letters.settings import DAYS_AGO
from agony.models import QandA
from pgsearch.utils import searchArticlesAndPhotos

from . import models, settings, utils
from .forms import (
    ArticleForm,
    ArticleNewForm,
    ArticleListForm,
    AdvancedSearchForm,
    AuthorForm,
)
from payment.models import Commission
from socialmedia.models import Tweet
from socialmedia.forms import TweetForm
from republisher.models import RepublisherArticle
from republisher.forms import RepublisherArticleForm

logger = logging.getLogger(__name__)


def get_blocks(group_name="Home"):
    try:
        return Group.objects.get(name=group_name).get_blocks()
    except:
        return []


def parse_shortcodes(content):
    if not content:
        return ""

    def _render_shortcode_block(kind, obj, articles, feature_first=True, show_summary_featured=True, show_summary_standard=True, title=None, show_title_featured=True, show_title_standard=True):
        """
        kind: 'topic' | 'category' | 'chart_of_the_week'
        obj: Topic | Category | None
        articles: iterable[Article]
        feature_first: bool
        show_summary_featured: bool
        show_summary_standard: bool
        title: str | None
        show_title_featured: bool
        show_title_standard: bool
        """
        if not articles:
            return ""

        if title:
            display_title = title
        elif obj:
            display_title = obj.name
        else:
            display_title = "Chart of the Week"

        url = obj.get_absolute_url() if obj else "/category/charts/"

        if kind == 'chart_of_the_week':
             return render_to_string(
                "blocks/chart_of_the_week.html",
                {
                    "title": display_title,
                    "url": url,
                    "articles": articles,
                    "feature_first": feature_first,
                    "show_summary_featured": show_summary_featured,
                    "show_summary_standard": show_summary_standard,
                    "show_title_featured": show_title_featured,
                    "show_title_standard": show_title_standard,
                },
            )

        heading_html = render_to_string(
            "blocks/shortcode_heading.html",
            {"title": display_title, "url": url, "kind": kind},
        )

        content_html = ""

        if feature_first:
            first = articles[0]
            rest = articles[1:]

            content_html += render_to_string(
                "blocks/article_summary_block.html",
                {
                    "article": first,
                    "include_summary": "1" if show_summary_featured else "0",
                    "include_title": "1" if show_title_featured else "0",
                    "include_image": "1",
                    "block_variant": "featured",
                },
            )
        else:
            rest = articles

        content_html += "".join(
            render_to_string(
                "blocks/article_summary_block.html",
                {
                    "article": a,
                    "include_summary": "1" if show_summary_standard else "0",
                    "include_title": "1" if show_title_standard else "0",
                    "include_image": "1",
                    "block_variant": "compact",
                },
            )
            for a in rest
        )

        footer_html = render_to_string(
            "blocks/shortcode_read_more.html",
            {"url": url},
        )

        return (
            '<section class="home-shortcode-block">'
            f"{heading_html}"
            f"{content_html}"
            f"{footer_html}"
            "</section>"
        )

    # parsses {{topic:slug:count}} or {{topic:slug:count:featured}} or {{topic:slug:count:featured:sum_feat:sum_std}}
    for match in re.finditer(r"{{topic:([-\w]+):(\d+)(?::([01]))?(?::([01]))?(?::([01]))?(?::([^}:]*))?(?::([01]))?(?::([01]))?}}", content):
        full_match = match.group(0)
        slug = match.group(1)
        count = match.group(2)
        featured_str = match.group(3)
        sum_feat_str = match.group(4)
        sum_std_str = match.group(5)
        title = match.group(6)
        title_feat_str = match.group(7)
        title_std_str = match.group(8)

        feature_first = True
        if featured_str == '0':
            feature_first = False

        show_summary_featured = True
        if sum_feat_str == '0':
            show_summary_featured = False

        show_summary_standard = True
        if sum_std_str == '0':
            show_summary_standard = False

        show_title_featured = True
        if title_feat_str == '0':
            show_title_featured = False

        show_title_standard = True
        if title_std_str == '0':
            show_title_standard = False

        try:
            topic = models.Topic.objects.get(slug=slug)
            qs = models.Article.objects.published().filter(topics=topic)[: int(count)]
            html = _render_shortcode_block("topic", topic, list(qs), feature_first, show_summary_featured, show_summary_standard, title, show_title_featured, show_title_standard)
            content = content.replace(full_match, html)
        except models.Topic.DoesNotExist:
            content = content.replace(full_match, "")

    # parse {{category:slug:count}} or {{category:slug:count:featured}} or {{category:slug:count:featured:sum_feat:sum_std}}
    for match in re.finditer(r"{{category:([-\w]+):(\d+)(?::([01]))?(?::([01]))?(?::([01]))?(?::([^}:]*))?(?::([01]))?(?::([01]))?}}", content):
        full_match = match.group(0)
        slug = match.group(1)
        count = match.group(2)
        featured_str = match.group(3)
        sum_feat_str = match.group(4)
        sum_std_str = match.group(5)
        title = match.group(6)
        title_feat_str = match.group(7)
        title_std_str = match.group(8)

        feature_first = True
        if featured_str == '0':
            feature_first = False

        show_summary_featured = True
        if sum_feat_str == '0':
            show_summary_featured = False

        show_summary_standard = True
        if sum_std_str == '0':
            show_summary_standard = False

        show_title_featured = True
        if title_feat_str == '0':
            show_title_featured = False

        show_title_standard = True
        if title_std_str == '0':
            show_title_standard = False

        try:
            category = models.Category.objects.get(slug=slug)
            qs = models.Article.objects.published().filter(category=category)[: int(count)]
            html = _render_shortcode_block("category", category, list(qs), feature_first, show_summary_featured, show_summary_standard, title, show_title_featured, show_title_standard)
            content = content.replace(full_match, html)
        except models.Category.DoesNotExist:
            content = content.replace(full_match, "")

    # parse {{chart_of_the_week:count:featured:sum_feat:sum_std:title}}
    for match in re.finditer(r"{{chart_of_the_week:(\d+)(?::([01]))?(?::([01]))?(?::([01]))?(?::([^}:]*))?(?::([01]))?(?::([01]))?}}", content):
        full_match = match.group(0)
        count = match.group(1)
        featured_str = match.group(2)
        sum_feat_str = match.group(3)
        sum_std_str = match.group(4)
        title = match.group(5)
        title_feat_str = match.group(6)
        title_std_str = match.group(7)

        feature_first = True
        if featured_str == '0':
            feature_first = False

        show_summary_featured = True
        if sum_feat_str == '0':
            show_summary_featured = False

        show_summary_standard = True
        if sum_std_str == '0':
            show_summary_standard = False

        show_title_featured = True
        if title_feat_str == '0':
            show_title_featured = False

        show_title_standard = True
        if title_std_str == '0':
            show_title_standard = False

        try:
            category = models.Category.objects.get(slug='charts')
            qs = models.Article.objects.published().filter(category=category)[: int(count)]
            html = _render_shortcode_block("chart_of_the_week", category, list(qs), feature_first, show_summary_featured, show_summary_standard, title, show_title_featured, show_title_standard)
            content = content.replace(full_match, html)
        except models.Category.DoesNotExist:
            content = content.replace(full_match, "")

    if "{{creative_commons_gallery}}" in content:
        from gallery.models import Photograph
        # get up to three random featured photos
        photos = list(Photograph.objects.filter(featured=True).order_by('?')[:3])
        if len(photos) < 3:
            additional = Photograph.objects.exclude(pk__in=[p.pk for p in photos]).order_by('?')[:3 - len(photos)]
            photos.extend(additional)
        
        if photos:
            html = render_to_string("blocks/creative_commons_gallery.html", {"photos": photos})
            content = content.replace("{{creative_commons_gallery}}", html)
        else:
             content = content.replace("{{creative_commons_gallery}}", "")

    return content


def get_blocks_in_context(context, group_name="Home", context_key="blocks"):
    context[context_key] = get_blocks(group_name)

    for block in context[context_key]:
        if hasattr(block, 'html'):
            block.html = parse_shortcodes(block.html)

    # Add featured front page photos if any blocks in the group contain _Featured_Photos
    blocks = context[context_key]
    if any(block.name == "_Featured_Photos" for block in blocks):
        from django.utils import timezone
        from gallery.models import Photograph

        now = timezone.now()
        featured_photos = Photograph.objects.filter(
            featured_on_front_page_from__lte=now, featured_on_front_page_to__gte=now
        ).order_by("-date_taken")

        context["featured_front_page_photos"] = featured_photos

    return context


class ArticleList(generic.ListView):
    context_object_name = "article_list"
    template_name = "newsroom/article_list.html"
    paginate_by = settings.ARTICLES_PER_PAGE

    def get_queryset(self):
        return models.Article.objects.list_view()

    def get_context_data(self, **kwargs):
        context = super(ArticleList, self).get_context_data(**kwargs)
        #  context = get_blocks_in_context(context)
        context["most_popular_html"] = models.MostPopular.get_most_popular_html()
        context["most_deeply_read_html"] = models.MostDeeplyRead.get_most_deeply_read_html()
        date_from = timezone.now() - datetime.timedelta(days=DAYS_AGO)
        context["letters"] = (
            Letter.objects.published()
            .filter(published__gte=date_from)
            .order_by("-published")
        )
        context["agony"] = QandA.objects.published().order_by("-published")
        return context


def last_article_modified(request):
    return models.Article.objects.published().latest("modified").modified


class HomePage(ArticleList):
    template_name = "newsroom/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context = get_blocks_in_context(context, "Home_Top", "topblocks")
        context = get_blocks_in_context(context, "Home_0", "home_0")
        context = get_blocks_in_context(context, "Home_1", "home_1")
        context = get_blocks_in_context(context, "Home_2", "home_2")
        context = get_blocks_in_context(context, "Home_3", "home_3")
        context = get_blocks_in_context(context, "Home_4", "home_4")
        context = get_blocks_in_context(context, "Home_5", "home_5")
        context = get_blocks_in_context(context, "Home_6", "home_6")
        context = get_blocks_in_context(context, "Home_7", "home_7")
        return context

    # LEAVE THIS COMMENTED OUT CODE IN CASE OF EMERGENCY IN
    # WHICH CODE NEEDS TO CHANGE URGENTLY.

    def get(self, request, *args, **kwargs):
        # Add messages here. E.g.
        # messages.add_message(
        #     request,
        #     messages.INFO,
        #     "We are publishing irregularly, if at all, until 6 January 2026. Have a safe holiday season.",
        # )
        request = super(HomePage, self).get(request, args, kwargs)
        return request


home_page_view = HomePage.as_view()
# For last modified caching, uncomment this. Extreme but works.
# home_page_view = last_modified(last_article_modified)(home_page_view)


class OpinionAnalysisList(ArticleList):
    def get_queryset(self):
        return models.Article.objects.list_view().filter(
            Q(category__name="Opinion") | Q(category__name="Analysis")
        )

    def get_context_data(self, **kwargs):
        context = super(OpinionAnalysisList, self).get_context_data(**kwargs)
        context["heading"] = "Opinion and Analysis"
        return context


class GroundViewList(ArticleList):
    def get_queryset(self):
        return models.Article.objects.list_view().filter(
            Q(category__name="GroundView")
            | Q(
                topics__name__in=[
                    "GroundView",
                ]
            )
        )

    def get_context_data(self, **kwargs):
        context = super(GroundViewList, self).get_context_data(**kwargs)
        context["heading"] = "GroundView: Our editorials"
        return context


class AuthorList(generic.ListView):
    model = models.Author

    def get_queryset(self):
        return models.Author.objects.exclude(freelancer="t")


class AuthorDetail(ArticleList):
    template_name = "newsroom/author_detail.html"

    def get_queryset(self):
        self.author = get_object_or_404(models.Author, pk=self.args[0])
        if self.author.freelancer == "t":
            raise Http404
        return models.Article.objects.list_view().filter(
            Q(author_01=self.author)
            | Q(author_02=self.author)
            | Q(author_03=self.author)
            | Q(author_04=self.author)
            | Q(author_05=self.author)
            | Q(cached_byline_no_links__icontains=str(self.author))
        )

    def get_context_data(self, **kwargs):
        context = super(AuthorDetail, self).get_context_data(**kwargs)
        context["heading"] = "Articles by " + str(self.author)
        context["image"] = self.author.photo
        context["description"] = self.author.description
        context["author"] = self.author
        return context


class CategoryList(generic.ListView):
    model = models.Category


class CategoryDetail(ArticleList):
    def get_queryset(self):
        self.category = get_object_or_404(models.Category, slug__iexact=self.args[0])
        return models.Article.objects.list_view().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super(CategoryDetail, self).get_context_data(**kwargs)
        context["heading"] = self.category.name
        return context


class CompactArticleList(generic.ListView):
    template_name = "newsroom/compact_article_list.html"
    model = models.Article
    context_object_name = "article_list"
    paginate_by = settings.ARTICLES_PER_PAGE

    def get_queryset(self):
        return models.Article.objects.list_view()


class CompactArticleDetail(generic.DetailView):
    template_name = "newsroom/compact_article_detail.html"
    model = models.Article

    def get_object(self):
        article = super().get_object()
        if article.is_published():
            return article
        else:
            raise Http404


class RegionList(generic.ListView):
    model = models.Region


class RegionDetail(ArticleList):
    def get_queryset(self):
        self.region = get_object_or_404(models.Region, name=self.args[0])
        return models.Article.objects.list_view().filter(
            Q(region__in=self.region.get_descendants()) | Q(region=self.region)
        )

    def get_context_data(self, **kwargs):
        context = super(RegionDetail, self).get_context_data(**kwargs)
        query = Q(name=self.region.name)
        region_name = str(self.region)
        while region_name:
            region_name = region_name.rpartition("/")[0]
            query = query | Q(name=region_name)
        regions = models.Region.objects.filter(query)
        regions = [
            "<a href='"
            + reverse("newsroom:region.detail", args=(region.name,))
            + "'>"
            + region.name.rpartition("/")[2]
            + "</a>"
            for region in regions
        ]
        context["title"] = str(self.region).rpartition("/")[2]
        context["heading"] = "|".join(regions)
        return context


class TopicList(generic.ListView):
    model = models.Topic

    def get_context_data(self, **kwargs):
        categories = models.Category.objects.all()
        context = super(TopicList, self).get_context_data(**kwargs)
        context["categories"] = categories
        return context


class TopicDetail(ArticleList):
    template_name = "newsroom/topic_detail.html"

    def get_queryset(self):
        self.topic = get_object_or_404(models.Topic, slug=self.args[0])
        if self.topic.newest_first is True:
            return models.Article.objects.published().filter(topics=self.topic)
        else:
            return (
                models.Article.objects.published()
                .filter(topics=self.topic)
                .order_by("published")
            )

    def get_context_data(self, **kwargs):
        context = super(TopicDetail, self).get_context_data(**kwargs)
        context["heading"] = self.topic.name.upper()
        context["topic"] = self.topic
        return context

    def get_template_names(self):
        return (self.topic.template,)


class ListCorrection(generic.ListView):
    model = models.Correction


def get_correction_article(request):
    article_pk = request.GET.get("article_pk", None)
    if article_pk is None:
        raise Http404
    try:
        return models.Article.objects.get(pk=int(article_pk))
    except:
        raise Http404


class CreateCorrection(PermissionRequiredMixin, CreateView):
    model = models.Correction
    fields = [
        "update_type",
        "text",
        "use_html",
        "notify_republishers",
        "display_at_top",
    ]
    permission_required = "newsroom.add_correction"

    def get_context_data(self, **kwargs):
        context = super(CreateCorrection, self).get_context_data(**kwargs)
        context["article"] = get_correction_article(self.request)
        return context

    def form_valid(self, form):
        article_pk = self.request.GET.get("article_pk", None)
        if article_pk is None:
            raise Http404
        try:
            article = models.Article.objects.get(pk=int(article_pk))
        except:
            raise Http404

        form.instance.article = article
        return super(CreateCorrection, self).form_valid(form)


class UpdateCorrection(PermissionRequiredMixin, UpdateView):
    model = models.Correction
    fields = [
        "update_type",
        "text",
        "use_html",
        "notify_republishers",
        "display_at_top",
    ]
    permission_required = "newsroom.change_correction"

    def get_context_data(self, **kwargs):
        context = super(UpdateCorrection, self).get_context_data(**kwargs)
        context["article"] = get_correction_article(self.request)
        return context


class DeleteCorrection(PermissionRequiredMixin, DeleteView):
    model = models.Correction
    permission_required = "newsroom.delete_correction"

    def get_success_url(self):
        slug = self.object.article.slug
        return reverse("newsroom:article.detail", args=(slug,))

    def get_context_data(self, **kwargs):
        context = super(DeleteCorrection, self).get_context_data(**kwargs)
        context["article"] = get_correction_article(self.request)
        return context


# Support functions for article editing


def check_concurrent_edit(request):
    """This is an Ajax callback on article update pages to
    check if another user has updated the article.
    """
    if (
        request.method == "POST"
        and request.headers.get("x-requested-with") == "XMLHttpRequest"
        and request.user.has_perm("newsroom.change_article")
    ):
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
                article__pk=article.pk, user=request.user
            )
            user_edit.changed = changed
        except models.UserEdit.DoesNotExist:
            user_edit = models.UserEdit()
            user_edit.article = article
            user_edit.changed = changed
            user_edit.user = request.user
        finally:
            user_edit.save()
        cutoff = timezone.now() - datetime.timedelta(seconds=30)
        user_edits = (
            models.UserEdit.objects.filter(article=article)
            .exclude(user=request.user)
            .filter(edit_time__gte=cutoff)
        )
        users = [obj.editStatusPlusName() for obj in user_edits]
        return JsonResponse({"edited_by": edited_by, "users": users}, safe=False)
    else:
        raise Http404


"""Used by various article views to get default context they all need
"""


def get_context(article):
    date_from = timezone.now() - datetime.timedelta(days=DAYS_AGO)
    if article.region and (
        article.region.name
        not in [
            "None",
            "",
            "(None)",
        ]
    ):
        display_region = article.region.name.rpartition("/")[2]
    else:
        display_region = ""

    try:
        dict = {
            "article": article,
            "display_region": display_region,
            "recommended": article.get_recommended(),
            "related": article.get_related(),
            "blocks": get_blocks("Article"),
            "article_body": article.body,
            "article_letters": article.letter_set.published(),
            "most_popular_html": models.MostPopular.get_most_popular_html(),
            "letters": Letter.objects.published()
            .filter(published__gte=date_from)
            .order_by("-published"),
            "agony": QandA.objects.published().order_by("-published"),
            "content_type": "article",
            "form": None,
            # 'tweetFormSet': None,
            "republisherFormSet": None,
            "correctionFormSet": None,
            "from_form": 0,
            "can_edit": False,
        }
    except Exception as e:
        logging.error("Couldn't get extra context for article: " + str(article.pk))
        dict = {"article": article}
    return dict


"""These functions were originally two generic Django class views (DetailView
and UpdateView). But the logic was hidden behind Django's opaque and not very
well documented system. This might seem complex with lots of coding that Django
could take care of, but at least I can understand what's going on here without
having to search reams of documentation and StackOverview questions.
Nevertheless, some refactoring needed here.

"""


def article_post(request, slug):
    if request.user.has_perm("newsroom.change_article") == False:
        return HttpResponseForbidden()
    article = get_object_or_404(models.Article, slug=slug)
    version = article.version
    form = ArticleForm(request.POST, instance=article)

    # TweetFormSet = inlineformset_factory(models.Article, Tweet, form=TweetForm)
    # tweetFormSet = TweetFormSet(request.POST, instance=article,
    #                            prefix="tweets")

    RepublisherFormSet = inlineformset_factory(
        models.Article, RepublisherArticle, form=RepublisherArticleForm
    )
    republisherFormSet = RepublisherFormSet(
        request.POST, instance=article, prefix="republishers"
    )
    CorrectionFormSet = inlineformset_factory(
        models.Article,
        models.Correction,
        fields=(
            "update_type",
            "text",
            "use_html",
            "notify_republishers",
            "display_at_top",
        ),
    )
    correctionFormSet = CorrectionFormSet(
        request.POST, instance=article, prefix="corrections"
    )

    if (
        form.is_valid()
        and republisherFormSet.is_valid()
        and correctionFormSet.is_valid()
    ):
        # Check we edited the latest version
        if version > form.cleaned_data["version"]:
            messages.add_message(
                request, messages.ERROR, utils.get_edit_lock_msg(article.user)
            )
            return render(
                request,
                article.template,
                {
                    **get_context(article),
                    **{
                        "form": form,
                        # 'tweetFormSet': tweetFormSet,
                        "republisherFormSet": republisherFormSet,
                        "correctionFormSet": correctionFormSet,
                        "from_form": 1,
                        "can_edit": True,
                    },
                },
            )
        article = form.save()
        article.user = request.user
        article.save(force_update=True)
        # tweetFormSet.save()
        republisherFormSet.save()
        correctionFormSet.save()
        # Check if user clicked "Publish" button
        if request.POST["btn_publish_now"] == "y":
            article.publish_now()
            messages.add_message(request, messages.INFO, "Article published.")
        elif request.POST["btn_unsticky"] == "y":
            article.unsticky()
            messages.add_message(
                request, messages.INFO, "This article is no longer sticky."
            )
        elif request.POST["btn_top_story"] == "y":
            article.make_top_story()
            messages.add_message(request, messages.INFO, "This is the top article.")
        elif request.POST["btn_secret_link"] == "y":
            article.save()
            article_gen_preview(request, article.pk)
            messages.add_message(request, messages.INFO, "Private link created.")
        elif request.POST["btn_full_width"] == "y":
            article.undistracted_layout = True
            article.save()
            messages.add_message(request, messages.INFO, "Full width article.")
        elif request.POST["btn_half_width"] == "y":
            article.undistracted_layout = False
            article.save()
            messages.add_message(request, messages.INFO, "Normal width article.")
        else:
            messages.add_message(request, messages.INFO, "Changes saved.")
        return HttpResponseRedirect(
            reverse("newsroom:article.detail", args=(article.slug,))
        )
    else:
        messages.add_message(
            request, messages.ERROR, "Please fix the error(s). Changes not yet saved."
        )
        # if tweetFormSet.is_valid() == False:
        #    messages.add_message(request, messages.ERROR,
        #                    "There is an error with the tweets.")
        if republisherFormSet.is_valid() == False:
            messages.add_message(
                request, messages.ERROR, "There is an error with the republishers."
            )
        if correctionFormSet.is_valid() == False:
            messages.add_message(
                request, messages.ERROR, "There is an error with the corrections."
            )
        return render(
            request,
            article.template,
            {
                **get_context(article),
                **{
                    "can_edit": True,
                    "form": form,
                    # 'tweetFormSet': tweetFormSet,
                    "republisherFormSet": republisherFormSet,
                    "correctionFormSet": correctionFormSet,
                    "from_form": 1,
                },
            },
        )


@staff_member_required
def article_gen_preview(request, pk):
    if request.user.has_perm("newsroom.change_article"):
        article = get_object_or_404(models.Article, pk=pk)
    else:
        return HttpResponseForbidden()

    if article.secret_link == "":
        if article.secret_link_view == "n":
            article.secret_link_view = "r"
        article.save()

    return HttpResponseRedirect(
        reverse("newsroom:article.preview", args=(article.secret_link,))
    )


def article_preview(request, secret_link):
    article = get_object_or_404(models.Article, secret_link=secret_link)

    if article.secret_link_view != "o" and article.is_published():
        return HttpResponseRedirect(
            reverse("newsroom:article.detail", args=(article.slug,))
        )

    if article.secret_link_view == "n":
        return HttpResponseForbidden()

    messages.add_message(
        request, messages.ERROR, "This is a private link to an unpublished article."
    )

    return render(request, article.template, get_context(article))


def article_detail(request, slug):
    if request.method == "POST":
        return article_post(request, slug)
    else:  # GET
        article = get_object_or_404(models.Article, slug=slug)
        if request.user.has_perm("newsroom.change_article"):
            form = ArticleForm(instance=article)

            # TweetFormSet = inlineformset_factory(models.Article, Tweet,
            #                                     form=TweetForm, extra=1,
            #                                     can_delete_extra=False)
            # tweetFormSet = TweetFormSet(instance=article, prefix="tweets")

            RepublisherFormSet = inlineformset_factory(
                models.Article,
                RepublisherArticle,
                extra=5,
                can_delete_extra=False,
                form=RepublisherArticleForm,
            )
            republisherFormSet = RepublisherFormSet(
                instance=article, prefix="republishers"
            )

            CorrectionFormSet = inlineformset_factory(
                models.Article,
                models.Correction,
                extra=1,
                can_delete_extra=False,
                fields=(
                    "update_type",
                    "text",
                    "use_html",
                    "notify_republishers",
                    "display_at_top",
                ),
            )
            correctionFormSet = CorrectionFormSet(
                instance=article, prefix="corrections"
            )
        else:
            form = None
            # tweetFormSet = None
            republisherFormSet = None
            correctionFormSet = None
        if article.is_published() or request.user.is_staff:
            if request.user.is_staff and not article.is_published():
                messages.add_message(
                    request, messages.INFO, "This article is not published."
                )
            can_edit = False
            if request.user.is_staff and request.user.has_perm(
                "newsroom.change_article"
            ):
                can_edit = True
                query_edit = request.GET.get("edit", "true")
                if query_edit.lower() == "no" or query_edit.lower() == "false":
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
                        '<aside class="article-advert" style="display:none;">',
                    )
                    article_body = article_body.replace(
                        '<aside class="supportus-edit">',
                        '<aside class="supportus" style="display:none;">',
                    )

                if article.template_process is True:
                    t = Template(article_body)
                    c = Context({"article": article})
                    article_body = t.render(c)

            return render(
                request,
                article.template,
                {
                    **get_context(article),
                    **{
                        "can_edit": can_edit,
                        "form": form,
                        # 'tweetFormSet': tweetFormSet,
                        "republisherFormSet": republisherFormSet,
                        "correctionFormSet": correctionFormSet,
                    },
                },
            )
        else:
            raise Http404


@staff_member_required
def article_new(request):
    if request.method == "POST":
        form = ArticleNewForm(request.POST)
        if request.user.has_perm("newsroom.add_article"):
            if form.is_valid():
                article = form.save()
                return HttpResponseRedirect(
                    reverse("newsroom:article.detail", args=(article.slug,)) + "?edit=y"
                )
            else:
                messages.add_message(request, messages.ERROR, "Please correct errors")
        else:
            return HttpResponseForbidden()
    else:
        form = ArticleNewForm()
    return render(
        request,
        "newsroom/article_new.html",
        {
            "form": form,
        },
    )


def article_print(request, slug):
    article = get_object_or_404(models.Article, slug=slug)
    if article.is_published() or request.user.is_staff:
        return render(request, "newsroom/article_print.html", {"article": article})
    else:
        raise Http404


def copy_article(request, slug):
    article = get_object_or_404(models.Article, slug=slug)
    if (
        article.is_published() or request.user.is_staff
    ) and article.encourage_republish:
        if request.user.is_staff and not article.is_published():
            messages.add_message(
                request, messages.INFO, "This article is not published."
            )
        return render(request, "newsroom/copy_article.html", {"article": article})
    else:
        raise Http404


####################################################

""" Redirect images on old Drupal site
"""


class RedirectOldImages(View):
    def get(self, request, path):
        url = "/media/old/" + path
        return redirect(url)


"""Redirect hand constructed features (mainly an old site phenomenon

"""


class RedirectHandConstructedFeatures(View):
    def get(self, request, path):
        url = "/media/features/" + path
        return redirect(url)


"""Redirect old /content/ articles to new /article/

"""


class RedirectContentToArticle(View):
    def get(self, request, path):
        url = "/article/" + path
        return redirect(url)


"""newsletter generator form
"""


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
                articles = (
                    models.Article.objects.published()
                    .filter(published__date__gte=date_from)
                    .filter(published__date__lte=date_to)
                )
            else:
                articles = models.Article.objects.published().filter(
                    published__date__gte=date_from
                )
            site_url = "http://" + Site.objects.get_current().domain
            for article in articles:
                output.append(
                    "<h3><a href='"
                    + site_url
                    + article.get_absolute_url()
                    + "'>"
                    + article.title
                    + "</a></h3>"
                )
                output.append("<p>" + strip_tags(article.cached_summary_text) + "</p>")
                output.append(
                    "<p style='font-style:italic;'>"
                    + article.cached_byline_no_links
                    + "</p>\n"
                )
    else:
        form = ArticleListForm()

    return render(
        request,
        "newsroom/article_list_form.html",
        {"form": form, "output": output, "len_articles": len(articles)},
    )


def has_author(user):
    has_author = False
    try:
        has_author = user.author is not None
    except models.Author.DoesNotExist:
        pass
    return has_author


def account_profile(request):
    if request.method == "POST":
        if request.user.is_authenticated is True:
            if has_author(request.user):
                if Commission.can_bill_allowance(request.user.author):
                    Commission.create_allowance(request.user.author)
    allowance = False
    allowance_processed = False
    if request.user.is_authenticated is True:
        if has_author(request.user):
            allowance = Commission.can_bill_allowance(request.user.author)
            if allowance is False and request.user.author.allowance is True:
                allowance_processed = True
            if request.user.author.password_changed is False:
                messages.add_message(
                    request, messages.WARNING, "Please change your password."
                )
    return render(
        request,
        "newsroom/account_profile.html",
        {"allowance": allowance, "allowance_processed": allowance_processed},
    )


def logout_from_all_sessions(request):
    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        auth_user_id = session.get_decoded().get("_auth_user_id", None)
        if auth_user_id == str(request.user.id):
            session.delete()
    return redirect("newsroom:home")


def advanced_search(request):
    page = None
    query = request.GET.get("adv_search", "")
    search_type = request.GET.get("search_type")
    first_author = request.GET.get("first_author")
    first_author_only = True if first_author == "on" else False
    author_text = request.GET.get('author')

    try:
        author_param = request.GET.get("author")
        if author_param and not str(author_param).isdigit():
            author_param = None
    except (ValueError, TypeError):
        author_param = None

    if author_param is None and "author" in request.GET:
        get_params = request.GET.copy()
        get_params.pop("author")
        request.GET = get_params

    if request.GET.get("search_type") == "image":
        inc_photos = True
        inc_articles = False
        gallery = True
    else:
        inc_photos = True if search_type == "image" or search_type == "both" else False
        gallery = False

    if request.GET.get("search_type") == "article":
        inc_articles = True
        inc_photos = False
    else:
        inc_articles = (
            True if search_type == "article" or search_type == "both" else False
        )

    adv_search_form = AdvancedSearchForm(request.GET or None)

    if adv_search_form.is_valid():
        cleaned_adv_form = adv_search_form.cleaned_data
        author_pk = (
            cleaned_adv_form.get("author").pk
            if cleaned_adv_form.get("author")
            else None
        )
        category_pk = (
            cleaned_adv_form.get("category").pk
            if cleaned_adv_form.get("category")
            else None
        )
        topic_pk = (
            cleaned_adv_form.get("topics").pk
            if cleaned_adv_form.get("topics")
            else None
        )
        if (
            request.GET.get("is_simple") == "true"
            and cleaned_adv_form.get("adv_search") == ""
        ):
            article_list = models.Article.objects.none()
        else:
            try:
                article_list = searchArticlesAndPhotos(
                    cleaned_adv_form.get("adv_search"),
                    inc_articles,
                    inc_photos,
                    author_pk,
                    first_author_only,
                    category_pk,
                    topic_pk,
                    cleaned_adv_form.get("date_from"),
                    cleaned_adv_form.get("date_to"),
                )
            except Exception as e:
                print("Exception", e)
                logger.error("Advanced Search Failed calling searchArticlesAndPhotos")
                article_list = models.Article.objects.none()
    else:
        article_list = models.Article.objects.none()

    try:
        num_results = int(request.GET.get("results_per_page"))
    except:
        if search_type == "image":
            num_results = settings.SEARCH_RESULTS_PER_PAGE * 4
        else:
            num_results = settings.SEARCH_RESULTS_PER_PAGE

    paginator = Paginator(article_list, num_results)
    page_num = request.GET.get("page")
    if page_num is None:
        page_num = 1
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    except:
        logger.error("Advanced Search Failed in pagination")
    finally:
        try:
            num_pages = paginator.num_pages
        except:
            logger.error("Advanced Search failed to get num_pages")
            num_pages = 1

    additional_parameters = ""
    try:
        if author_pk:
            additional_parameters += "&author=" + str(author_pk)
        if category_pk:
            additional_parameters += "&category=" + str(category_pk)
        if topic_pk:
            additional_parameters += "&topics=" + str(topic_pk)
        if cleaned_adv_form.get("date_from"):
            additional_parameters += "&date_from=" + str(
                cleaned_adv_form.get("date_from").strftime("%Y-%m-%d")
            )
        if cleaned_adv_form.get("date_to"):
            additional_parameters += "&date_to=" + str(
                cleaned_adv_form.get("date_to").strftime("%Y-%m-%d")
            )
        if cleaned_adv_form.get("results_per_page"):
            additional_parameters += "&results_per_page=" + str(
                cleaned_adv_form.get("results_per_page")
            )
        if author_text:
            additional_parameters += "&author_text=" + str(author_text)
    except:
        additional_parameters = ""

    return render(
        request,
        "search/search.html",
        {
            "query": query,
            "page": page,
            "page_num": page_num,
            "num_pages": num_pages,
            "num_items": len(article_list),
            "search_type": search_type,
            "gallery": gallery,
            "additional_parameters": additional_parameters,
            "adv_search_form": adv_search_form,
        },
    )


# def handler404(request, exception, template_name="404.html"):
#     return render(request,
#                   '404.html',
#                   {'most_popular_html': models.MostPopular.get_most_popular_html(),
#                    'toy_html': 'toys/govtbudgets.html',},
#                   status=404)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = "newsroom.add_author"
    model = models.Author
    form_class = AuthorForm


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = "newsroom.change_author"
    model = models.Author
    form_class = AuthorForm


topic_fields = [
    "name",
    "slug",
    "introduction",
    "newest_first",
]


class TopicCreate(PermissionRequiredMixin, CreateView):
    permission_required = "newsroom.add_topic"
    model = models.Topic
    fields = topic_fields


class TopicUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = "newsroom.change_topic"
    model = models.Topic
    fields = topic_fields


class WetellListView(ListView):
    model = models.WetellBulletin
    paginate_by = 10


class WetellDetailView(DetailView):
    model = models.WetellBulletin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            items = json.loads(self.object.data)
        except Exception as e:
            msg = "Error converting bulletin data" + str(e)
            logger.error(msg)
            context["bulletin"] = {}
            return context

        context["bulletin"] = items

        return context


class WetellLatestView(WetellDetailView):
    def get_object(self):
        return models.WetellBulletin.objects.latest("published")


""" Used to test logging
"""


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

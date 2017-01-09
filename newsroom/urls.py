from django.conf.urls import url
from django.views.decorators.cache import cache_page
from django.views.generic.base import RedirectView
from . import views
from . import feeds
from .utils import cache_except_staff
from . import settings


urlpatterns = [
    url(r'^$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.home_page_view),
        name='home'),

    url(r'^search/', views.search, name='article.search'),

    url(r'^category/opinion_and_analysis/$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.OpinionAnalysisList.as_view()), name='article.opinion_analysis'),

    url(r'^category/$', views.CategoryList.as_view(),
        name="category.list"),

    url(r'^category/([-\s\w]+)/$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.CategoryDetail.as_view()), name='category.detail'),

    url(r'^region/$', views.RegionList.as_view(),
        name="region.list"),

    url(r'^region/(.*)$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.RegionDetail.as_view()), name='region.detail'),

    url(r'^topic/$', views.TopicList.as_view(),
        name="topic.list"),

    url(r'^topic/([-\s\w]+)/$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.TopicDetail.as_view()), name='topic.detail'),

    url(r'^user/$', views.account_profile,
        name="user.profile"),

    ###############################
    # Article list generate

    url(r'^generate_article_list/$',
        views.generate_article_list, name='generate_article_list'),

    ###############################
    # Old feature article redirects
    url(r'^article/redhills-ruins-cape-towns-forgotten-district-six_2043/$',
        RedirectView.as_view(url='/media/features/redhill/redhill_2043.html',
                                      permanent=False)),

    url(r'^article/mpumalanga-crisis-why-nobody-listening_2236/$',
        RedirectView.as_view(url='/media/features/mpumalanga/mpumalanga_0002.html',
                                      permanent=False)),

    url(r'^article/will-i-make-money-today-waiting-work-side-road_2245/$',
        RedirectView.as_view(url='/media/features/menatsideofroad/menatroadside_0003.html',
                                      permanent=False)),

    url(r'^article/long-trek-education-city-students_2400/$',
        RedirectView.as_view(url='/media/features/westlake/westlake_0004.html',
                                      permanent=False)),

    url(r'^article/house-full-faeces-khayelitsha_2447/$',
        RedirectView.as_view(url='/media/features/faeces/house_faeces_0005.html',
                                      permanent=False)),

    url(r'^article/fishing-black-river_2514/$',
        RedirectView.as_view(url='/media/features/blackriver/blackriver_0006.html',
                                      permanent=False)),

    url(r'^article/ocean-view-fisher-blues-part-one_2657/$',
        RedirectView.as_view(url='/media/features/daff/daff_1_0008.html',
                                      permanent=False)),

    url(r'^article/ocean-view-fisher-blues-part-two_2658/$',
        RedirectView.as_view(url='/media/features/daff/daff_2_0008.html',
                                      permanent=False)),

    url(r'^article/how-free-state-health-system-being-destroyed_2722/$',
        RedirectView.as_view(url='/media/features/freestatehealth/freestatehealth.html',
                                      permanent=False)),

    url(r'^article/tee-along-n2_2761/$',
        RedirectView.as_view(url='/media/features/n2golfer/n2golfer.html',
                                      permanent=False)),

    url(r'^article/living-hole-ground-district-six_2767/$',
        RedirectView.as_view(url='/media/features/holeground/holeground.html',
                                      permanent=False)),

    url(r'^article/rhodes-falls_2824/$',
        RedirectView.as_view(url='/media/features/RhodesFalls/rhodesfalls.html',
                                      permanent=False)),

    url(r'^article/lost-karretjie-people-karoo_2825/$',
        RedirectView.as_view(url='/media/features/karretjie/karretjiepeople.html',
                                      permanent=False)),

    url(r'^article/beautiful-photos-old-cape-town_2869/$',
        RedirectView.as_view(url='/media/features/oldctphotos/oldctphotos.html',
                                      permanent=False)),

    url(r'^article/custodian-baths_2931/$',
        RedirectView.as_view(url='/media/features/longstreet/longstreet.html',
                                      permanent=False)),

    url(r'^article/hout-bays-scrapyard-sculptors_2955/$',
        RedirectView.as_view(url='/media/features/houtbaysculptors/houtbaysculptors.html',
                                      permanent=False)),

    url(r'^article/when-government-gentrifies-case-de-waal-drive-flats_2985/$',
        RedirectView.as_view(url='/media/features/gentrification/gentrification.html',
                                      permanent=False)),

    url(r'^article/waiting-waiting-and-waiting-doctor_3064/$',
        RedirectView.as_view(url='/media/features/clinicqueues/clinicqueues_0016.html',
                                      permanent=False)),

    url(r'^article/battle-over-bleak-houses-citys-edge_3078/$',
        RedirectView.as_view(url='/media/features/wolwerivier/wolwerivier_0017.html',
                                      permanent=False)),

    url(r'^article/murder-long-street-congolese-bouncers-and-private-security-industry_3092/$',
        RedirectView.as_view(url='/media/features/murderlongstreet/murderlongstreet_0018.html',
                                      permanent=False)),

    url(r'^article/incredible-journey-how-lady-lost-mongrel-found-her-way-home_3104/$',
        RedirectView.as_view(url='/media/features/incrediblejourney/incrediblejourney_0019.html',
                                      permanent=False)),

    url(r'^article/why-hout-bay-fishermen-die-making-living_3200/$',
        RedirectView.as_view(url='/media/features/hangberg/hangberg_0020.html',
                                      permanent=False)),


    url(r'^article/cape-towns-pakistani-cellphone-connection_3247/$',
        RedirectView.as_view(url='/media/features/cellphones/cellphones_0021.html',
                                      permanent=False)),

    url(r'^article/long-battle-get-mines-cough_3271/$',
        RedirectView.as_view(url='/media/features/silicosis/silicosis_0022.html',
                                      permanent=False)),

    url(r'^article/student-fees-facts-figures-and-observations_3423/$',
        RedirectView.as_view(url='/media/features/studentfees/studentfees_0023.html',
                                      permanent=False)),

    url(r'^article/photos-and-video-students-uwc-march-feesmustfall_3433/$',
        RedirectView.as_view(url='/media/features/uwcmarch/uwcmarch_0024.html',
                                      permanent=False)),

    url(r'^article/feesmustfall-protest-union-buildings-photo-time-line-what-happened_3434/$',
        RedirectView.as_view(url='/media/features/unionbuildings/unionbuildings_0025.html',
                                      permanent=False)),


    url(r'^article/toilet-collectors_3462/$',
        RedirectView.as_view(url='/media/features/potapota/potapota_0026.html',
                                      permanent=False)),

    url(r'^article/2015-photos_3606/$',
        RedirectView.as_view(url='/media/features/2015photos/2015photos.html',
                                      permanent=False)),

    # Some old flatpages

    url(r'^about-groundup/$',
        RedirectView.as_view(url='/about/',
                                      permanent=True)),

    url(r'^content/contact-us/$',
        RedirectView.as_view(url='/',
                                      permanent=True)),

    url(r'^get-your-opinion-piece-published/$',
        RedirectView.as_view(url='/publish/',
                                      permanent=True)),



    ###############################

    url(r'^article/(?P<slug>[-\w]+)/$',
        cache_except_staff(
            decorator=cache_page(settings.CACHE_PERIOD,
                                 key_prefix='article'))
        (views.article_detail), name='article.detail'),

    url(r'^copy_article/(?P<slug>[-\w]+)/$',
        views.copy_article, name='article.copy'),

    url(r'^article_concurrent$',
        views.check_concurrent_edit, name='article.concurrent_check'),

    url(r'^author/$', views.AuthorList.as_view(),
        name="author.list"),

    url(r'^author/([0-9]+)/$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.AuthorDetail.as_view()), name='author.detail'),

    url(r'^sites/default/(?P<path>.*)$',
        views.RedirectOldImages.as_view(), name='old_image.redirect'),

    url(r'^features/(?P<path>.*)$',
        views.RedirectHandConstructedFeatures.as_view(),
        name='features.redirect'),

    ####################################
    # Redirect /content/ to /article

    url(r'^content/(?P<path>.*)$',
        views.RedirectContentToArticle.as_view(), name='content.redirect'),

    url(r'^photoessay/(?P<path>.*)$',
        views.RedirectContentToArticle.as_view(), name='content.redirect'),

    url(r'^gallery/(?P<path>.*)$',
        views.RedirectContentToArticle.as_view(), name='content.redirect'),


    ####################################

    url(r'^sitenews/rss/$', feeds.LatestArticlesRssFeed()),
    url(r'^sitenews/atom/$', feeds.LatestArticlesAtomFeed()),
]

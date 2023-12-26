from django.views.decorators.cache import cache_page
from django.views.generic.base import RedirectView
from django.urls import path, re_path

from . import feeds, settings, views
from .utils import cache_except_staff

app_name = "newsroom"


urlpatterns = [
    re_path(r'^$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.home_page_view),
        name='home'),

    re_path(r'^advanced_search/$', views.advanced_search, name='advanced.search'),

    re_path(r'^category/opinion_and_analysis/$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.OpinionAnalysisList.as_view()),
        name='article.opinion_analysis'),

    re_path(r'^category/groundview/$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.GroundViewList.as_view()),
        name='article.groundview'),

    path('correction/list/', views.ListCorrection.as_view(),
         name='correction.list'),
    path('correction/create/', views.CreateCorrection.as_view(),
         name='correction.create'),
    path('correction/update/<int:pk>', views.UpdateCorrection.as_view(),
         name='correction.update'),
    path('correction/delete/<int:pk>', views.DeleteCorrection.as_view(),
         name='correction.delete'),


    re_path(r'^category/$', views.CategoryList.as_view(),
        name="category.list"),

    re_path(r'^category/([-\s\w]+)/$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.CategoryDetail.as_view()), name='category.detail'),

    re_path(r'^region/$', views.RegionList.as_view(),
        name="region.list"),

    re_path(r'^region/(.*)$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.RegionDetail.as_view()), name='region.detail'),

    # Make it a long cache because this makes hundreds of database calls
    re_path(r'^topic/$', cache_page(settings.CACHE_PERIOD * 25)
        (views.TopicList.as_view()),
        name="topic.list"),

    re_path(r'^topic/([-\s\w]+)/$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.TopicDetail.as_view()), name='topic.detail'),

    re_path(r'^user/$', views.account_profile,
        name="user.profile"),

    re_path(r'^account/logout-from-all-devices/$', views.logout_from_all_sessions,
        name="account_logout_from_all_devices"),

    ##############################
    # Author create and update

    path('author/create/', views.AuthorCreate.as_view(), name='author.add'),
    path('author/update/<int:pk>/', views.AuthorUpdate.as_view(),
         name='author.update'),


    ###############################
    # Article list generate

    re_path(r'^generate_article_list/$',
        views.generate_article_list, name='generate_article_list'),

    ##############################
    # Topic create and update

    path('topic_edit/create/', views.TopicCreate.as_view(), name='topic_create'),
    path('topic_edit/update/<int:pk>/', views.TopicUpdate.as_view(),
         name='topic_update'),

    ###############################
    # Article preview

    path('preview/<slug:secret_link>/', views.article_preview,
         name='article.preview'),
    path('prev_gen/<int:pk>', views.article_gen_preview,
         name='article.gen_preview'),


    ###############################
    # Wetell
    path('wetell/', views.WetellListView.as_view(),
         name='wetell.list'),

    path('wetell/latest/', views.WetellLatestView.as_view(),
         name='wetell.latest'),

    path('wetell/<int:pk>/', views.WetellDetailView.as_view(),
         name='wetell.detail'),

    ###############################
    # Old feature article redirects
    re_path(r'^article/redhills-ruins-cape-towns-forgotten-district-six_2043/$',
        RedirectView.as_view(url='/media/features/redhill/redhill_2043.html',
                             permanent=False)),

    re_path(r'^article/mpumalanga-crisis-why-nobody-listening_2236/$',
        RedirectView.as_view(url='/media/features/mpumalanga/mpumalanga_0002.html',
                             permanent=False)),

    re_path(r'^article/will-i-make-money-today-waiting-work-side-road_2245/$',
        RedirectView.as_view(url='/media/features/menatsideofroad/menatroadside_0003.html',
                             permanent=False)),

    re_path(r'^article/long-trek-education-city-students_2400/$',
        RedirectView.as_view(url='/media/features/westlake/westlake_0004.html',
                             permanent=False)),

    re_path(r'^article/house-full-faeces-khayelitsha_2447/$',
        RedirectView.as_view(url='/media/features/faeces/house_faeces_0005.html',
                             permanent=False)),

    re_path(r'^article/fishing-black-river_2514/$',
        RedirectView.as_view(url='/media/features/blackriver/blackriver_0006.html',
                             permanent=False)),

    re_path(r'^article/ocean-view-fisher-blues-part-one_2657/$',
        RedirectView.as_view(url='/media/features/daff/daff_1_0008.html',
                             permanent=False)),

    re_path(r'^article/ocean-view-fisher-blues-part-two_2658/$',
        RedirectView.as_view(url='/media/features/daff/daff_2_0008.html',
                             permanent=False)),

    re_path(r'^article/how-free-state-health-system-being-destroyed_2722/$',
        RedirectView.as_view(url='/media/features/freestatehealth/freestatehealth.html',
                             permanent=False)),

    re_path(r'^article/tee-along-n2_2761/$',
        RedirectView.as_view(url='/media/features/n2golfer/n2golfer.html',
                             permanent=False)),

    re_path(r'^article/living-hole-ground-district-six_2767/$',
        RedirectView.as_view(url='/media/features/holeground/holeground.html',
                             permanent=False)),

    re_path(r'^article/rhodes-falls_2824/$',
        RedirectView.as_view(url='/media/features/RhodesFalls/rhodesfalls.html',
                             permanent=False)),

    re_path(r'^article/lost-karretjie-people-karoo_2825/$',
        RedirectView.as_view(url='/media/features/karretjie/karretjiepeople.html',
                             permanent=False)),

    re_path(r'^article/beautiful-photos-old-cape-town_2869/$',
        RedirectView.as_view(url='/media/features/oldctphotos/oldctphotos.html',
                                      permanent=False)),

    re_path(r'^article/custodian-baths_2931/$',
        RedirectView.as_view(url='/media/features/longstreet/longstreet.html',
                             permanent=False)),

    re_path(r'^article/hout-bays-scrapyard-sculptors_2955/$',
        RedirectView.as_view(url='/media/features/houtbaysculptors/houtbaysculptors.html',
                             permanent=False)),

    re_path(r'^article/when-government-gentrifies-case-de-waal-drive-flats_2985/$',
        RedirectView.as_view(url='/media/features/gentrification/gentrification.html',
                             permanent=False)),

    re_path(r'^article/waiting-waiting-and-waiting-doctor_3064/$',
        RedirectView.as_view(url='/media/features/clinicqueues/clinicqueues_0016.html',
                             permanent=False)),

    re_path(r'^article/battle-over-bleak-houses-citys-edge_3078/$',
        RedirectView.as_view(url='/media/features/wolwerivier/wolwerivier_0017.html',
                             permanent=False)),

    re_path(r'^article/murder-long-street-congolese-bouncers-and-private-security-industry_3092/$',
        RedirectView.as_view(url='/media/features/murderlongstreet/murderlongstreet_0018.html',
                             permanent=False)),

    re_path(r'^article/incredible-journey-how-lady-lost-mongrel-found-her-way-home_3104/$',
        RedirectView.as_view(url='/media/features/incrediblejourney/incrediblejourney_0019.html',
                             permanent=False)),

    re_path(r'^article/why-hout-bay-fishermen-die-making-living_3200/$',
        RedirectView.as_view(url='/media/features/hangberg/hangberg_0020.html',
                             permanent=False)),


    re_path(r'^article/cape-towns-pakistani-cellphone-connection_3247/$',
        RedirectView.as_view(url='/media/features/cellphones/cellphones_0021.html',
                             permanent=False)),

    re_path(r'^article/long-battle-get-mines-cough_3271/$',
        RedirectView.as_view(url='/media/features/silicosis/silicosis_0022.html',
                             permanent=False)),

    re_path(r'^article/student-fees-facts-figures-and-observations_3423/$',
        RedirectView.as_view(url='/media/features/studentfees/studentfees_0023.html',
                             permanent=False)),

    re_path(r'^article/photos-and-video-students-uwc-march-feesmustfall_3433/$',
        RedirectView.as_view(url='/media/features/uwcmarch/uwcmarch_0024.html',
                             permanent=False)),

    re_path(r'^article/feesmustfall-protest-union-buildings-photo-time-line-what-happened_3434/$',
        RedirectView.as_view(url='/media/features/unionbuildings/unionbuildings_0025.html',
                             permanent=False)),


    re_path(r'^article/toilet-collectors_3462/$',
        RedirectView.as_view(url='/media/features/potapota/potapota_0026.html',
                             permanent=False)),

    re_path(r'^article/2015-photos_3606/$',
        RedirectView.as_view(url='/media/features/2015photos/2015photos.html',
                             permanent=False)),

    # Some old flatpages

    re_path(r'^about-groundup/$',
        RedirectView.as_view(url='/about/',
                             permanent=True)),

    re_path(r'^content/contact-us/$',
        RedirectView.as_view(url='/',
                             permanent=True)),

    re_path(r'^get-your-opinion-piece-published/$',
        RedirectView.as_view(url='/publish/',
                             permanent=True)),


    # Old search
    re_path(r'^search/$',
        RedirectView.as_view(url='/advanced_search/',
                             permanent=True)),


    ###############################

    re_path(r'^article/(?P<slug>[-\w]+)/$',
        cache_except_staff(
            decorator=cache_page(settings.CACHE_PERIOD,
                                 key_prefix='article'))
        (views.article_detail), name='article.detail'),

    re_path(r'^article_add/',
         views.article_new, name='article.add'),

    re_path(r'^article-print/(?P<slug>[-\w]+)/$',
        cache_except_staff(
            decorator=cache_page(settings.CACHE_PERIOD,
                                 key_prefix='article'))
        (views.article_print), name='article.print'),


    re_path(r'^copy_article/(?P<slug>[-\w]+)/$',
        views.copy_article, name='article.copy'),

    re_path(r'^article_concurrent$',
        views.check_concurrent_edit, name='article.concurrent_check'),

    re_path(r'^author/$', views.AuthorList.as_view(),
        name="author.list"),

    re_path(r'^author/([0-9]+)/$',
        cache_except_staff(decorator=cache_page(settings.CACHE_PERIOD))
        (views.AuthorDetail.as_view()), name='author.detail'),

    re_path(r'^sites/default/(?P<path>.*)$',
        views.RedirectOldImages.as_view(), name='old_image.redirect'),

    re_path(r'^features/(?P<path>.*)$',
        views.RedirectHandConstructedFeatures.as_view(),
        name='features.redirect'),

    ####################################
    # Redirect /content/ to /article

    re_path(r'^content/(?P<path>.*)$',
        views.RedirectContentToArticle.as_view(), name='content.redirect'),

    re_path(r'^photoessay/(?P<path>.*)$',
        views.RedirectContentToArticle.as_view(), name='content.redirect'),

    re_path(r'^gallery/(?P<path>.*)$',
        views.RedirectContentToArticle.as_view(), name='content.redirect'),


    ####################################

    path('sitenews/rss/', feeds.LatestArticlesRssFeed()),
    path('sitenews/atom/', feeds.LatestArticlesAtomFeed()),
    path('sitenews/rss_full/', feeds.LatestFullArticlesRssFeed()),
    path('sitenews/atom_full/', feeds.LatestFullArticlesAtomFeed()),
]

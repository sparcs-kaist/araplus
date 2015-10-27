from apps.session.urls import url


# This url is under "session/group/"
urlpatterns = [
    url(r'^$', 'apps.session.group.views.view_group_list'),
    url(r'^make/', 'apps.session.group.views.make_group'),
    url(r'^message/(?P<groupname>[a-z A-Z 0-9]+)/$',
        'apps.session.group.views.group_message'),
    url(r'^message/(?P<groupname>[a-z A-Z 0-9]+)/manage/',
        'apps.session.group.views.manage'),
]

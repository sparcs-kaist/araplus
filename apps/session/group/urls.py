from apps.session.urls import url


# This url is under "session/group/"
urlpatterns = [
    url(r'^$', 'apps.session.group.views.view_group_list'),
    url(r'^makegroup/', 'apps.session.group.views.make_group'),
]

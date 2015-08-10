from apps.session.urls import url


# This url is under "session/message/"
urlpatterns = [
    url(r'^$', 'apps.session.message.views.check_message'),
    url(r'^send/', 'apps.session.message.views.send_message'),
    url(r'^thread/$', 'apps.session.message.views.go_thread'),
    url(r'^thread/(?P<nickname>[a-z A-Z 0-9]+)/',
        'apps.session.message.views.check_thread'),
    # ex) session/message/thread/tonykim
    url(r'^sent/', 'apps.session.message.views.check_sent_message'),
    url(r'^block/', 'apps.session.message.views.block'),
    url(r'^blocklist/', 'apps.session.message.views.show_block_list'),
]

from django.conf.urls import url
from apps.session.urls import url
from .. import views


# This url is under "message/"
urlpatterns = [
    url(r'^$', 'apps.session.views.send_message'),
    url(r'check/', 'apps.session.views.send_message'),
    url(r'thread/individual/(?P<nickname>[a-z A-Z 0-9]+)/',
        'apps.session.views.check_thread'),
    url(r'sent/', 'apps.session.views.check_sent_message'),
    url(r'block/', 'apps.session.views.block'),
    url(r'blocklist/', 'apps.session.views.show_block_list'),
]



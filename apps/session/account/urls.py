from apps.session.urls import url


# This url is under  "session/account"
urlpatterns = [
    url(r'^$', 'apps.session.account.views.account_info'),
    url(r'^modify/$','apps.session.account.views.account_modify'),
]

from django.conf import settings
from django.urls import include, path

from common import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    path("robots.txt", views.RobotsTxtView.as_view(), name="robots_txt"),
    path("todays_album/", views.TodaysAlbumView.as_view(), name="todays_album"),
    path("past_albums/", views.AlbumListView.as_view(), name="past_albums"),
    path("review/<uuid:pk>/", views.AlbumReviewView.as_view(), name="album_review"),
    path("album_reviews/<uuid:pk>", views.AlbumReviewListView.as_view(), name="album_review_list"),
]
if settings.DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

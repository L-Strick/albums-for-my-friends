from django.conf import settings
from django.urls import include, path

from common import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("logout", views.LogoutView.as_view(), name="logout"),
    path("robots.txt", views.RobotsTxtView.as_view(), name="robots_txt"),
    path("todays_album/", views.TodaysAlbumView.as_view(), name="todays_album"),
    path("past_albums/", views.AlbumListView.as_view(), name="past_albums"),
    path("review/album/<uuid:album_id>/", views.AlbumReviewView.as_view(), name="create_album_review"),
    path("review/<uuid:pk>/", views.AlbumReviewView.as_view(), name="album_review"),
    path("album_reviews/<uuid:pk>/", views.AlbumReviewListView.as_view(), name="album_review_list"),
    path("album_reviews/<uuid:review_id>/user/<uuid:user_id>/vote/<str:vote>/", views.ReviewVoteView.as_view(), name="user_review_vote"),
    path("statistics/", views.StatisticsView.as_view(), name="statistics"),
]
if settings.DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

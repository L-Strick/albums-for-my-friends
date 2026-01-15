import random
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.contrib import messages
from django.contrib.auth import logout
from django.conf import settings
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse
from django.views.generic.edit import FormView, UpdateView
from common.forms import SampleForm, AlbumReviewForm
from common.models import Album, AlbumReview, User, UserReviewThumb


class IndexView(TemplateView):
    template_name = "common/index.html"


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("index")


class RobotsTxtView(View):
    def get(self, request):
        if settings.PRODUCTION:
            # Allow all (note that a blank Disallow block means "allow all")
            lines = ["User-agent: *", "Disallow:"]
        else:
            # Block all
            lines = ["User-agent: *", "Disallow: /"]
        return HttpResponse("\n".join(lines), content_type="text/plain")


class TodaysAlbumView(FormView):
    template_name = 'common/todays_album.html'
    form_class = AlbumReviewForm
    album = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.album = self.get_todays_album()

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        try:
            album_review = AlbumReview.objects.get(album=self.album, user=self.request.user)
            return form_class(instance=album_review, **self.get_form_kwargs())
        except AlbumReview.DoesNotExist:
            return form_class(**self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.album = self.album
        form.instance.user = self.request.user
        form.save()
        return super(TodaysAlbumView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"album": self.album})
        return context

    def get_todays_album(self):
        today = datetime.now(ZoneInfo('America/New_York'))
        doy = today.weekday()
        if doy in [0, 3]:
            if not Album.objects.filter(made_todays_album__gte=datetime.now(ZoneInfo('America/New_York')) - timedelta(hours=24)).exists():
                album = random.choice(Album.objects.filter(made_todays_album__isnull=True))
                album.update(made_todays_album=datetime.now(ZoneInfo('America/New_York')))
                return album
            else:
                return Album.objects.filter(made_todays_album__isnull=False).order_by('-made_todays_album').first()
        else:
            return Album.objects.filter(made_todays_album__isnull=False).order_by('-made_todays_album').first()

    def get_success_url(self):
        return reverse("todays_album")


class AlbumListView(ListView):
    model = Album
    template_name = 'common/album_list_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        albums = self.get_queryset()
        user_reviews = AlbumReview.objects.filter(album__in=albums, user=self.request.user)
        user_review_lookup = {
            review.album_id: {"rating": review.rating, "id": review.id}
            for review in user_reviews
        }
        for album in albums:
            if album.id not in user_review_lookup.keys():
                user_review_lookup[album.id] = {"rating": '--', "id": ''}
        context["user_review_lookup"] = user_review_lookup
        return context

    def get_queryset(self):
        todays_album_id = None
        if TodaysAlbumView().album:
            todays_album_id = TodaysAlbumView().album.id
        return self.model.objects.filter(
            Q(~Q(id=todays_album_id) & Q(made_todays_album__isnull=False))
        ).prefetch_related('reviews')


class AlbumReviewView(UpdateView):
    model = AlbumReview
    form_class = AlbumReviewForm
    template_name = 'common/album_review.html'

    def get_object(self, queryset=None):
        try:
            return super(AlbumReviewView, self).get_object(queryset)
        except AttributeError:
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(AlbumReviewView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(AlbumReviewView, self).post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        try:
            if self.kwargs.get('pk'):
                album_review = AlbumReview.objects.get(album_id=self.kwargs.get('pk'), user=self.request.user)
                return form_class(instance=album_review, **self.get_form_kwargs())
            else:
                return form_class(**self.get_form_kwargs())
        except AlbumReview.DoesNotExist:
            return form_class(**self.get_form_kwargs())

    def form_valid(self, form):
        if not self.object:
            form.instance.album = Album.objects.get(id=self.kwargs['album_id'])
            form.instance.user = self.request.user
        form.save()
        return super(AlbumReviewView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'album_id' in self.kwargs:
            album = Album.objects.get(id=self.kwargs['album_id'])
        elif self.object:
            album = self.object.album
        else:
            album = None
        context['album'] = album
        return context

    def get_success_url(self):
        return reverse("past_albums")


class AlbumReviewListView(ListView):
    model = AlbumReview
    template_name = 'common/album_review_list_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = Album.objects.get(id=self.kwargs.get('pk'))
        reviews = album.reviews.all()
        user_likes = []
        user_dislikes = []
        like_counter_lookup = {review.id: UserReviewThumb.objects.filter(review=review, thumbs_up=True).count() for review in reviews}
        dislike_counter_lookup = {review.id: UserReviewThumb.objects.filter(review=review, thumbs_down=True).count() for review in reviews}
        for review in reviews:
            if UserReviewThumb.objects.filter(review=review, user=self.request.user, thumbs_up=True).exists():
                user_likes.append(review.id)
            if UserReviewThumb.objects.filter(review=review, user=self.request.user, thumbs_down=True).exists():
                user_dislikes.append(review.id)
        reviewed_users = reviews.values_list('user_id', flat=True)
        waiting_on = User.objects.filter(~Q(id__in=reviewed_users))
        context.update({"album": album, "user_likes": user_likes, "user_dislikes": user_dislikes, "like_counter_lookup": like_counter_lookup, "dislike_counter_lookup": dislike_counter_lookup, "waiting_on": waiting_on})
        return context

    def get_queryset(self):
        return AlbumReview.objects.filter(album_id=self.kwargs.get('pk'))


class StatisticsView(TemplateView):
    template_name = 'common/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.all()
        todays_album_id = None
        if TodaysAlbumView().album:
            todays_album_id = TodaysAlbumView().album.id
        reviews = AlbumReview.objects.filter(~Q(album__id=todays_album_id) & Q(rating__isnull=False))
        user_reviews = defaultdict(list)
        user_data_dict = {}
        for review in reviews:
            user_reviews[review.user].append(review.rating)
        reviewed_albums = Album.objects.filter(~Q(id=todays_album_id) & Q(made_todays_album__isnull=False))
        user_submitted_albums = defaultdict(list)
        for album in reviewed_albums:
            user_submitted_albums[album.submitted_by].append(album)
        for user in users:
            if user_reviews[user]:
                user_data_dict[user] = {"max": max(user_reviews[user]), "min": min(user_reviews[user]), "avg": str(round(statistics.mean(user_reviews[user]), 2))}
            else:
                user_data_dict[user] = {"max": "--", "min": "--", "avg": "--"}
            if user_submitted_albums[user]:
                user_data_dict[user]["submitted_avg"] = str(round(statistics.mean([float(album.get_average_score()) for album in user_submitted_albums[user]]), 2))
            else:
                user_data_dict[user]["submitted_avg"] = "--"
            user_data_dict[user]["likes"] = UserReviewThumb.objects.filter(review__user=user, thumbs_up=True).count()
            user_data_dict[user]["dislikes"] = UserReviewThumb.objects.filter(review__user=user, thumbs_down=True).count()
        context["user_data_dict"] = user_data_dict
        if reviews.count() > 0:
            context["average_review"] = str(round(statistics.mean(reviews.values_list('rating', flat=True)), 2))
        else:
            context["average_review"] = "--"
        average_scores = [(album, float(album.get_average_score())) for album in reviewed_albums]
        highest_rated_album = sorted(average_scores, key=lambda x: x[1], reverse=True)[0]
        lowest_rated_album = sorted(average_scores, key=lambda x: x[1])[0]
        album_ratings_lookup = {album.id: album.reviews.filter(rating__isnull=False).values_list('rating', flat=True) for album in reviewed_albums}
        album_controversy = [(album, round(statistics.stdev(album_ratings_lookup[album.id]), 2), max(album_ratings_lookup[album.id]), min(album_ratings_lookup[album.id])) for album in reviewed_albums if len(album_ratings_lookup[album.id]) > 1]
        most_controversial_album = sorted(album_controversy, key=lambda x: x[1], reverse=True)[0] if len(album_controversy) > 0 else (None, None, None, None)
        least_controversial_album = sorted(album_controversy, key=lambda x: x[1])[0] if len(album_controversy) > 0 else (None, None, None, None)
        context.update({
            "highest_rated_album": highest_rated_album[0],
            "lowest_rated_album": lowest_rated_album[0],
            "most_controversial_album": most_controversial_album[0],
            "most_controversial_stdev": most_controversial_album[1],
            "most_controversial_high": most_controversial_album[2],
            "most_controversial_low": most_controversial_album[3],
            "least_controversial_album": least_controversial_album[0],
            "least_controversial_stdev": least_controversial_album[1],
            "least_controversial_high": least_controversial_album[2],
            "least_controversial_low": least_controversial_album[3],
        })
        return context


class ReviewVoteView(View):
    def post(self, *args, **kwargs):
        user = User.objects.get(id=kwargs.get('user_id'))
        review = AlbumReview.objects.get(id=kwargs.get('review_id'))
        vote = kwargs.get('vote')
        user_thumb = UserReviewThumb.objects.filter(review=review, user=user).first()
        if not user_thumb:
            user_thumb = UserReviewThumb.objects.create(review=review, user=user)
        if vote == 'like':
            if user_thumb.thumbs_up:
                user_thumb.update(thumbs_up=False, thumbs_down=False)
            else:
                user_thumb.update(thumbs_up=True, thumbs_down=False)
        elif vote == 'dislike':
            if user_thumb.thumbs_down:
                user_thumb.update(thumbs_up=False, thumbs_down=False)
            else:
                user_thumb.update(thumbs_up=False, thumbs_down=True)
        return redirect('album_review_list', pk=review.album.id)


class SampleFormView(FormView):
    # TODO: delete me; this is just a reference example
    form_class = SampleForm

def error_404(request, exception):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)

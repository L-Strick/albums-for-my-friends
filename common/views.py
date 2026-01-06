import random
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
from common.models import Album, AlbumReview, User


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
        context.update({"album": Album.objects.get(id=self.kwargs.get('pk'))})
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
        reviews = AlbumReview.objects.filter(~Q(album__id=todays_album_id))
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
                user_data_dict[user] = {"max": max(user_reviews[user]), "min": min(user_reviews[user]), "avg": str(round(sum(user_reviews[user]) / len(user_reviews[user]), 2))}
            else:
                user_data_dict[user] = {"max": "--", "min": "--", "avg": "--"}
            if user_submitted_albums[user]:
                user_data_dict[user]["submitted_avg"] = str(round(sum([album.get_average_score for album in user_submitted_albums[user]]) / len(user_submitted_albums[user]), 2))
            else:
                user_data_dict[user]["submitted_avg"] = "--"
        context["user_data_dict"] = user_data_dict
        return context


class SampleFormView(FormView):
    # TODO: delete me; this is just a reference example
    form_class = SampleForm

def error_404(request, exception):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)

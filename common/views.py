import random
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
from common.models import Album, AlbumReview


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
        if Album.objects.filter(made_todays_album__gte=datetime.now(ZoneInfo('America/New_York')) - timedelta(hours=24)).exists():
            return Album.objects.filter(made_todays_album__gte=datetime.now(ZoneInfo('America/New_York')) - timedelta(hours=24)).first()
        else:
            album = random.choice(Album.objects.filter(made_todays_album__isnull=True))
            album.update(made_todays_album=datetime.now(ZoneInfo('America/New_York')))
            return album

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
        return self.model.objects.filter(
            Q(~Q(id=TodaysAlbumView().album.id) & Q(made_todays_album__isnull=False))
        ).prefetch_related('reviews')


class AlbumReviewView(UpdateView):
    model = AlbumReview
    form_class = AlbumReviewForm
    template_name = 'common/album_review.html'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        try:
            album_review = AlbumReview.objects.get(album_id=self.kwargs.get('pk'), user=self.request.user)
            return form_class(instance=album_review, **self.get_form_kwargs())
        except AlbumReview.DoesNotExist:
            return form_class(**self.get_form_kwargs())

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


class SampleFormView(FormView):
    # TODO: delete me; this is just a reference example
    form_class = SampleForm

def error_404(request, exception):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)

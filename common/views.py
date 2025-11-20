import random
from datetime import datetime, timedelta

from django.contrib.auth import logout
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse
from django.views.generic.edit import FormView
from common.forms import SampleForm
from common.models import Album


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


class TodaysAlbumView(TemplateView):
    album = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.album = self.get_todays_album()

    def get_todays_album(self):
        if Album.objects.filter(made_todays_album__gte=datetime.now() - timedelta(hours=24)).exists():
            return Album.objects.filter(made_todays_album__gte=datetime.now() - timedelta(hours=24)).first()
        else:
            today = datetime.now().date()
            random.seed(today)
            choices = Album.objects.filter(made_todays_album__isnull=True)
            return random.choice(choices)


class SampleFormView(FormView):
    # TODO: delete me; this is just a reference example
    form_class = SampleForm

def error_404(request, exception):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)

from django.contrib.auth import logout
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse
from django.views.generic.edit import FormView
from common.forms import SampleForm


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


class SampleFormView(FormView):
    # TODO: delete me; this is just a reference example
    form_class = SampleForm

def error_404(request, exception):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)

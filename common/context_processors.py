from common.constants import EMAIL_WHITELIST


def django_settings(request):
    from django.conf import settings
    return {
        "PRODUCTION": settings.PRODUCTION,
        "LOCALHOST": settings.LOCALHOST,
        "EMAIL_WHITELIST": EMAIL_WHITELIST,
    }

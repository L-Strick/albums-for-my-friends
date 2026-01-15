from common.constants import EMAIL_WHITELIST


def django_settings(request):
    from django.conf import settings
    return {
        "PRODUCTION": settings.PRODUCTION,
        "LOCALHOST": settings.LOCALHOST,
        "EMAIL_WHITELIST": EMAIL_WHITELIST,
        "user_id": request.user.id,
        "DATATABLES_CSS_URL": '//cdn.datatables.net/2.3.6/css/dataTables.dataTables.min.css',
        "DATATABLES_JS_URL": "//cdn.datatables.net/2.3.6/js/dataTables.min.js",
        "DATATABLES_DATE_URL": "//cdn.datatables.net/plug-ins/2.3.6/sorting/datetime-moment.js",
    }

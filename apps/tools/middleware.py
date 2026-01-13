from django.utils import translation


class ForceLanguageMiddleware:
    """
    Middleware that activates language from cookie for all requests,
    including those outside i18n_patterns.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.COOKIES.get("django_language", "uk")
        translation.activate(language)
        request.LANGUAGE_CODE = language
        response = self.get_response(request)
        # Set default cookie if not present
        if "django_language" not in request.COOKIES:
            response.set_cookie("django_language", "uk", max_age=365 * 24 * 60 * 60)
        return response

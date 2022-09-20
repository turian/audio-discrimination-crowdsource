from django.conf import settings


def get_color(request):
    """Changes the color of top navbar according to
    DEVELOPMENT_MODE environment variable
    """
    if settings.DEVELOPMENT_MODE == "production":
        color_classes = "navbar-light bg-light"
    elif settings.DEVELOPMENT_MODE == "staging":
        color_classes = "navbar-dark bg-dark"
    elif settings.DEVELOPMENT_MODE == "local":
        color_classes = "navbar-dark bg-primary"
    return {"color_classes": color_classes}

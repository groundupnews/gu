from django.conf import settings

def newsroom_template_variables(request):
    return {'logo': settings.NEWSROOM_LOGO}

from newsroom import settings

def newsroom_template_variables(request):
    return {'logo': settings.LOGO}

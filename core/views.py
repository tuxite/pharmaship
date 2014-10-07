# -*- coding: utf-8; -*-
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.utils import translation
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch


import json

SYSTEM_APPS = ['core', 'bootstrapform']

def settings_links():
    """Returns a list of links for settings views."""
    # TODO: Update with Djan 1.7 AppConfig
    links = []
    for application in settings.INSTALLED_APPS:
        # Do not take in account Django's applications
        if "django" in application or application in SYSTEM_APPS:
            continue
        # By default, adding the general settings application to the dict
        if application == "settings":
            links.append({
                'name': _("Settings"),
                'url': reverse("settings:index"),
                'active': True
            })  
        # Looking if the applications has settings that can be imported
        else:
            try:
                links.append({
                    'name': _(application.capitalize()),
                    'url': reverse("settings:{0}:index".format(application)),
                })              
            except NoReverseMatch:
                pass
        
    links.append({'name': _('Import'), 'url': reverse("settings:import")})
    return links
    
def app_links(namespace):
    """Returns a list of links for application views."""
    links = []
    for application in settings.INSTALLED_APPS:
        # Do not take in account Django's applications
        if "django" in application or application in SYSTEM_APPS:
            continue
        # By default, adding the general settings application to the dict
        if application == "settings":
            # Settings application already taken in account in the layout
            continue
        
        if application == "inventory":
            a = "pharmaship"
        else:
            a = application
        if a == namespace.split(":")[0]:
            links.append({"name": a.capitalize(), "url_name": a + ":index", 'active': True})
        else:
            links.append({"name": a.capitalize(), "url_name": a + ":index"})
    return links

@permission_required('settings')
def settings_validation(request, form, instance=None):
    """Validates the form in args."""
    f = form(request.POST, instance=instance)
    if f.is_valid(): # All validation rules pass
        f.save()
        # Returning nothing
        data = json.dumps({'success':_('Data updated')})
        return HttpResponse(data, content_type="application/json")
    else:
        errors = dict([(k, [unicode(e) for e in v]) for k,v in f.errors.items()])
        data = json.dumps({'error': _('Something went wrong!'), 'details':errors})
        return HttpResponseBadRequest(data, content_type = "application/json")

@login_required
def index(request):
    """Default view. Displays an overview of the requisitions."""

    return render_to_response('core/index.html', {
                    'user': request.user,
                    'title': _("Home"),
                    'head_links': app_links(request.resolver_match.namespace),
                    },
                    context_instance=RequestContext(request))

@login_required
def set_language(request, language_code):
    if translation.check_for_language(language_code):
        if hasattr(request, 'session'):
                request.session['django_language'] = language_code
        else:
            request.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code)
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseBadRequest("Language code ({0}) unknown.".format(language_code), content_type="application/json")
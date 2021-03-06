# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpRequest
import re
from typing import Optional, Text

from zerver.models import get_realm, Realm, UserProfile

def get_subdomain(request):
    # type: (HttpRequest) -> Text

    # The HTTP spec allows, but doesn't require, a client to omit the
    # port in the `Host` header if it's "the default port for the
    # service requested", i.e. typically either 443 or 80; and
    # whatever Django gets there, or from proxies reporting that via
    # X-Forwarded-Host, it passes right through the same way.  So our
    # logic is a bit complicated to allow for that variation.
    #
    # For EXTERNAL_HOST, we take a missing port to mean that any port
    # should be accepted in Host.  It's not totally clear that's the
    # right behavior, but it keeps compatibility with older versions
    # of Zulip, so that's a start.

    host = request.get_host().lower()

    m = re.search('\.%s(:\d+)?$' % (settings.EXTERNAL_HOST,),
                  host)
    if m:
        subdomain = host[:m.start()]
        if subdomain in settings.ROOT_SUBDOMAIN_ALIASES:
            return Realm.SUBDOMAIN_FOR_ROOT_DOMAIN
        return subdomain

    return Realm.SUBDOMAIN_FOR_ROOT_DOMAIN

def is_subdomain_root_or_alias(request):
    # type: (HttpRequest) -> bool
    return get_subdomain(request) == Realm.SUBDOMAIN_FOR_ROOT_DOMAIN

def user_matches_subdomain(realm_subdomain, user_profile):
    # type: (Optional[Text], UserProfile) -> bool
    if realm_subdomain is None:
        return True
    return user_profile.realm.subdomain == realm_subdomain

def is_root_domain_available():
    # type: () -> bool
    if settings.ROOT_DOMAIN_LANDING_PAGE:
        return False
    return get_realm(Realm.SUBDOMAIN_FOR_ROOT_DOMAIN) is None

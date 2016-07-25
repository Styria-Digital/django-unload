# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django

DJANGO_VERSION = django.VERSION

if DJANGO_VERSION > (1, 8):
    from django.template.defaultfilters import register as filter_lib
    from django.templatetags.cache import register as cache_lib
    from django.templatetags.future import register as future_lib
    from django.templatetags.i18n import register as i18n_lib
    from django.templatetags.l10n import register as l10n_lib
    from django.templatetags.static import register as static_lib
    from django.templatetags.tz import register as tz_lib


BUILT_IN_FILTERS = filter_lib.filters.keys()
CACHE_FILTERS = cache_lib.filters.keys()
FUTURE_FILTERS = future_lib.filters.keys()
I18N_FILTERS = i18n_lib.filters.keys()
L10N_FILTERS = l10n_lib.filters.keys()
STATIC_FILTERS = static_lib.filters.keys()
TZ_FILTERS = tz_lib.filters.keys()

# https://docs.djangoproject.com/en/1.9/ref/templates/builtins/#built-in-tag-reference
BUILT_IN_TAGS = {
    'as': None,
    'autoescape': 'endautoescape',
    'block': 'endblock',
    'blocktrans': 'endblocktrans',
    'comment': 'endcomment',
    'csrf_token': None,
    'cycle': None,
    'debug': None,
    'extends': None,
    'filter': 'endfilter',
    'firstof': None,
    'for': 'endfor',
    'elif': None,
    'else': None,
    'empty': None,
    'if': 'endif',
    'ifchanged': 'endifchanged',
    'ifequal': 'endifequal',
    'ifnotequal': 'endifnotequal',
    'in': None,
    'include': None,
    'load': None,
    'lorem': None,
    'not': None,
    'now': None,
    'spaceless': 'endspaceless',
    'ssi': None,
    'templatetag': None,
    'url': None,
    'verbatim': 'endverbatim',
    'widthratio': None,
    'with': 'endwith'
}

I18N_TAGS = {
    'trans': 'endtrans',
    'blocktrans': 'endblocktrans',
    'plural': None,
    'get_language_info_list': None,
    'get_available_languages': None,
    'get_language_info': None,
    'language': None,
    'get_current_language': None,
    'get_current_language_bidi': None
}

L10N_TAGS = {
    'localize': 'endlocalize'
}

CACHE_TAGS = {
    'cache': 'endcache'
}

STATIC_TAGS = {
    'static': None,
    'get_media_prefix': None,
    'get_static_prefix': None
}

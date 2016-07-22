# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django

DJANGO_VERSION = django.VERSION

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

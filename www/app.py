#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Genial Wang'

import logging; logging.basicConfig(level=logging.INFO)
import sys, os
reload(sys)
sys.setdefaultencoding('utf-8')
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from plugin import highlight, toc, meta
import plugin.tool as tool

def init_jinja2(**kw):
    logging.info('init jinja2...')
    options = dict(
            autoescape = kw.get('autoescape', True),
            block_start_string = kw.get('block_start_string', '{%'),
            block_end_string = kw.get('block_end_string', '%}'),
            variable_start_string = kw.get('variable_start_string', '{{'),
            variable_end_string = kw.get('variable_end_string', '}}'),
            auto_reload = kw.get('auto_reload', True)
            )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    return env

def datetime_filter(t):
    dt = datetime.fromtimestamp(t)
    return '%syear %smonth %sday' % (dt.year, dt.month, dt.day)

a = [['flor1','one','tow'],['flor2','three','four']]
args = dict(foo = a)
env = init_jinja2(filters = dict(datetime = datetime_filter))
html = env.get_template('blogs.html').render(**args)
try:
    _pwd = './html/test.html'
    _dir = os.path.dirname(_pwd)
    if not os.path.exists(_dir):
        os.makedirs(_dir)
    f = open(_pwd, 'w')
    f.write(html)
except:
    tool.log('error')('html dir not found')


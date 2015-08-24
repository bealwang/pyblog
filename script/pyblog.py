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
from plugin import highlight, toc, meta

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
        path = ('../www/templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    return env

def get_file(path='../www/html/'):
    list_files = os.listdir(path)
    dirname = [x for x in list_files if os.path.isdir(path+x)]
    files = []
    for dir in dirname:
        temp_files = os.listdir(path+dir)
        dir_files = list(filter(lambda x: x.endswith('.html'),temp_files))
        if dir_files:
            dir_files = map(lambda x: os.path.splitext(x)[0],dir_files)
            dir_files.insert(0,dir)
            files.append(dir_files)
    return files

def render_template(template_name, args):
    env = init_jinja2()
    html = env.get_template(template_name+'.html').render(**args)
    try:
        if 'index' == template_name:
            _pwd = '../www/'+template_name+'.html'
        else:
            _pwd = '../www/html/blog/'+template_name+'.html'
        _dir = os.path.dirname(_pwd)
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        f = open(_pwd, 'w')
        f.write(html)
    except:
        logging.error('html dir not found')


if __name__ == '__main__':
    args = dict(foo = get_file())
    render_template('blog', args)
    render_template('index', args)

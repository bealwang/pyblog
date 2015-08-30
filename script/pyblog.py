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

class TocRenderer(highlight.HighlightMixin, toc.TocMixin ,mistune.Renderer):
    pass

def init_jinja2(**kw):
    logging.info('init jinja2...')
    options = dict(
            autoescape = kw.get('autoescape', False),
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
    html = env.get_template(template_name+'.html').render(**args).encode('utf-8')
    try:
        if 'index' == template_name or 'aboutme' == template_name:
            _pwd = '../www/'+template_name+'.html'
        else:
            _pwd = os.path.join('../www/html', args['categories'], args['basename'])
        _dir = os.path.dirname(_pwd)
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        f = open(_pwd, 'w')
        f.write(html)
    except:
        logging.error('html dir not found')

def generate_meta(args):
    p = u'<meta name = "description" content="' + args['title']  + '">'
    p += u'<meta name = "Keywords" content="' + args['tags'] + '">'
    return p

def md2html(md_pwd, mdp):
    dirname, filename = os.path.split(md_pwd)
    basename = os.path.splitext(filename)[0]+".html"
    categories = dirname.split("/")[-1]
    try:
        md = open(md_pwd,'r').read()
        utils = open('../www/templates/utils.html', 'r').read()
    except:
        logging.error('invalid md_pwd')
        return
    mdp.renderer.reset_toc()
    args, md = meta.parse(md)
    md = Environment().from_string(utils+md).render()
    content = mdp(md)
    args['categories'] = categories
    args['basename'] = basename
    args['content'] = content
    args['meta'] = generate_meta(args)
    render_template('blog', args)
    args['foo'] = get_file()
    render_template('index', args)
    render_template('aboutme', args)

if __name__ == '__main__':
    renderer = TocRenderer(linenos=True, inlinestyles=False)
    #renderer.reset_toc()
    mdp = mistune.Markdown(escape=True, renderer=renderer)
    #if len(sys.argv) == 1:
    #    md2html_all(mdp, 'post', '')
    #elif sys.argv[1] == 'test':
    #    md2html_all(mdp, 'post', '/home/septicmk/blog/html_test')
    #elif sys.argv[1] == 'sitemap':
    #    sitemap_update()
    md2html('../blogs/test/txt.md', mdp)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Genial Wang'

import logging; logging.basicConfig(level=logging.INFO)
import sys, os,re
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from jinja2 import Environment, FileSystemLoader
from plugin import highlight, toc, meta
reload(sys)
sys.setdefaultencoding('utf-8')

class TocRenderer(highlight.HighlightMixin, toc.TocMixin ,mistune.Renderer):
    pass

def init_jinja2(**kw):
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
        path = ('../templates')
    env = Environment(loader=FileSystemLoader(path), **options)
    return env

def findtoc(html):
    r1 = re.compile(r'<h2.*?>(.*?)<\/h2>')
    m = re.findall(r1, html)
    return m

def render_template(template_name, args):
    env = init_jinja2()
    html = env.get_template(template_name+'.html').render(**args).encode('utf-8')
    try:
        if 'index' == template_name or 'aboutme' == template_name:
            _pwd = '../'+template_name+'.html'
        else:
            _pwd = os.path.join('../blogs', args['showName']+'.html')
        _dir = os.path.dirname(_pwd)
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        f = open(_pwd, 'w')
        f.write(html)
        logging.info("write at "+_pwd)
    except:
        logging.error('html dir not found')

def generate_meta(args):
    p = u'<meta name="description" content="' + args['title']  + '">'
    p += u'<meta name="Keywords" content="' + args['tags'] + '">'
    return p

def parse_md(md_pwd, mdp, foo, rep):
    dirname, filename = os.path.split(md_pwd)
    try:
        md = open(md_pwd,'r').read()
        utils = open('../templates/utils.html', 'r').read()
    except:
        logging.error('invalid md_pwd')
        return
    mdp.renderer.reset_toc()
    args, md = meta.parse(md)

    showName = unicode(args['showName'], errors='ignore')
    showFile = unicode(args['showFile'], errors='ignore')
    title = unicode(args['title'], errors='ignore')
    rep[showName] = title
    ls = foo.get(showFile, None)
    if ls is None:
        foo[showFile] = [showName]
    else:
        ls.append(showName)

    md = Environment().from_string(utils+md).render()
    content = mdp(md)
    item_toc = findtoc(content)
    args['content'] = content
    args['meta'] = generate_meta(args)
    args['item_toc'] = item_toc
    args['show_url'] = "genialwang.com/blogs/" + showName + ".html"
    render_template('blog', args)
    return foo, rep

def parse_md_all(mdp, md_dir="../mdblogs"):
    args = dict()
    foo = dict()
    rep = dict()
    foo_file = list()
    for root, dirs, files in os.walk(md_dir):
        filter_files = filter(lambda x:os.path.splitext(x)[1]==".md", files)
        for md_files in filter_files:
            md_path = os.path.join(root, md_files)
            foo, rep = parse_md(md_path, mdp, foo, rep)
    for k, v in foo.items():
        v.insert(0, k)
        foo_file.append(v)
    args['foo'] = foo_file
    args['rep'] = rep
    render_template('index', args)
    render_template('aboutme', args)

def sitemap_update():
    pwd = os.getcwd()
    _pwd = os.path.join(pwd,'html','sitemap.xml')
    des = open(_pwd, 'w')
    conf = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
      http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
"""
    conf += u"<url><loc>http://blog.septicmk.com/</loc>"
    conf += u"<lastmod>"+ get_mod_time("html/index.html") +u"</lastmod>"
    conf += u"<changefreq>weekly</changefreq>"
    conf += u"<priority>1.00</priority></url>"
    list_dirs = os.walk('html')
    for root, dirs, files in list_dirs:
        for f in files:
            if f.endswith('.html') and f!="google7b6f6c7b39c2bc4e.html" and f!='baidu_verify_lk0v2QeMl2.html':
                conf += u"<url><loc>http://blog.septicmk.com/"+ os.path.join(root, f)[5:] + u"</loc>"
                conf += u"<lastmod>"+ get_mod_time(os.path.join(root,f)) + u"</lastmod>"
                conf += u"<changefreq>weekly</changefreq>"
                conf += u"<priority>0.80</priority></url>"
    conf += u"</urlset>"
    des.write(conf)

if __name__ == '__main__':
    renderer = TocRenderer(linenos=True, inlinestyles=False)
    mdp = mistune.Markdown(escape=True, renderer=renderer)
    parse_md_all(mdp)

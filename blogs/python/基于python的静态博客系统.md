title:基于python的静态博客系统
tags:python, 静态, 博客, seo, 代码高亮
-----
##引言
当前流行的博客系统有很多,博主简单介绍两款:

- WordPress(WP):一个巨无霸的存在,但是博主在WP中并没有找到能很好支持markdown的插件.很多人离开的原因很
简单,它看起来已经不像是一个博客了...
- Hexo:这是一款台湾大学生的作品.相比于WP,hexo是一个基于node.js的小萝莉.作为一款轻量级的静态博客,hexo
越来越受人青睐.

好了,如果你觉得Hexo已经可以满足你的需求,那你就可以跳过本文了.但是如果你觉得WP实在是过于臃肿;如果你觉
得Hexo仍然存在很多冗余的东西;如果你想自主开发一个简单但却不平凡的博客系统,那么你可以参考本文的做法.
(下文将本文实现的博客系统称为pyblog)

##主要需求

 - 容易操作和使用
 - 博客快速生成
 - 支持markdown
 - 页面风格可定制

##运行环境

 - python2.7
 - jinja2 == 2.8
 - pygments == 2.0.2
 - mistune == 0.7

##构建前端框架
一个简洁优雅的前端界面可以让博客看起来更加舒适,本文结合前端框架[uikit](http://getuikit.com/)和一些第
三方JQuery插件进行前端界面的构建.界面采用平面化的风格,适当地添加了平滑滚动效果以增加用户体验.
{{ alert("博主对uikit原生的配色和布局方案可能略作改动,请谨慎使用", "warning") }}

##解析Markdown
得益于Mistune的使用,pyblog可以方便地将markdown文件解析为html文件.但是只是解析还不行,我们还有代码高亮
等一系列的需求尚未得到满足.
###代码高亮
首先,在pygment的帮助下,博主解决了代码高亮的问题.简单地说,pygment就是一个渲染代码的工具,它支持论坛,百
科等等页面中的超过300种语言书写的代码的高亮.

令人欣喜的是,pygment可以和Mistune配合使用来高亮markdown中的由符号{{ text("```", "success") }}包起来
的代码.按照Mistune的文档重写block_code模块.
```python
#highlight.py
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def block_code(text, lang, inlinestyles=False, linenos=False):
    if not lang:
        text = text.strip()
        return u'<pre><code>%s</code></pre>\n' % mistune.escape(text)

    try:
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(
            noclasses=inlinestyles, linenos=linenos
        )
        code = highlight(text, lexer, formatter)
        if linenos:
            return '<div class="source">%s</div>\n' % code
        return code
    except:
        return '<pre class="%s"><code>%s</code></pre>\n' % (
            lang, mistune.escape(text)
        )


class HighlightMixin(object):
    def block_code(self, text, lang):
        inlinestyles = self.options.get('inlinestyles')
        linenos = self.options.get('linenos')
        return block_code(text, lang, inlinestyles, linenos)
```
这一步只是设置了相应的markdown文件的解析规则,然后使用如下命令生成相应的CSS渲染文件,本博客使用的是
vim的native配色方案,更多的配色方案请参考[pygment](http://pygments.org/)官网.
```shell
pygmentize -f html -a .source -S native > pygments.css
```
###导航栏
其次,博主重写了toc模块,抓取markdown文件中的二级标题作为博客的垂直导航栏的内容.
```python
#toc.py
class TocMixin(object):
    def reset_toc(self):
        self.toc_tree = []
        self.toc_count = 0

    def header(self, text, level, raw=None):
        if level == 2:
            rv = '<h%d id="toc-%d">%s</h%d>\n' % (
                level, self.toc_count, text, level
            )
            self.toc_count += 1
        else:
            rv = '<h%d>%s</h%d>\n' % (
                level, text, level
            )

        self.toc_tree.append((self.toc_count, text, level, raw))
        return rv

    def render_toc(self, level=3):
        """Render TOC to HTML.

        :param level: render toc to the given level
        """
        return ''.join(self._iter_toc(level))

    def _iter_toc(self, level):
        first_level = None
        last_level = None

        yield '<ul id="table-of-content">\n'

        for toc in self.toc_tree:
            index, text, l, raw = toc

            if l > level:
                # ignore this level
                continue

            if first_level is None:
                # based on first level
                first_level = l
                last_level = l
                yield '<li><a href="#toc-%d">%s</a>' % (index, text)
            elif last_level == l:
                yield '</li>\n<li><a href="#toc-%d">%s</a>' % (index, text)
            elif last_level == l - 1:
                last_level = l
                yield '<ul>\n<li><a href="#toc-%d">%s</a>' % (index, text)
            elif last_level > l:
                # close indention
                yield '</li>'
                while last_level > l:
                    yield '</ul>\n</li>\n'
                    last_level -= 1
                yield '<li><a href="#toc-%d">%s</a>' % (index, text)

        # close tags
        yield '</li>\n'
        while last_level > first_level:
            yield '</ul>\n</li>\n'
            last_level -= 1

        yield '</ul>\n'
```
同样的,这里只是设置了markdown文件的解析规则,相应的二级标题的内容我们可以使用正则表达式获取.
```python
def findtoc(html):
    r1 = re.compile(r'<h2.*?>(.*?)<\/h2>')
    m = re.findall(r1, html)
    return m
```
最后需要将{{ text("HighlightMixin", "success") }}类和{{ text("TocMixin", "success") }}类加进Mistune
中.
```python
class TocRenderer(highlight.HighlightMixin, toc.TocMixin ,mistune.Renderer):
    pass
```
###使用jinja2
上述的工作做完之后,我们就可以着手具体的解析工作了.pyblog使用[jinja2](http://jinja.pocoo.org/)渲染
HTML模板.废话不多说,解析markdown的代码如下.
```python
def parse_md(md_pwd, mdp):
    dirname, filename = os.path.split(md_pwd)
    basename = os.path.splitext(filename)[0]+".html"
    categories = dirname.split("/")[-1]
    try:
        md = open(md_pwd,'r').read()
        utils = open('../templates/utils.html', 'r').read()
    except:
        logging.error('invalid md_pwd')
        return
    mdp.renderer.reset_toc()
    args, md = meta.parse(md)
    md = Environment().from_string(utils+md).render()
    content = mdp(md)
    item_toc = findtoc(content)
    args['categories'] = categories
    args['basename'] = basename
    args['content'] = content
    args['meta'] = generate_meta(args)
    args['item_toc'] = item_toc
    render_template('blog', args)
```
其中的args是位于markdown文件头的一些属性,我们依然可以使用正则表达式将它们提取出来.
```python
import re

INDENTATION = re.compile(r'\n\s{2,}')
META = re.compile(r'^(\w+):\s*(.*(?:\n\s{2,}.*)*)\n')

def parse(text):
    rv = {}
    m = META.match(text)

    while m:
        key = m.group(1)
        value = m.group(2)
        value = INDENTATION.sub('\n', value.strip())
        rv[key] = value
        text = text[len(m.group(0)):]
        m = META.match(text)

    return rv, text
```
当然了,为了避免愚蠢的每次都解析所有的md文件,pyblog提供了批量解析和单个文件解析的方案,在此就不多说了.
##扩展功能
###数学公式
这个不难,直接使用[mathjax](https://www.mathjax.org/),将下面的代码复制到标签内就可以使用了.
```HTML
<script type="text/x-mathjax-config"> 
    MathJax.Hub.Config({ 
        tex2jax: {inlineMath: [['$','$'], ['\\(','\\)']]} 
    }); 
</script>
<script type="text/javascript"
    src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>
```
###评论框
pyblog主要面向的是国内的用户,所以本着尽量避免翻墙的原则,选用了国内有名的[友言](http://www.uyan.cc/).
作为评论插件.登陆注册之后将你的专属js链接加入到博客模板即可.例如博主的专属js链接如下.
```HTML
    <script type="text/javascript" src="http://v2.uyan.cc/code/uyan.js?uid=2057486"></script>
```
{{ alert("这是博主的代码,需要换成自己的,请谨慎使用", "warning") }}

###用户概览
使用[Google Analytics](https://www.google.com/analytics/)可以统计分析网站上发生的活动,十分强大.同样
的,需要注册登陆之后将自己的专属js代码加入到模板中即可生效.博主的专属js代码为:
```JavaScript
(function(i,s,o,g,r,a,m)
 {i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
        m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
 })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
   ga('create', 'UA-66672167-1', 'auto');
   ga('send', 'pageview');
```
{{ alert("这是博主的代码,需要换成自己的,请谨慎使用", "warning") }}

###自定义标签
pyblog支持自定义标签,所有自定义的标签都在utils.html模板中:
```python
{ macro btn(value, link, type='primary') }
<a href="{link}" target="_blank"><button class="uk-button uk-button-{type}" type="button">{value}</button></a>
{ endmacro }

{ macro img(src, title, alt, group = 'my_group') }
<a href="{src}" data-uk-lightbox="{group:'{group}'}" title="{title}">
    <img src="{src}" alt="{alt}" />
</a>
{ endmacro }

{ macro alert(value, type='danger') }
<div class="uk-alert uk-alert-{type}">
    { if type == 'warning' }
    <i class="uk-icon-warning"></i>
    { elif type == 'danger' }
    <i class="uk-icon-bug"></i>
    { elif type == 'success' }
    <i class="uk-icon-check-square"></i>
    { else }
    <i class="uk-icon-info"></i>
    { endif }
    {{value}}
</div>
{ endmacro }
```
{{ alert("这些标签都是适应uikit框架的,用户可以修改适应其他的风格", "warning") }}

##其他
相关源码已托管于Github,有需要的朋友请自行下载使用.
{{ btn("获取源码","https://github.com/genialwang/pyblog") }}

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

##主要需求

 - 容易操作和使用
 - 博客快速生成
 - 支持markdown
 - 页面风格可定制
 - 自动SEO

##运行环境

 - python2.7
 - jinja2 == 2.8
 - pygments == 2.0.2
 - mistune == 0.7

##构建前端框架
一个简洁优雅的前端界面可以让博客看起来更加舒适,本文结合前端框架[uikit](http://getuikit.com/)和一些第
三方JQuery插件进行前端界面的构建.界面采用平面化的风格,适当地添加了平滑滚动效果以增加用户体验.
{{ alert("博主对uikit原生的配色和布局方案可能略作改动,请谨慎使用") }}

##解析Markdown
得益于Mistune的使用,pyblog可以方便地将markdown文件解析为html文件.它的基本用法如下:
```python
    renderer = TocRenderer(linenos=True, inlinestyles=False)
    mdp = mistune.Markdown(escape=True, renderer=renderer)
```

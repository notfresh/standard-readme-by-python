import os, sys

from .templite import Templite
from .question_list import query
from .md_add_space import update_space
from .md_update_url import update_url

def readme():
    os.path.abspath(__file__)
    ppath = os.path.dirname
    ppath_value = ppath(os.path.abspath(__file__))
    tmp_name = 'standard-readme-django-cn.template'
    tmp_path = os.path.join(ppath_value, tmp_name)
    context = query()
    print('@context')
    with open(tmp_path, encoding='utf-8') as f:
        tmp_content = f.read()
    tpl = Templite(tmp_content, context)
    output_path = os.path.join(os.getcwd(), 'README.md')
    ret_txt = tpl.render(output_path=output_path)
    print("README.md generated in current dir")

help_txt= """
使用 md2 -h 来获取帮助
使用 md2 readme 在当前目录生成 README 文件
使用 md2 update-url filename 来更新md文件的网页链接
使用 md2 update-space filename 来更新md文件的英文字母和汉字的空格
"""

def md():
    args = sys.argv
    if len(args)>1 and args[1] == '-h':
        print(help_txt)
    if len(args)>1 and args[1] == 'readme':
        readme()
    if len(args) >= 3 and args[1] == 'update-url':
        update_url(args[2])
    if len(args) >= 3 and args[1] == 'update-space':
        update_space(args[2])





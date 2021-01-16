import sys

g_data = {}
g_dependency = {
    'bannerPath': ['banner',True], # bannerPath 依赖 banner
    'license': ['mit',False],# license 依赖 mit,但是依赖关系相反
    'diffYear': ['currentYear',False] # license 依赖 mit,但是依赖关系相反
}

def validate_name(name):
    return len(name) > 2

def validate_maintainer(maintainer):
    return len(maintainer) > 2

def validate_confirm(value):
    return value in ('y', 'n')

def validate_length(value):
    return len(value) > 0

def filter_confirm(value):
    return value == 'y' #  if y return True, else False

questions = [
    {
        'name': 'moduleName',
        'message': '这个项目的名称什么呢(大于两个字符)?',
        'type': 'input',
        'default': '名称待定',
        'validate': validate_name
    }, {
        'name': 'banner',
        'message': '你有一个项目的banner吗?(y/n[default])',
        'type': 'confirm',
        'default': 'n'
    }, {
        'name': 'bannerPath',
        'message': 'banner的路径在哪里(可以是项目里的文件)? 例如: \'img/banner.png\'',
        'type': 'input',
        'when': g_data.get('banner', 'n')
    }, {
        'name': 'badge',
        'message': '你需要一个标准 README 项目徽章吗?(y[default]/n)',
        'type': 'confirm',
        'default': 'y'
    }, {
        'name': 'badges',
        'message': '你需要为更多其他徽章预留位置吗?(y/n[default])',
        'type': 'confirm',
        'default': 'n'
    }, {
        'name': 'longDescription',
        'message': '你是否需要预留一个详细的描述段落?(y[default]/n)',
        'type': 'confirm',
        'default': 'y'
    }, {
        'name': 'security',
        'message': '你是否需要一个优先说明的安全提示段落?(y/n[default])',
        'type': 'confirm',
        'default': 'n'
    }, {
        'name': 'background',
        'message': '你是否需要项目背景描述段落?(y[default]/n)',
        'type': 'confirm',
        'default': 'y'
    }, {
        'name': 'API',
        'message': '你是否需要一个API接口描述段落?(y/n[default])',
        'type': 'confirm',
        'default': 'n'
    }, {
        'name': 'maintainers',
        'message': '谁是主要的维护者?',
        'type': 'input',
        'validate': validate_maintainer
    },
    {
        'name': 'contributingFile',
        'message': '你有 CONTRIBUTING.md(贡献说明文档)吗?(y/n[default])',
        'type': 'confirm',
        'default': 'n'
    },
    {
        'name': 'prs',
        'message': '接受Pr吗?(y[default]/n)',
        'type': 'confirm',
        'default': 'y'
    },
    {
        'name': 'mit',
        'message': '你选择 MIT 开源许可证吗?(y[default]/n)',
        'type': 'confirm',
        'default': 'y'
    }
    , {
        'name': 'license',
        'message': '你想要什么许可证?',
        'type': 'input',
        'validate': validate_length
    },
    {
        'name': 'licensee',
        'message': '许可证的持有人是谁(也许是你的名字)?',
        'type': 'input',
        'validate': validate_length
    }, {
        'name': 'currentYear',
        'message': '许可证的持有时间是今年吗?(y[default]/n)',
        'type': 'confirm',
        'validate': 'y',
    }, {
        'name': 'diffYear',
        'message': '指定一个许可证的持有年份',
        'type': 'input'
    }
]

def depend(name):
    dependency = g_dependency.get(name,[])
    if not dependency: # 没有依赖,返回True
        return True
    if dependency[1]:
        return g_data.get(dependency[0], False)
    else:
        return not g_data.get(dependency[0], False)

def _query():
    for quest in questions:
        if quest['type'] == 'input' and depend(quest['name']) :
            while True:
                value = input(quest['message']) or quest.get('default', '')
                if quest.get('validate', False): # 是否需要检测,默认不需要检测
                    flag = quest['validate'](value)
                    if flag: break # 检测是否合法
                    else:
                        print('输入不合规范')
                else:
                    break
            g_data[quest['name']] = value # 不要放在外面,否则会用value的残值
        elif quest['type'] == 'confirm' and depend(quest['name']) :
            while True:
                value = input(quest['message']) or quest.get('default', 'y')
                flag = validate_confirm(value)
                if flag:
                    value = filter_confirm(value) # 检测是否合法
                    break
                else:
                    print('输入不合规范')
            g_data[quest['name']] = value
    return g_data

def query():
    try:
        data = _query()
        return data
    except KeyboardInterrupt as e:
        print("终止生成模板~")
        sys.exit(0)
    except Exception as e:
        print("系统异常")
        print(e)
        sys.exit(1)

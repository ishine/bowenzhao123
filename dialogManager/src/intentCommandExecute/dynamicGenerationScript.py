# -*- coding: utf-8 -*-
# @Time : 2018/07/26 14:00 
# @Author : zhoutaotao
# @File : dynamicGenerationScript.py
# @Software: dialogManagerServerDev
# @Desc:动态生成用户执行脚本类

import os
import sys
import traceback
class DynamicGenerationScript(object):
    """用户自定义执行脚本类

    支持
    Attributes:
        basePath,当前脚本所在路径
        strDefault,用户默认脚本处理函数字符串
    """
    def __init__(self):
        """类中用到的常量初始化下"""
        self.basePath = os.getcwd()+"/utils/dialogManager/src/userScript"
        self.strDefault = """\ndef handler(self,msg):\n    return msg"""

    def _processStr(self, str, script):
        """字符串处理,把用户的handler函数整合到自动产生的class里面.生产一个类的字符串,供写入到的动态产生的py文件中
        """
        arr = str.split("\n")
        ret = ''
        ret = """#!coding=utf-8\nimport os\nimport sys\n"""
        ret = ret + "class "+script+"""(object):\n    def __init__(self):\n        pass\n"""

        for item in arr:
            # print('    '+item)
            ret = ret + '\n    '+item
        return ret

    def _addInit(self, id, scriptName):
        """添加__init__.py文件包管理

        添加包管理语句,例如from .Weather import *
        先判断__init.py文件是否存在,
             1)若不存在,先创建,再导入
             2)若存在,直接导入
        判断是否已导入,防止重复导入

        Args:
            id,用户id
            scriptName,用户自定义脚本包名称(文件名和类名)

        Returns:
            无
        """
        path = os.path.join(self.basePath, id)
        if not os.path.exists(path):
            os.makedirs(path)
            os.mknod(os.path.join(path, "__init__.py"))
        filePath = os.path.join(path, "__init__.py")
        ret = """try:\n    from ."""+scriptName+""" import *\nexcept:\n    pass\n"""
        w = open(filePath, 'a+')
        w.seek(0)
        content = w.read()
        if(content.find(ret) < 0):
            w.seek(2)
            w.write(ret)
        w.close()

    def _addInitHandler(self, id, scriptName):
        """添加初始化默认用户处理脚本

        添加始化默认用户处理脚本,默认是返回原始数据,例如
        def handler(self,msg):
            return msg

        Args:
            id,用户id
            scriptName,用户自定义脚本包名称(文件名和类名)

        Returns:
            无
        """
        ret = self._processStr(self.strDefault, script=scriptName)
        path = os.path.join(self.basePath, id)
        if not os.path.exists(path):
            os.makedirs(path)
            # os.mknod(os.path.join(path, "__init__.py"))
        filePath = os.path.join(path, scriptName+".py")
        w = open(filePath, 'w')
        w.write(ret)
        w.close()

    def addDefaultHandler(self, id, scriptName):
        """添加用户默认脚本处理

        添加__init__.py包管理
        添加handler初始默认处理脚本

        Args:
            id,用户id
            scriptName,用户自定义脚本包名称(文件名和类名)
        """
        # self._addInit(id, scriptName)
        self._addInitHandler(id, scriptName)

    def addUserHandler(self,id, scriptName, userScript):
        """添加用户自定义脚本处理

        添加__init__.py包管理
        添加handler初始默认处理脚本
        @example:
        DynamicGenerationScript().addUserHandler(id='user111',
                                                    scriptName='Weather',
                                                    userScript='xxxx')
        Args:
            id,用户id
            scriptName,用户自定义脚本包名称(文件名和类名)
            userScript,用户自定义脚本内容,例如:
                def handler(self,data):
                    print(data)
                    ret = {}
                    ret['text'] = 'user handler'
                    return ret
        """
        # self._addInit(id, scriptName)
        ret = self._processStr(userScript, scriptName)
        path = os.path.join(self.basePath, id)
        if not os.path.exists(path):
            os.makedirs(path)
            # os.mknod(os.path.join(path, "__init__.py"))
        filePath = os.path.join(path, scriptName+".py")
        w = open(filePath, 'w')
        w.write(ret)
        w.close()

    def callUserHandler(self, id, scriptName,msg):
        """调用用户脚本
        @example:
        DynamicGenerationScript().callUserHandler(id='user111',
                                                    scriptName='Weather',
                                                    msg={'text':'你好'})
        Args:
            id,{string},用户id
            scriptName,{string},用户自定义脚本包名称(文件名和类名)
            msg,{json}, 语义解析返回的结果,json格式

        Returns:
            返回用户处理后的内容,json格式,例如:
            {
                'status': '400',
                'msg': {
                        'text': '用户模块调用异常,请检查用户自定义执行脚本'
                        }
            }
        """

        package = "utils.dialogManager.src.userScript."+id+"."+scriptName
        try:
            moudle = __import__(package,fromlist=True)
            # 使用getattr()获取moudle的类
            moudleClass = getattr(moudle, scriptName)
            data = moudleClass().handler(msg)
            # ret = {}
            # ret['status'] = '200'
            # ret['msg'] = data
            data['status']='200'
            ret = data
            return ret
        except:
            traceback.print_exc()
            return {'status': '400','text': '用户模块调用异常,请检查用户自定义执行脚本'}


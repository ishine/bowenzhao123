# -*- coding: utf-8 -*-
# @Time : 2018/08/02 09:50 
# @Author : zhoutaotao
# @File : xml2json.py.py
# @Software: dialogManagerServerDev
# @Desc:用户流程配置文件转换为json文件

import os
import sys
from compiler_xml import Transform

class XML2JSON(object):
    """用户流程配置文件转换为json文件
    """
    def __init__(self):
        """初始化"""
        pass

    def transfrom(self,xmlPath,jsonPath):
        """配置文件从 xml 转换为 json

        Args:
            xmlPath: xml文件目录
            jsonPath: 要保存的json文件目录

        Returns:
            无
        """
        input_lines = []
        with open(xmlPath, 'r') as f:
            input_lines = f.readlines()
        output_lines = Transform().run(input_lines)
        with open(jsonPath, 'w') as f:
            for line in output_lines:
                f.write("%s\n" % line)

if __name__ == "__main__":
    XML2JSON().transfrom(xmlPath="../../data/quota_adjust0905_3.xml",
                         jsonPath="../../data/quota_adjust0905_3.json")
# -*- coding: utf-8 -*-
# @Time : 2018/9/17 10:27 AM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : treeNode.py
# @Software: PyCharm
# @desc:

from .tree import Tree

class TreeNode(Tree):

    def __init__(self,value,height=None):
        Tree.__init__(self)
        self.val = value
        self.left = None
        self.right = None
        self.height = height
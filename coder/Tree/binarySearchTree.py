# -*- coding: utf-8 -*-
# @Time : 2018/9/17 10:26 AM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : binarySearchTree.py
# @Software: PyCharm
# @desc:

from .tree import Tree
from .treeNode import TreeNode
import sys
class binarySearchTree(Tree):

    def __init__(self):
        Tree.__init__(self)
        self.treeNode = TreeNode(0)
        self.ans = []
        self.path = []

    def insertNode(self,root,node):
        """

        :param root: the tree that is inserted by the node
        :param node: the inserted node
        :return: root
        """
        if not root:
            return

        if node.val <= root.val:
            if not root.left:
                root.left = node
                return root
            return self.insertNode(root.left,node)

        if node.val > root.val:
            if not root.right:
                root.right = node
                return root
            return self.insertNode(root.right,node)

    def createTree(self,list):
        if not list:
            return

        root = TreeNode(list[0])
        for i in range(1,len(list)):
            node = TreeNode(list[i])
            self.insertNode(root,node)

        return root

    def searchNode(self,root,value):
        if not root:
            return

        if root.val == value:
            return root

        if value < root.val:
            self.searchNode(root.left,value)

        if value > root.val:
            self.searchNode(root.right,value)

    def deleteNode(self,root,node):
        pass

    def setHeight(self,root):
        if not root:
            return 0
        return max(self.setHeight(root.left),self.setHeight(root.right)) + 1

    def getLargest(self,root):
        if not root:
            return

        if not root.right:
            return root.val

        if root.right:
            return self.getLargest(root.right)

    def getSmallest(self,root):
        if not root:
            return
        if not root.right:
            return root.val
        if root.right:
            return self.getSmallest(root.right)

    def preorderTraverse(self,root):
        if not root:
            return
        self.ans.append(root.val)
        self.preorderTraverse(root.left)
        self.preorderTraverse(root.right)

    def levelorderTraverse(self,root):
        """ 水平遍历，先进先出，因此使用队列

        :param root:
        :return:
        """
        if not root:
            return []
        ans = []
        Queen = []
        while Queen:
            temp = Queen.pop(0)
            if temp.left:
                Queen.append(temp.left)
                ans.append(temp.left.val)
            if temp.right:
                Queen.append(temp.right)
                ans.append(temp.right.val)
        return ans

    # *************************************************
    def zigzagTraverse(self,root):
        """ zigzag遍历，先从左到右，在从右到左
        从左到右:
            * 提取: 先提取左边，在提取右边(后进先出)
            * 保存: 先保存左边，再保存右边
        从右到左边:
            * 提取: 先提取右边的，再提取左边的(后进先出)
            * 保存: 先保存右边的，再保存左边的
        经过以上分析，使用两个stack
        :param root:
        :return:
        """
        if not root:
            return []
        stackOne, stackTwo, ans = [root], [], []
        while stackOne or stackTwo:
            while stackOne:
                temp = stackOne.pop()  # 提取最后一个
                if temp.left:
                    stackTwo.append(temp.left)
                    ans.append(temp.left.val)
                if temp.right:
                    stackTwo.append(temp.right)
                    ans.append(temp.right.val)
            while stackTwo:
                temp = stackTwo.pop()  # 提取最后一个
                if temp.right:
                    stackOne.append(root.right)
                    ans.append(root.right.val)
                if temp.left:
                    stackOne.append(root.left)
                    ans.append(root.left.val)
        return ans
    # **************************************************

    def mirrorTree(self,root):
        if not root:
            return
        left = root.left
        right = root.right
        root.left = right
        root.right = left
        self.mirrorTree(root.left)
        self.mirrorTree(root.right)

    def rightRotate(self,root):
        """ 将左子树向右旋转, 左子树作为根，根节点作为右子树，原左子树的右子书现作为右子树的左节点

        :param root:
        :return:
        """
        if not root or not root.left:
            return
        right = root
        rightLeft = root.left.right
        root = root.left
        root.right = right
        root.right.left = rightLeft

    def leftRotate(self,root):
        if not root or not root.right:
            return
        left = root
        leftRight = root.right.left
        root = root.right
        root.right = left
        root.left.right = leftRight

    # ***********************************************
    def flattenTree(self,root):
        """ change a binary tree to a linked list

        :param root:
        :return: root of the tree
        """
        if not root:
            return

        if not root.left and not root.right:
            return root

        temp = root.right
        root.right = None
        node = self.flattenTree(root.left)
        node.right = temp
        return self.flattenTree(temp)
    # ************************************************

    def sumRootLeaf(self,root,path):
        """
        Given a binary tree containing digits from 0-9 only, each root-to-leaf path could represent a number.

        An example is the root-to-leaf path 1->2->3 which represents the number 123.

        Find the total sum of all root-to-leaf numbers.
        Example:

        Input: [1,2,3]
          1
         / \
        2   3
        Output: 25
        Explanation:
        The root-to-leaf path 1->2 represents the number 12.
        The root-to-leaf path 1->3 represents the number 13.
        Therefore, sum = 12 + 13 = 25.

        规则: 将path转为Int
        :param root:
        :return:
        """
        if not root:
            return 0

        if not root.left and not root.right:
            return int(path)

        return self.sumRootLeaf(root.left,path+[root.val]) + self.sumRootLeaf(root.right,[root.val]+path+[root.val])

    def getMinMax(self,root):
        if not root:
            return sys.maxsize,-sys.maxsize - 1
        if not root.left and not root.right:
            return root.val, root.val
        leftMin,leftMax = self.getMinMax(root.left)
        rightMin,rightMax = self.getMinMax(root.right)
        return min(leftMax,root.val),max(rightMin,root.val)
    # *********************************************************

    def validateBST(self,root,minimum,maximum):
        """
        Example 1:

        Input:
           2
          / \
         1   3
        Output: true
        Example 2:

           5
          / \
         1   4
            / \
           3   6
        Output: false
        Explanation: The input is: [5,1,4,null,null,3,6]. The root node's value is 5 but its right child's value is 4.

        Rule:
             从上向下比较
                 左子树比root小，比min大
                 右子树比root大，比max小
             * root.left is None or (root.left is validate BST & root.val > maximum(root.left))
             * root.right is None or (root.right is validate BST & root.val <= minimum(root.rigth))
        Args:
            root:
            minimum: minimum of tree
            maximum: maximum of tree
        :return:
        """

        if not root:
            return True

        if not root.left and not root.right:
            return True
        if root.val > maximum or root.val < minimum:
            return False
        return self.validateBST(root.left,minimum,root.val) and self.validateBST(root.right,root.val,maximum)
    # *********************************************************


    def sumPath(self,root,target,path):
        """
        Given a binary tree and a sum, find all root-to-leaf paths where each path's sum equals the given sum.

        Example:

        Given the below binary tree and sum = 22,
              5
             / \
            4   8
           /   / \
          11  13  4
         /  \    / \
        7    2  5   1
        [
            [5,4,11,2],
           [5,8,4,5]
        ]
        Rule:
            * Judge if the role is equal to the target, if equal, add/not add
            * if not equal, the go on to the left&right, add&not add
        Args:
            root:
            target:
            path:
        :return:
        """
        if not root:
            return
        if root.val == target:
            self.ans.append(path+[root.val])

        self.sumPath(root.left,target,path)
        self.sumPath(root.left,target-root.val,path+[root.val])
        self.sumPath(root.right, target, path)
        self.sumPath(root.right, target - root.val, path + [root.val])


    # *****************************************************
    def uniqueBST(self,left,right,path,num):
        """
        Given n, how many structurally unique BST's (binary search trees) that store values 1 ... n?

        Example:
        Input: 3
        Output:
        [
         [1,null,3,2],
         [3,2,null,1],
         [3,1,null,null,2],
          [2,1,3],
         [1,null,2,null,3]
        ]
        Explanation:
        The above output corresponds to the 5 unique BST's shown below:


         1         3     3      2      1
         \       /     /      / \      \
         3     2      1      1   3     2
         /     /       \                \
        2     1         2               3

        选定一个点作为根，依次产生可行的子树，然后加入到最后的解里面
        The way to solve this problem is to find a root in the given number then construct valid left and right subtrees
        then append it to the solution. valid condition is left<mid<right
        :return:
        """

        """
        if start > end:
            return [None]
        solution = []
        for rootval in range(start, end + 1):
            left = self.uniqueBST(start, rootval - 1)
            right = self.uniqueBST(rootval + 1, end)
            for i in left:
                for j in right:
                    root = TreeNode(rootval)
                    root.left = i
                    root.right = j
                    solution.append(root)
        return solution
        """
        if left < right:
            return

        if len(path) == num:
            self.ans.append(path)

        for i in range(left,right+1):
            node = TreeNode(i)
            self.uniqueBST(left,i-1,path+[node],num)
            self.uniqueBST(i+1,right,path+[node],num)
    # ******************************************************
# -*- coding: utf-8 -*-
# @Time : 2018/9/17 11:23 AM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : string.py
# @Software: PyCharm
# @desc:

class String(object):

    def __init__(self):
        self.ans = []
        self.maxlength = 0
        pass

    def findLCsubSequenceLength(self,s,t):
        """  使用

        :return:
        """
        """
        if not s or not t:
            return 0
        if s[-1] == t[-1]:
            return self.findLCsequenceLength(s.pop(),t.pop()) + 1
        if s[-1] != t[-1]:
            return max(self.findLCsequenceLength(s.pop(),t),self.findLCsequencelength(s,t.pop()))
             
        """
        memo = [[0]*len(s+1)]*len(t+1)
        if not s or not t:
            return 0
        for i in range(1,len(s)+1):
            for j in range(len(t)+1):
                if s[i] == t[j]:
                    memo[i][j] = memo[i-1][j-1] + 1
                else:
                    memo[i][j] = max(memo[i][j-1],memo[i-1][j])
        return memo[-1][-1]

    def findAllLCsubSequence(self,s,t,i,j,path,memo):
        """ 这里不能使用self.ans,因为dp会重复调用

        :param s:
        :param t:
        :return:
        """
        """
        if i==0 or j==0:
            return pathList

        if s[i] == t[j]:
            pathList = [path+[s[i]] for path in pathList]
            return self.findAllLCsubSequence(s,t,i-1,j-1,pathList,memo)

        if memo[i-1][j] < memo[i][j-1]:
            return self.findAllLCsubSequence(s,t,i,j-1,pathList,memo)
        if memo[i-1][j] > memo[i][j-1]:
            return self.findAllLCsubSequence(s,t,i-1,j,pathList,memo)
        if memo[i-1][j] == memo[i][j-1]:
            return self.findAllLCsubSequence(s,t,i,j-1,pathList,memo).extend(self.findAllLCsubSequence(s,t,i-1,j,pathList,memo))
        """
        if i == 0 or j == 0:
            self.ans.append(path)
        if s[i] == t[j]:
            self.findAllLCsubSequence(s,t,i-1,j-1,path+[s[i]],memo)
        if memo[i-1][j] < memo[i][j-1]:
            self.findAllLCsubSequence(s,t,i,j-1,path,memo)
        if memo[i-1][j] > memo[i][j-1]:
            self.findAllLCsubSequence(s,t,i-1,j,path,memo)
        if memo[i-1][j] == memo[i][j-1]
            self.findAllLCsubSequence(s,t,i-1,j,path,memo)
            self.findAllLCsubSequence(s,t,i,j-1,path,memo)



    def findLCsubString(self,s,t):
        """
        如果使用递归是否重复调用self.ans.append()？
        :return:
        """
        """
        if not s or not t:
            self.max = max(self.max,maxLength)
            
        if s[-1] == t[-1]:
            self.findAllLCstring(s.pop(),t.pop(),maxLength+1)
            
        if s[-1] != t[-1]:
            self.findAllLCstring(s.pop(),t,0)
            self.findAllLCstring(s,t.pop(),0)
        """
        maxLength = 0
        memo = [[0]*len(s)]*len(t)
        for i in range(1,len(s)+1):
            for j in range(1,len(t)+1):
                if s[i] == t[j]:
                    memo[i][j] = memo[i-1][j-1] + 1
                    maxLength = max(maxLength,memo[i][j])
        return maxLength

    def findLRepeatedsubSequence(self,s,i,j):
        """ 对于一个给定的字符串，找到最长的有重复的子串
        可以转化为两个相同的串，找到LCS
        :param s:
        :return:
        """
        if i == 0 or j == 0:
            return 0
        if s[i] == s[j] and i != j:
            return self.findLRepeatedsubSequence(s,i-1,j-1) + 2
        return max(self.findLRepeatedsubSequence(s,i-1,j),self.findLRepeatedsubSequence(s,i,j-1))

    def findSCsuperSequence(self,s,t,i,j):
        if i == 0 or j == 0:
            return 0
        if s[i] != t[j]:
            return self.findSCsuperSequence(s,t,i-1,j-1) + 1
        return min(self.findSCsuperSequence(s,t,i-1,j),self.findSCsuperSequence(s,t,i,j-1)) + 1

    def countNumofPattern(self,s,t,i,j):
        """

        :param s:
        :param t:
        :param i:
        :param j:
        :return:
        """
        if i == 0:
            return 0
        if j == 0:
            return 1
        if s[i] == t[j]:
            return self.countNumofPattern(s,t,i-1,j-1) + self.countNumofPattern(s,t,i-1,j)
        return self.countNumofPattern(s,t,i-1,j)

    def validateParent(self,s,t,i):
        """

        :param s:
        :param t:
        :param i:
        :return:
        """
        if i == 0:
            return not t
        if s[i] == "(":
            self.validateParent(s,t.append('('),i-1)
        if s[i] == ")":
            if not t:
                return False
            return self.validateParent(s,t.pop(),i-1)
        if s[i] == "*":
            return self.validateParent(s,t,i-1) or self.validateParent(s,t.append('('),i-1) or self.validateParent(s,t.pop(),i-1)

    def breakWord(self,s,dic):
        """

        :param s:
        :param dic:
        :return:
        """
        def dp(i,j):
            if j == len(s)-1:
                return s[i:j] in dic

            if s[i:j+1] in dic:
                return dp(j+1,j+1) or dp(i,j+1)

            if s[i:j+1] not in dic:
                return dp(i,j+1)

# ********************************************
    def wildCardMatching(self,s,t):
        """

        :param s: origin
        :param t: regular expression
        :return:
        """
        def dp(i,j):
            """

            :param i: position of s
            :param j: position of t
            :return:
            """
            if i == 0 and j == 0:
                return True

            if j == 0:
                return False

            if i == 0:
                for k in range(j,-1,-1):
                    if k !=  "*":
                        return False
                return True

            if t[j] == "*":
                return dp(i,j+1) or dp(i+1,j)  # 使用至少一次，使用0次

            if t[j] != '?' and s[i] != t[j]:
                return False

            return dp(i+1,j+1)

# **********************************************
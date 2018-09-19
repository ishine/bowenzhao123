# -*- coding: utf-8 -*-
# @Time : 2018/9/17 11:23 AM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : list.py
# @Software: PyCharm
# @desc:

class List(object):
    def __init__(self):
        self.ans = []
        self.maxLength = 0

    def findLIsubSequence(self, s, i, j):
        """ 如果大于prev
            * 替代前一个最大的
            * 不选择
            如果小于prev
            * 选择
            * 不选择

        :param s: Array
        :param i: the index of last sequence
        :param j:
        :return:
        """
        if i < 0:
            return 0
        if s[i] > s[j]:
            return max(self.findLIsubSequence(s, i - 1, j), self.findLIsubSequence(s, i - 1, s[i]))
        return max(self.findLIsubSequence(s, i - 1, s[i]) + 1, self.findLIsubSequence(s, i - 1, j))

    def findLBitsubSequence(self, s, i):
        """

        :param s: Array
        :param i: pivot element
        :return:
        """
        s_1 = s[:i + 1]
        s_2 = -s[i:]
        return self.findLIsubSequence(s_1, len(s_1) - 1, s_1[-1]), self.findLIsubSequence(s_2, len(s_2) - 1,
                                                                                          s_2[-1]) - 1

    def maxSumIsubSequence(self, s, i, prev):
        """ increasing subsequence with maximum num

        :param s:
        :return:
        """
        if i < 0:
            return 0
        if s[i] > prev:
            return max(self.maxSumIsubSequence(s, i - 1, s[i]) + s[i] - prev, self.maxSumIsubSequence(s, i - 1, prev))
        return max(self.maxSumIsubSequence(s, i - 1, s[i]) + s[i], self.maxSumIsubSequence(s, i - 1, prev))

    def partitionInter(self,s,i,s1,s2,target):
        """

        :param s:
        :param i:
        :param s1:
        :param s2:
        :param target:
        :return:
        """
        if i == 0:
            return sum(s1) == sum(s2) == target
        return self.partitionInter(s,i-1,s1+[s[i]],s2,target) or self.partitionInter(s,i-1,s1,s2+[s[i]],target)


    def minsubSetSum(self,s,i,s1,s2):
        if i == 0:
            return abs(s1-s2)
        return min(self.minsubSetSum(s,i-1,s1+[s[i]],s2),self.minsubSetSum(s,i-1,s1,s2+[s[i]]))

    def permutation(self,s,path,memo):
        """
        Given a collection of distinct integers, return all possible permutations.

        Example:

        Input: [1,2,3]

        Output:
        [
         [1,2,3],
         [1,3,2],
         [2,1,3],
         [2,3,1],
         [3,1,2],
         [3,2,1]
         ]

        :param s:
        :return:
        """
        if len(path) == len(s):
            self.ans.append(path)
        for i in range(len(s)):
            if not memo[i]:
                memo[i] = True
                self.permutation(s,path+[s[i]])
                memo[i] = False
        """
        if len(path) == len(s):
            self.ans.append(path)
        for i in range(len(s)):
            if not memo[i]:
                if i not in path:
                self.permutation(s,path+[s[i]])
        """

    def combinationSum(self,num):
        """
        Given a set of candidate numbers (candidates) (without duplicates) and a target number (target),
        find all unique combinations in candidates where the candidate numbers sums to target.

        The same repeated number may be chosen from candidates unlimited number of times.

        Note:

        All numbers (including target) will be positive integers.
        The solution set must not contain duplicate combinations.
        Example 1:

        Input: candidates = [2,3,6,7], target = 7,
        A solution set is:
        [
          [7],
          [2,2,3]
        ]
        Example 2:

        Input: candidates = [2,3,5], target = 8,
        A solution set is:
        [
          [2,2,2,2],
          [2,3,3],
         [3,5]
        ]
        :return:
        """

        ans = []
        s = sorted(s)

        def dfs(path, i):

            if i == len(s) or sum(path) > num:
                return

            if sum(path) == num:
                ans.append(path)
                return

            dfs(path + [s[i]], i)
            dfs(path, i + 1)

        dfs([], 0)
        return ans


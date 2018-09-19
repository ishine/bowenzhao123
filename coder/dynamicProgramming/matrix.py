# -*- coding: utf-8 -*-
# @Time : 2018/9/18 6:42 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : matrix.py
# @Software: PyCharm
# @desc:


class Matrix(object):
    """

    """
    def __init__(self):
        self.ans = []
        self.max = 0
        self.min = 0

    def _dp(self,i,j):
        pass

    def _dp(self,i,j,matrixdimList):

        if j <= i+1:
            return 0
        return max([self._dp(i,k)+self._dp(k,j)+matrixdimList[i]*matrixdimList[k]*matrixdimList[j] for k in range(i+1,j)])

    def _dp(self,i,j,matrix):

        if i < 0 or j < 0:
            return 0
        return max(self._dp(i-1,j),self._dp(i,j-1)) + matrix[i][j]


    def multiplyChain(self,matrixdimList):
        if not matrixdimList:
            return 0
        return self._dp(0,len(matrixdimList)-1,matrixdimList)

    def minPathSum(self,matrix):
        if not matrix:
            return 0
        return self._dp(matrix.shape[0],matrix.shape[1],matrix)

    def allPathGivenSum(self,matrix,num,i,j):
        if i < 0 or j < 0:
            return 0

        if i == 0 or j == 0:
            return num == 0

        return self.allPathGivenSum(matrix,num-matrix[i-1][j],i-1,j) or self.allPathGivenSum(matrix,num-matrix[i][j-1],i,j-1)

# **********************************************************
    def findLongestSequence(self,matrix):
        """

        :param matrix:
        :return:
        """
        def dp(i,j):
            if i< 0 or j< 0 or i >= matrix.shape[0] or j >= matrix.shape[1]:
                return 0
            m = dp(i,j-1) if (j>=1 and matrix[i][j-1]-matrix[i][j]==1) else 0
            n = dp(i-1,j) if (i>=1 and matrix[i-1][j]-matrix[i][j]==1) else 0
            p = dp(i,j+1) if (j+1 < matrix.shape[0] and matrix[i][j+1]-matrix[i][j]==1) else 0
            q = dp(i+1,j) if (i+1 < matrix.shape[1] and matrix[i+1][j]-matrix[i][j]==1) else 0
            return max(m,n,p,q) + 1
        return max(dp(i,j) for i in range(matrix.shape[0]) for j in range(matrix.shape[1]))
# ***********************************************************

    def maxSumsubMatrix(self,matrix,k):
        """

        :param matrix:
        :return:
        """
        memo = [[0]*matrix.shape[0]]*matrix.shape[1]
        memo[0][0] = matrix[0][0]
        for i in range(1,matrix.shape[0]):
            for j in range(1,matrix.shape[1]):
                memo[i][j] = memo[i-1][j] + memo[i][j-1] + matrix[i][j] - memo[i-1][j-1]
        def dp(i,j):
            if i < k or j < k:
                return 0
            return max(dp(i-1,j),dp(i,j-1),memo[i][j]-memo[i-k][j-k])

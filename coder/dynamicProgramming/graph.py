# -*- coding: utf-8 -*-
# @Time : 2018/9/19 11:28 AM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : graph.py
# @Software: PyCharm
# @desc:


class Graph(object):
    """
        Attributes:
            graph: graph in python is used by two-dimension list
            Example:
             a,b,c,d,e,f,g,h=range(8)
             N=[[b,c,d,e,f],#a
                [c,e],#b
                [d],#c
                [e],#d
                [f],#e
               [c,g,h],#f
               [f,h],#g
               [f,g]#h
               ]
    """

    def __init__(self,graph):
        self.graph = graph
        self.path = []


    def findShortestPathLength(self,start,end):
        """  从start到end最短路径
        从start出发，遍历临近的矩阵，对每一个k进行访问(并标记为已访问)，判断是否有end
        * 有end -> 和最小的比较
        * 没有end -> 以k为起点，查找end

        :param graph:
        :param start:
        :param end:
        :return:
        """
        visited = [False]*len(self.graph)
        def dp(start,end):
            if visited == [True]*len(self.graph):
                return [False]*len(self.graph) + 1
            shortest = len(self.graph)
            for i in self.graph[start]:
                if visited[i]:
                    continue
                if i == end:
                    return 1
                else:
                    visited[i] = True  #  如何将其再转化为False
                    shortest = min(dp(i,end)+1,shortest)
                    visited[i] = False
            return shortest
        visited[start] = True
        shortest = dp(start,end) + 1
        return shortest if shortest <= len(self.graph) else None

    def findAllPath(self,start,end):
        visited = [False]*len(self.graph)
        def dp(start,end,path):
            if len(path) == len(self.graph):
                return
            for i in self.graph[start]:
                if visited[i]:
                    continue
                if i == end:
                    self.path.append(path+[i])
                else:
                    visited[i] = True
                    dp(i,end,path+[i])
                    visited[i] = False

        visited[start] = True
        dp(start,end,[start])
        return self.path

    def shortestPathVisitingAllNode(self):
        pass

# **************************************************
    def findCycle(self):
        visited = [False] * len(self.graph)

        def dp(start,prev):
            if visited == [True]*len(self.graph):
                return True
            for i in self.graph[start]:
                if not visited[i]:
                     if not dp(i,start):
                         return False
                else:
                    if prev == i:
                        return False
            return True

        for i in range(len(self.graph)):
            visited[i] = True
            if not dp(i,-1):
                return False
            visited[i] = False
        return True
# **************************************************
if __name__ == '__main__':
    graph = Graph([[1],[0,2,4],[1,3,4],[2],[1,2]])
    length = graph.findShortestPathLength(1,3)
    print(length)
    pathList = graph.findAllPath(1,3)
    print(pathList)
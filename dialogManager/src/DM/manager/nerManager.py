#!coding=utf-8

from ....src.NER.namedEntityRecog import NamedEntityRecog
class NERManager(object):
    def __init__(self):
        self.namedEntityRecogObj = NamedEntityRecog()

    def getNamedEntityRecog(self, userQuery, slotInfo, id):

        """根据用户输入文本获取命名实体识别结果

        Args:
            userQuery,用户输入文本
            id, 用户id

        Returns:
            {
                "LOCATION":
                         [
                             {
                                 "NERValue":"上海"，
                                  "preContext":["从"],
                                  "surContext":["到"]
                             }
                         ]
            }
        """

        return self.namedEntityRecogObj.getNER(userQuery, slotInfo, id)

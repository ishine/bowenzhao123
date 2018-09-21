#!coding=utf-8
from ...src.NER import NER
from ...src.NER import contextDetector
from ...src.DM.manager import sceneInfoManager
from ...src.NER import namedEntityNormalization

import traceback
import logging

class NamedEntityRecog(object):

    def __init__(self):

        #加载BiLSTM_CRF模型
        self.myNERProcess = NER.NERProcessor()
        self.contextDetector = contextDetector.ContextDetector()
        self.NENormorlizer = namedEntityNormalization.NamedEntityNormalization()


    def getNER(self,userQuery,slotInfo,id):

        """ 根据用户输入文本获取命名实体识别结果

        Args:
            userQuery,用户输入的文本
            slotInfo,
            id,

        Returns:
           {
                "LOCATION":
                         [
                             {
                                 "NERValue":"上海"，
                                  "preContext":["从"],
                                  "sufContext":["到"]
                             }
                         ]
            }


        """
        try:
            res = {}
            #1. 先用规则进行命名实体识别
            entitiesByRules = self.myNERProcess.NERByRules(userQuery,id)
            print('entitiesByRules')
            print(entitiesByRules)

            # 2. 再用用户自定义字典进行命名实体识别
            entitiesByDict = self.myNERProcess.NERByDic(userQuery, id)
            print('entitiesByDict')
            print(entitiesByDict)

            #3. 合并字典和规则的识别结果
            entities = self.myNERProcess.mergeNamedEntities(userQuery,entitiesByDict,entitiesByRules)

            #4. 用模型进行命名实体识别
            entitiesByModel = self.myNERProcess.NERByModel(userQuery)
            print('模型结果:')
            print(entitiesByModel)

            #5. 转化命名实体识别结果,把模型识别的类型转换成用户/系统组合的实体类型
            entitiesByModel = self.myNERProcess.mapEntities(entitiesByModel, slotInfo, id)

            #6. 合并命名实体识别结果,把模型结果和之前的结果进行合并,去冲突
            entities = self.myNERProcess.mergeNamedEntities(userQuery, entitiesByModel, entities)
            print("合并命名实体识别结果:")
            print(entities)

            print('转化结果')
            print(entities)

            #7. 找出命名实体的上下文信息
            res = self.contextDetector.detectContext(userQuery, entities, slotInfo)
            #print(res)

            #7. 命名实体规范化
            res = self.NENormorlizer.norEntities(res)
            # print(res)
            return res
        except:
            traceback.print_exc()
            logging.info(traceback.format_exc())



'''
if __name__ == '__main__':
    myObject = NamedEntityRecog()
    mySlotManager = slotManager.SlotManager()
    slotInfo = mySlotManager.slotInfoExtract('天气')


    print('slotInfo.intent: ', slotInfo.intent)
    print('slotInfo.sceneInfo: ', slotInfo.sceneInfo)
    print('slotInfo.intentCommandExecute: ',slotInfo.intentCommandExecute)


    myObject.getNER('今天下午天气',slotInfo)
'''



class ContextDetector():
    def __init__(self):
        pass

    def getWindowSize(self, slotInfo):

        '''
        找出slotInfo中槽的前缀后缀最大长度
        :param slotInfo:
        :return:{"LOCATION":{'preContextLen':xxx, 'sufContextLen':xxx},}
        '''

        windowSizeInfo = {}
        #print(slotInfo.sceneInfo)

        for _slot in slotInfo.slot:

            #print('slotInfo.sceneInfo\n')
            #print(_slot)

            receiveNE = _slot['receiveEntityType']

            if receiveNE not in windowSizeInfo:
                windowSizeInfo[receiveNE] = {'preContextLen':0,'sufContextLen':0}

            _preContext = _slot['context']['preContext']
            for _tmp in _preContext:
                _preContextLen = len(_tmp)
                if _preContextLen > windowSizeInfo[receiveNE]['preContextLen']:
                    windowSizeInfo[receiveNE]['preContextLen'] = _preContextLen

            _sufContext = _slot['context']['sufContext']
            for _tmp in _sufContext:
                _sufContextLen = len(_tmp)
                if _sufContextLen > windowSizeInfo[receiveNE]['sufContextLen']:
                    windowSizeInfo[receiveNE]['sufContextLen'] = _sufContextLen

        #print(windowSizeInfo)
        return windowSizeInfo



    def detectContext(self, sent, entities, slotInfo):
        '''
        找出命名实体的上下文信息，也就是命名实体左右窗口的词
        命名实体前window_size个字作为prefix，和后window_size个字作为suffix

        {
        'entityName': {EntityValue:'xxx', 'preContext':[],'sufContext':[]}, ...,

        }

        示例： {'LOCATION':[{'entityValue':'北京','preContext':'[要]','sufContext':[]},{'entityName':'上海','preContext':[从],'sufContext':[]},..],}
        :return:
        '''

        res = {}
        windowSizeInfo = self.getWindowSize(slotInfo)

        for name in entities:

            if name not in windowSizeInfo:
                continue

            res[name] = []

            for i in range(len(entities[name])):
                _entityRes = {'NERValue': None, 'preContext': None, 'sufContext': None}

                NE = entities[name][i][0]
                _entityRes['NERValue'] = NE
                start_index = entities[name][i][1]
                end_index = entities[name][i][2]
                prefix = self.getWindowContent(sent, start_index, 'preContext',windowSizeInfo[name]['preContextLen'])
                _entityRes['preContext'] = ''.join(prefix)
                suffix = self.getWindowContent(sent, end_index, 'sufContext',windowSizeInfo[name]['sufContextLen'])
                _entityRes['sufContext'] = ''.join(suffix)

                res[name].append(_entityRes)

        return res

    def getWindowContent(self,sent, position, direction,window_size):

        sent_len = len(sent)

        res = []

        if direction == 'preContext':
            for i in range(position-window_size, position):
                if i < 0:
                    continue
                res.append(sent[i])
        elif direction == 'sufContext':
            for i in range(position+1, window_size+position+1):
                if i >= sent_len:
                    continue
                res.append(sent[i])

        return res

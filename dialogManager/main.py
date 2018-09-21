#!coding=utf-8
from src.DM.dialogManager import DialogManager

if __name__ == "__main__":
    DialogManagerObj = DialogManager()
    while(True):
        print('Please input your sentence:')
        sent = input()
        if sent == '' or sent.isspace():
            print('See you next time!')
            break
        else:
            result = DialogManagerObj.getDialogAnswer(sent)

            if(result['status'] == '200'):
                msg = result['msg']
                print(msg)
            else:
                print(result['msg'])



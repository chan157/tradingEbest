import win32com.client as wc
import pythoncom as pcom
import time


class XASessionCallbackEvent:
    login_success = False # 로그인 성공여부 체크

    def OnLogin(self, szCode, szMsg):
        print("로그인 결과 수신 %s, %s" % (szCode, szMsg))
        XASessionCallbackEvent.login_success = True


class XAQueryCallbackEvent:
    tr_success = False
    shcode_list = []

    def OnReceiveData(self, code):
        print(code)

        if code == "t9945":
            occurs_count = self.GetBlockCount("t99450utBlock")
            for i in range(occurs_count):
                shcode = self.GetFieldData("t99450utBlock", "shcode", i)
                XAQueryCallbackEvent.shcode_list.append(shcode)
            
            XAQueryCallbackEvent.tr_success = True 


class Main():
    def __init__(self):
        print("실행합니다.")

        # XASessioin 객체 생성 #
        self.XASession = wc.DispatchWithEvents("XA_Session.XASession", XASessionCallbackEvent)
        print(self.XASession)

        # 서버 연결 실패시 False, 모의서버:demo, 실서버:hts
        if self.XASession.ConnectServer("demo.ebestsec.co.kr", 20001) == True:
            print("서버 연결 완료")
        else:
            nErrCode = self.XASession.GetLastError()
            strErrMsg =self.XASession.GetErrorMessage(nErrCode)
            print(strErrMsg)

        ################################ 로그인 하기 #################################
        if self.XASession.Login("chan157", "chan4916", "", 0, False) == True:
            print("로그인 요청 성공")
        
        while XASessionCallbackEvent.login_success == False:
            # https://mail.python.org/pipermail/python-win32/2007-June/005963.html
            # 내용 참고하면 공부하기 좋다고 함

            # 루프를 돌면서 메세지가 들어왔는지 체크함
            # 루프르 돌리는 동안 다른 코드를 실행시키는 것은 비효율 적
            pcom.PumpWaitingMessages()
            time.sleep(0.1)
        
        # 코스닥 종목 조회하기 
        self.event = wc.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryCallbackEvent)
        self.event.ResFileName = "C:/eBEST/xingAPI/Res/t9945.res"
        self.event.SetFieldData("t9945InBlock", "gubun", 0, "2")
        self.event.Request(False)

        while XAQueryCallbackEvent.tr_success == False:
            pcom.PumpWaitingMessages()
            time.sleep(0.1)

if __name__ == "__main__":
    Main()
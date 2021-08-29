from login_data import *

import win32com.client as wc
import pythoncom as pcom
import time


class XASessionCallbackEvent:
    login_success = False # 로그인 성공여부 체크

    def OnLogin(self, szCode, szMsg):
        print("로그인 결과 수신 %s, %s" % (szCode, szMsg))
        XASessionCallbackEvent.login_success = True


class EventClass_t9945: # XAQueryCallbackEvent
    tr_success = False # tr요청 성공여부
    shcode_list = []
    t_9945_e = None

    def OnReceiveData(self, code):
        print("입력된 코드 : ", code)

        if code == "t9945":
            occurs_count = self.GetBlockCount("t9945OutBlock")
            print(occurs_count)
            for i in range(occurs_count):
                shcode = self.GetFieldData("t9945OutBlock", "shcode", i)
                EventClass_t9945.shcode_list.append(shcode)
            
            EventClass_t9945.tr_success = True 
        

class EventClass_t8413:
    tr_success = False # tr요청 성공여부
    t_8413_e = None 
    date_list = []
    rate_list = []
    close_list = []

    def OnReceiveData(self, code):
        print("입력된 코드 : ", code)

        if code == "t8413": # 일주월 봉 데이터 조회
            print("가격 봉 데이터 조회")

            shcode = self.GetFieldData("t8413OutBlock", "shcode", 0)
            cts_date = self.GetFieldData("t8413OutBlock", "cts_date", 0)
            occurs_count = self.GetBlockCount("t8413OutBlock1")

            for i in reversed(range(occurs_count)): # 역순으로 넣음
                date = self.GetFieldData("t8413OutBlock1", "date", i) 
                close = self.GetFieldData("t8413OutBlock1", "close", i) 
                close = int(close)
                rate = self.GetFieldData("t8413OutBlock1", "rate", i) # 수정주가 비율
                rate = float(rate)

                if len(EventClass_t8413.rate_list) > 0:
                    for rat in EventClass_t8413.rate_list:
                        # 수정주가 비율 계산
                        close = round(close * (1 + rat/100) )
                
                # 수정주가 반영된 가격을 리스트에 담음
                EventClass_t8413.date_list.append(rate)
                EventClass_t8413.close_list.append(close)

                if rate != 0.0:
                    EventClass_t8413.rate_list.append(rate)

            print(cts_date)
            if self.IsNext is True:
                Main.t8413_request(shcode=shcode, gubun='2', qrycnt=500, sdate="", edate="99999999", 
                                cts_date =cts_date, comp_yn="N", occurs=self.IsNext)
            else:
                EventClass_t8413.tr_success = True


class EventClass_t8412:
    tr_success = False
    t_8412_e = None
    date_list = []
    time_list = []
    close_list = []


    def OnReceiveData(self, code):
        print("입력된 코드 : ", code)

        if code == "t8412":
            print("분 봉 데이터 조회")

            shcode = self.GetFieldData("t8412OutBlock", "shcode", 0)
            cts_date = self.GetFieldData("t8412OutBlock", "cts_date", 0)
            cts_time = self.GetFieldData("t8412OutBlock", "cts_time", 0)
            occurs_count = self.GetBlockCount("t8412outBlock1")

            for i in reversed(range(occurs_count)): # 역순으로 넣음
                date = self.GetFieldData("t8412OutBlock1", "date", i) 
                time = self.GetFieldData("t8412OutBlock1", "time", i)
                close = self.GetFieldData("t8412OutBlock1", "close", i) 
                close = int(close)

                EventClass_t8412.close_list.append(close)
                EventClass_t8412.date_list.append(date)
                EventClass_t8412.time_list.append(time)


            if self.IsNext is True:
                Main.t8412_request(shcode=shcode, ncnt='1', qrycnt=500, nday='0',
                            sdate="", stime="", edate="99999999", etime="", 
                            cts_date="", cts_time="", comp_yn="N", occurs=self.IsNext)
            else:
                EventClass_t8412.tr_success = True




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
        if self.XASession.Login(id, pw, "", 0, False) == True:
            print("로그인 요청 성공")
        
        while XASessionCallbackEvent.login_success == False:
            # https://mail.python.org/pipermail/python-win32/2007-June/005963.html
            # 내용 참고하면 공부하기 좋다고 함

            # 루프를 돌면서 메세지가 들어왔는지 체크함
            # 루프르 돌리는 동안 다른 코드를 실행시키는 것은 비효율 적
            pcom.PumpWaitingMessages()
            time.sleep(0.1)
        
        # 코스닥 종목 조회하기 
        print("코스닥 종목 조회 시작")
        EventClass_t9945.t9945_e = wc.DispatchWithEvents("XA_DataSet.XAQuery", EventClass_t9945)
        EventClass_t9945.t9945_e.ResFileName = "C:/eBEST/xingAPI/Res/t9945.res"
        EventClass_t9945.t9945_e.SetFieldData("t9945InBlock", "gubun", 0, "2")
        EventClass_t9945.t9945_e.Request(False)

        while EventClass_t9945.tr_success == False:
            pcom.PumpWaitingMessages()
            time.sleep(0.1)
        print("코스닥 종목 조회 완료")


        # # 일주월 봉 데이터 조회
        # print("일봉 데이터 조회 시작")
        # EventClass_t8413.t8413_e = wc.DispatchWithEvents("XA_DataSet.XAQuery", EventClass_t8413)
        # EventClass_t8413.t8413_e.ResFileName = "C:/eBEST/xingAPI/Res/t8413.res"
        # for shcode in EventClass_t9945.shcode_list:
        #     Main.t8413_request(shcode=shcode, gubun='2', qrycnt=500, 
        #                     sdate="", edate="99999999", cts_date="",
        #                     comp_yn="N", occurs=False)

        # 분 봉 데이터 조회
        print("분 봉 데이터 조회 시작")
        EventClass_t8412.t8412_e = wc.DispatchWithEvents("XA_DataSet.XAQuery", EventClass_t8412)
        EventClass_t8412.t8412_e.ResFileName = "C:/eBEST/xingAPI/Res/t8412.res"
        for shcode in EventClass_t9945.shcode_list:
            print("종목 코드 : ", shcode)
            Main.t8412_request(shcode=shcode, ncnt='1', qrycnt=500, nday='0',
                            sdate="", stime="", edate="99999999", etime="", 
                            cts_date="", cts_time="", comp_yn="N", occurs=False)
            print("<< 결과 출력 >>")
            for t, p in zip(EventClass_t8412.time_list, EventClass_t8412.close_list):
                print(f"{t} : {p}")

        print("분 봉 데이터 조회 종료")



    @staticmethod
    def t8413_request(shcode=None, gubun=None, qrycnt=None,
                    sdate=None, edate=None, cts_date=None, comp_yn=None, occurs=False):
        time.sleep(3.1)
        EventClass_t8413.t8413_e.SetFieldData("t8413InBlock", "shcode", 0, shcode)
        EventClass_t8413.t8413_e.SetFieldData("t8413InBlock", "gubun", 0, gubun)
        EventClass_t8413.t8413_e.SetFieldData("t8413InBlock", "qrycnt", 0, qrycnt)
        EventClass_t8413.t8413_e.SetFieldData("t8413InBlock", "sdate", 0, sdate)
        EventClass_t8413.t8413_e.SetFieldData("t8413InBlock", "edate", 0, edate)
        EventClass_t8413.t8413_e.SetFieldData("t8413InBlock", "cts_date", 0, cts_date)
        EventClass_t8413.t8413_e.SetFieldData("t8413InBlock", "comp_yn", 0, comp_yn)

        EventClass_t8413.t8413_e.Request(occurs)
        EventClass_t8413.tr_success = False # False 초기화
        while EventClass_t8413.tr_success == False:
            pcom.PumpWaitingMessages()

        print("일봉 데이터 조회 종료")

    @staticmethod
    def t8412_request(shcode=None, ncnt=None, qrycnt=None, nday=None,
                    sdate=None, stime=None, edate=None, etime=None, 
                    cts_date=None, cts_time=None, comp_yn=None, occurs=False):
        time.sleep(3.1)
        EventClass_t8412.t8412_e.SetFieldData("t8412InBlock", "shcode", 0, shcode)
        EventClass_t8412.t8412_e.SetFieldData("t8412InBlock", "ncnt", 0, ncnt)
        EventClass_t8412.t8412_e.SetFieldData("t8412InBlock", "qrycnt", 0, qrycnt)
        EventClass_t8412.t8412_e.SetFieldData("t8412InBlock", "nday", 0, nday)
        EventClass_t8412.t8412_e.SetFieldData("t8412InBlock", "sdate", 0, sdate)
        EventClass_t8412.t8412_e.SetFieldData("t8412InBlock", "stime", 0, stime)
        EventClass_t8412.t8412_e.SetFieldData("t8412InBlock", "edate", 0, edate)
        EventClass_t8412.t8412_e.SetFieldData("t8412InBlock", "etime", 0, etime)
        EventClass_t8412.t8412_e.SetFieldData("t8412InBlock", "cts_date", 0, cts_date)
        EventClass_t8412.t8412_e.SetFieldData("t8412InBlock", "cts_time", 0, cts_time)
        EventClass_t8412.t8412_e.SetFieldData("t8412InBlock", "comp_yn", 0, comp_yn)

        EventClass_t8412.t8412_e.Request(occurs)
        EventClass_t8412.tr_success = False # False 초기화
        while EventClass_t8412.tr_success == False:
            pcom.PumpWaitingMessages()

        print("분봉 데이터 조회 종료")


if __name__ == "__main__":
    Main()
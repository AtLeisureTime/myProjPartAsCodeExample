import sys
import requests
import time
import random
import threading

class MainThreadInfo:
    def __init__(self):
        self.__perf_start_time = time.perf_counter()
        self.req_num = 0

    def rest(self):
        self.printPrxInfo()
        
        sleep_time = 301-(time.perf_counter()-self.__perf_start_time)
        if sleep_time < 0:
            sleep_time = 0

        time.sleep(sleep_time + random.random()*3.4)
        
        self.__perf_start_time = time.perf_counter()
        self.req_num = 0

    def calcAvReqTime(self):
        return (time.perf_counter() - self.__perf_start_time) / self.req_num
    
    def printPrxInfo(self):
        if self.req_num > 0:
            print ('th_{0}: {1:.2f}s, {2} OK, {3:.2f}s/OK '.format(threading.current_thread().getName(), \
                time.perf_counter() - self.__perf_start_time, self.req_num, self.calcAvReqTime()))
        
main_server = MainThreadInfo()

def tryingHardGetResponse(linkOnPage, errF, session='None'):        
    count = 0
    repeat_count = 4
    while count < repeat_count:
        if session == 'None':
            r = requests.get(linkOnPage)
        else:
            r = session.get(linkOnPage)
        main_server.req_num += 1
        
        if r.status_code != 200:
            count = count + 1
            errF.write(linkOnPage + ': ' + str(r.status_code) + ' error[' + str(count) + ']\n')            
            main_server.rest()
        else:
            if main_server.req_num == 15:
                main_server.rest()
            else:
                time.sleep(2.44 + random.random()*1.37)
            break
        
    if count == repeat_count:
        errF.write(linkOnPage + ' is not opened\n')
    else:
        return r

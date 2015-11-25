import sys
import time
import random
import threading
import pycurl
from io import BytesIO

mode_list = ['Silent','Detailed']
mode_ind = 0

class URLQueue:
    def __init__(self):
        self.__list = []
        self.__mutex = threading.RLock()        

    def add(self, key):
        with self.__mutex:
            self.__list.append(key)
            if mode_list[mode_ind] == 'Detailed':
                print('URLQueue: +url')

    def getURL(self, curl_ind):
        count = 0
        while not self.__list:
            time.sleep(2.11)
            count += 1
            if count > 3:
                return
        
        with self.__mutex:
            ind = random.randint(0, len(self.__list)-1)
            url = self.__list[ind]
            self.__list.remove(url)
            if mode_list[mode_ind] == 'Detailed':
                print('URLQueue: -url')
            prox_manager.incReqCounter(curl_ind)
            return url

URLQueMan = URLQueue()

class RespQueue:
    def __init__(self):
        self.__dict = {}
        self.__mutex = threading.RLock()

    def add(self, url, resp):
        with self.__mutex:
            self.__dict[url] = resp
            if mode_list[mode_ind] == 'Detailed':
                print('RespQueue: +resp')

    def check(self, url):
        with self.__mutex:
            resp = self.__dict.get(url)
            if resp:
                self.__dict.pop(url)                
                if mode_list[mode_ind] == 'Detailed':
                    print('RespQueue: -resp')
                return resp        

RespQueMan = RespQueue()


def tryingHardGetResponse(linkOnPage, errF, session='None'):

    URLQueMan.add(linkOnPage)
    resp = RespQueMan.check(linkOnPage)
    while not resp:
        time.sleep(2.11)
        resp = RespQueMan.check(linkOnPage)
    if mode_list[mode_ind] == 'Detailed' or mode_list[mode_ind] == 'Silent':
        print('+resp thr{0}'.format(threading.current_thread().getName()))
    if resp.decode('utf-8') == '\n':
        return
    return resp

class Proxies:    
    def __init__(self, file_name):        
        self.__addrs_array = []
        
        addrs_list_F = open(file_name, 'r')        
        for line in addrs_list_F:
            self.__addrs_array.append(line[0:-1])
        addrs_list_F.close()
        random.shuffle(self.__addrs_array)
        
        self.__addrs_num = len(self.__addrs_array)
        self.__index = 0

        self.__stat_dict = {}

    def incReqCounter(self, curl_ind):        
        self.__stat_dict[curl_ind][0] += 1        
    
    def getNewAddress(self, curl_ind):
        self.__index += 1
        if self.__index >= self.__addrs_num:
            self.__index = 0
        prx_adr = []
        adr = self.__addrs_array[self.__index]
        left_adr_part = adr[0:adr.find(':')]
        right_adr_part = adr[adr.find(':')+1:]
        proxy = 'socks5://' + left_adr_part
        prx_adr.append(proxy)
        prx_adr.append(right_adr_part)       

        if self.__stat_dict.get(curl_ind):
            if mode_list[mode_ind] == 'Detailed':
                print('\nCurl {0}: {1} req-ts in {2:.2f}s\nnew prx_adr:{3}\n'.format(curl_ind, self.__stat_dict[curl_ind][0], time.perf_counter() - self.__stat_dict[curl_ind][1], prx_adr))
        self.__stat_dict[curl_ind] = [0, time.perf_counter()]
        
        return prx_adr

def getSucIds(objs_list):
    ids_list = []
    for elem in objs_list:
        ids_list.append(id(elem))
    return ids_list

def getFailedIds(objs_list):
    ids_list = []
    for obj_tuple in objs_list:
        ids_list.append(id(obj_tuple[0]))
    return ids_list

prox_manager = Proxies('E:\ParsingRes\prx\prx_list.txt')
c_num = 8

user_agents = [ 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0', \                
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36 OPR/32.0.1948.25', \
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.33 Safari/537.36', \
                'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko', \
                'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)', \
                'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)', \
                'Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14']
random.shuffle(user_agents)

class SleepTimeManager:
    def __init__(self):
        self.__curl_dict = {}
        for i in range(0, c_num):
            self.__curl_dict[i] = [0, 1.8+random.random()]

    def getSleepTime(self, curl_ind, resp_code):
        if resp_code != 200 and self.__curl_dict[curl_ind][0] < 8:            
            self.__curl_dict[curl_ind][0] += 1
            self.__curl_dict[curl_ind][1] = (self.__curl_dict[curl_ind][1] + random.random()*(self.__curl_dict[curl_ind][0]+1.6)) * 2.1
        if resp_code == 200:
            self.__curl_dict[curl_ind] = [0, 1.8+random.random()]
        if mode_list[mode_ind] == 'Detailed':
            print('sl_t[curl {0}]:{1:.2f}s'.format(curl_ind, self.__curl_dict[curl_ind][1]))   
        return self.__curl_dict[curl_ind][1]

class FailedUrlList:
    def __init__(self):
        self.__failed_url_list = []
        self.__mutex = threading.RLock()
        
    def add(self, url):        
        with self.__mutex:
            self.__failed_url_list.append(url)

    def getFUList(self):
        return self.__failed_url_list
            
    def reqFUListCopy(self):
        global c_num
        fu_list_len = len(self.__failed_url_list)
        if fu_list_len > 0:
            failed_url_list_copy = self.__failed_url_list
            self.__failed_url_list = []
            random.shuffle(failed_url_list_copy)
            if fu_list_len < c_num:
                c_num = fu_list_len
            return failed_url_list_copy
        return []
    
failed_url_list = FailedUrlList()

def do_work(new_mode_ind):
    global mode_ind
    mode_ind = new_mode_ind
    m = pycurl.CurlMulti()
    c = []
    buf = []
    url_list = []
    stm = SleepTimeManager()
    
    for i in range(0, c_num):
        
        c.append(pycurl.Curl())
        
        c[i].setopt(pycurl.USERAGENT, user_agents[random.randint(0, len(user_agents)-1)])
        c[i].setopt(pycurl.FOLLOWLOCATION, 1)
        c[i].setopt(pycurl.MAXREDIRS, 7)
        
        adr = prox_manager.getNewAddress(i)
        c[i].setopt(pycurl.PROXY, adr[0])
        c[i].setopt(pycurl.PROXYPORT, int(adr[1]))
        
        c[i].setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
        
        url_list.append(URLQueMan.getURL(i))        
        c[i].setopt(c[i].URL, url_list[i])
        
        buf.append(BytesIO())
        c[i].setopt(c[i].WRITEDATA, buf[i])        
        m.add_handle(c[i])

    SELECT_TIMEOUT = 1.1

    # stir the state machine into action
    while 1:
        ret, num_handles = m.perform()
        if ret != pycurl.E_CALL_MULTI_PERFORM:
            break
    if mode_list[mode_ind] == 'Detailed':
        print('do_work after while 1[0]')
        
    # keep going until all the connections have terminated
    while num_handles:
        # the select method uses fdset internally to determine which file descriptors to check
        ret = m.select(SELECT_TIMEOUT)
        if ret == -1:  continue
        while 1:
            ret, num_handles = m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                info = m.info_read()                
                ids_suc_obj = getSucIds(info[1])
                ids_failed_obj = getFailedIds(info[2])

                fl_add_handle = False
                for i in range(0, c_num):
                    if id(c[i]) in ids_suc_obj:                        
                        
                        if mode_list[mode_ind] == 'Detailed':
                            print('curl {0}: {1}'.format(i, c[i].getinfo(c[i].RESPONSE_CODE)))
                            
                        if c[i].getinfo(c[i].RESPONSE_CODE) != 200:
                            time.sleep(stm.getSleepTime(i, c[i].getinfo(c[i].RESPONSE_CODE)))
                            m.remove_handle(c[i])
                                                        
                            adr = prox_manager.getNewAddress(i)
                            c[i].setopt(pycurl.USERAGENT, user_agents[random.randint(0, len(user_agents)-1)])
                            c[i].setopt(pycurl.PROXY, adr[0])
                            c[i].setopt(pycurl.PROXYPORT, int(adr[1]))
                            
                            RespQueMan.add(url_list[i], '\n'.encode('utf-8'))
                            buf[i].truncate(0)
                            buf[i].seek(0)

                            failed_url_list.add(url_list[i])
                            url_list[i] = URLQueMan.getURL(i)
                            if url_list[i]:                                
                                c[i].setopt(c[i].URL, url_list[i])                            
                                m.add_handle(c[i])
                                fl_add_handle = True
                        else:
                            time.sleep(stm.getSleepTime(i, c[i].getinfo(c[i].RESPONSE_CODE)))
                            m.remove_handle(c[i])
                            
                            RespQueMan.add(url_list[i], buf[i].getvalue())
                            buf[i].truncate(0)
                            buf[i].seek(0)
                            
                            url_list[i] = URLQueMan.getURL(i)
                            if url_list[i]:                                
                                c[i].setopt(c[i].URL, url_list[i])                            
                                m.add_handle(c[i])
                                fl_add_handle = True

                    if id(c[i]) in ids_failed_obj:
                        m.remove_handle(c[i])
                        if mode_list[mode_ind] == 'Detailed':
                            print(info)
                        time.sleep(stm.getSleepTime(i, 200))
                        
                        adr = prox_manager.getNewAddress(i)
                        c[i].setopt(pycurl.PROXY, adr[0])
                        c[i].setopt(pycurl.PROXYPORT, int(adr[1]))
                        
                        m.add_handle(c[i])
                        fl_add_handle = True
                       
                if fl_add_handle == False:
                    break           
                
    for i in range(0, c_num):
        c[i].close()        
    m.close()

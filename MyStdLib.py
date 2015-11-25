import sys
import time
import requests
import random
import threading
import json
import statistics
import ctypes

import MyResponseGetting
import MyResponseGetting2

#b#
def getTextAfter(all_text, left_text):
    begin = all_text.find(left_text)
    if int(begin) != -1:
        return all_text[begin + len(left_text):len(all_text)]

def getTextInTheMiddle(all_text, left_text, right_text):
    begin = all_text.find(left_text)
    end = all_text.find(right_text, begin)
    if int(begin) != -1 and int(end) != -1:
        return all_text[begin + len(left_text):end]

def getAllTextFragsInTheMiddle(all_text, left_text, right_text):

    def recurse(begins_found, ends_found, start_iter):
        begin = all_text.find(left_text, start_iter)
        end = all_text.find(right_text, begin)
        if int(begin) != -1 and int(end) != -1:
            return recurse(begins_found + [begin + len(left_text)], ends_found + [end], end + len(right_text))
        else:
            Frags = []    
            for i in range(len(begins_found)):
                Frags += [ all_text [ begins_found[i] : ends_found[i] ] ]
            return Frags

    return recurse([], [], 0)
#e#

#b#
def getPriceMedian(input_data):
    DAYLIMIT = 7

    stat_data = []
    strs = input_data.split('],[')
    strFields = strs[-1].split(',')
    nextTime = time.strptime(strFields[0][1:].split(':')[0], '%b %d %Y %H')
    dayNum = 0

    i = len(strs) - 2
    while i >= 0 and dayNum <= DAYLIMIT:
        strFields = strs[i].split(',')
        timeInField = time.strptime(strFields[0][1:].split(':')[0], '%b %d %Y %H')
        if nextTime[2] != timeInField[2]:
            dayNum += 1 # it's wrong if item isn't selled every day
        if dayNum != 0 and dayNum <= DAYLIMIT:
            hourPrice = float(strFields[1])
            hourCount = int(strFields[2][1:-1])
            stat_data += [hourPrice]*hourCount
        nextTime = timeInField
        i = i - 1
    #print(' !{0:.2f}'.format(statistics.mode(stat_data)*55.6))
    return statistics.median(stat_data)

def calcDayPopul(input_data):    
    DAYLIMIT = 14

    strs = input_data.split('],[')
    strFields = strs[-1].split(',')
    nextTime = time.strptime(strFields[0][1:].split(':')[0], '%b %d %Y %H')
    totalItemNum = 0
    dayNum = 0

    i = len(strs) - 2
    while i >= 0 and dayNum <= DAYLIMIT:
        strFields = strs[i].split(',')
        timeInField = time.strptime(strFields[0][1:].split(':')[0], '%b %d %Y %H')
        if nextTime[2] != timeInField[2]:
            dayNum += 1 # it's wrong if item isn't selled every day
        if dayNum != 0 and dayNum <= DAYLIMIT:
            totalItemNum += int(strFields[2][1:-1])
        nextTime = timeInField
        i = i - 1
        
    if dayNum == 0:
        return 0  

    return totalItemNum / dayNum

def calcDayPopulFact(day_popul, sell_order_num):
    return day_popul / sell_order_num

def getItemPricesRUB(j, errF):        
    # capturing price info
    all_text = str(j['listinginfo'])
    converted_prices = getAllTextFragsInTheMiddle(all_text, '\'converted_price\': ', ',')
    converted_fees = getAllTextFragsInTheMiddle(all_text, '\'converted_fee\': ', ',')

    if not converted_prices or not converted_fees:
        errF.write('Problem with price extracting\n')
        return
    #
    prices = []
    try:
        for i, converted_price in enumerate(converted_prices):
            if converted_prices[i][-1] == '}':
                converted_prices[i] = converted_prices[i][:-1]
            if converted_fees[i][-1] == '}':
                converted_fees[i] = converted_fees[i][:-1]
            prices.append((float(converted_prices[i]) + float(converted_fees[i])) / 100)
    except:
        print(converted_price)
        sys.exit()
        
    return prices

def getStickersInfo(j, errF):
    stickList = []
    id_arr = []
    try:
        for key, value in j['assets']['730']['2'].items():
            ind = len(value['descriptions']) - 1
            if value['descriptions'][ind]['value'] != ' ':
                all_text = str(value['descriptions'][ind]['value'])
                stickList.append(getTextInTheMiddle(all_text, 'Sticker: ', '<'))
                id_arr.append(key)
    except:
        print('Problem with json file in getStickersInfo function\n')
        sys.exit()
        
    return [stickList, id_arr]

def getPricesInfo(j, errF):
    priceDict = {}
    try:
        for key, value in j['listinginfo'].items():
            priceDict[value['asset']['id']] = (float(value['converted_price']) + float(value['converted_fee'])) / 100
    except:
        print('Problem with json file in getPricesInfo function\n')
        sys.exit()
        
    return priceDict

def getItemPrice(j, id_val, errF):
    try:
        for key, value in j['listinginfo'].items():
            if value['asset']['id'] == str(id_val):
                return (float(value['converted_price']) + float(value['converted_fee'])) / 100                
    except Exception as e:
        print('Problem with json file in getItemPrice function\n')
        errF.write('Problem with json file in getItemPrice function:{0}\n'.format(e))
        return -1.0

def calcExchanRate(errF):
    line = 'http://steamcommunity.com/market/listings/730/%E2%98%85%20Butterfly%20Knife%20%7C%20Fade%20%28Factory%20New%29'
    url1 = line + '/render/?query=&start=0&count=20&country=RU&language=english&currency=1'
    fields_list = ['success', 'listinginfo']
    j1 = getJSON2(url1, fields_list, errF)
    if not j1:
        return 0
    url2 = line + '/render/?query=&start=0&count=20&country=RU&language=english&currency=5'
    j2 = getJSON2(url2, fields_list, errF)
    if not j2:
        return 0
    priceUSDDict = getPricesInfo(j1, errF)
    priceRUBDict = getPricesInfo(j2, errF)
    sumER = 0
    el_num = 0
    for key in priceRUBDict.keys():
        if key in priceUSDDict:
            sumER += float(priceRUBDict[key]) / float(priceUSDDict[key])
            el_num += 1
    return sumER / el_num

def getCleanItemName(line):
    dirty_name = line[line.rfind('/')+1:]
    ind_separ = dirty_name.find('%')
    while ind_separ != -1:
        dirty_name = dirty_name[:ind_separ] + ' ' + dirty_name[ind_separ+3:]
        ind_separ = dirty_name.find('%')
    return dirty_name
#e#

#b#
def checkJSONFields(j, fields_list, url, errF):
    for field in fields_list:
        if not field in j:
            errF.write('{0}: there is no field \'{1}\' in json file'.format(url, field))
            return False
    return True
    
def getJSON(url, fields_list, errF):
    # getting json file and info about its integrity using proxy servers
    r = MyResponseGetting.tryingHardGetResponse(url, errF)
    if r is None:
        return

    try:
        j = json.loads(r.decode('utf-8')) #.replace("\'", '"')
    except Exception as e:
        print(url + ': problem with json file\n')
        print(e)
        errF.write(url + ': problem with json file\n')
        return
    
    if j is None:
        errF.write(url + ': json is None\n')
        return

    if not checkJSONFields(j, fields_list, url, errF):
        return
    return j

def getJSON2(url, fields_list, errF):
    # getting json file and info about its integrity without using proxy servers
    r = requests.get(url)
    if r.status_code != 200:
        print('stat_code: {0}'.format(r.status_code))
        return

    try:
        j = r.json()        
    except:
        errF.write(url + ': problem with json file\n')
        return
    
    if j is None:
        errF.write(url + ': json is None\n')
        return

    if not checkJSONFields(j, fields_list, url, errF):
        return
    return j

def getJSON3(url, fields_list, errF):
    # getting json file and info about its integrity without using proxy servers,
    # but taking into account sleep time
    r = MyResponseGetting2.tryingHardGetResponse(url, errF)
    if r.status_code != 200:
        print('stat_code: {0}'.format(r.status_code))
        return

    try:
        j = r.json()        
    except:
        errF.write(url + ': problem with json file\n')
        return
    
    if j is None:
        errF.write(url + ': json is None\n')
        return

    if not checkJSONFields(j, fields_list, url, errF):
        return
    return j
#e#
        
#b#
class RandPageSwitcher:
    def __init__(self, start_page, last_page, step):        
        self.__page_list = []
        for page in range(start_page, last_page + 1):
            self.__page_list.append(page)
        random.shuffle(self.__page_list)

        self.__page_ind = 0
        self.__last_page_ind = len(self.__page_list)-1
        self.step = step
        self.__mutex = threading.RLock()

    def NextPageStartItemNum(self):
        with self.__mutex:
            if self.__page_ind > self.__last_page_ind:
                return
            start_item_num = (self.__page_list[self.__page_ind] - 1) * self.step
            self.__page_ind += 1
            return start_item_num

class LineInd:
    def __init__(self, ind_max):
        self.__ind = -1
        self.__ind_max = ind_max
        self.__mutex = threading.RLock()
        
    def getNewInd(self):
        with self.__mutex:            
            self.__ind += 1
            if self.__ind >= self.__ind_max:
                return -1
            return self.__ind
#e#
        
#b#
def createURL(url_sample, start_num, count):
    substr1 = '&start='
    substr2 = '&count='
    delim = '&'
    
    ind_substr1 = url_sample.find(substr1)    
    if int(ind_substr1) == -1:
        return
    end1 = url_sample.find(delim, ind_substr1 + len(substr1))
    
    ind_substr2 = url_sample.find(substr2)    
    if int(ind_substr2) == -1:
        return
    end2 = url_sample.find(delim, ind_substr2 + len(substr2))
    
    return url_sample[0:ind_substr1 + len(substr1)] + str(start_num) + url_sample[end1: ind_substr2 + len(substr2)] + \
           str(count) + url_sample[end2:]

def processPages(ps, url_sample, processingFunc, ProcFuncArgs): # openedWrF, errF, additnlParms = ()):    
    start_num = ps.NextPageStartItemNum()
    
    while not start_num is None:
        print (start_num)
        url = createURL(url_sample, start_num, ps.step)
        processingFunc(url, ProcFuncArgs)
        
        start_num = ps.NextPageStartItemNum()

def processURLList(urls, url_ind, processingFunc, ProcFuncArgs):
    l_i = url_ind.getNewInd()
    
    while l_i != -1:
        url = urls[l_i]
        processingFunc(url, ProcFuncArgs)
        
        l_i = url_ind.getNewInd()
      
def startMltThrProcess(Target, ArgsT, ArgsDW):
    thread_num = MyResponseGetting.c_num
    thr = []
    for i in range(0, thread_num):
        thr.append(threading.Thread(name=str(i), target=Target, args=ArgsT))

    thr.append(threading.Thread(name=str(thread_num), target=MyResponseGetting.do_work, args=ArgsDW))
    
    for i in range(0, thread_num+1):
        thr[i].start()
    for i in range(0, thread_num+1):
        thr[i].join()

def calcNumPageUsingJSONResp(url, step, errF):    
    j = getJSON2(url, ['total_count'], errF)
    if not j:
        return
    total_num_item = int(j['total_count'])
    num_page = total_num_item // step
    if total_num_item % step != 0:
        num_page += 1
    return num_page
#e#

def deleteRepetitionsInFile(fname):
    F = open(fname, 'r')
    lines = F.readlines()
    F.close()
    F = open(fname, 'w')
    
    ind_list = [x for x in range(0, len(lines))]
    str_num = len(ind_list)
    
    for i in range(0, str_num):
        
        if not i in ind_list:
            continue
            
        for j in range(i + 1, str_num):            
            if not j in ind_list:
                continue
            if lines[i] == lines[j]:
                ind_list.remove(j)
                
        F.write(lines[i])    
    F.close()

def appendToClipboard(data):
    strcpy = ctypes.cdll.msvcrt.strcpy
    ocb = ctypes.windll.user32.OpenClipboard    #Basic Clipboard functions
    ecb = ctypes.windll.user32.EmptyClipboard
    gcd = ctypes.windll.user32.GetClipboardData
    scd = ctypes.windll.user32.SetClipboardData
    ccb = ctypes.windll.user32.CloseClipboard
    ga = ctypes.windll.kernel32.GlobalAlloc    # Global Memory allocation
    gl = ctypes.windll.kernel32.GlobalLock     # Global Memory Locking
    gul = ctypes.windll.kernel32.GlobalUnlock
    GMEM_DDESHARE = 0x2000

    data_enc = 'ascii'
    data = data.encode(data_enc, 'ignore').decode(data_enc)
    ocb(None)
    ecb()
    hCd = ga(GMEM_DDESHARE, len(bytes(data,data_enc))+1)
    pchData = gl(hCd)
    strcpy(ctypes.c_char_p(pchData),bytes(data,data_enc))
    gul(hCd)
    scd(1,hCd)
    ccb()

import sys
import time
from bs4 import BeautifulSoup

import MyStdLib
import MyResponseGetting
   
def parseListItemsPage(linkOnPage, ProcFuncArgs):
    resF = ProcFuncArgs[0]
    errF = ProcFuncArgs[1]
    USD_TO_RUB_RATE = float(sys.argv[1])

    j = MyStdLib.getJSON(linkOnPage, ['results_html'], errF)
    if not j:
        print('-1')
        return

    # getting name & price info for each item    
    soup2 = BeautifulSoup(j['results_html'])
    
    prices = soup2.find_all('span', style='color:white') # prices of items
    names = soup2.find_all('span', class_='market_listing_item_name') # names of items

    if not prices or not names:
        errF.write(linkOnPage + ': some item\'s information is not found\n')
        print('-2')
        return
    
    if len(prices) != len(names):
        errF.write(linkOnPage + ': ' + str(len(prices)) + ' prices and ' + str(len(names)) + ' names\n')
        print('-3')
        return
    #

    # getting price and quantity values for each item    
    for i, price in enumerate(prices):
        t = price.text
        price = MyStdLib.getTextInTheMiddle(t, '$', ' USD')
        if price is None:
            price = MyStdLib.getTextAfter(t, '$')
            if price is None:
                errF.write(linkOnPage + ': price wasn\'t retrieved\n')
                print('-4')
                print(t)
                return
        prices[i] = float(price) * USD_TO_RUB_RATE
    
    for i, name in enumerate(names):
        names[i] = MyStdLib.getTextAfter(name.text, 'Sticker | ')
        try:
            resF.write('{0}\t{1:6.2f}\n'.format(names[i], prices[i]))
        except:
            print(names[i], prices[i])


def main():
    
    resF = open('E:\Res\stickScan.txt', 'w')
    errF = open('E:\Res\stickScanErr.txt', 'w')

    #sys.argv[1] = MyStdLib.calcExchanRate(errF)
    #print(sys.argv[1])
    
    start_t = time.perf_counter()

    url_sample = 'http://steamcommunity.com/market/search/render/?query=&start=0&count=10' + \
          '&search_descriptions=0&sort_column=price&sort_dir=desc&appid=730' +\
          '&category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any' +\
          '&category_730_TournamentTeam%5B%5D=any&category_730_Weapon%5B%5D=any' + \
          '&category_730_Type%5B%5D=tag_CSGO_Tool_Sticker'   

    start_page = 1
    last_page = 1
    step = 10
    num_page = MyStdLib.calcNumPageUsingJSONResp(url_sample, step, errF)
    if num_page:
        last_page = num_page    

    ps = MyStdLib.RandPageSwitcher(start_page, last_page, step)

    ProcFuncArgs = (resF, errF)
    ArgsT=(ps, url_sample, parseListItemsPage, ProcFuncArgs)
    ArgsDW=(1,)
    MyStdLib.startMltThrProcess(MyStdLib.processPages, ArgsT, ArgsDW)
    print(MyResponseGetting.failed_url_list.getFUList())
    
    failed_url_list_copy = MyResponseGetting.failed_url_list.reqFUListCopy()
    if failed_url_list_copy:        
        line_ind = MyStdLib.LineInd(len(failed_url_list_copy))
        ArgsT = (failed_url_list_copy, line_ind, parseListItemsPage, ProcFuncArgs)        
        MyStdLib.startMltThrProcess(MyStdLib.processURLList, ArgsT, ArgsDW)
        print(MyResponseGetting.failed_url_list.getFUList())
    
    end_t = time.perf_counter()
    print('\nPerf_time:{0:.2f}s'.format(end_t - start_t))
    
    resF.close()
    errF.close()

if __name__ == "__main__":
    sys.argv = [sys.argv[0], '65.78']
    argc = len(sys.argv)    
    if len(sys.argv) != 2:
        print ("Usage error!")
        sys.exit()
    main()

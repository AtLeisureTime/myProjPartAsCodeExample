# myProjPartAsCodeExample

    MyResponseGetting.py

URLQueue - очередь на обработку запросов.
RespQueue - очередь из ответов на запросы.

Добавление запроса, ожидание и получение ответа осуществляется в функции tryingHardGetResponse(linkOnPage, errF, session='None').

Обработка запросов в c_num потоков происходит в функции do_work(new_mode_ind).
URL-адреса запросов извлекаются из URLQueue, обрабатываются, и ответы сервера записываются в RespQueue в кодировке utf-8 в случае, 
если прокси-сервер совершит перепорученный ему запрос и получит ответ с 200-ым кодом. Если код ответа прокси-сервера не 200-ый, то 
меняется адрес прокси-сервера и URL-адрес запроса заносится в список неудавшихся запросов. Если прокси-сервер не ответит, меняется 
адрес прокси-сервера и запрос с этим же URL-адресом совершается заново. Во всех случаях между запросами происходит пауза, 
продолжительность которой по определенному алгоритму устанавливает менеджер задания времени сна SleepTimeManager.


    MyResponseGetting2.py

Функция tryingHardGetResponse(linkOnPage, errF, session='None') - осуществление запроса без использования прокси-сервера, с 
повторными запросами и паузами в случае не 200-го кода ответа.


    MyStdLib.py

Наиболее часто используемые в проекте функции, разбитые на логические блоки.


    stick_scanner.py

Пример запуска многопоточной обработки запросов. Меняются значения start и count в url_sample. В файл stickScan.txt записываются 
названия наклеек и их цена в рублях. В файл stickScanErr.txt заносится информация об ошибках.

В функции parseListItemsPage(linkOnPage, ProcFuncArgs) происходит поиск интересующей информации внутри тегов html-кода, являющегося 
значением одного из полей в файле формата json.
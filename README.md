#Это тестовое задание в Яндекс

##Задание 1 - exercise_1

###Запуск

```main.py```

в файле main.py есть параметры:

CHOSEN_ALGORITHM - алгоритм, который будет обрабатывать файл (всего четыре)
по умолчанью =1

CSV_FILE - название csv файла с контрактами - по умолчанью ='pp-complete.csv'

RESULT_FILE - название файла в который будет сохранен результат (все результаты
лежат в папке results) по умолчанью ='result.txt'

Если надо затрэкать функции, чтобы посмотреть результаты, то требуется
выполнить команду ```pip install -r requirements.txt``` и раскомментировать в utils.py 
76-111, 262, 274, 297 и 312 строчки

###Краткое описание решения

Это первое задание. Изначально из формулировки задания не было понятно, что именно нужно вывести - контракты на дома,
которые продали больше одного раза или адрес с контрактами ниже или просто список адресов. По итогу был выбран последний
вариант, потому что первые не выглядят логичными (ведь мы на то и делаем поиск, чтобы из контрактов вытянуть адреса).
Таким образом я сделал несколько алгоритмов:

1) find_duplicates_easy_way - самый простой и банальный способ, просто в лоб парсим файл и считаем кто сколько раз нам
попался. Он самый простой, но и по идее самый эффективный по времени (но он держит в памяти сразу весь словарь,
что ест много памяти).

2) find_duplicates_external_search - самый криво написанный но по идее самый менее жрущий память алгоритм - обрабатывает файл
чанками и загружает их в файлы на диск в виде jsonов, а дальше склеивает (его можно очень сильно усовершенствовать, но
мне пока что не хватило знаний, чтобы это сделать).

3) find_duplicates_regex - то же что и первый алгоритм, только через регулярку - чем меньше файл, тем быстрее работает.
Если бы файл был до гигабайта - то он был бы самым лучшим среди всех.

4) find_duplicates_split - поэкспериментировал со стандартными фукнциями питона, если файл небольшой то по времени он
работает еще быстрее чем третий алгоритм, но... это колхоз)) никто в здравом уме так делать не будет, поэтому алгоритм
чисто экспериментальный, но на срезе до миллиона строк он себя показывал очень даже шустро (после миллиона он может
просто так выдать 170 секунд, причем непонятно почему, лучший результат что я получил это 140 секунд)

Вот результаты тестов алгоритмов:

|Параметр        | Результат              |
|----------------|------------------------|
|Function        |find_duplicates_easy_way|
|Memory before   | 12,140,544             |
|Memory after    | 12,992,512             |
|Memory consumed | 851,968                |
|Time            |124.14728617668152      |


|Параметр        | Результат                      |
|----------------|--------------------------------|
|Function        | find_duplicates_external_search|
|Memory before   | 11,927,552                     |
|Memory after    | 1,207,910,400                  |
|Memory consumed | 1,195,982,848                  |
|Time            | 295.1373801231384              |


|Параметр        | Результат            |
|----------------|----------------------|
|Function        | find_duplicates_regex|
|Memory before   | 11,927,552           |
|Memory after    | 16,252,928           |
|Memory consumed | 4,325,376            |
|Time            |184.78774785995483    |


|Параметр        | Результат            |
|----------------|----------------------|
|Function        | find_duplicates_split|
|Memory before   | 11,894,784           |
|Memory after    | 12,337,152           |
|Memory consumed | 442,368              |
|Time            | 140.17971396446228   |

При всех моих попытках оптимизировать второй алгоритм, сильно уменьшить использование памяти мне не удалось (точнее
это привело к троекратному увеличению времени). Я думаю что счетчик памяти немного врет и второй алгоритм в моменте
должен использовать памяти меньше чем другие, но в конце слияния образуется узкое горлышко, которое я не придумал как
убрать, но я думаю что если его еще доработать, то он был бы самым оптимальным, возможно мне не хватило опыта и знаний,
чтобы довести его до ума, а может я не додумался до чего то элементарного и переусложнил код.

По итогу самый нормальный алгоритм - это первый, который был написан за 10 минут, а на остальные ушло 2 дня

##Задание 3 - exercise_3

###Запуск

в .env нужно указать BOT_TOKEN - токен бота и TELEGRAM_CHANNEL - канал
в тг (предварительно нужно добавить бота в канал и назначить администратором)

далее запускаем команду ```docker-compose up --build --detach```

Все, наслаждаемся свежими новостями, повторно присылать одни и те же 
новости бот не будет - я его отучил ;)

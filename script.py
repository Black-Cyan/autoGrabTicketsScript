import json
import threading
import time
from queue import Queue

import DrissionPage.errors as dp_err
import requests
import yaml
from DrissionPage import ChromiumPage
from DrissionPage.common import Actions
from prettytable import PrettyTable
from pypinyin import pinyin, Style
from requests import JSONDecodeError

print('--------脚本作者：墨青--------')
print('Github仓库：https://github.com/BlackCyan07/autoGrabTicketsScript')

# 将输入的城市转换为拼音
def change(chinese):
    text1 = pinyin(chinese, style=Style.NORMAL)
    string = ''.join([t[0] for t in text1])
    return string

# 定义多线程目标函数
def fetch_data(c, train_date, from_city, to_city, headers, result_queue):
    url = f'https://kyfw.12306.cn/otn/leftTicket/query{chr(c) if c != 0 else ""}?leftTicketDTO.train_date={train_date}&leftTicketDTO.from_station={from_city}&leftTicketDTO.to_station={to_city}&purpose_codes=ADULT'
    response = requests.get(headers=headers, url=url)
    try:
        data = response.json()
        result_queue.put(data)
    except JSONDecodeError:
        pass

# 选择目标城市
def choose_city(city_items_selector,target_city_name):
    city_items = []
    # 获取下拉列表的所有元素
    for cis in city_items_selector:
        cities = dp.eles(cis)
        city_items.extend(cities)

    # 遍历每个下拉列表元素，寻找匹配的城市
    for city_item in city_items:
        city = city_item.ele('css:.ralign').text.strip()
        if city == target_city_name:
            city_item.click()
            break



# 引用配置文件
with open('config/config.yml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)
f = open('config/cities.json', encoding='utf-8').read()
city_data = json.loads(f)

# 定义请求头
headers = {
    'Cookie' : '_uab_collina=171959196059070525462211; JSESSIONID=934CC95F7C881851D560D6EF8B7B67B5; tk=OYBnZPnapPHALsWNqLyIlFgK3ADcfICc3mdXI8QJZ-slmB1B0; _jc_save_wfdc_flag=dc; guidesStatus=off; highContrastMode=defaltMode; cursorStatus=off; _jc_save_toDate=2024-10-10; route=6f50b51faa11b987e576cdb301e545c4; BIGipServerotn=1943601418.64545.0000; _jc_save_fromStation=%u5A04%u5E95%u5357%2CUOQ; _jc_save_toStation=%u9686%u56DE%2CLHA; BIGipServerpassport=954728714.50215.0000; _jc_save_fromDate=2024-10-11; uKey=3a678c0f4997b5f9ce2423e0bc56c25fdf1b511105ed9aa129a89ddddb3f230d',
    'User-Agent' :  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
}

train_date = input('请输入出发日期（YYYY-MM-DD）：')
fromCity = input('请输入出发城市：')
toCity = input('请输入到达城市：')

result_queue = Queue()
threads = []
iterable = [0]
iterable.extend(range(65, 91))

# 创建多线程
for c in iterable:
    thread = threading.Thread(target=fetch_data, args=(c, train_date, city_data[fromCity], city_data[toCity], headers, result_queue))
    threads.append(thread)
    thread.start()
for thread in threads:
    thread.join()
json_data = None
while not result_queue.empty():
    result = result_queue.get()
    if result:
        json_data = result
        break

# 解析数据
result = json_data['data']['result']

# 实例化对象
tb = PrettyTable()
tb.field_names = [
    '序号',
    '车次',
    '出发时间',
    '到达时间',
    '耗时',
    '二等座',
    '一等座',
    '特等座',
    '无座',
    '硬座',
    '硬卧',
    '软卧'
]
# 定义序号
page = 1
# for循环遍历，提取列表元素内容
for i in result:
    # 字符串分割，返回列表
    index = i.split('|')
    # 通过列表索引位置取值
    num = index[3] # 车次
    start_time = index[8] # 出发时间
    end_time = index[9] # 到达时间
    use_time = index[10] # 耗时
    second_class = index[30] # 二等座
    first_class = index[31] # 一等座
    topGrade = index[32] # 特等座
    hard_sleeper = index[28] # 硬卧
    hard_seat = index[29] # 硬座
    no_seat = index[26] # 无座
    soft_sleeper = index[23] #软卧
    dit = {
        '车次' : num,
        '出发时间' : start_time,
        '到达时间' : end_time,
        '耗时' : use_time,
        '二等座' : second_class,
        '一等座' : first_class,
        '特等座' : topGrade,
        '无座' : no_seat,
        '硬座' : hard_seat,
        '硬卧' : hard_sleeper,
        '软卧' : soft_sleeper
    }

    tb.add_row([
        page,
        num,
        start_time,
        end_time,
        use_time,
        second_class,
        first_class,
        topGrade,
        hard_sleeper,
        hard_seat,
        no_seat,
        soft_sleeper,
    ])
    page += 1
if result:
    print(tb)
else:
    print('暂无该方案车次，程序自动退出')
    exit()

username = config['username']
password = config['password']
id_card = config['id_card']
Num = input('请选择你想购买的车次序号：')

# 打开浏览器
dp = ChromiumPage(9333)
ac = Actions(dp)
dp.get('https://kyfw.12306.cn/otn/leftTicket/init')
"""判断是否有登录账号"""
text = dp.ele('css:#login_user').text
if text == '登录':
    # 输入账号密码登录
    dp.ele('css:#login_user').click()
    dp.ele('css:#J-userName').input(username)
    dp.ele('css:#J-password').input(password)
    time.sleep(0.5)
    dp.ele('css:#J-login').click()
    dp.ele('css:#id_card').input(id_card)
    time.sleep(0.5)
    dp.ele('css:#verification_code').click()
    code = input('请输入手机收到的验证码：')
    dp.ele('css:#code').input(code)
    time.sleep(0.5)
    dp.ele('css:#sureClick').click()
    time.sleep(0.5)
    while dp.ele('xpath://*[@id="message"]/p'):
        code = input('验证码输入错误！请重新输入验证码：')
        dp.ele('css:#code').clear().input(code)
        dp.ele('css:#sureClick').click()
dp.get('https://kyfw.12306.cn/otn/leftTicket/init')
# 定位输入框
# 出发站
input_selector = 'css:#fromStationText'
ac.move_to(input_selector).click()
time.sleep(0.3)
ac.type(change(fromCity))
time.sleep(0.3)
city_items_selector = ['css:#panel_cities .citylineover','css:#panel_cities .cityline']
choose_city(city_items_selector,fromCity)
# 终点站
input_selector = 'css:#toStationText'
ac.move_to(input_selector).click()
time.sleep(0.3)
ac.type(change(toCity))
time.sleep(0.3)
city_items_selector = ['css:#panel_cities .citylineover','css:#panel_cities .cityline']
choose_city(city_items_selector,toCity)

print('正在抢票中...')
# 点击查询按钮
dp.ele('css:#query_ticket').click()

# 创建计时器
start = time.time()
while True:
    if (not dp.ele(f'css:#queryLeftTable tr:nth-child({int(Num)*2-1}) .btn72')) and (second_class == '*' or hard_seat == '*'):
        if time.strftime('%H:%M:%S', time.localtime()) == '17:29:59' or time.strftime('%H:%M:%S', time.localtime()) == '16:59:59':
            dp.refresh()
            # 执行两步操作，增加容错
            try:
                dp.ele('css:#query_ticket').click()
            except dp_err.ElementLostError:
                dp.ele('css:#query_ticket').click()
        elif time.time() - start >= config['heart']:
            dp.refresh()
            print(f'车票还未开售，等待开售...(等待{config["heart"]}秒自动刷新，请勿关闭脚本)')
            # 执行两步操作，增加容错
            try:
                dp.ele('css:#query_ticket').click()
            except dp_err.ElementLostError:
                dp.ele('css:#query_ticket').click()
            start = time.time()
        continue
    else:
        # 点击预定按钮
        dp.ele(f'css:#queryLeftTable tr:nth-child({int(Num)*2-1}) .btn72').click()
        time.sleep(1)
        # 选择乘车人
        dp.ele('css:#normalPassenger_0').click()
        if dp.ele('xpath://*[@id="dialog_xsertcj"]/div[2]'):
            if config['isStu'] == 'y':
                dp.ele('css:#dialog_xsertcj_ok').click()
            else:
                dp.ele('css:#dialog_xsertcj_cancel').click()
        time.sleep(1)
        # 提交订单
        dp.ele('css:#submitOrder_id').click()
        dp.ele('css:#qr_submit_id').click()
        break

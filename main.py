from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

# "name,mm-dd,..."
DATE_MEMO = os.environ["DATE_MEMO_NAME_VALUE"]

today = datetime.now()
start_date = os.environ['LOVE_START']  # yyyy-mm-dd
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']  # yyyy-mm-dd

app_id = os.environ["APP_ID"]  # from wechat open
app_secret = os.environ["APP_SECRET"]  # from wechat open

user_ids = os.environ["USER_ID"].split("\n")  # from wechat open
template_id = os.environ["TEMPLATE_ID"]  # from wechat open

# "name,mm-dd,..."
memo_name_value = list(map(lambda it: it.strip(), DATE_MEMO.split(",")))
memo_name = memo_name_value[0::2]
memo_value = memo_name_value[1::2]


def get_weather():
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  return weather['weather'], math.floor(weather['temp']), math.floor(weather['high']), math.floor(weather['low'])

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_live_days():
  """出生了多少天"""
  birth = datetime.strptime(birthday, "%Y-%m-%d")
  return (datetime.now() - birth).days

def get_nearest_memo_days():
  year = date.today().year
  min_day = 366
  name = memo_name[0]
  for i in range(len(memo_value)):
    memo_date = memo_value[i]
    cur = datetime.strptime(str(year) + "-" + memo_date, "%Y-%m-%d")
    if cur >= datetime.now() and (cur - today).days < min_day:
      min_day = (cur - today).days
      name = memo_name[i]
    elif cur < datetime.now(): # 如果当前纪念日已过，计算下个纪念日时间
      cur = cur.replace(year=year + 1)
      if (cur - today).days < min_day:
        min_day = (cur - today).days
        name = memo_name[i]
  return name, min_day

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature, highest, lowest = get_weather()
memo_info = get_nearest_memo_days()
data = {"weather": {"value": wea, "color": get_random_color()},
        "temperature": {"value": temperature, "color": get_random_color()},
        "love_days": {"value": get_count(), "color": get_random_color()},
        "days_memo_name": {"value": memo_info[0], "color": get_random_color()},
        "days_memo_left": {"value": memo_info[1], "color": get_random_color()},
        "words": {"value": get_words(), "color": get_random_color()},
        "highest": {"value": highest, "color": get_random_color()},
        "lowest": {"value": lowest, "color": get_random_color()}}
count = 0
for user_id in user_ids:
  res = wm.send_template(user_id, template_id, data)
  count+=1

print("发送了" + str(count) + "条消息")

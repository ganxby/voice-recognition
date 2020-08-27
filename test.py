from tinkoff_voicekit_client import ClientSTT
import re
import datetime
import random
import psycopg2
import os

API_KEY = ""
SECRET_KEY = ""

client = ClientSTT(API_KEY, SECRET_KEY)

audio_config = {
    "encoding": "LINEAR16",
    "sample_rate_hertz": 8000,
    "num_channels": 1
}

while True:
    try:
        global entering_path
        entering_path = input(str("Введите путь к wav-файлу: "))
        check1 = open(entering_path, 'r')
        check1.close()
        break

    except FileNotFoundError:
        print("Ошибка. Введите корректный путь!\n")
        check2 = open(' ', 'a') #Вставьте свой путь для логирования ошибок
        check2.write("Ошибка FileNotFoundError - файл не найден\n")
        check2.close()
        pass

entering_telnum = input("Введите номер телефона: ")
entering_flag = input("Сохранить в базу данных? (да/нет): ")
print()

response = client.recognize(entering_path, audio_config)

elem = response[0]["alternatives"][0]["transcript"]
time = response[0]["end_time"]

result = []

def func1():
    if "автоответчик" in elem:
        return 0
    elif "автоответчик" not in elem:
        return 1

def func2():
    if re.search(r'нет|неудобно|до свидания', elem):
        return 0
    elif re.search(r'говорите|да конечно|слушаю', elem):
        return 1

if func1() == 0:
    print("Обнаружен автоответчик!")
    result.append("автоответчик")
elif func1() == 1:
    print("Автоответчик не обнаружен!")
    if func2() == 0:
        print("Человек отказался разговаривать!")
        result.append("человек отказался разговаривать")
    elif func2() == 1:
        print("Человек согласился разговаривать!")
        result.append("человек согласился разговаривать")

append = open(' ', 'a') #Вставьте свой путь для логировани
rndnumb = str(random.randrange(100000, 999999, 1))
one = str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S") + ' ' + "id" + rndnumb)
append.write(one)

if func1() == 0:
    append.write(" автоответчик ")
elif func1() == 1:
    append.write(" человек ")
    if func2() == 0:
        append.write("отказался ")
    elif func2() == 1:
        append.write("согласился ")

append.write(entering_telnum + " " + time + " " + "'" + elem + "'" + '\n')
append.close()

if entering_flag == "да":
    con = psycopg2.connect(
      database="",
      user="",
      password="",
      host="127.0.0.1",
      port="5432"
    )

    cur = con.cursor()
    cur.execute(
      "INSERT INTO voice_data (DATE,DURATION,ID,RESULT,TEL_NUMBER,TEXT) VALUES (%s, %s, %s, %s, %s, %s)",
       (
       datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), time, rndnumb, *result, entering_telnum, elem
       )
    )

    con.commit()
    con.close()

os.remove(entering_path)
input()

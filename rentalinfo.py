import telegram  # 텔레그램 모듈을 가져옵니다.
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler  # import modules

my_token = '770204912:AAF-VH_TCoVEb3TBzTTGW76rPkk3W3wQgyA'


# message reply function
def get_message(bot, update):
    update.message.reply_text("got text")
    update.message.reply_text(update.message.text)


# help reply function
def help_command(bot, update):
    update.message.reply_text("무엇을 도와드릴까요?")


# #1. 텔레그램 봇 테스트
# my_token = '770204912:AAF-VH_TCoVEb3TBzTTGW76rPkk3W3wQgyA'   #토큰을 변수에 저장합니다.
#
# bot = telegram.Bot(token = my_token)   #bot을 선언합니다.
#
# updates = bot.getUpdates()  #업데이트 내역을 받아옵니다.
#
# for u in updates :
#     print(u.message)
#     print("message")
#
# chat_id = bot.getUpdates()[-1].message.chat.id
# bot.sendMessage(chat_id = chat_id, text="봇테스트 완료되었습니다.")

# 업데이트 변경내역 확인
import requests
from bs4 import BeautifulSoup
import os
import psycopg2
import logging


# 파일의 위치
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))



def get_conn(p_db_type):
    conn = ''
    if p_db_type == '':
        p_db_type = 'TIB'

    if p_db_type == 'TIB':
        JDBC_DRIVER = os.environ["JAVA_HOME"] + "\\lib\\tibero5-jdbc.jar"
        JDBC_LIBS = os.environ["JAVA_HOME"] + "\\lib"
        # conn = jaydebeapi.connect("com.tmax.tibero.jdbc.TbDriver", "jdbc:tibero:thin:@localhost:7069:DBTBROT",["sys", "tibero"], JDBC_DRIVER, [])
        print(JDBC_DRIVER)

    if p_db_type == 'PGS':
        conn = psycopg2.connect(dbname="postgres", user="postgres", password="", host="localhost", port="5432")

    return conn


def startRentalAlm(conn):
    # 초기에 렌탈목록 전체 삭제일자 넣기(없는목록을 제거할 수 없어 전체 삭제일자 넣은 후 있을 경우 NULL로 업데이트

    curs = conn.cursor()
    # 전체 업데이트
    insert_sql = """UPDATE  ALM_LIST SET  ALM_YN = 'Y'
                 """

    logging.debug(insert_sql)
    curs.execute(insert_sql)
    conn.commit()


def stopRentalAlm(conn):
    # 초기에 렌탈목록 전체 삭제일자 넣기(없는목록을 제거할 수 없어 전체 삭제일자 넣은 후 있을 경우 NULL로 업데이트

    curs = conn.cursor()
    # 전체 업데이트
    insert_sql = """UPDATE  ALM_LIST SET  ALM_YN = 'N'
                 """

    logging.debug(insert_sql)
    curs.execute(insert_sql)
    conn.commit()


def start_alm(bot, update):
    conn = get_conn('PGS')
    startRentalAlm(conn)
    update.message.reply_text("알람 시작했습니다.")
    conn.close()


def stop_alm(bot, update):
    conn = get_conn('PGS')
    stopRentalAlm(conn)
    update.message.reply_text("알람 중지했습니다.")
    conn.close()


def rtlList(bot, update):
    conn = get_conn('PGS')
    curs = conn.cursor()
    query = """ select * 
                  from RT_PD_LIST
                 where rt_scd = '1'
                   and delt_dt is null
            """
    # print(query)
    curs.execute(query)

    rows = curs.fetchall()
    for c in rows:
        # cur_pd_nm = c[0]
        # cur_rt_scd = c[1]
        update.message.reply_text(c[0] + " 라켓 렌탈 가능합니다")

    conn.close()


def sendMessage(msg):
    my_token = '770204912:AAF-VH_TCoVEb3TBzTTGW76rPkk3W3wQgyA'  # 토큰을 변수에 저장합니다.

    bot = telegram.Bot(token=my_token)  # bot을 선언합니다.
    #
    # updates = bot.getUpdates()  #업데이트 내역을 받아옵니다.
    #
    # for u in updates :
    #     print(u.message)
    #     print("message")
    #
    chat_id = bot.getUpdates()[-1].message.chat.id
    bot.sendMessage(chat_id=chat_id, text=msg)



updater = Updater(my_token)

message_handler = MessageHandler(Filters.text, get_message)
updater.dispatcher.add_handler(message_handler)

help_handler = CommandHandler('help', help_command)
updater.dispatcher.add_handler(help_handler)

help_handler = CommandHandler('start', start_alm)
updater.dispatcher.add_handler(help_handler)

help_handler = CommandHandler('stop', stop_alm)
updater.dispatcher.add_handler(help_handler)

help_handler = CommandHandler('list', rtlList)
updater.dispatcher.add_handler(help_handler)

updater.start_polling(timeout=3, clean=True)
updater.idle()

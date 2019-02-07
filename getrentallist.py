# 업데이트 변경내역 확인
import requests
from bs4 import BeautifulSoup
import os
import psycopg2
import logging

def getRentalList(url):

    req = requests.get(url)
    logging.debug("req = requests.get(url)")

    req.encoding = 'utf-8'

    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    # 제품리스트에서 렌탈목록 가져옴
    all_divs = soup.find_all("article", class_="product_list")

    # DB CONNECT
    logging.debug("DB CONNECT")
    conn = get_conn('PGS')
    # 처음시작일 경우에만 전체 업데이트
    if url == 'https://www.yonex.co.kr/cs/rentalList.do?pageIndex=1':
        logging.debug("updRentalDel(conn)")
        updRentalDel(conn)

    logging.debug("렌탈 데이터 처리")
    for n in all_divs:
        for i in n.get_text().split('\n'):
            if i != "":
                # print(i)
                if i[0:4] == "예약마감":
                    print(i[5:] + " 라켓은 예약 마감되었습니다.")
                    regRentalProd(i[5:], '2', conn)
                else:
                    print(i + " 라켓은 렌탈가능합니다.")
                    regRentalProd(i, '1', conn)


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


def regRentalProd(prodNm, rtScd, conn):
    # 상태확인
    # conn = get_conn('PGS')
    curs = conn.cursor()
    query = """ select PD_NM,RT_SCD
                  from RT_PD_LIST
                 where PD_NM  ='""" + prodNm + """'
            """
    #
    # print(query)

    # curs.prepare(query)

    # print(query)
    curs.execute(query)

    # print(curs.fetchone())

    rows = []
    rows = curs.fetchall()
    cur_pd_nm = ''
    cur_rt_scd = ''
    for c in rows:
        cur_pd_nm = c[0]
        cur_rt_scd = c[1]
        # print("pd_nm : "+c[0])
        # print("rt_scd : " + c[1])
    # rows = [item[0] for item in curs.fetchall()]
    # for item in curs.fetchall():
    #     rows.append(item[0])
    # rows = [item[0] ]

    # print(rows)

    # rtScd = ""
    # 텔레그램 렌탈가능 메시지 보내기
    if cur_rt_scd != rtScd and rtScd == '1':
        # print("텔레그램 렌탈가능 알림")
        # print("pd_nm : "+cur_pd_nm)
        # print("rt_scd : " + cur_rt_scd)
        sendMessage(prodNm + " 라켓 렌탈 가능합니다.")

    # 등록,변경
    insert_sql = """INSERT INTO RT_PD_LIST (PD_NM,RT_SCD,INST_DT,STAT_UPDT_DT,DELT_DT) 
                           VALUES ('""" + prodNm + """','""" + rtScd + """', CURRENT_DATE,CURRENT_DATE,NULL) 
                           ON CONFLICT (PD_NM) DO UPDATE SET RT_SCD = '""" + rtScd + """' 
                                                            ,STAT_UPDT_DT = CURRENT_DATE
                                                            ,DELT_DT = NULL"""

    logging.debug(insert_sql)
    curs.execute(insert_sql)
    conn.commit()


def updRentalDel(conn):
    # 초기에 렌탈목록 전체 삭제일자 넣기(없는목록을 제거할 수 없어 전체 삭제일자 넣은 후 있을 경우 NULL로 업데이트

    curs = conn.cursor()
    # 전체 업데이트
    insert_sql = """UPDATE  RT_PD_LIST SET  DELT_DT = CURRENT_DATE
                    WHERE DELT_DT IS NULL
                 """

    logging.debug(insert_sql)
    curs.execute(insert_sql)
    conn.commit()



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

#log mode
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s')

getRentalList('https://www.yonex.co.kr/cs/rentalList.do?pageIndex=1')
getRentalList('https://www.yonex.co.kr/cs/rentalList.do?pageIndex=2')

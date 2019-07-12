# -*- coding: utf-8 -*-
import re

import urllib.request
import urllib.parse
import pandas
import lxml
import datetime

# from openpyxl import Workbook
from bs4 import BeautifulSoup
# from operator import itemgetter


# 원래 크롤링 순서
# 날짜, 종가, 전일비, 시가, 고가, 저가, 거래량
# 변환 후 순서
# 날짜, 시가, 고가, 저가, 거래량(볼륨), 종가, 전일비
def change_rows_in_list(data):
    for col in data:
        col[0], col[1], col[2], col[3], col[4], col[5], col[6] = col[0], col[3], col[4], col[5], col[6], col[1], col[2]
    return


def get_company_id_with_name(name):
    code_df = pandas.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
    # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌 
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
    # 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다. 
    code_df = code_df[['회사명', '종목코드']] 
    # 한글로된 컬럼명을 영어로 바꿔준다. 
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

    # '삼성전자'회사명의 행 번호 찾기
    rownum = code_df['name'].isin([name]).values
    # 해당 행에서 코드만 추출
    row = code_df[code_df.name == name]['code']
    # 파싱

    # company_code = str(row)[7:14].strip()
    company_code = str(row).split(' ')[4][:7].strip()
    # print(type(company_code))
    # if company_code:
    #     get_company_name_with_wrong_input(name)
    #     return

    return company_code

def get_company_name_with_id(code):
    code_df = pandas.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
    # 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌 
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
    # 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다. 
    code_df = code_df[['회사명', '종목코드']] 
    # 한글로된 컬럼명을 영어로 바꿔준다. 
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

    # '삼성전자'회사명의 행 번호 찾기
    rownum = code_df['code'].isin([code]).values
    # 해당 행에서 코드만 추출
    row = code_df[code_df.code == code]['name']
    # 파싱
    print(row)
    p = re.compile("[^0-9]")
    company_name = str(row)
    company_name = "".join(p.findall(company_name))[4:]
    spacepos = company_name.find('\n')
    company_name = company_name[:spacepos]
    # print(company_name)
    return company_name

# def get_company_name_with_wrong_input(name):

#     url = "https://finance.daum.net/domestic/search?q="
#     url2 = urllib.parse.quote_plus(name)
#     full_url = url + url2
#     print(full_url)
#     source_code = urllib.request.urlopen(full_url).read()
#     soup = BeautifulSoup(source_code, "html.parser")

#     table = soup.find("div", class_="box_contents")
#     # find_all("a", class_="txt")

#     print(table)
#     company_name = []
#     # while len(company_name)<=10:
#     #     company_name.append("")

#     return


def get_all_company_id():
    return

def list_to_csv(data, company_id):
    df = pandas.DataFrame(data)

    now = datetime.datetime.now()
    date = now.strftime('%Y%m%d')
    
    # 파일형식은 '종목번호_현재날짜.csv'
    filename = company_id + '_' + date + ".csv"
    df.to_csv(filename, header=None, index=None)


def crawl_stock_with_id(company_id):
    
    crawled_data = []

    # 30페이지 크롤링
    for page in range(35):
        url = "https://finance.naver.com/item/sise_day.nhn?code=" + company_id + "&page=" + str(page)
        source_code = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(source_code, "html.parser")
    
        data_in_page = soup.find_all("span", class_="tah")
        tmplist = []

        # 페이지별 크롤링
        for data in data_in_page:
            
            tmpstr = data.getText().strip().replace(',', '')
            
            if '.' in tmpstr:
                if len(tmplist) != 0:
                    crawled_data.append(tmplist)
                tmplist = []
                tmplist.append(tmpstr)
            else:
                tmplist.append(int(tmpstr))

    # print(crawled_data)
    change_rows_in_list(crawled_data)
    # print("------------")
    # print(crawled_data)

    return crawled_data

def get_chart_with_id(company_id):
    url = "https://finance.naver.com/item/main.nhn?code=" + company_id
    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code, "html.parser")
    
    # 이미지 크기는 (700, 289)
    img_url = soup.find("img", id="img_chart_area").get("src")

    now = datetime.datetime.now()
    date = now.strftime('%Y%m%d%H%M')
    
    # 파일형식은 '종목번호_현재날짜.csv'
    img_name = company_id + '_' + date + ".png"

    urllib.request.urlretrieve(img_url, "./static/img/" + img_name)

    return img_url

def get_similar_company_id(company_id):

    url = "https://finance.naver.com/item/main.nhn?code=" + company_id
    source_code = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source_code, "html.parser")

    company_list = []

    # tabledata = soup.find("div", class_="trade_compare").find("thead").find_all("em")
    tabledata = soup.find("div", class_="trade_compare").find("thead").find_all("em")

    for data in tabledata:
        data = str(data)
        company_list.append(data[4:10])

    print(company_list[1:])
    return company_list[1:]


from __future__ import annotations

import logging
import sys
import time
from pprint import pprint

import pendulum
# import pymysql

from airflow.models.dag import DAG
from airflow.operators.python import (
    PythonOperator
)

log = logging.getLogger(__name__)

PATH_TO_PYTHON_BINARY = sys.executable

# MySQL Connector Python을 임포트합니다.
import mysql.connector
from mysql.connector import errorcode

# 외부 api 요청을 위해 임포트
import requests
# json 객체 관련 작업을 위해 임포트
import json
# 문자열을 datetime으로 바꾸기 위해 임포트
from datetime import datetime


# MySQL 연결 정보를 설정합니다.
MYSQL_HOST = 'j10e105.p.ssafy.io'
MYSQL_PORT = '3306'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'GGAME!buk105'
MYSQL_DATABASE = 'ggame'



# 커넥션 생성
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)

# 커서 생성
cursor = conn.cursor()


with DAG(
    dag_id="dags_sget_game_data",
    schedule="0 0 * * *",
    start_date=pendulum.datetime(2021, 1, 1, tz="Asia/Seoul"),
    catchup=False,
    tags=["please","mysql","test"],
):
    
    def update_game_data(app_id, detail_json):
        print("###################UPDATE GAME DATA RUN!!!#######################")
        detail_body = detail_json.get(app_id).get("data")
        # game객체에 필요한 값 추출
        game_id = app_id
        game_name = detail_body.get("name").replace('"', '')
        game_short_description = detail_body.get("short_description").replace('"', '')
        # 상세설명이 길어서 MEDIUMTEXT 형식으로 저장
        game_detailed_description = detail_body.get("detailed_description").replace('"', '')
        game_header_img = detail_body.get("header_image")
        if not detail_body.get("website"):
            log.info("NO WESITE")
            game_website = ""
        game_website = detail_body.get("website")
        # devloper list를 문자열로
        if not detail_body.get("developers"):
            print("NO DEVELOPER")
            game_developer = ""
        else:
            game_developer = ', '.join([element.replace('"', '') for element in detail_body.get("developers")])
        # publisher list를 문자열로
        game_publisher = ', '.join([element.replace('"', '') for element in detail_body.get("publishers")])
        if not detail_body.get("price_overview") :
            log.info("NO PRICE OVERVIEW")
            game_price_initial = 0
            game_price_final = 0
            game_discount_percent = 0
        else:
            game_price_initial = detail_body.get("price_overview").get("initial")
            game_price_final = detail_body.get("price_overview").get("final")
            game_discount_percent = detail_body.get("price_overview").get("discount_percent")
        # game_release_date는 문자열로 저장(형태가 너무 다양함)
        game_release_date = detail_body.get("release_date").get("date").replace('"', '')
        
        # list를 json 객체로 만든 후 저장
        screenshots_json = {
            "screenshots": detail_body.get("screenshots")
        } 
        json_game_screenshot_img = json.dumps(screenshots_json) # json 객체를 문자열로 변환
        game_screenshot_img = json_game_screenshot_img
        
    
        # # mysql db에 업데이트
        query = f"""
        update game 
        set 
        game_name = "{game_name}"
        , game_short_description = "{game_short_description}"
        , game_detailed_description = "{game_detailed_description}"
        , game_header_img = "{game_header_img}"
        , game_website = "{game_website}"
        , game_developer = "{game_developer}"
        , game_publisher = "{game_publisher}"
        , game_price_initial = {game_price_initial}
        , game_price_final = {game_price_final}
        , game_discount_percent = {game_discount_percent}
        , game_release_date = "{game_release_date}"
        , game_screenshot_img = '{game_screenshot_img}'
        , updated_dt = now()
        
        where  game_id = {game_id}
        """
        print("update query:::", query)
        # 쿼리 실행
        cursor.execute(query)

        
        # 태그 카테고리 제발요
        get_tag_category(app_id, detail_json)

        # TODO: 태그 저장 잊지말고 하자구!!!!!!!!! 


        conn.commit()
        print("update commit", app_id)

    def for_tag(game_id, code_id, list):
        for element in list:
            # 태그 테이블에 존재하지 않는 카테고리라면 태그 테이블이 추가
            tag_id = element['id']
            tag_name = element['description']
            is_exist_query = f"select * from tag where code_id = '{code_id}' and tag_id = {tag_id}"
            cursor.execute(is_exist_query)
            result = cursor.fetchone()
            print("result::::::::::::", result)
            if result is None:
                insert_tag_query = f"insert into tag (code_id, tag_id, tag_name) values ('{code_id}', {tag_id}, '{tag_name}')"
                cursor.execute(insert_tag_query)
                conn.commit()
                print("insert into tag :: ", tag_id, "-" ,tag_name)
                
            # game_tag 테이블에 추가
            try:
                insert_game_tag_query = f"insert into game_tag (game_id, tag_id, code_id) values ({game_id}, {tag_id}, '{code_id}')"
                cursor.execute(insert_game_tag_query)
                conn.commit()
                print("insert into game_tag :: ", game_id, " - ", tag_id, " - ", code_id)
            except mysql.connector.Error as err:
                if isinstance(err, mysql.connector.IntegrityError) and err.errno == 1062:
                    print("for_tag 함수에서 중복 키 오류 발생:", err)
                    continue   
                else:
                    print("for_tag 함수에서 MySQL 커넥터 오류:", err)
            

    def get_tag_category(game_id, detail_json):
        detail_body = detail_json.get(game_id).get("data")
        categories = detail_body.get("categories")
        genres = detail_body.get("genres")
        print("#####categories:::", categories)
        print("#####genres:::", genres)
        
        if categories is not None:  
            for_tag(game_id, 'CAT', categories)

        if genres is not None: 
            for_tag(game_id, 'GEN', genres)
        
    

        

    # [START howto_operator_python]
    # ===============================================================
    # 내가 지정한 태스크
    def get_game_data():

        # # 커넥션 생성
        # conn = mysql.connector.connect(
        #     host=MYSQL_HOST,
        #     port=MYSQL_PORT,
        #     user=MYSQL_USER,
        #     password=MYSQL_PASSWORD,
        #     database=MYSQL_DATABASE
        # )

        # # 커서 생성
        # cursor = conn.cursor()

        # 게임 목록 API 요청
        game_list_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2"
        res = requests.get(game_list_url)
    
        try:
            if res.status_code != 200:
                raise Exception("게임리스트를 받아오는데 실패했습니다.")
            else:
                # 게임 id-name 받아오기
                res_json = res.json()
                applist = res_json.get("applist").get("apps")
                print(applist[0])
                print(len(applist))

                # 받은 리스트 순회하며 상세정보 저장하기
                for idx, app in enumerate(applist):
                    print("app [%d]: " %idx, app)

                    # 게임 상세 정보 API 요청
                    game_detail_url = f'https://store.steampowered.com/api/appdetails?appids={app.get("appid")}&l=koreana'
                    detail_res = requests.get(game_detail_url)

                    if detail_res.status_code != 200:
                        log.info(f"{app.get('appid')}번 게임 상세 정보를 받아오는데 실패했습니다.")
                    else: 
                        app_id = str(app.get("appid"))
                        detail_json = detail_res.json()
                       
                        if not detail_json.get(app_id).get("success") :
                            log.info(f"{app.get('appid')}번 게임 상세 정보가 존재하지 않습니다.")
                            continue

                        else:
                            try:
                                # # 이미 디비에 데이터가 존재할 때 update
                                # is_exist_query = f"select * from game where game_id = {app_id}"
                                # cursor.execute(is_exist_query)
                                # row = cursor.fetchall()
                                # conn.commit()
                                # if row is not None:
                                #     update_game_data(app_id, detail_json)
                                #     continue
                                
                                # 데이터가 존재하지 않을 때 insert
                                print("################### INSERT GAME DATA !!!#######################")
                                detail_body = detail_json.get(app_id).get("data")
                                # game객체에 필요한 값 추출
                                game_id = app_id
                                # print("game_id ", game_id)
                                game_name = detail_body.get("name").replace('"', '')
                                # print("game_name ", game_name)
                                game_short_description = detail_body.get("short_description").replace('"', '')
                                # print("game_short_description ", game_short_description)
                                # 상세설명이 길어서 Blob데이터 형식으로 저장 (인코딩 방식은 utf-8)
                                game_detailed_description = detail_body.get("detailed_description").replace('"', '')
                                # print("game_detailed_description ", game_detailed_description)
                                game_header_img = detail_body.get("header_image")
                                # print("game_header_img ", game_header_img)
                                if not detail_body.get("website"):
                                    log.info("@@@@@@ no website")
                                game_website = detail_body.get("website")
                                # print("game_website: ", game_website)
                                # devloper list를 문자열로
                                if not detail_body.get("developers"):
                                    print("@@@@@@@@ no developer")
                                    game_developer = ""
                                else:
                                    game_developer = ', '.join([element.replace('"', '') for element in detail_body.get("developers")])
                                # print("game_developer: ", game_developer)
                                # publisher list를 문자열로
                                game_publisher = ', '.join([element.replace('"', '') for element in detail_body.get("publishers")])
                                print("game_publisher: ", game_publisher)
                                if not detail_body.get("price_overview") :
                                    log.info("@@@@@@@@@@ no price overview")
                                    game_price_initial = 0
                                    game_price_final = 0
                                    game_discount_percent = 0
                                else:
                                    game_price_initial = detail_body.get("price_overview").get("initial")
                                    # print("game_price_initial ",game_price_initial )
                                    game_price_final = detail_body.get("price_overview").get("final")
                                    # print("game_price_final: ", game_price_final)
                                    game_discount_percent = detail_body.get("price_overview").get("discount_percent")
                                    # print("game_discount_percent: ", game_discount_percent)

                                # 문자열로 받은 release_date를 date type으로 저장
                                game_release_date = detail_body.get("release_date").get("date").replace('"', '')
                                
                                # list를 json 객체로 만든 후 저장
                                screenshots_json = {
                                    "screenshots": detail_body.get("screenshots")
                                } 
                                json_game_screenshot_img = json.dumps(screenshots_json)
                                # print("screenshots_json:::::::::", screenshots_json)
                                game_screenshot_img = json_game_screenshot_img
                                
                                query = f"""
                                insert into game 
                                (
                                game_id
                                , game_name
                                , game_short_description
                                , game_detailed_description
                                , game_header_img
                                , game_website
                                , game_developer
                                , game_publisher
                                , game_price_initial
                                , game_price_final
                                , game_discount_percent
                                , game_release_date
                                , game_screenshot_img
                                , updated_dt
                                ) 
                                values (
                                {game_id}
                                , "{game_name}"
                                , "{game_short_description}"
                                , "{game_detailed_description}"
                                , "{game_header_img}"
                                , "{game_website}"
                                , "{game_developer}"
                                , "{game_publisher}"
                                , {game_price_initial}
                                , {game_price_final}
                                , {game_discount_percent}
                                , "{game_release_date}"
                                , '{game_screenshot_img}'
                                , now()
                                )
                                """
                                print("insert query:::", query)

                                # 쿼리 실행
                                cursor.execute(query)
                                conn.commit()

                                 # 태그 카테고리 제발요
                                get_tag_category(app_id, detail_json)


                                # print("commit", app_id)
                            except mysql.connector.Error as err:
                            #     print("MYSQL CONNECTOR ERROR:::", err)
                            #     continue
                                if isinstance(err, mysql.connector.IntegrityError) and err.errno == 1062:
                                    print("중복 키 오류 발생:", err)
                                    update_game_data(app_id, detail_json)
                                    
                                else:
                                    print("MySQL 커넥터 오류:", err)
        # 중복된 키를 발견했을 때 수행할 작업 추가
        except Exception as e:
            log.info("예외 발생:: ", e)
           
        
        finally:
            cursor.close()
            conn.close()

    run_get_game_data_task = PythonOperator(task_id="get_game_data_task", python_callable=get_game_data)

    #test_task = MysqlOperator()

    run_get_game_data_task
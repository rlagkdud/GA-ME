from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.hooks.mysql_hook import MySqlHook
from steam_reviews import ReviewLoader
import requests
from time import sleep
import nltk
nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer


# MySQL 연결 설정
MYSQL_CONN_ID = 'mysql_default'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 14),
}

MAX_RETRIES = 3

def load_reviews_with_retry(game_id, max_reviews):
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            review_loader = ReviewLoader().set_language('english')
            reviews_en = review_loader.load_from_api(game_id, max_reviews)
        
            return reviews_en
        except requests.exceptions.SSLError as e:
            print(f"SSLError 발생: {e}")
            print("재시도 중...")
            retry_count += 1
            sleep(5)  # 재시도 전에 잠시 대기
    print(f"최대 재시도 횟수({MAX_RETRIES})를 초과하여 리뷰를 가져오지 못했습니다.")
    return None


def get_game_ids(**kwargs):
    mysql_hook = MySqlHook(mysql_conn_id=MYSQL_CONN_ID)
    conn = mysql_hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT game_id FROM game")
    game_ids = [row[0] for row in cursor.fetchall()]
    print(game_ids)
    cursor.close()
    conn.close()
    
    kwargs['ti'].xcom_push(key='game_ids', value=game_ids)
    return game_ids



def process_reviews(**kwargs):
    ti = kwargs['ti']
    game_ids = ti.xcom_pull(task_ids='get_game_ids', key='game_ids')

    analyzer = SentimentIntensityAnalyzer()
    cnt = 0

    for game_id in game_ids:
        mysql_hook = MySqlHook(mysql_conn_id=MYSQL_CONN_ID)
        conn = mysql_hook.get_conn()
        cursor = conn.cursor()

        sql = f"SELECT MAX(review_created_dt) FROM review WHERE game_id = {game_id}"
        cursor.execute(sql)
        latest_review_date = cursor.fetchone()[0]

        max_reviews = 10000
        reviews_en = load_reviews_with_retry(game_id, max_reviews)

        if reviews_en is not None:
            print("리뷰를 성공적으로 불러왔습니다.")
            print('game_id =', game_id)
        else:
            print("리뷰를 불러오지 못했습니다.")
            continue

        if not reviews_en.data['reviews'] or len(reviews_en.data['reviews']) < 1:
            print(f"No reviews found for game ID: {game_id}")
            continue
        else:
            print('리뷰길이', len(reviews_en.data['reviews']))
            
            

        reviews_review = reviews_en.data['reviews']
        sorted_reviews = sorted(reviews_review, key=lambda x: x['timestamp_updated'], reverse=True) # updated 기준으로 정렬

        
        cursor.execute(f"SELECT game_review_like_cnt, game_review_unlike_cnt, game_review_is_use_cnt FROM game_score_info WHERE game_id = '{game_id}'")
        result = cursor.fetchone()

        
        game_review_cnt = reviews_en.data['query_summary']['total_reviews']
        if result:
            game_review_like_cnt = result[0]
            game_review_unlike_cnt = result[1]
        else:
            game_review_like_cnt = 0
            game_review_unlike_cnt = 0
        updated_dt = datetime.now().date()


        # 그 뭐시냐 댓글 단 순간 평균 플레이 타임
        # sorted_reviews에서 각 review의 'author'의 'playtime_at_review' 값을 추출하여 리스트로 만듭니다.
        playtimes = [review_['author'].get('playtime_at_review', 0) for review_ in sorted_reviews]

        # 평균 playtime_at_review 계산
        average_playtime = sum(playtimes) / len(playtimes)

        # 평균 playtime_at_review의 10% 계산
        threshold = average_playtime * 0.1
        for review in sorted_reviews:
            cnt += 1
            print('덱이 진행한 리뷰 개수', cnt)
            # 리뷰의 timestamp_created 값
            timestamp_created = review['timestamp_updated'] ## 컬럼 updated로 바꿔 줘야할 듯 ? db 날리고
            # UNIX timestamp를 datetime -> date 객체로 변환
            review_datetime = datetime.fromtimestamp(timestamp_created)
            review_created_dt = review_datetime.date()
            
            
            # game_id, review_id, review_content, review_is_good, review_created_dt, 
            # review_playtime_at, review_playtime_total, review_playtime_recent
            # review_is_use, updated_dttm
            game_id = int(game_id)
            print(type(review['recommendationid']), review['recommendationid'])
            review_id = int(review['recommendationid'])
            review_content = review['review']
            review_is_good = 'NULL'


            review_playtime_at = review['author'].get('playtime_at_review', 0)
            review_playtime_total = review['author'].get('playtime_forever', 0)
            review_playtime_recent = review['author'].get('playtime_last_two_weeks', 0)
            review_is_use = False
            updated_dttm = datetime.now()
            
            if review_playtime_at <= threshold:
                # 평균 플탐에 비해 10%이하인 댓글 배제 
                continue

            if latest_review_date is None or review_created_dt > latest_review_date:
                print('시간시간', review_created_dt, latest_review_date)
                # 리뷰 저장 코드 작성
                scores = analyzer.polarity_scores(review_content)
                # {'neg': 0.0, 'neu': 0.308, 'pos': 0.692, 'compound': 0.6249}
                compound_score = scores['compound']
                if compound_score >= 0:
                    print("긍정적인 감정입니다.")
                    review_is_good = True
                    game_review_like_cnt += 1
                else:
                    print("부정적인 감정입니다.")
                    review_is_good = False
                    game_review_unlike_cnt += 1
                
                # 1.3배 이상 늘어난 현재 플탐인 경우 True로 바꿔줌
                if review_playtime_total >= 1.3 * review_playtime_at:
                    print("신규 댓글 + 플탐 OOOOOOO")
                    review_is_use = True
                else:
                    print("신규 댓글 + 플탐 XXXX")
                    review_is_use = False
                

                # print(game_id, review_id, review_content, review_is_good, review_created_dt, review_playtime_at, review_playtime_total, review_playtime_recent, review_is_use, updated_dttm)
                sql = """INSERT INTO review (game_id, review_id, review_content, review_is_good, review_created_dt, review_playtime_at, review_playtime_total, review_playtime_recent, review_is_use, updated_dttm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (game_id, review_id, review_content, review_is_good, review_created_dt, review_playtime_at, review_playtime_total, review_playtime_recent, review_is_use, updated_dttm))
                
                conn.commit()

            else:
                # 1.3배 이상 늘어난 현재 플탐인 경우 True로 바꿔줌
                if review_playtime_total >= 1.3 * review_playtime_at:
                    print("존재하는 댓글 + 플탐 해당 OOOOOOOO")
                    review_is_use = True
                    


                    sql = """UPDATE review 
                            SET review_is_use = %s, updated_dttm = %s
                            WHERE game_id = %s AND review_id = %s"""
                    cursor.execute(sql, (review_is_use, updated_dttm, game_id, review_id))
                    
                    conn.commit()

                else:
                    print("존재하는 댓글 + 플탐 해당 X")
                    review_is_use = False

        try:
            # print(game_id, review_content, review_is_good, review_created_dt, review_playtime_at, review_playtime_total, review_playtime_recent, review_is_use, updated_dttm)
            sql = """
                INSERT INTO game_score_info (game_id, game_review_cnt, game_review_like_cnt, game_review_unlike_cnt, updated_dt) 
                VALUES (%s, %s, %s, %s, %s) 
                ON DUPLICATE KEY UPDATE 
                    game_review_cnt = VALUES(game_review_cnt), 
                    game_review_like_cnt = VALUES(game_review_like_cnt), 
                    game_review_unlike_cnt = VALUES(game_review_unlike_cnt), 
                    updated_dt = VALUES(updated_dt)
            """
            cursor.execute(sql, (game_id, game_review_cnt, game_review_like_cnt, game_review_unlike_cnt, updated_dt))
            conn.commit()
            print("Review 데이터가 성공적으로 저장되었습니다.")
        except Exception as e:
            conn.rollback()
            print("Review 데이터 저장 중 오류 발생:", e)
        finally:
            cursor.close()
            conn.close()
            
with DAG('dags_reduce_weight', 
         default_args=default_args, 
         schedule_interval=None, 
         tags=["mysql","weight",'weekly'],
         catchup=False) as dag:

    get_game_ids_task = PythonOperator(
        task_id='get_game_ids',
        python_callable=get_game_ids,
        provide_context=True,
        dag=dag
    )

    process_reviews_task = PythonOperator(
        task_id='process_reviews',
        python_callable=process_reviews,
        provide_context=True,
        dag=dag
    )

    get_game_ids_task >> process_reviews_task

# setup_data.py
"""
users.csv 컬럼 구조:
- user_id: 고유 사용자 ID (문자열, 자동 생성)
- username: 사용자명 (화면에 표시, 중복 불가)
- password: 비밀번호 (평문 저장)
- created_at: 가입일 (YYYY-MM-DD 형식)
"""

# 예시 데이터
"""
user_id,username,password,created_at
user_001,김개발,pass123,2024-08-11
user_002,이데이터,mypass,2024-08-11
"""


import pandas as pd
import os

def create_data_folder():
    """data 폴더와 초기 CSV 파일들 생성"""

    # data 폴더 생성
    if not os.path.exists('data'):
        os.makedirs('data')
        print("📁 data 폴더가 생성되었습니다.")

    # 빈 users.csv 파일 생성
    if not os.path.exists('data/users.csv'):
        users_columns = ['user_id', 'username', 'password', 'created_at']
        empty_users = pd.DataFrame(columns=users_columns)
        empty_users.to_csv('data/users.csv', index=False, encoding='utf-8')
        print("📄 data/users.csv 파일이 생성되었습니다.")

    # 빈 posts.csv 파일 생성 (3단계용)
    if not os.path.exists('data/posts.csv'):
        posts_columns = ['post_id', 'user_id', 'content', 'timestamp']
        empty_posts = pd.DataFrame(columns=posts_columns)
        empty_posts.to_csv('data/posts.csv', index=False, encoding='utf-8')
        print("📄 data/posts.csv 파일이 생성되었습니다.")

    # 빈 likes.csv 파일 생성 (3단계용)
    if not os.path.exists('data/likes.csv'):
        likes_columns = ['like_id', 'user_id', 'post_id', 'timestamp']
        empty_likes = pd.DataFrame(columns=likes_columns)
        empty_likes.to_csv('data/likes.csv', index=False, encoding='utf-8')
        print("📄 data/likes.csv 파일이 생성되었습니다.")

    print("✅ 초기 설정이 완료되었습니다!")

if __name__ == "__main__":
    create_data_folder()


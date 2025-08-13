# user_manager.py
import pandas as pd
import os
from datetime import datetime
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "error.log")
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s")

class UserManager:
    def __init__(self):
        self.csv_path = os.path.join(BASE_DIR, 'data', 'users.csv')
        self.ensure_csv_exists()

    def ensure_csv_exists(self):
        try:
            if not os.path.exists(self.csv_path):
                os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
                pd.DataFrame(columns=['user_id', 'username', 'password', 'created_at']).to_csv(self.csv_path, index=False, encoding='utf-8')
        except Exception as e:
            logging.error(f"CSV 생성 오류: {e}")

    def load_users(self):
        try:
            return pd.read_csv(self.csv_path, encoding='utf-8')
        except Exception as e:
            logging.error(f"CSV 로드 오류: {e}")
            return pd.DataFrame(columns=['user_id', 'username', 'password', 'created_at'])

    def save_users(self, df):
        try:
            df.to_csv(self.csv_path, index=False, encoding='utf-8')
        except Exception as e:
            logging.error(f"CSV 저장 오류: {e}")

    def create_user(self, username, password):
        username, password = username.strip(), password.strip()
        users_df = self.load_users()
        if username in users_df['username'].values:
            return False, "이미 존재하는 사용자명입니다."

        new_user_id = f"user_{len(users_df) + 1:03d}"
        new_user = {
            'user_id': new_user_id,
            'username': username,
            'password': password,
            'created_at': datetime.now().strftime('%Y-%m-%d')
        }
        users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
        self.save_users(users_df)
        return True, "회원가입이 완료되었습니다!"

    def login_user(self, username, password):
        username, password = username.strip(), password.strip()
        users_df = self.load_users()
        user_data = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
        if len(user_data) == 1:
            return True, user_data.iloc[0].to_dict()
        return False, None

    def get_user_count(self):
        return len(self.load_users())

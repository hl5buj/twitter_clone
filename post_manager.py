# post_manager.py
import pandas as pd
import os
from datetime import datetime
import uuid

DATA_DIR = os.path.abspath("data")

class PostManager:
    def __init__(self):
        self.posts_path = os.path.join(DATA_DIR, 'posts.csv')
        self.likes_path = os.path.join(DATA_DIR, 'likes.csv')
        self.setup_files()

    def setup_files(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(self.posts_path):
            pd.DataFrame(columns=['post_id', 'user_id', 'content', 'timestamp']).to_csv(self.posts_path, index=False, encoding='utf-8')
        if not os.path.exists(self.likes_path):
            pd.DataFrame(columns=['like_id', 'user_id', 'post_id', 'timestamp']).to_csv(self.likes_path, index=False, encoding='utf-8')

    def load_posts(self):
        return pd.read_csv(self.posts_path, encoding='utf-8')

    def load_likes(self):
        return pd.read_csv(self.likes_path, encoding='utf-8')

    def save_posts(self, df):
        df.to_csv(self.posts_path, index=False, encoding='utf-8')

    def save_likes(self, df):
        df.to_csv(self.likes_path, index=False, encoding='utf-8')

    def create_post(self, user_id, content):
        posts_df = self.load_posts()
        new_post = {
            'post_id': str(uuid.uuid4())[:8],
            'user_id': user_id.strip(),
            'content': content.strip(),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        posts_df = pd.concat([pd.DataFrame([new_post]), posts_df], ignore_index=True)
        self.save_posts(posts_df)
        return True

    def get_posts_with_likes(self):
        posts_df = self.load_posts()
        likes_df = self.load_likes()
        if posts_df.empty:
            return pd.DataFrame()
        if not likes_df.empty:
            like_counts = likes_df.groupby('post_id').size().reset_index(name='like_count')
            result = posts_df.merge(like_counts, on='post_id', how='left')
        else:
            result = posts_df.copy()
            result['like_count'] = 0
        result['like_count'] = result['like_count'].fillna(0).astype(int)
        return result

    def toggle_like(self, user_id, post_id):
        likes_df = self.load_likes()
        existing = likes_df[(likes_df['user_id'] == user_id) & (likes_df['post_id'] == post_id)]
        if not existing.empty:
            likes_df = likes_df[~((likes_df['user_id'] == user_id) & (likes_df['post_id'] == post_id))]
            self.save_likes(likes_df)
            return False
        else:
            new_like = {
                'like_id': str(uuid.uuid4())[:8],
                'user_id': user_id.strip(),
                'post_id': post_id.strip(),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            likes_df = pd.concat([likes_df, pd.DataFrame([new_like])], ignore_index=True)
            self.save_likes(likes_df)
            return True

    def is_liked_by_user(self, user_id, post_id):
        likes_df = self.load_likes()
        return not likes_df[(likes_df['user_id'] == user_id) & (likes_df['post_id'] == post_id)].empty

    def delete_post(self, post_id, user_id):
        posts_df = self.load_posts()
        post = posts_df[(posts_df['post_id'] == post_id) & (posts_df['user_id'] == user_id)]
        if post.empty:
            return False
        posts_df = posts_df[posts_df['post_id'] != post_id]
        self.save_posts(posts_df)
        likes_df = self.load_likes()
        likes_df = likes_df[likes_df['post_id'] != post_id]
        self.save_likes(likes_df)
        return True

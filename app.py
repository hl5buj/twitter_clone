# app.py
import streamlit as st
import os
import logging
import traceback  # 디버그 모드에서 상세 에러 출력
from auth import show_auth_page, logout_user
from user_manager import UserManager
from post_manager import PostManager

# -------------------------
# 개발/디버그 모드 플래그
# -------------------------
DEBUG_MODE = True

# 기본 경로 및 로깅 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "error.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG if DEBUG_MODE else logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# 페이지 설정
st.set_page_config(
    page_title="프롬프트 트위터",
    page_icon="🐦",
    layout="wide"
)

# -------------------------
# 페이지 함수들
# -------------------------
def show_home_page(current_user, post_mgr, user_mgr):
    """홈 화면 - 실제 게시글 목록"""
    st.header("📝 최근 프롬프트")

    try:
        posts_with_likes = post_mgr.get_posts_with_likes()
    except Exception as e:
        logging.error(f"get_posts_with_likes 오류: {e}")
        if DEBUG_MODE:
            st.error(traceback.format_exc())
        else:
            st.error("게시글을 불러오는 중 오류가 발생했습니다.")
        posts_with_likes = []

    if not posts_with_likes or len(posts_with_likes) == 0:
        st.info("📝 아직 작성된 프롬프트가 없습니다. 첫 번째 프롬프트를 작성해보세요!")
        if st.button("✍️ 글쓰기로 이동"):
            st.session_state.menu = "✍️ 글쓰기"
            st.rerun()
        return

    try:
        users_df = user_mgr.load_users()
    except Exception as e:
        logging.error(f"users load 오류: {e}")
        if DEBUG_MODE:
            st.error(traceback.format_exc())
        users_df = None

    if users_df is None or users_df.empty:
        posts_display = posts_with_likes.copy()
        posts_display['username'] = "알 수 없음"
    else:
        posts_display = posts_with_likes.merge(
            users_df[['user_id', 'username']],
            on='user_id',
            how='left'
        )
        posts_display['username'] = posts_display['username'].fillna("알 수 없음")

    for idx, post in posts_display.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 11])
            with col1:
                st.image("https://images.unsplash.com/photo-1743449661678-c22cd73b338a?w=500&auto=format&fit=crop&q=60", width=50)

            with col2:
                col_info, col_action = st.columns([8, 4])
                with col_info:
                    ts = str(post.get('timestamp', ''))
                    time_str = ts.split(' ')[1][:5] if ' ' in ts else ts[:16]
                    st.markdown(f"**{post.get('username', '알 수 없음')}** • {time_str}")

                with col_action:
                    try:
                        if post['user_id'] == current_user['user_id']:
                            if st.button("🗑️", key=f"del_{post['post_id']}", help="삭제"):
                                if post_mgr.delete_post(post['post_id'], current_user['user_id']):
                                    st.success("게시글이 삭제되었습니다!")
                                    st.rerun()
                    except Exception as e:
                        logging.error(f"삭제 버튼 처리 오류: {e}")
                        if DEBUG_MODE:
                            st.error(traceback.format_exc())

                st.markdown(post.get('content', ''))

                try:
                    is_liked = post_mgr.is_liked_by_user(current_user['user_id'], post['post_id'])
                except Exception as e:
                    logging.error(f"is_liked_by_user 오류: {e}")
                    if DEBUG_MODE:
                        st.error(traceback.format_exc())
                    is_liked = False

                like_emoji = "❤️" if is_liked else "🤍"
                like_count = int(post.get('like_count', 0))

                try:
                    if st.button(f"{like_emoji} {like_count}", key=f"like_{post['post_id']}"):
                        liked = post_mgr.toggle_like(current_user['user_id'], post['post_id'])
                        st.success("좋아요!" if liked else "좋아요 취소")
                        st.rerun()
                except Exception as e:
                    logging.error(f"좋아요 처리 오류: {e}")
                    if DEBUG_MODE:
                        st.error(traceback.format_exc())
        st.divider()

def show_write_page(current_user, post_mgr):
    st.header("✍️ 새 프롬프트 작성")
    st.markdown("💡 **다른 사람들이 실제로 사용할 수 있는 프롬프트를 공유해보세요!**")

    with st.form("write_form", clear_on_submit=True):
        content = st.text_area(
            "프롬프트 내용",
            placeholder="어떤 상황에서 사용하는 프롬프트인지...",
            height=200
        )
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            submitted = st.form_submit_button("🚀 게시하기", type="primary")

        if submitted:
            if content.strip():
                try:
                    success = post_mgr.create_post(current_user['user_id'], content.strip())
                    if success:
                        st.success("프롬프트가 게시되었습니다! 🎉")
                        st.balloons()
                        import time
                        time.sleep(1.5)
                        st.session_state.menu = "🏠 홈"
                        st.rerun()
                    else:
                        st.error("게시 중 오류가 발생했습니다.")
                except Exception as e:
                    logging.error(f"create_post 오류: {e}")
                    if DEBUG_MODE:
                        st.error(traceback.format_exc())
                    st.error("게시 중 오류가 발생했습니다.")
            else:
                st.error("내용을 입력해주세요!")

def show_profile_page(current_user, post_mgr, user_mgr):
    st.header("👤 내 프로필")
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image("https://images.unsplash.com/photo-1743449661678-c22cd73b338a?w=500&auto=format&fit=crop&q=60", width=100)

    with col2:
        st.markdown(f"### {current_user.get('username', '알 수 없음')}")
        st.markdown(f"**가입일:** {current_user.get('created_at', '')}")

    st.divider()

    posts_with_likes = post_mgr.get_posts_with_likes()
    my_posts = posts_with_likes[posts_with_likes['user_id'] == current_user['user_id']]

    if len(my_posts) > 0:
        st.info(f"총 {len(my_posts)}개의 프롬프트를 작성했습니다.")
        for idx, post in my_posts.iterrows():
            with st.container():
                col1, col2 = st.columns([8, 4])
                with col1:
                    preview = post['content'][:100] + "..." if len(post['content']) > 100 else post['content']
                    st.markdown(f"**{preview}**")
                    st.caption(f"작성: {post['timestamp']} • 좋아요: {int(post['like_count'])}개")
                with col2:
                    if st.button("🗑️ 삭제", key=f"profile_del_{post['post_id']}"):
                        if post_mgr.delete_post(post['post_id'], current_user['user_id']):
                            st.success("삭제되었습니다!")
                            st.rerun()
            st.divider()
    else:
        st.info("📝 아직 작성한 프롬프트가 없습니다.")
        if st.button("✍️ 첫 프롬프트 작성하기"):
            st.session_state.menu = "✍️ 글쓰기"
            st.rerun()

# -------------------------
# 매니저 초기화
# -------------------------
@st.cache_resource
def init_managers():
    return UserManager(), PostManager()

user_mgr, post_mgr = init_managers()

# -------------------------
# Session State 초기화
# -------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'menu' not in st.session_state:
    st.session_state.menu = "🏠 홈"

# -------------------------
# 앱 실행
# -------------------------
if not st.session_state.logged_in:
    show_auth_page()
else:
    current_user = st.session_state.get('current_user')
    if not current_user or 'user_id' not in current_user:
        st.warning("세션 정보가 유실되어 로그아웃합니다. 다시 로그인해주세요.")
        logout_user()
    else:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.title("🐦 프롬프트 트위터")
            st.markdown(f"**{current_user.get('username', '사용자')}님 환영합니다!** ✨")
        with col2:
            if st.button("🚪 로그아웃"):
                logout_user()

        menu = st.sidebar.selectbox(
            "📋 메뉴",
            ["🏠 홈", "✍️ 글쓰기", "👤 프로필"],
            index=["🏠 홈", "✍️ 글쓰기", "👤 프로필"].index(st.session_state.menu)
        )

        if menu != st.session_state.menu:
            st.session_state.menu = menu
            st.rerun()

        try:
            if menu == "🏠 홈":
                show_home_page(current_user, post_mgr, user_mgr)
            elif menu == "✍️ 글쓰기":
                show_write_page(current_user, post_mgr)
            elif menu == "👤 프로필":
                show_profile_page(current_user, post_mgr, user_mgr)
        except Exception as e:
            logging.error(f"페이지 렌더링 오류: {e}")
            if DEBUG_MODE:
                st.error(traceback.format_exc())
            else:
                st.error("페이지를 불러오는 중 오류가 발생했습니다.")


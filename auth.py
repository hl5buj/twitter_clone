# auth.py
import streamlit as st
import pandas as pd
import os
import logging
import traceback
from user_manager import UserManager

# 기본 경로 및 로깅 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "error.log")
logging.basicConfig(filename=LOG_FILE, level=logging.ERROR,
                    format="%(asctime)s [%(levelname)s] %(message)s")

# 디버그 모드 (True면 화면에 바로 에러 출력)
DEBUG_MODE = True

user_mgr = UserManager()

def show_auth_page():
    st.header("🔐 로그인 / 회원가입")

    tab_login, tab_register = st.tabs(["로그인", "회원가입"])

    with tab_login:
        login_id = st.text_input("로그인 ID", key="login_id")
        password = st.text_input("비밀번호", type="password", key="login_pw")
        if st.button("🚀 로그인"):
            try:
                if user_mgr.authenticate(login_id, password):
                    st.session_state.logged_in = True
                    st.session_state.current_user = user_mgr.get_user_by_login_id(login_id)
                    st.success(f"환영합니다, {st.session_state.current_user['username']}님! 🎉")
                    st.rerun()
                else:
                    st.error("로그인 실패: ID 또는 비밀번호를 확인해주세요.")
            except Exception as e:
                logging.error(f"로그인 처리 오류: {e}\n{traceback.format_exc()}")
                if DEBUG_MODE:
                    st.error(f"로그인 처리 중 오류 발생: {e}")
                    st.code(traceback.format_exc(), language="python")

    with tab_register:
        reg_id = st.text_input("새 로그인 ID", key="reg_id")
        reg_username = st.text_input("사용자 이름", key="reg_username")
        reg_pw = st.text_input("비밀번호", type="password", key="reg_pw")
        reg_pw_confirm = st.text_input("비밀번호 확인", type="password", key="reg_pw_confirm")
        if st.button("📝 회원가입"):
            try:
                if not reg_id.strip() or not reg_username.strip():
                    st.error("ID와 사용자 이름은 필수입니다.")
                elif reg_pw != reg_pw_confirm:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    success = user_mgr.add_user(reg_id, reg_username, reg_pw)
                    if success:
                        st.success("회원가입이 완료되었습니다! 로그인 해주세요.")
                    else:
                        st.error("이미 존재하는 ID입니다.")
            except Exception as e:
                logging.error(f"회원가입 처리 오류: {e}\n{traceback.format_exc()}")
                if DEBUG_MODE:
                    st.error(f"회원가입 처리 중 오류 발생: {e}")
                    st.code(traceback.format_exc(), language="python")


def logout_user():
    try:
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.success("로그아웃되었습니다.")
        st.rerun()
    except Exception as e:
        logging.error(f"로그아웃 처리 오류: {e}\n{traceback.format_exc()}")
        if DEBUG_MODE:
            st.error(f"로그아웃 처리 중 오류 발생: {e}")
            st.code(traceback.format_exc(), language="python")


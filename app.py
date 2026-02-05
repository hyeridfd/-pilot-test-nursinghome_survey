import streamlit as st
import os
import sys

from supabase import create_client, Client
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# surveys 모듈 import
from surveys.basic_survey import show_basic_survey
from surveys.nutrition_survey import show_nutrition_survey
from surveys.satisfaction_survey import show_satisfaction_survey

#########
st.title("🔍 Supabase Storage 테스트")

# Supabase 연결
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# 파일 업로드 테스트
uploaded_file = st.file_uploader("테스트 이미지 업로드", type=['jpg', 'jpeg', 'png'])

if uploaded_file and st.button("업로드 테스트"):
    try:
        # 파일 읽기
        file_bytes = uploaded_file.read()
        st.write(f"파일 크기: {len(file_bytes)} bytes")
        
        # Storage에 업로드
        file_name = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        response = supabase.storage.from_('nutrition-photos').upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": uploaded_file.type}
        )
        
        st.success(f"✅ 업로드 성공! 파일명: {file_name}")
        
        # URL 가져오기
        url = supabase.storage.from_('nutrition-photos').get_public_url(file_name)
        st.write(f"URL: {url}")
        st.image(url)
        
    except Exception as e:
        st.error(f"❌ 업로드 실패: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
#####

KST = ZoneInfo('Asia/Seoul')

def get_kst_now():
    """현재 한국 시간 반환 (ISO 8601 형식)"""
    return datetime.now(KST).isoformat()
    
# Supabase 초기화
@st.cache_resource
def init_supabase():
    url = None
    key = None
    
    # Streamlit secrets 우선 확인
    if hasattr(st, 'secrets') and 'SUPABASE_URL' in st.secrets:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    else:
        # 환경 변수에서 가져오기
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        st.error("⚠️ Supabase 설정이 필요합니다. Streamlit Cloud의 Secrets 또는 로컬 .env 파일을 확인해주세요.")
        st.stop()
    
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"❌ Supabase 연결 실패: {str(e)}")
    st.info("💡 Streamlit Cloud Settings → Secrets에 SUPABASE_URL과 SUPABASE_KEY를 추가했는지 확인해주세요.")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="요양원 건강 및 블루푸드 설문조사",
    page_icon="📋",
    layout="wide"
)

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'elderly_id' not in st.session_state:
    st.session_state.elderly_id = None
if 'surveyor_id' not in st.session_state:
    st.session_state.surveyor_id = None
if 'nursing_home_id' not in st.session_state:
    st.session_state.nursing_home_id = None
if 'current_survey' not in st.session_state:
    st.session_state.current_survey = None

# 로그인 확인 함수
def verify_login(nursing_home_id, surveyor_id, elderly_id):
    try:
        # 요양원 확인
        nh_response = supabase.table('nursing_homes').select('*').eq('id', nursing_home_id).execute()
        if not nh_response.data:
            return False, "요양원 ID가 존재하지 않습니다."
        
        # 조사원 확인
        surveyor_response = supabase.table('surveyors').select('*').eq('id', surveyor_id).eq('nursing_home_id', nursing_home_id).execute()
        if not surveyor_response.data:
            return False, "조사원 ID가 존재하지 않거나 해당 요양원에 속하지 않습니다."
        
        # 어르신 확인
        elderly_response = supabase.table('elderly_residents').select('*').eq('id', elderly_id).eq('nursing_home_id', nursing_home_id).execute()
        if not elderly_response.data:
            return False, "어르신 ID가 존재하지 않거나 해당 요양원에 속하지 않습니다."
        
        return True, "로그인 성공"
    except Exception as e:
        return False, f"오류 발생: {str(e)}"

# 설문 진행 상황 조회/생성
def get_or_create_survey_progress(elderly_id, surveyor_id, nursing_home_id):
    try:
        # 기존 진행 상황 조회
        response = supabase.table('survey_progress').select('*').eq('elderly_id', elderly_id).execute()
        
        if response.data:
            return response.data[0]
        else:
            # 없으면 생성
            new_progress = {
                'elderly_id': elderly_id,
                'surveyor_id': surveyor_id,
                'nursing_home_id': nursing_home_id,
                'basic_survey_completed': False,
                'nutrition_survey_completed': False,
                'satisfaction_survey_completed': False,
                'all_surveys_completed': False
            }
            response = supabase.table('survey_progress').insert(new_progress).execute()
            return response.data[0]
    except Exception as e:
        st.error(f"설문 진행 상황 조회 오류: {str(e)}")
        return None

# 로그인 페이지
def login_page():
    st.title("📋 요양원 건강 및 블루푸드 설문조사")
    st.markdown("---")
    
    # 일반 사용자 로그인
    st.header("설문 조사 로그인")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nursing_home_id = st.text_input("요양원 ID", key="nh_id")
    with col2:
        surveyor_id = st.text_input("조사원 ID", key="sv_id")
    with col3:
        elderly_id = st.text_input("어르신 ID", key="el_id")
    
    if st.button("로그인", type="primary"):
        if nursing_home_id and surveyor_id and elderly_id:
            success, message = verify_login(nursing_home_id, surveyor_id, elderly_id)
            if success:
                st.session_state.logged_in = True
                st.session_state.nursing_home_id = nursing_home_id
                st.session_state.surveyor_id = surveyor_id
                st.session_state.elderly_id = elderly_id
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("모든 ID를 입력해주세요.")
    
    st.markdown("---")
    
    # 관리자 로그인
    with st.expander("관리자 로그인"):
        admin_password = st.text_input("관리자 비밀번호", type="password", key="admin_pw")
        if st.button("관리자 로그인"):
            # Streamlit secrets 우선 확인
            if hasattr(st, 'secrets') and 'ADMIN_PASSWORD' in st.secrets:
                correct_password = st.secrets["ADMIN_PASSWORD"]
            else:
                correct_password = os.getenv("ADMIN_PASSWORD", "admin123")
            
            if admin_password == correct_password:
                st.session_state.is_admin = True
                st.session_state.logged_in = True
                st.success("관리자 로그인 성공!")
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")

# 설문 선택 대시보드
def survey_dashboard():
    st.title("📋 설문 선택")
    
    # 상단 정보 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"🏥 요양원 ID: {st.session_state.nursing_home_id}")
    with col2:
        st.info(f"👤 조사원 ID: {st.session_state.surveyor_id}")
    with col3:
        st.info(f"👴 어르신 ID: {st.session_state.elderly_id}")
    
    st.markdown("---")
    
    # 설문 진행 상황 조회
    progress = get_or_create_survey_progress(
        st.session_state.elderly_id,
        st.session_state.surveyor_id,
        st.session_state.nursing_home_id
    )
    
    if not progress:
        st.error("설문 진행 상황을 불러올 수 없습니다.")
        return
    
    # 설문 상태 표시
    st.subheader("📊 설문 진행 현황")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = "✅ 완료" if progress.get('basic_survey_completed') else "⏳ 미완료"
        st.metric("1. 기초 조사표", status)
    with col2:
        status = "✅ 완료" if progress.get('nutrition_survey_completed') else "⏳ 미완료"
        st.metric("2. 영양 조사표", status)
    with col3:
        status = "✅ 완료" if progress.get('satisfaction_survey_completed') else "⏳ 미완료"
        st.metric("3. 만족도 및 선호도 조사표", status)
    
    st.markdown("---")
    
    # 전체 완료 상태
    if progress.get('all_surveys_completed'):
        st.success("🎉 모든 설문이 완료되었습니다!")
    
    # 설문 선택 버튼
    st.subheader("설문 선택")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 1. 기초 조사표", use_container_width=True, type="primary"):
            st.session_state.current_survey = "basic"
            st.rerun()
    
    with col2:
        if st.button("🥗 2. 영양 조사표", use_container_width=True, type="primary"):
            st.session_state.current_survey = "nutrition"
            st.rerun()
    
    with col3:
        if st.button("😊 3. 만족도 및 선호도 조사표", use_container_width=True, type="primary"):
            st.session_state.current_survey = "satisfaction"
            st.rerun()
    
    st.markdown("---")
    
    # 로그아웃 버튼
    if st.button("로그아웃"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# 관리자 대시보드
def admin_dashboard():
    st.title("🔐 관리자 대시보드")
    
    tabs = st.tabs(["요양원 관리", "조사원 관리", "어르신 관리", "설문 진행 현황"])
    
    # 요양원 관리
    with tabs[0]:
        st.subheader("🏥 요양원 목록")
        try:
            response = supabase.table('nursing_homes').select('*').execute()
            if response.data:
                df = pd.DataFrame(response.data)
                st.dataframe(df, use_container_width=True)
                st.metric("전체 요양원 수", len(df))
            else:
                st.info("등록된 요양원이 없습니다.")
        except Exception as e:
            st.error(f"데이터 조회 오류: {str(e)}")
    
    # 조사원 관리
    with tabs[1]:
        st.subheader("👤 조사원 목록")
        try:
            response = supabase.table('surveyors').select('*').execute()
            if response.data:
                df = pd.DataFrame(response.data)
                st.dataframe(df, use_container_width=True)
                st.metric("전체 조사원 수", len(df))
            else:
                st.info("등록된 조사원이 없습니다.")
        except Exception as e:
            st.error(f"데이터 조회 오류: {str(e)}")
    
    # 어르신 관리
    with tabs[2]:
        st.subheader("👴 어르신 목록")
        try:
            response = supabase.table('elderly_residents').select('*').execute()
            if response.data:
                df = pd.DataFrame(response.data)
                st.dataframe(df, use_container_width=True)
                st.metric("전체 어르신 수", len(df))
            else:
                st.info("등록된 어르신이 없습니다.")
        except Exception as e:
            st.error(f"데이터 조회 오류: {str(e)}")
    
    # 설문 진행 현황
    with tabs[3]:
        st.subheader("📊 설문 진행 현황")
        try:
            response = supabase.table('survey_progress').select('*').execute()
            if response.data:
                df = pd.DataFrame(response.data)
                st.dataframe(df, use_container_width=True)
                
                # 통계
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("전체 응답자", len(df))
                with col2:
                    completed = df['basic_survey_completed'].sum()
                    st.metric("기초 조사표 완료", f"{completed} ({completed/len(df)*100:.1f}%)")
                with col3:
                    completed = df['nutrition_survey_completed'].sum()
                    st.metric("영양 조사표 완료", f"{completed} ({completed/len(df)*100:.1f}%)")
                with col4:
                    completed = df['satisfaction_survey_completed'].sum()
                    st.metric("만족도 조사표 완료", f"{completed} ({completed/len(df)*100:.1f}%)")
                
                # 전체 완료율
                all_completed = df['all_surveys_completed'].sum()
                st.metric("전체 완료", f"{all_completed} ({all_completed/len(df)*100:.1f}%)")
            else:
                st.info("설문 진행 현황이 없습니다.")
        except Exception as e:
            st.error(f"데이터 조회 오류: {str(e)}")
    
    st.markdown("---")
    if st.button("로그아웃"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# 메인 앱
def main():
    # 로그인 안 된 경우
    if not st.session_state.logged_in:
        login_page()
        return
    
    # 관리자인 경우
    if st.session_state.is_admin:
        admin_dashboard()
        return
    
    # 일반 사용자인 경우
    if st.session_state.current_survey is None:
        survey_dashboard()
    elif st.session_state.current_survey == "basic":
        show_basic_survey(supabase, st.session_state.elderly_id, 
                         st.session_state.surveyor_id, st.session_state.nursing_home_id)
    elif st.session_state.current_survey == "nutrition":
        show_nutrition_survey(supabase, st.session_state.elderly_id,
                            st.session_state.surveyor_id, st.session_state.nursing_home_id)
    elif st.session_state.current_survey == "satisfaction":
        show_satisfaction_survey(supabase, st.session_state.elderly_id,
                               st.session_state.surveyor_id, st.session_state.nursing_home_id)

if __name__ == "__main__":
    main()

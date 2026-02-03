import streamlit as st
import json
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo('Asia/Seoul')

def get_kst_now():
    """현재 한국 시간 반환"""
    return datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')

def show_nutrition_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    st.title("🥗 2. 영양 조사표")
    
    # 진행 상태 초기화
    if 'nutrition_page' not in st.session_state:
        st.session_state.nutrition_page = 1
    
    # 기존 데이터 불러오기
    if 'nutrition_data' not in st.session_state:
        try:
            response = supabase.table('nutrition_survey').select('*').eq('elderly_id', elderly_id).execute()
            if response.data:
                st.session_state.nutrition_data = response.data[0]
            else:
                st.session_state.nutrition_data = {}
        except:
            st.session_state.nutrition_data = {}
    
    # 페이지 진행 표시 (3페이지로 변경)
    total_pages = 3
    st.progress(st.session_state.nutrition_page / total_pages)
    st.caption(f"페이지 {st.session_state.nutrition_page} / {total_pages}")
    
    # 페이지별 내용
    if st.session_state.nutrition_page == 1:
        show_page1_meal_portions()  # 5일 식사량 조사
    elif st.session_state.nutrition_page == 2:
        show_page2_plate_waste_visual()  # 5일 잔반량 조사 (목측법)
    elif st.session_state.nutrition_page == 3:
        show_page3_submit(supabase, elderly_id, surveyor_id, nursing_home_id)  # 제출

def create_visual_guide():
    """목측법 원형 가이드 생성"""
    st.markdown("""
    <style>
    .visual-guide {
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .visual-item {
        text-align: center;
        flex: 1;
    }
    .visual-item svg {
        width: 80px;
        height: 80px;
    }
    .visual-label {
        margin-top: 10px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
    
    <div class="visual-guide">
        <div class="visual-item">
            <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
            </svg>
            <div class="visual-label">0. 다 먹음</div>
        </div>
        <div class="visual-item">
            <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
                <path d="M 50 50 L 50 5 A 45 45 0 0 1 95 50 Z" fill="#2c3e50"/>
            </svg>
            <div class="visual-label">1. 조금 남김<br/>(약 25%)</div>
        </div>
        <div class="visual-item">
            <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
                <path d="M 50 50 L 50 5 A 45 45 0 0 1 50 95 Z" fill="#2c3e50"/>
            </svg>
            <div class="visual-label">2. 반 정도 남김<br/>(약 50%)</div>
        </div>
        <div class="visual-item">
            <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
                <path d="M 50 50 L 50 5 A 45 45 0 1 1 5 50 Z" fill="#2c3e50"/>
            </svg>
            <div class="visual-label">3. 대부분 남김<br/>(약 75%)</div>
        </div>
        <div class="visual-item">
            <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="#2c3e50" stroke="#333" stroke-width="2"/>
            </svg>
            <div class="visual-label">4. 모두 남김<br/>(100%)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_food_waste_selector(label, key, default_value=0):
    """음식별 잔반량 선택기 (원형 이미지 포함)"""
    st.markdown(f"**{label}**")
    
    # SVG 원형 이미지 정의
    circles = [
        # 0. 다 먹음
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
        </svg>""",
        # 1. 조금 남김 (25%) - 1/4만 칠하기
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
            <path d="M 50 50 L 50 5 A 45 45 0 0 1 95 50 Z" fill="#2c3e50"/>
        </svg>""",
        # 2. 반 정도 남김 (50%) - 1/2만 칠하기
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
            <path d="M 50 50 L 50 5 A 45 45 0 0 1 50 95 Z" fill="#2c3e50"/>
        </svg>""",
        # 3. 대부분 남김 (75%) - 3/4만 칠하기
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
            <path d="M 50 50 L 50 5 A 45 45 0 1 1 5 50 Z" fill="#2c3e50"/>
        </svg>""",
        # 4. 모두 남김 (100%)
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="#2c3e50" stroke="#333" stroke-width="2"/>
        </svg>"""
    ]
    
    labels = ["0. 다 먹음", "1. 조금", "2. 반", "3. 대부분", "4. 모두"]
    
    # 5개 컬럼으로 원형 이미지 배치
    cols = st.columns(5)
    for i, (col, circle, label_text) in enumerate(zip(cols, circles, labels)):
        with col:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 8px;">
                {circle}
                <div style="font-size: 11px; margin-top: 5px; color: #666;">{label_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 라디오 버튼을 5개 컬럼으로 나누어 배치
    radio_cols = st.columns(5)
    
    # 임시로 선택 저장
    if f"{key}_selected" not in st.session_state:
        st.session_state[f"{key}_selected"] = default_value
    
    for i, col in enumerate(radio_cols):
        with col:
            button_type = "primary" if st.session_state[f"{key}_selected"] == i else "secondary"
            if st.button(f"{i}", 
                        key=f"{key}_radio_{i}", 
                        use_container_width=True,
                        type=button_type):
                st.session_state[f"{key}_selected"] = i
                st.rerun()
    
    return st.session_state[f"{key}_selected"]

def show_page1_meal_portions():
    """1페이지: 1인 분량 음식 질량 조사 (5일)"""
    st.subheader("1인 분량 음식 질량 조사 (5일)")
    
    st.info("📝 5일간 제공된 음식의 질량을 측정하여 기록해주세요. (단위: g)")
    
    # 탭 크기 조정 CSS
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 10px 24px;
        font-size: 18px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    data = st.session_state.nutrition_data
    
    # 기존 데이터 불러오기
    existing_portions = data.get('meal_portions', {})
    if isinstance(existing_portions, str):
        existing_portions = json.loads(existing_portions) if existing_portions else {}
    
    meal_portions = {}
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 1일차", "📅 2일차", "📅 3일차", "📅 4일차", "📅 5일차"])
    
    # 1일차
    with tab1:
        day = 1
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.write("**아침**")
            breakfast_rice = st.number_input("밥/죽 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_rice', 0)), step=1.0, key=f"day{day}_breakfast_rice")
            breakfast_soup = st.number_input("국/탕 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_soup', 0)), step=1.0, key=f"day{day}_breakfast_soup")
            breakfast_main = st.number_input("주찬 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_main', 0)), step=1.0, key=f"day{day}_breakfast_main")
            breakfast_side1 = st.number_input("부찬1 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_side1', 0)), step=1.0, key=f"day{day}_breakfast_side1")
            breakfast_side2 = st.number_input("부찬2 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_side2', 0)), step=1.0, key=f"day{day}_breakfast_side2")
            breakfast_kimchi = st.number_input("김치 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_kimchi', 0)), step=1.0, key=f"day{day}_breakfast_kimchi")
        with col2:
            st.write("**간식1**")
            snack1 = st.number_input("간식 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_snack1', 0)), step=1.0, key=f"day{day}_snack1")
        with col3:
            st.write("**점심**")
            lunch_rice = st.number_input("밥/죽 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_rice', 0)), step=1.0, key=f"day{day}_lunch_rice")
            lunch_soup = st.number_input("국/탕 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_soup', 0)), step=1.0, key=f"day{day}_lunch_soup")
            lunch_main = st.number_input("주찬 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_main', 0)), step=1.0, key=f"day{day}_lunch_main")
            lunch_side1 = st.number_input("부찬1 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_side1', 0)), step=1.0, key=f"day{day}_lunch_side1")
            lunch_side2 = st.number_input("부찬2 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_side2', 0)), step=1.0, key=f"day{day}_lunch_side2")
            lunch_kimchi = st.number_input("김치 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_kimchi', 0)), step=1.0, key=f"day{day}_lunch_kimchi")
        with col4:
            st.write("**간식2**")
            snack2 = st.number_input("간식 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_snack2', 0)), step=1.0, key=f"day{day}_snack2")
        with col5:
            st.write("**저녁**")
            dinner_rice = st.number_input("밥/죽 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_rice', 0)), step=1.0, key=f"day{day}_dinner_rice")
            dinner_soup = st.number_input("국/탕 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_soup', 0)), step=1.0, key=f"day{day}_dinner_soup")
            dinner_main = st.number_input("주찬 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_main', 0)), step=1.0, key=f"day{day}_dinner_main")
            dinner_side1 = st.number_input("부찬1 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_side1', 0)), step=1.0, key=f"day{day}_dinner_side1")
            dinner_side2 = st.number_input("부찬2 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_side2', 0)), step=1.0, key=f"day{day}_dinner_side2")
            dinner_kimchi = st.number_input("김치 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_kimchi', 0)), step=1.0, key=f"day{day}_dinner_kimchi")
        
        meal_portions.update({
            f'day{day}_breakfast_rice': breakfast_rice, f'day{day}_breakfast_soup': breakfast_soup, f'day{day}_breakfast_main': breakfast_main,
            f'day{day}_breakfast_side1': breakfast_side1, f'day{day}_breakfast_side2': breakfast_side2, f'day{day}_breakfast_kimchi': breakfast_kimchi,
            f'day{day}_snack1': snack1, f'day{day}_lunch_rice': lunch_rice, f'day{day}_lunch_soup': lunch_soup,
            f'day{day}_lunch_main': lunch_main, f'day{day}_lunch_side1': lunch_side1, f'day{day}_lunch_side2': lunch_side2,
            f'day{day}_lunch_kimchi': lunch_kimchi, f'day{day}_snack2': snack2, f'day{day}_dinner_rice': dinner_rice,
            f'day{day}_dinner_soup': dinner_soup, f'day{day}_dinner_main': dinner_main, f'day{day}_dinner_side1': dinner_side1,
            f'day{day}_dinner_side2': dinner_side2, f'day{day}_dinner_kimchi': dinner_kimchi
        })
        
        daily_total = breakfast_rice + breakfast_soup + breakfast_main + breakfast_side1 + breakfast_side2 + breakfast_kimchi + snack1 + lunch_rice + lunch_soup + lunch_main + lunch_side1 + lunch_side2 + lunch_kimchi + snack2 + dinner_rice + dinner_soup + dinner_main + dinner_side1 + dinner_side2 + dinner_kimchi
        st.markdown("---")
        st.metric(f"{day}일차 총 제공량", f"{daily_total:.0f}g")
    
    # 2일차부터 5일차까지 동일한 구조로 반복
    for day, tab in [(2, tab2), (3, tab3), (4, tab4), (5, tab5)]:
        with tab:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.write("**아침**")
                breakfast_rice = st.number_input("밥/죽 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_rice', 0)), step=1.0, key=f"day{day}_breakfast_rice")
                breakfast_soup = st.number_input("국/탕 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_soup', 0)), step=1.0, key=f"day{day}_breakfast_soup")
                breakfast_main = st.number_input("주찬 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_main', 0)), step=1.0, key=f"day{day}_breakfast_main")
                breakfast_side1 = st.number_input("부찬1 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_side1', 0)), step=1.0, key=f"day{day}_breakfast_side1")
                breakfast_side2 = st.number_input("부찬2 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_side2', 0)), step=1.0, key=f"day{day}_breakfast_side2")
                breakfast_kimchi = st.number_input("김치 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_breakfast_kimchi', 0)), step=1.0, key=f"day{day}_breakfast_kimchi")
            with col2:
                st.write("**간식1**")
                snack1 = st.number_input("간식 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_snack1', 0)), step=1.0, key=f"day{day}_snack1")
            with col3:
                st.write("**점심**")
                lunch_rice = st.number_input("밥/죽 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_rice', 0)), step=1.0, key=f"day{day}_lunch_rice")
                lunch_soup = st.number_input("국/탕 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_soup', 0)), step=1.0, key=f"day{day}_lunch_soup")
                lunch_main = st.number_input("주찬 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_main', 0)), step=1.0, key=f"day{day}_lunch_main")
                lunch_side1 = st.number_input("부찬1 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_side1', 0)), step=1.0, key=f"day{day}_lunch_side1")
                lunch_side2 = st.number_input("부찬2 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_side2', 0)), step=1.0, key=f"day{day}_lunch_side2")
                lunch_kimchi = st.number_input("김치 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_lunch_kimchi', 0)), step=1.0, key=f"day{day}_lunch_kimchi")
            with col4:
                st.write("**간식2**")
                snack2 = st.number_input("간식 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_snack2', 0)), step=1.0, key=f"day{day}_snack2")
            with col5:
                st.write("**저녁**")
                dinner_rice = st.number_input("밥/죽 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_rice', 0)), step=1.0, key=f"day{day}_dinner_rice")
                dinner_soup = st.number_input("국/탕 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_soup', 0)), step=1.0, key=f"day{day}_dinner_soup")
                dinner_main = st.number_input("주찬 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_main', 0)), step=1.0, key=f"day{day}_dinner_main")
                dinner_side1 = st.number_input("부찬1 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_side1', 0)), step=1.0, key=f"day{day}_dinner_side1")
                dinner_side2 = st.number_input("부찬2 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_side2', 0)), step=1.0, key=f"day{day}_dinner_side2")
                dinner_kimchi = st.number_input("김치 (g)", min_value=0.0, max_value=1000.0, value=float(existing_portions.get(f'day{day}_dinner_kimchi', 0)), step=1.0, key=f"day{day}_dinner_kimchi")
            
            meal_portions.update({
                f'day{day}_breakfast_rice': breakfast_rice, f'day{day}_breakfast_soup': breakfast_soup, f'day{day}_breakfast_main': breakfast_main,
                f'day{day}_breakfast_side1': breakfast_side1, f'day{day}_breakfast_side2': breakfast_side2, f'day{day}_breakfast_kimchi': breakfast_kimchi,
                f'day{day}_snack1': snack1, f'day{day}_lunch_rice': lunch_rice, f'day{day}_lunch_soup': lunch_soup,
                f'day{day}_lunch_main': lunch_main, f'day{day}_lunch_side1': lunch_side1, f'day{day}_lunch_side2': lunch_side2,
                f'day{day}_lunch_kimchi': lunch_kimchi, f'day{day}_snack2': snack2, f'day{day}_dinner_rice': dinner_rice,
                f'day{day}_dinner_soup': dinner_soup, f'day{day}_dinner_main': dinner_main, f'day{day}_dinner_side1': dinner_side1,
                f'day{day}_dinner_side2': dinner_side2, f'day{day}_dinner_kimchi': dinner_kimchi
            })
            
            daily_total = breakfast_rice + breakfast_soup + breakfast_main + breakfast_side1 + breakfast_side2 + breakfast_kimchi + snack1 + lunch_rice + lunch_soup + lunch_main + lunch_side1 + lunch_side2 + lunch_kimchi + snack2 + dinner_rice + dinner_soup + dinner_main + dinner_side1 + dinner_side2 + dinner_kimchi
            st.markdown("---")
            st.metric(f"{day}일차 총 제공량", f"{daily_total:.0f}g")
    
    # 5일 총량 계산
    total_portions = sum(meal_portions.values())
    st.markdown("---")
    st.subheader("📊 5일간 총 제공량")
    st.metric("총계", f"{total_portions:.0f}g", 
             delta=f"1일 평균 {total_portions/5:.0f}g")
    
    # 데이터 저장
    st.session_state.nutrition_data['meal_portions'] = json.dumps(meal_portions, ensure_ascii=False)
    
    navigation_buttons()

def show_page2_plate_waste_visual():
    """2페이지: 잔반량 조사 (5일) - 목측법"""
    st.subheader("잔반량 조사 (5일) - 목측법")
    
    st.info("📝 5일간 남긴 음식의 양을 원형 이미지를 보고 선택해주세요.")
    
    # 탭 크기 조정 CSS
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 10px 24px;
        font-size: 18px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 상단에 가이드 표시
    create_visual_guide()
    
    # 목측법 비율 정의
    visual_ratios = [0.0, 0.25, 0.50, 0.75, 1.0]
    
    data = st.session_state.nutrition_data
    
    # 제공량 데이터 불러오기
    meal_portions_data = data.get('meal_portions', {})
    if isinstance(meal_portions_data, str):
        meal_portions_data = json.loads(meal_portions_data) if meal_portions_data else {}
    
    # 기존 잔반 데이터 불러오기 (목측 레벨은 세션 임시 저장소에서)
    existing_waste = st.session_state.get('plate_waste_visual_temp', {})
    
    plate_waste_visual = {}
    plate_waste_grams = {}
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 1일차", "📅 2일차", "📅 3일차", "📅 4일차", "📅 5일차"])
    
    # 각 탭 처리 함수
    def process_day_waste(day, tab):
        with tab:
            # 아침 식사
            st.markdown("#### 🌅 아침")
            breakfast_rice_waste = create_food_waste_selector("밥/죽", f"day{day}_breakfast_rice_waste", int(existing_waste.get(f'day{day}_breakfast_rice_waste', 0)))
            breakfast_soup_waste = create_food_waste_selector("국/탕", f"day{day}_breakfast_soup_waste", int(existing_waste.get(f'day{day}_breakfast_soup_waste', 0)))
            breakfast_main_waste = create_food_waste_selector("주찬", f"day{day}_breakfast_main_waste", int(existing_waste.get(f'day{day}_breakfast_main_waste', 0)))
            breakfast_side1_waste = create_food_waste_selector("부찬1", f"day{day}_breakfast_side1_waste", int(existing_waste.get(f'day{day}_breakfast_side1_waste', 0)))
            breakfast_side2_waste = create_food_waste_selector("부찬2", f"day{day}_breakfast_side2_waste", int(existing_waste.get(f'day{day}_breakfast_side2_waste', 0)))
            breakfast_kimchi_waste = create_food_waste_selector("김치", f"day{day}_breakfast_kimchi_waste", int(existing_waste.get(f'day{day}_breakfast_kimchi_waste', 0)))
            
            st.markdown("---")
            st.markdown("#### 🍪 간식1")
            snack1_waste = create_food_waste_selector("간식", f"day{day}_snack1_waste", int(existing_waste.get(f'day{day}_snack1_waste', 0)))
            
            st.markdown("---")
            st.markdown("#### ☀️ 점심")
            lunch_rice_waste = create_food_waste_selector("밥/죽", f"day{day}_lunch_rice_waste", int(existing_waste.get(f'day{day}_lunch_rice_waste', 0)))
            lunch_soup_waste = create_food_waste_selector("국/탕", f"day{day}_lunch_soup_waste", int(existing_waste.get(f'day{day}_lunch_soup_waste', 0)))
            lunch_main_waste = create_food_waste_selector("주찬", f"day{day}_lunch_main_waste", int(existing_waste.get(f'day{day}_lunch_main_waste', 0)))
            lunch_side1_waste = create_food_waste_selector("부찬1", f"day{day}_lunch_side1_waste", int(existing_waste.get(f'day{day}_lunch_side1_waste', 0)))
            lunch_side2_waste = create_food_waste_selector("부찬2", f"day{day}_lunch_side2_waste", int(existing_waste.get(f'day{day}_lunch_side2_waste', 0)))
            lunch_kimchi_waste = create_food_waste_selector("김치", f"day{day}_lunch_kimchi_waste", int(existing_waste.get(f'day{day}_lunch_kimchi_waste', 0)))
            
            st.markdown("---")
            st.markdown("#### 🍪 간식2")
            snack2_waste = create_food_waste_selector("간식", f"day{day}_snack2_waste", int(existing_waste.get(f'day{day}_snack2_waste', 0)))
            
            st.markdown("---")
            st.markdown("#### 🌙 저녁")
            dinner_rice_waste = create_food_waste_selector("밥/죽", f"day{day}_dinner_rice_waste", int(existing_waste.get(f'day{day}_dinner_rice_waste', 0)))
            dinner_soup_waste = create_food_waste_selector("국/탕", f"day{day}_dinner_soup_waste", int(existing_waste.get(f'day{day}_dinner_soup_waste', 0)))
            dinner_main_waste = create_food_waste_selector("주찬", f"day{day}_dinner_main_waste", int(existing_waste.get(f'day{day}_dinner_main_waste', 0)))
            dinner_side1_waste = create_food_waste_selector("부찬1", f"day{day}_dinner_side1_waste", int(existing_waste.get(f'day{day}_dinner_side1_waste', 0)))
            dinner_side2_waste = create_food_waste_selector("부찬2", f"day{day}_dinner_side2_waste", int(existing_waste.get(f'day{day}_dinner_side2_waste', 0)))
            dinner_kimchi_waste = create_food_waste_selector("김치", f"day{day}_dinner_kimchi_waste", int(existing_waste.get(f'day{day}_dinner_kimchi_waste', 0)))
            
            # 목측 레벨 저장
            plate_waste_visual.update({
                f'day{day}_breakfast_rice_waste': breakfast_rice_waste, f'day{day}_breakfast_soup_waste': breakfast_soup_waste,
                f'day{day}_breakfast_main_waste': breakfast_main_waste, f'day{day}_breakfast_side1_waste': breakfast_side1_waste,
                f'day{day}_breakfast_side2_waste': breakfast_side2_waste, f'day{day}_breakfast_kimchi_waste': breakfast_kimchi_waste,
                f'day{day}_snack1_waste': snack1_waste, f'day{day}_lunch_rice_waste': lunch_rice_waste,
                f'day{day}_lunch_soup_waste': lunch_soup_waste, f'day{day}_lunch_main_waste': lunch_main_waste,
                f'day{day}_lunch_side1_waste': lunch_side1_waste, f'day{day}_lunch_side2_waste': lunch_side2_waste,
                f'day{day}_lunch_kimchi_waste': lunch_kimchi_waste, f'day{day}_snack2_waste': snack2_waste,
                f'day{day}_dinner_rice_waste': dinner_rice_waste, f'day{day}_dinner_soup_waste': dinner_soup_waste,
                f'day{day}_dinner_main_waste': dinner_main_waste, f'day{day}_dinner_side1_waste': dinner_side1_waste,
                f'day{day}_dinner_side2_waste': dinner_side2_waste, f'day{day}_dinner_kimchi_waste': dinner_kimchi_waste
            })
            
            # 그램 단위로 변환
            waste_items = {
                'breakfast_rice': (breakfast_rice_waste, f'day{day}_breakfast_rice'),
                'breakfast_soup': (breakfast_soup_waste, f'day{day}_breakfast_soup'),
                'breakfast_main': (breakfast_main_waste, f'day{day}_breakfast_main'),
                'breakfast_side1': (breakfast_side1_waste, f'day{day}_breakfast_side1'),
                'breakfast_side2': (breakfast_side2_waste, f'day{day}_breakfast_side2'),
                'breakfast_kimchi': (breakfast_kimchi_waste, f'day{day}_breakfast_kimchi'),
                'snack1': (snack1_waste, f'day{day}_snack1'),
                'lunch_rice': (lunch_rice_waste, f'day{day}_lunch_rice'),
                'lunch_soup': (lunch_soup_waste, f'day{day}_lunch_soup'),
                'lunch_main': (lunch_main_waste, f'day{day}_lunch_main'),
                'lunch_side1': (lunch_side1_waste, f'day{day}_lunch_side1'),
                'lunch_side2': (lunch_side2_waste, f'day{day}_lunch_side2'),
                'lunch_kimchi': (lunch_kimchi_waste, f'day{day}_lunch_kimchi'),
                'snack2': (snack2_waste, f'day{day}_snack2'),
                'dinner_rice': (dinner_rice_waste, f'day{day}_dinner_rice'),
                'dinner_soup': (dinner_soup_waste, f'day{day}_dinner_soup'),
                'dinner_main': (dinner_main_waste, f'day{day}_dinner_main'),
                'dinner_side1': (dinner_side1_waste, f'day{day}_dinner_side1'),
                'dinner_side2': (dinner_side2_waste, f'day{day}_dinner_side2'),
                'dinner_kimchi': (dinner_kimchi_waste, f'day{day}_dinner_kimchi')
            }
            
            daily_waste_g = 0
            for item_name, (waste_level, portion_key) in waste_items.items():
                portion_amount = meal_portions_data.get(portion_key, 0)
                waste_ratio = visual_ratios[waste_level]
                waste_g = portion_amount * waste_ratio
                plate_waste_grams[f'day{day}_{item_name}_waste'] = waste_g
                daily_waste_g += waste_g
            
            st.markdown("---")
            st.metric(f"{day}일차 총 잔반량", f"{daily_waste_g:.0f}g")
    
    # 각 탭 처리
    process_day_waste(1, tab1)
    process_day_waste(2, tab2)
    process_day_waste(3, tab3)
    process_day_waste(4, tab4)
    process_day_waste(5, tab5)
    
    # 5일 총 잔반량 계산
    total_waste = sum(plate_waste_grams.values())
    st.markdown("---")
    st.subheader("📊 5일간 총 잔반량")
    st.metric("총계", f"{total_waste:.0f}g", delta=f"1일 평균 {total_waste/5:.0f}g")
    
    # 섭취율 계산
    if meal_portions_data:
        total_portions = sum(meal_portions_data.values())
        intake_rate = ((total_portions - total_waste) / total_portions * 100) if total_portions > 0 else 0
        st.metric("평균 섭취율", f"{intake_rate:.1f}%")
    
    # 데이터 저장 (그램 단위만 DB에 저장)
    st.session_state.nutrition_data['plate_waste'] = json.dumps(plate_waste_grams, ensure_ascii=False)
    
    # 목측 레벨은 세션에만 임시 저장 (UI 상태 유지용, DB에는 저장하지 않음)
    if 'plate_waste_visual_temp' not in st.session_state:
        st.session_state['plate_waste_visual_temp'] = {}
    st.session_state['plate_waste_visual_temp'] = plate_waste_visual
    
    navigation_buttons()

def show_page3_submit(supabase, elderly_id, surveyor_id, nursing_home_id):
    """3페이지: 데이터 요약 및 제출"""
    st.subheader("영양 조사 데이터 요약")
    
    data = st.session_state.nutrition_data
    
    # 제공량 데이터
    meal_portions_data = data.get('meal_portions', {})
    if isinstance(meal_portions_data, str):
        meal_portions_data = json.loads(meal_portions_data) if meal_portions_data else {}
    
    # 잔반량 데이터
    plate_waste_data = data.get('plate_waste', {})
    if isinstance(plate_waste_data, str):
        plate_waste_data = json.loads(plate_waste_data) if plate_waste_data else {}
    
    # 통계 계산
    total_portions = sum(meal_portions_data.values()) if meal_portions_data else 0
    total_waste = sum(plate_waste_data.values()) if plate_waste_data else 0
    total_intake = total_portions - total_waste
    intake_rate = (total_intake / total_portions * 100) if total_portions > 0 else 0
    
    # 요약 표시
    st.markdown("### 📊 5일간 섭취 현황")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 제공량", f"{total_portions:.0f}g", 
                 delta=f"1일 평균 {total_portions/5:.0f}g")
    
    with col2:
        st.metric("총 잔반량", f"{total_waste:.0f}g", 
                 delta=f"1일 평균 {total_waste/5:.0f}g")
    
    with col3:
        st.metric("총 섭취량", f"{total_intake:.0f}g", 
                 delta=f"1일 평균 {total_intake/5:.0f}g")
    
    with col4:
        color = "normal" if intake_rate >= 75 else "inverse" if intake_rate >= 50 else "off"
        st.metric("평균 섭취율", f"{intake_rate:.1f}%")
    
    st.markdown("---")
    
    # 섭취율 해석
    if intake_rate >= 75:
        st.success("✅ **양호한 섭취율**: 식사를 잘 하고 계십니다.")
    elif intake_rate >= 50:
        st.warning("⚠️ **주의 필요**: 섭취량이 다소 부족합니다. 식사량 증가를 고려해주세요.")
    else:
        st.error("🚨 **개선 필요**: 섭취량이 매우 부족합니다. 영양 상담을 권장합니다.")
    
    st.markdown("---")
    
    # 제출 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            st.session_state.nutrition_page -= 1
            st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
            # 세션 초기화
            if 'nutrition_data' in st.session_state:
                del st.session_state.nutrition_data
            if 'nutrition_page' in st.session_state:
                del st.session_state.nutrition_page
            if 'plate_waste_visual_temp' in st.session_state:
                del st.session_state['plate_waste_visual_temp']
            st.session_state.current_survey = None
            st.rerun()
    
    with col3:
        if st.button("✅ 제출", use_container_width=True, type="primary"):
            save_nutrition_survey(supabase, elderly_id, surveyor_id, nursing_home_id)

def save_nutrition_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    """설문 데이터 저장"""
    try:
        data = st.session_state.nutrition_data.copy()
        
        # DB에 존재하지 않는 컬럼 제거
        if 'plate_waste_visual' in data:
            del data['plate_waste_visual']
        
        data.update({
            'elderly_id': elderly_id,
            'surveyor_id': surveyor_id,
            'nursing_home_id': nursing_home_id,
            'updated_at': get_kst_now()
        })
        
        # 기존 데이터 확인
        response = supabase.table('nutrition_survey').select('id').eq('elderly_id', elderly_id).execute()
        
        if response.data:
            # 업데이트
            supabase.table('nutrition_survey').update(data).eq('elderly_id', elderly_id).execute()
        else:
            # 새로 추가
            supabase.table('nutrition_survey').insert(data).execute()
        
        # 진행 상황 업데이트
        supabase.table('survey_progress').update({
            'nutrition_survey_completed': True,
            'last_updated': get_kst_now()
        }).eq('elderly_id', elderly_id).execute()
        
        st.success("✅ 영양 조사표가 저장되었습니다!")
        
        # 세션 초기화
        del st.session_state.nutrition_data
        del st.session_state.nutrition_page
        if 'plate_waste_visual_temp' in st.session_state:
            del st.session_state['plate_waste_visual_temp']
        st.session_state.current_survey = None
        
        
        if st.button("대시보드로 돌아가기"):
            st.rerun()
        
    except Exception as e:
        st.error(f"저장 중 오류가 발생했습니다: {str(e)}")

def navigation_buttons():
    """페이지 이동 버튼"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.nutrition_page > 1:
            if st.button("⬅️ 이전", use_container_width=True):
                st.session_state.nutrition_page -= 1
                st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
            # 세션 초기화
            if 'nutrition_data' in st.session_state:
                del st.session_state.nutrition_data
            if 'nutrition_page' in st.session_state:
                del st.session_state.nutrition_page
            if 'plate_waste_visual_temp' in st.session_state:
                del st.session_state['plate_waste_visual_temp']
            st.session_state.current_survey = None
            st.rerun()
    
    with col3:
        if st.session_state.nutrition_page < 3:
            if st.button("다음 ➡️", use_container_width=True, type="primary"):
                st.session_state.nutrition_page += 1
                st.rerun()

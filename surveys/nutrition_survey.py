import streamlit as st
import json
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo('Asia/Seoul')

def get_kst_now():
    """현재 한국 시간 반환"""
    return datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')

def upload_image_to_supabase(supabase, file, elderly_id, day, meal_type, photo_type):
    """
    Supabase Storage에 이미지 업로드
    
    Args:
        supabase: Supabase 클라이언트
        file: 업로드할 파일 객체
        elderly_id: 어르신 ID
        day: 날짜 (1-5)
        meal_type: 식사 종류 (breakfast, snack1, lunch, snack2, dinner)
        photo_type: 사진 종류 (provision=제공량, waste=잔반량)
    
    Returns:
        str: 업로드된 이미지의 공개 URL 또는 None
    """
    try:
        # 파일명 생성
        timestamp = datetime.now(KST).strftime('%Y%m%d_%H%M%S')
        file_extension = file.name.split('.')[-1] if '.' in file.name else 'jpg'
        file_name = f"{elderly_id}_{photo_type}_day{day}_{meal_type}_{timestamp}.{file_extension}"
        
        # ✅ 파일 포인터를 처음으로 되돌리기
        file.seek(0)
        
        # 이미지를 바이트로 읽기
        file_bytes = file.read()
        
        # ✅ 파일 크기 확인
        if len(file_bytes) == 0:
            st.error(f"❌ 파일이 비어있습니다: {file.name}")
            return None
        
        # Supabase Storage에 업로드
        response = supabase.storage.from_('nutrition-photos').upload(
            file_name,
            file_bytes,
            file_options={"content-type": file.type}
        )
        
        # ✅ 업로드 성공 확인
        if response:
            # 공개 URL 생성
            public_url = supabase.storage.from_('nutrition-photos').get_public_url(file_name)
            return public_url
        else:
            st.error(f"❌ 업로드 실패: {file_name}")
            return None
            
    except Exception as e:
        st.error(f"❌ 이미지 업로드 실패: {str(e)}")
        return None

def delete_image_from_supabase(supabase, photo_url, photo_key, storage_dict_name):
    """
    Supabase Storage에서 이미지 삭제
    
    Args:
        supabase: Supabase 클라이언트
        photo_url: 삭제할 사진의 URL
        photo_key: 세션 스테이트 딕셔너리에서 삭제할 키
        storage_dict_name: 세션 스테이트 딕셔너리 이름 ('uploaded_provision_photos' 또는 'uploaded_waste_photos')
    
    Returns:
        bool: 삭제 성공 여부
    """
    try:
        # URL에서 파일명 추출
        file_name = photo_url.split('/')[-1]
        
        # Supabase Storage에서 삭제
        supabase.storage.from_('nutrition-photos').remove([file_name])
        
        # ✅ 세션 스테이트에서도 제거 (이 부분이 중요!)
        if photo_key in st.session_state.get(storage_dict_name, {}):
            del st.session_state[storage_dict_name][photo_key]
        
        # 성공
        return True
        
    except Exception as e:
        st.error(f"❌ 삭제 실패: {str(e)}")
        return False

def show_nutrition_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    st.title("🥗 2. 영양 조사표")
    
    # Supabase 클라이언트를 세션에 저장
    if 'supabase' not in st.session_state:
        st.session_state.supabase = supabase
    
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
    
    # 페이지 진행 표시
    total_pages = 3
    st.progress(st.session_state.nutrition_page / total_pages)
    st.caption(f"페이지 {st.session_state.nutrition_page} / {total_pages}")
    
    # 페이지별 내용
    if st.session_state.nutrition_page == 1:
        show_page1_meal_portions(elderly_id)
    elif st.session_state.nutrition_page == 2:
        show_page2_plate_waste_visual(elderly_id)
    elif st.session_state.nutrition_page == 3:
        show_page3_submit(supabase, elderly_id, surveyor_id, nursing_home_id)
        
    # ✅ 업로드된 사진 URL 저장용 세션 초기화
    if 'uploaded_provision_photos' not in st.session_state:
        st.session_state.uploaded_provision_photos = {}
    if 'uploaded_waste_photos' not in st.session_state:
        st.session_state.uploaded_waste_photos = {}

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
    
    circles = [
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
        </svg>""",
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
            <path d="M 50 50 L 50 5 A 45 45 0 0 1 95 50 Z" fill="#2c3e50"/>
        </svg>""",
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
            <path d="M 50 50 L 50 5 A 45 45 0 0 1 50 95 Z" fill="#2c3e50"/>
        </svg>""",
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="white" stroke="#333" stroke-width="2"/>
            <path d="M 50 50 L 50 5 A 45 45 0 1 1 5 50 Z" fill="#2c3e50"/>
        </svg>""",
        """<svg viewBox="0 0 100 100" style="width:60px;height:60px">
            <circle cx="50" cy="50" r="45" fill="#2c3e50" stroke="#333" stroke-width="2"/>
        </svg>"""
    ]
    
    labels = ["0. 다 먹음", "1. 조금 남김", "2. 반 정도 남김", "3. 대부분 남김", "4. 모두 남김"]
    
    cols = st.columns(5)
    for i, (col, circle, label_text) in enumerate(zip(cols, circles, labels)):
        with col:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 8px;">
                {circle}
                <div style="font-size: 11px; margin-top: 5px; color: #666;">{label_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    radio_cols = st.columns(5)
    
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

def render_photo_uploader(day, meal_type, meal_label, photo_type, elderly_id):
    """
    사진 업로더 렌더링 (업로드 + 삭제 기능)
    
    Args:
        day: 날짜 (1-5)
        meal_type: 식사 종류 (breakfast, snack1, lunch, snack2, dinner)
        meal_label: 표시할 라벨 (🌅 아침, 🍪 간식1 등)
        photo_type: provision 또는 waste
        elderly_id: 어르신 ID
    """
    st.write(f"**{meal_label}**")
    
    # 세션 딕셔너리 선택
    storage_dict_name = 'uploaded_provision_photos' if photo_type == 'provision' else 'uploaded_waste_photos'
    photo_key = f'day{day}_{meal_type}'
    
    # ✅ 세션 딕셔너리가 없으면 생성
    if storage_dict_name not in st.session_state:
        st.session_state[storage_dict_name] = {}
    
    # 이미 업로드된 사진이 있으면 표시
    if photo_key in st.session_state[storage_dict_name]:
        photo_url = st.session_state[storage_dict_name][photo_key]
        
        # 컨테이너로 묶어서 표시
        with st.container():
            st.image(photo_url, use_container_width=True)
            
            # 삭제 버튼
            if st.button("🗑️ 삭제 및 재업로드", key=f"delete_{photo_type}_{photo_key}", use_container_width=True, type="secondary"):
                # ✅ 즉시 세션에서 제거
                del st.session_state[storage_dict_name][photo_key]
                
                # ✅ Supabase에서도 삭제 (백그라운드)
                try:
                    file_name = photo_url.split('/')[-1]
                    st.session_state.supabase.storage.from_('nutrition-photos').remove([file_name])
                except Exception as e:
                    # 삭제 실패해도 계속 진행 (세션에서는 이미 제거됨)
                    pass
                
                # ✅ 즉시 새로고침
                st.rerun()
    else:
        # 파일 업로더
        uploaded_file = st.file_uploader(
            f"{day}일차 {meal_label}",
            type=['jpg', 'jpeg', 'png'],
            key=f"day{day}_{meal_type}_{photo_type}_photo",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            # 즉시 업로드
            with st.spinner('업로드 중...'):
                url = upload_image_to_supabase(
                    st.session_state.supabase,
                    uploaded_file,
                    elderly_id,
                    day,
                    meal_type,
                    photo_type
                )
                if url:
                    st.session_state[storage_dict_name][photo_key] = url
                    st.rerun()

def show_page1_meal_portions(elderly_id):
    """1페이지: 제공량 사진 - 즉시 업로드"""
    st.subheader("1인 분량 음식 질량 조사 (5일)")

    st.warning("""
    📸 **사진 촬영 필수!**
    
    **사진을 선택하면 자동으로 업로드됩니다.**
    - 아침, 간식1, 점심, 간식2, 저녁 각각 1장씩 촬영
    - 업로드 후 삭제 버튼으로 재촬영 가능
    """)
    
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
    
    existing_portions = data.get('meal_portions', {})
    if isinstance(existing_portions, str):
        existing_portions = json.loads(existing_portions) if existing_portions else {}
    
    # 업로드된 사진 URL 저장 (세션)
    if 'uploaded_provision_photos' not in st.session_state:
        st.session_state.uploaded_provision_photos = {}
    
    existing_provision_photos = data.get('meal_provision_photos', {})
    if isinstance(existing_provision_photos, str):
        try:
            existing_provision_photos = json.loads(existing_provision_photos) if existing_provision_photos else {}
        except:
            existing_provision_photos = {}
    elif not isinstance(existing_provision_photos, dict):
        existing_provision_photos = {}
    
    # 기존 DB 사진을 세션에 복사
    if existing_provision_photos:
        for key, url in existing_provision_photos.items():
            if key not in st.session_state.uploaded_provision_photos:
                st.session_state.uploaded_provision_photos[key] = url
    
    meal_portions = {}
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 1일차", "📅 2일차", "📅 3일차", "📅 4일차", "📅 5일차"])
    
    def process_day_portions(day, tab):
        with tab:
            st.markdown("### 📸 식사 사진 업로드 (제공량)")
            
            photo_col1, photo_col2, photo_col3, photo_col4, photo_col5 = st.columns(5)
            
            # 아침
            with photo_col1:
                render_photo_uploader(day, 'breakfast', '🌅 아침', 'provision', elderly_id)
            
            # 간식1
            with photo_col2:
                render_photo_uploader(day, 'snack1', '🍪 간식1', 'provision', elderly_id)
            
            # 점심
            with photo_col3:
                render_photo_uploader(day, 'lunch', '☀️ 점심', 'provision', elderly_id)
            
            # 간식2
            with photo_col4:
                render_photo_uploader(day, 'snack2', '🍪 간식2', 'provision', elderly_id)
            
            # 저녁
            with photo_col5:
                render_photo_uploader(day, 'dinner', '🌙 저녁', 'provision', elderly_id)
         
            st.markdown("---")
            st.markdown("### 📝 음식 질량 입력")
            
            # 질량 입력
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
            
            daily_total = sum([breakfast_rice, breakfast_soup, breakfast_main, breakfast_side1, breakfast_side2, breakfast_kimchi,
                             snack1, lunch_rice, lunch_soup, lunch_main, lunch_side1, lunch_side2, lunch_kimchi,
                             snack2, dinner_rice, dinner_soup, dinner_main, dinner_side1, dinner_side2, dinner_kimchi])
            st.markdown("---")
            st.metric(f"{day}일차 총 제공량", f"{daily_total:.0f}g")
    
    process_day_portions(1, tab1)
    process_day_portions(2, tab2)
    process_day_portions(3, tab3)
    process_day_portions(4, tab4)
    process_day_portions(5, tab5)
    
    total_portions = sum(meal_portions.values())
    st.markdown("---")
    st.subheader("📊 5일간 총 제공량")
    st.metric("총계", f"{total_portions:.0f}g", delta=f"1일 평균 {total_portions/5:.0f}g")
    
    st.session_state.nutrition_data['meal_portions'] = json.dumps(meal_portions, ensure_ascii=False)
    
    navigation_buttons()

def show_page2_plate_waste_visual(elderly_id):
    """2페이지: 잔반량 사진 - 즉시 업로드"""
    st.subheader("잔반량 조사 (5일) - 목측법")
    
    st.warning("""
    📸 **사진 촬영 필수!**
    
    **사진을 선택하면 자동으로 업로드됩니다.**
    - 아침, 간식1, 점심, 간식2, 저녁 각각 1장씩 촬영
    - 잔반이 보이도록 촬영
    - 업로드 후 삭제 버튼으로 재촬영 가능
    """)
    
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
    
    create_visual_guide()
    
    visual_ratios = [0.0, 0.25, 0.50, 0.75, 1.0]
    
    data = st.session_state.nutrition_data
    
    meal_portions_data = data.get('meal_portions', {})
    if isinstance(meal_portions_data, str):
        meal_portions_data = json.loads(meal_portions_data) if meal_portions_data else {}
    
    existing_waste = st.session_state.get('plate_waste_visual_temp', {})
    
    # ✅ 업로드된 잔반 사진 URL 저장 (세션)
    if 'uploaded_waste_photos' not in st.session_state:
        st.session_state.uploaded_waste_photos = {}
    
    # 기존 잔반량 사진 URL 불러오기
    existing_waste_photos = data.get('meal_waste_photos', {})
    if isinstance(existing_waste_photos, str):
        try:
            existing_waste_photos = json.loads(existing_waste_photos) if existing_waste_photos else {}
        except:
            existing_waste_photos = {}
    elif not isinstance(existing_waste_photos, dict):
        existing_waste_photos = {}
    
    # 기존 DB 사진을 세션에 복사
    if existing_waste_photos:
        for key, url in existing_waste_photos.items():
            if key not in st.session_state.uploaded_waste_photos:
                st.session_state.uploaded_waste_photos[key] = url
    
    plate_waste_visual = {}
    plate_waste_grams = {}
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 1일차", "📅 2일차", "📅 3일차", "📅 4일차", "📅 5일차"])
    
    def process_day_waste(day, tab):
        with tab:
            # ✅ 사진 업로드 섹션 - 즉시 업로드
            st.markdown("### 📸 잔반 사진 업로드")
            
            photo_col1, photo_col2, photo_col3, photo_col4, photo_col5 = st.columns(5)
            
            # 아침
            with photo_col1:
                render_photo_uploader(day, 'breakfast', '🌅 아침', 'waste', elderly_id)
            
            # 간식1
            with photo_col2:
                render_photo_uploader(day, 'snack1', '🍪 간식1', 'waste', elderly_id)
            
            # 점심
            with photo_col3:
                render_photo_uploader(day, 'lunch', '☀️ 점심', 'waste', elderly_id)
            
            # 간식2
            with photo_col4:
                render_photo_uploader(day, 'snack2', '🍪 간식2', 'waste', elderly_id)
            
            # 저녁
            with photo_col5:
                render_photo_uploader(day, 'dinner', '🌙 저녁', 'waste', elderly_id)
            
            st.markdown("---")
            st.markdown("### 📝 잔반량 목측 평가")
            
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
    
    process_day_waste(1, tab1)
    process_day_waste(2, tab2)
    process_day_waste(3, tab3)
    process_day_waste(4, tab4)
    process_day_waste(5, tab5)
    
    total_waste = sum(plate_waste_grams.values())
    st.markdown("---")
    st.subheader("📊 5일간 총 잔반량")
    st.metric("총계", f"{total_waste:.0f}g", delta=f"1일 평균 {total_waste/5:.0f}g")
    
    if meal_portions_data:
        total_portions = sum(meal_portions_data.values())
        intake_rate = ((total_portions - total_waste) / total_portions * 100) if total_portions > 0 else 0
        st.metric("평균 섭취율", f"{intake_rate:.1f}%")
    
    st.session_state.nutrition_data['plate_waste'] = json.dumps(plate_waste_grams, ensure_ascii=False)
    
    if 'plate_waste_visual_temp' not in st.session_state:
        st.session_state['plate_waste_visual_temp'] = {}
    st.session_state['plate_waste_visual_temp'] = plate_waste_visual
    
    navigation_buttons()

def show_page3_submit(supabase, elderly_id, surveyor_id, nursing_home_id):
    """3페이지: 데이터 요약 및 제출"""
    st.subheader("영양 조사 데이터 요약")
    
    data = st.session_state.nutrition_data
    
    meal_portions_data = data.get('meal_portions', {})
    if isinstance(meal_portions_data, str):
        meal_portions_data = json.loads(meal_portions_data) if meal_portions_data else {}
    
    plate_waste_data = data.get('plate_waste', {})
    if isinstance(plate_waste_data, str):
        plate_waste_data = json.loads(plate_waste_data) if plate_waste_data else {}
    
    total_portions = sum(meal_portions_data.values()) if meal_portions_data else 0
    total_waste = sum(plate_waste_data.values()) if plate_waste_data else 0
    total_intake = total_portions - total_waste
    intake_rate = (total_intake / total_portions * 100) if total_portions > 0 else 0
    
    st.markdown("### 📊 5일간 섭취 현황")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 제공량", f"{total_portions:.0f}g", delta=f"1일 평균 {total_portions/5:.0f}g")
    
    with col2:
        st.metric("총 잔반량", f"{total_waste:.0f}g", delta=f"1일 평균 {total_waste/5:.0f}g")
    
    with col3:
        st.metric("총 섭취량", f"{total_intake:.0f}g", delta=f"1일 평균 {total_intake/5:.0f}g")
    
    with col4:
        st.metric("평균 섭취율", f"{intake_rate:.1f}%")
    
    st.markdown("---")
    
    if intake_rate >= 75:
        st.success("✅ **양호한 섭취율**: 식사를 잘 하고 계십니다.")
    elif intake_rate >= 50:
        st.warning("⚠️ **주의 필요**: 섭취량이 다소 부족합니다. 식사량 증가를 고려해주세요.")
    else:
        st.error("🚨 **개선 필요**: 섭취량이 매우 부족합니다. 영양 상담을 권장합니다.")
    
    st.markdown("---")
    
    # 📸 업로드된 사진 개수 표시
    provision_photos_count = len(st.session_state.get('uploaded_provision_photos', {}))
    waste_photos_count = len(st.session_state.get('uploaded_waste_photos', {}))
    total_photos = provision_photos_count + waste_photos_count
    
    st.info(f"📸 **업로드된 사진**: 제공량 {provision_photos_count}장, 잔반 {waste_photos_count}장 (총 {total_photos}장)")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            st.session_state.nutrition_page -= 1
            st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
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
        
        if 'plate_waste_visual' in data:
            del data['plate_waste_visual']
        
        # ✅ 세션에 저장된 사진 URL 사용
        provision_photos = st.session_state.get('uploaded_provision_photos', {})
        waste_photos = st.session_state.get('uploaded_waste_photos', {})
        
        if provision_photos:
            data['meal_provision_photos'] = json.dumps(provision_photos, ensure_ascii=False)
        
        if waste_photos:
            data['meal_waste_photos'] = json.dumps(waste_photos, ensure_ascii=False)
        
        # 데이터베이스 저장
        data.update({
            'elderly_id': elderly_id,
            'surveyor_id': surveyor_id,
            'nursing_home_id': nursing_home_id,
            'updated_at': get_kst_now()
        })
        
        response = supabase.table('nutrition_survey').select('id').eq('elderly_id', elderly_id).execute()
        
        if response.data:
            supabase.table('nutrition_survey').update(data).eq('elderly_id', elderly_id).execute()
        else:
            supabase.table('nutrition_survey').insert(data).execute()
        
        supabase.table('survey_progress').update({
            'nutrition_survey_completed': True,
            'last_updated': get_kst_now()
        }).eq('elderly_id', elderly_id).execute()
        
        st.success("✅ 영양 조사표가 저장되었습니다!")
        
        # ✅ 업로드된 사진 개수 표시
        total_photos = len(provision_photos) + len(waste_photos)
        if total_photos > 0:
            st.info(f"📸 총 {total_photos}장의 사진이 업로드되었습니다.")
        
        # 세션 정리
        del st.session_state.nutrition_data
        del st.session_state.nutrition_page
        if 'plate_waste_visual_temp' in st.session_state:
            del st.session_state['plate_waste_visual_temp']
        if 'uploaded_provision_photos' in st.session_state:
            del st.session_state.uploaded_provision_photos
        if 'uploaded_waste_photos' in st.session_state:
            del st.session_state.uploaded_waste_photos
        
        st.session_state.current_survey = None
        
        if st.button("대시보드로 돌아가기"):
            st.rerun()
        
    except Exception as e:
        st.error(f"저장 중 오류가 발생했습니다: {str(e)}")
        import traceback
        st.error(f"상세 오류:\n```\n{traceback.format_exc()}\n```")

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

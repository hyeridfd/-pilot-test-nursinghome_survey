import streamlit as st
import json
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo('Asia/Seoul')

def get_kst_now():
    """현재 한국 시간 반환"""
    return datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')

def show_basic_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    st.title("📝 1. 기초 조사표 (건강설문 조사표)")
    
    # 진행 상태 초기화
    if 'basic_page' not in st.session_state:
        st.session_state.basic_page = 1
    
    # 기존 데이터 불러오기
    if 'basic_data' not in st.session_state:
        try:
            response = supabase.table('basic_survey').select('*').eq('elderly_id', elderly_id).execute()
            if response.data:
                st.session_state.basic_data = response.data[0]
            else:
                st.session_state.basic_data = {}
        except:
            st.session_state.basic_data = {}
    
    # 페이지 진행 표시 (7페이지에서 9페이지로 증가)
    total_pages = 9
    st.progress(st.session_state.basic_page / total_pages)
    st.caption(f"페이지 {st.session_state.basic_page} / {total_pages}")
    
    # 페이지별 내용
    if st.session_state.basic_page == 1:
        show_page1()
    elif st.session_state.basic_page == 2:
        show_page2()
    elif st.session_state.basic_page == 3:
        show_page3()
    elif st.session_state.basic_page == 4:
        show_page4()
    elif st.session_state.basic_page == 5:
        show_page5_ipaq()  # 신체 활동 수준 조사 (IPAQ-SF)
    elif st.session_state.basic_page == 6:
        show_page6_mna()  # 영양 상태 평가 (MNA-SF)
    elif st.session_state.basic_page == 7:
        show_page7_kmbi()  # K-MBI 평가
    elif st.session_state.basic_page == 8:
        show_page8_mmse()  # MMSE-K 평가
    elif st.session_state.basic_page == 9:
        show_page9(supabase, elderly_id, surveyor_id, nursing_home_id)  # 시설 특성 및 제출

def show_page1():
    """1페이지: 인구통계학적 특성"""
    st.subheader("인구통계학적 특성")
    
    data = st.session_state.basic_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        gender = st.radio(
            "1. 귀하의 성별은 선택해 주십시오",
            options=["남자", "여자"],
            index=0 if data.get('gender') == "남자" else 1 if data.get('gender') == "여자" else 0,
            key="gender"
        )
        
        age = st.number_input(
            "2. 귀하의 출생연도를 작성해 주십시오",
            min_value=1900,
            max_value=datetime.now().year,
            value=int(data.get('age', 1950)) if int(data.get('age', 0) or 0) >= 1900 else 1950,
            step=1,
            key="age"
        )
        care_grade = st.selectbox(
            "3. 다음 중 귀하가 받으신 장기요양등급을 선택해 주십시오",
            options=["1등급", "2등급", "3등급", "4등급 이상"],
            index=0,
            key="care_grade"
        )
    
    with col2:
        residence_duration = st.selectbox(
            "4. 귀하가 현재 요양시설에 거주하신 기간은 얼마나 되셨습니까?",
            options=["1년 미만", "1년 이상 ~ 3년 미만", "3년 이상 ~ 5년 미만", "5년 이상 ~ 10년 미만", "10년 이상"],
            index=0,
            key="residence_duration"
        )
        
        education = st.selectbox(
            "5. 귀하의 최종 학력을 선택해 주십시오",
            options=["무학", "초등학교 졸업", "중학교 졸업", "고등학교 졸업", "대학교(전문대 포함) 졸업 이상"],
            index=0,
            key="education"
        )
        
        drinking_smoking = st.selectbox(
            "6. 귀하는 음주 및 흡연을 하고 계십니까?",
            options=["둘 다 안함", "과거에 음주를 했음", "과거에 흡연을 했음", "현재 음주하고 있음", "현재 흡연하고 있음", "둘 다 하고 있음"],
            index=0,
            key="drinking_smoking"
        )
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'gender': gender,
        'age': age,
        'care_grade': care_grade,
        'residence_duration': residence_duration,
        'education': education,
        'drinking_smoking': drinking_smoking
    })
    
    navigation_buttons()

def show_page2():
    """2페이지: 질환 정보"""
    st.subheader("질환 정보")
    
    data = st.session_state.basic_data
    
    st.write("**7. 귀하가 현재 보유하고 계신 질환을 모두 선택해 주십시오**")
    
    disease_options = [
        "없음", "고혈압", "당뇨병", "고지혈증", "심혈관 질환(심근경색, 협심증, 부정맥 등)",
        "뇌혈관 질환(뇌졸중, 뇌경색, 뇌출혈 등)", "갑상선 질환", "골다공증", "골관절염/류마티스 관절염",
        "암", "만성 폐쇄성 폐질환", "신장 질환", "간 질환", "위장 질환", "빈혈", "치매",
        "파킨슨병", "우울증", "기타"
    ]
    
    existing_diseases = data.get('diseases', [])
    if isinstance(existing_diseases, str):
        existing_diseases = json.loads(existing_diseases) if existing_diseases else []
    
    col1, col2, col3 = st.columns(3)
    selected_diseases = []
    
    for i, disease in enumerate(disease_options):
        with [col1, col2, col3][i % 3]:
            if st.checkbox(disease, value=disease in existing_diseases, key=f"disease_{i}"):
                selected_diseases.append(disease)
    
    if "기타" in selected_diseases:
        other_disease = st.text_input("기타 질환 입력", key="other_disease")
        if other_disease:
            selected_diseases.append(f"기타: {other_disease}")
    
    st.markdown("---")
    
    st.write("**8. 현재 복용 중인 약물 (복수 선택 가능)**")
    
    medication_options = [
        "복용하지 않음", "고혈압약", "당뇨병약", "고지혈증약", "항혈전제", "심장약",
        "갑상선약", "골다공증약", "진통소염제", "항암제", "천식약",
        "신장약", "간약", "위장약", "철분제", "치매약",
        "파킨슨약", "항우울제", "기타"
    ]
    
    existing_medications = data.get('medications', [])
    if isinstance(existing_medications, str):
        existing_medications = json.loads(existing_medications) if existing_medications else []
    
    col1, col2, col3 = st.columns(3)
    selected_medications = []
    
    for i, medication in enumerate(medication_options):
        with [col1, col2, col3][i % 3]:
            if st.checkbox(medication, value=medication in existing_medications, key=f"med_{i}"):
                selected_medications.append(medication)
    
    if "기타" in selected_medications:
        other_medication = st.text_input("기타 약물 입력", key="other_medication")
        if other_medication:
            selected_medications.append(f"기타: {other_medication}")
    
    st.markdown("---")
    
    medication_count = st.selectbox(
        "9. 약물 복용 개수",
        options=["1개", "2개", "3개", "4개 이상"],
        index=0,
        key="medication_count"
    )
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'diseases': json.dumps(selected_diseases, ensure_ascii=False),
        'medications': json.dumps(selected_medications, ensure_ascii=False),
        'medication_count': medication_count
    })
    
    navigation_buttons()

def show_page3():
    """3페이지: 식사 관련 특성"""
    st.subheader("식사 관련 특성")
    
    data = st.session_state.basic_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        chewing_difficulty = st.radio(
            "10. 귀하는 음식을 씹는 데 어려움이 있습니까?",
            options=["예", "아니오"],
            index=0 if data.get('chewing_difficulty') == True else 1,
            key="chewing_difficulty"
        )
        
        swallowing_difficulty = st.radio(
            "11. 귀하는 음식을 삼키는 데 어려움이 있습니까?",
            options=["예", "아니오"],
            index=0 if data.get('swallowing_difficulty') == True else 1,
            key="swallowing_difficulty"
        )
        
        food_preparation_method = st.selectbox(
            "12. 씹기 또는 삼키기에 어려움이 있다면, 귀하가 해당하는 음식 섭취 방법을 선택해 주십시오",
            options=["어렵지 않음", "일반식", "잘게 썬 음식", "갈은 음식", "믹서 음식(유동식)", "기타"],
            index=0,
            key="food_preparation_method"
        )
    
    with col2:
        eating_independence = st.selectbox(
            "13. 귀하는 평소 식사하실 때 어떻게 식사하십니까?",
            options=["스스로 식사할 수 있음", "요양보호사 등의 부분적인 도움 필요", "요양보호사 등의 전적인 도움 필요"],
            index=0,
            key="eating_independence"
        )
        
        meal_type = st.selectbox(
            "14. 귀하는 평소 식사하실 때 어떤 형태의 식사를 드십니까?",
            options=["일반식", "다진식", "연하식", "기타"],
            index=0,
            key="meal_type"
        )
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'chewing_difficulty': chewing_difficulty == "예",
        'swallowing_difficulty': swallowing_difficulty == "예",
        'food_preparation_method': food_preparation_method,
        'eating_independence': eating_independence,
        'meal_type': meal_type
    })
    
    navigation_buttons()

def show_page4():
    """4페이지: 기본 건강 측정치"""
    st.subheader("기본 건강 측정치")
    
    data = st.session_state.basic_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        height = st.number_input(
            "15. 신장 (cm)",
            min_value=0.0,
            max_value=250.0,
            value=float(data.get('height', 0)) if data.get('height') else 0.0,
            step=0.1,
            key="height"
        )
        
        weight = st.number_input(
            "16. 체중 (kg)",
            min_value=0.0,
            max_value=200.0,
            value=float(data.get('weight', 0)) if data.get('weight') else 0.0,
            step=0.1,
            key="weight"
        )
        
        waist = st.number_input(
            "17. 허리둘레 (cm)",
            min_value=0.0,
            max_value=200.0,
            value=float(data.get('waist_circumference', 0)) if data.get('waist_circumference') else 0.0,
            step=0.1,
            key="waist"
        )
        
        # BMI 자동 계산
        if height > 0 and weight > 0:
            bmi = weight / ((height / 100) ** 2)
            st.info(f"BMI: {bmi:.2f} kg/m²")
    
    with col2:
        systolic_bp = st.number_input(
            "18. 수축기 혈압 (mmHg)",
            min_value=0,
            max_value=300,
            value=int(data.get('systolic_bp', 0)) if data.get('systolic_bp') else 0,
            key="systolic_bp"
        )
        
        diastolic_bp = st.number_input(
            "19. 이완기 혈압 (mmHg)",
            min_value=0,
            max_value=200,
            value=int(data.get('diastolic_bp', 0)) if data.get('diastolic_bp') else 0,
            key="diastolic_bp"
        )
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'height': height,
        'weight': weight,
        'waist_circumference': waist,
        'systolic_bp': systolic_bp,
        'diastolic_bp': diastolic_bp
    })
    
    navigation_buttons()

def show_page5_ipaq():
    """5페이지: 신체 활동 수준 조사 (IPAQ-SF)"""
    st.subheader("신체 활동 수준 조사 (IPAQ-SF)")
    
    st.info("📝 지난 7일 동안의 신체 활동에 대해 응답해주세요.")
    
    data = st.session_state.basic_data
    
    st.markdown("### 1. 격렬한 신체 활동")
    st.caption("예: 무거운 물건 들기, 땅 파기, 에어로빅, 빠른 속도로 자전거 타기 등")
    
    col1, col2 = st.columns(2)
    with col1:
        vigorous_days = st.number_input(
            "지난 7일 동안 격렬한 신체 활동을 10분 이상 한 날은 며칠입니까?",
            min_value=0,
            max_value=7,
            value=int(data.get('vigorous_activity_days', 0)) if data.get('vigorous_activity_days') else 0,
            key="vigorous_days"
        )
    
    with col2:
        vigorous_time = st.number_input(
            "그러한 날 중 하루에 보통 얼마나 많은 시간을 격렬한 신체 활동을 하는데 보냈습니까? (분)",
            min_value=0,
            max_value=1440,
            value=int(data.get('vigorous_activity_time', 0)) if data.get('vigorous_activity_time') else 0,
            key="vigorous_time"
        )
    
    st.markdown("---")
    st.markdown("### 2. 중간 정도의 신체 활동")
    st.caption("예: 가벼운 물건 나르기, 보통 속도로 자전거 타기, 복식 테니스 등 (걷기는 제외)")
    
    col1, col2 = st.columns(2)
    with col1:
        moderate_days = st.number_input(
            "지난 7일 동안 중간 정도의 신체 활동을 10분 이상 한 날은 며칠입니까?",
            min_value=0,
            max_value=7,
            value=int(data.get('moderate_activity_days', 0)) if data.get('moderate_activity_days') else 0,
            key="moderate_days"
        )
    
    with col2:
        moderate_time = st.number_input(
            "그러한 날 중 하루에 보통 얼마나 많은 시간을 중간 정도의 신체 활동을 하는데 보냈습니까? (분)",
            min_value=0,
            max_value=1440,
            value=int(data.get('moderate_activity_time', 0)) if data.get('moderate_activity_time') else 0,
            key="moderate_time"
        )
    
    st.markdown("---")
    st.markdown("### 3. 걷기")
    st.caption("직장에서, 집에서, 장소 간 이동, 여가 시간의 모든 걷기를 포함")
    
    col1, col2 = st.columns(2)
    with col1:
        walking_days = st.number_input(
            "지난 7일 동안 10분 이상 걸은 날은 며칠입니까?",
            min_value=0,
            max_value=7,
            value=int(data.get('walking_days', 0)) if data.get('walking_days') else 0,
            key="walking_days"
        )
    
    with col2:
        walking_time = st.number_input(
            "그러한 날 중 하루에 보통 얼마나 많은 시간을 걷는데 보냈습니까? (분)",
            min_value=0,
            max_value=1440,
            value=int(data.get('walking_time', 0)) if data.get('walking_time') else 0,
            key="walking_time"
        )
    
    st.markdown("---")
    st.markdown("### 4. 앉아서 보낸 시간")
    st.caption("책상에 앉아 있거나, 친구를 만나거나, 독서할 때 앉거나, 텔레비전을 앉아서 또는 누워서 시청한 시간이 포함")
    
    sitting_time = st.number_input(
        "지난 7일 동안 평일 하루에 앉아서 보낸 시간은 얼마나 됩니까? (분)",
        min_value=0,
        max_value=1440,
        value=int(data.get('sitting_time', 0)) if data.get('sitting_time') else 0,
        key="sitting_time",
        help="직장, 집, 학교에서 공부/독서, TV 시청, 친구 방문 등 앉아서 보낸 모든 시간 포함"
    )
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'vigorous_activity_days': vigorous_days,
        'vigorous_activity_time': vigorous_time,
        'moderate_activity_days': moderate_days,
        'moderate_activity_time': moderate_time,
        'walking_days': walking_days,
        'walking_time': walking_time,
        'sitting_time': sitting_time
    })
    
    # 활동량 계산 및 표시
    total_vigorous = vigorous_days * vigorous_time * 8.0  # MET
    total_moderate = moderate_days * moderate_time * 4.0  # MET
    total_walking = walking_days * walking_time * 3.3  # MET
    total_met = total_vigorous + total_moderate + total_walking
    
    st.markdown("---")
    st.subheader("📊 신체 활동량 요약")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("격렬한 활동", f"{total_vigorous:.2f} MET-분/주")
    with col2:
        st.metric("중간 활동", f"{total_moderate:.2f} MET-분/주")
    with col3:
        st.metric("걷기", f"{total_walking:.2f} MET-분/주")
    with col4:
        st.metric("총 활동량", f"{total_met:.2f} MET-분/주")
    
    # 활동 수준 분류
    if total_met >= 3000 or (vigorous_days >= 3 and total_vigorous >= 1500):
        activity_level = "높은 신체 활동 (High)"
    elif total_met >= 600 or (vigorous_days >= 3) or (moderate_days + walking_days >= 5 and total_moderate + total_walking >= 600):
        activity_level = "중간 수준의 신체 활동 (Moderate)"
    else:
        activity_level = "낮은 신체 활동 (Low)"
    
    st.info(f"💪 신체 활동 수준: **{activity_level}**")
    
    navigation_buttons()

def show_page6_mna():
    """6페이지: 영양 상태 평가 (MNA-SF)"""
    st.subheader("영양 상태 평가 (MNA-SF)")
    
    st.info("📝 간이 영양 평가 (Mini Nutritional Assessment - Short Form)")
    
    data = st.session_state.basic_data
    
    # BMI 가져오기
    height = data.get('height', 0)
    weight = data.get('weight', 0)
    if height and weight and height > 0:
        bmi = weight / ((height / 100) ** 2)
        st.info(f"📊 기초 조사표 기준 BMI: {bmi:.2f} kg/m²")
    else:
        bmi = None
    
    # === A. 식욕 감퇴 ===
    st.markdown("### A. 지난 3개월 동안 밥맛이 없거나, 소화가 잘 안되거나, 씹고 삼키는 것이 어려워서 식사량이 줄었습니까?")
    
    appetite_options = {
        "많이 줄었다": 0,
        "조금 줄었다": 1,
        "변화 없다": 2
    }
    
    # 기존 값 찾기
    current_appetite_score = data.get('mna_appetite_change', 2)
    current_appetite_text = [k for k, v in appetite_options.items() if v == current_appetite_score][0] if current_appetite_score in appetite_options.values() else "변화 없다"
    
    appetite_change = st.radio(
        "식욕 변화",
        options=list(appetite_options.keys()),
        index=list(appetite_options.keys()).index(current_appetite_text),
        key="mna_appetite_change_radio",
        label_visibility="collapsed"
    )
    appetite_score = appetite_options[appetite_change]
    
    # === B. 체중 감소 ===
    st.markdown("### B. 지난 3개월 동안 몸무게가 줄었습니까?")
    
    weight_options = {
        "3kg 이상 감소": 0,
        "모르겠다": 1,
        "1kg~3kg 감소": 2,
        "변화 없다": 3
    }
    
    current_weight_score = data.get('mna_weight_change', 3)
    current_weight_text = [k for k, v in weight_options.items() if v == current_weight_score][0] if current_weight_score in weight_options.values() else "변화 없다"
    
    weight_change = st.radio(
        "체중 변화",
        options=list(weight_options.keys()),
        index=list(weight_options.keys()).index(current_weight_text),
        key="mna_weight_change_radio",
        label_visibility="collapsed"
    )
    weight_score = weight_options[weight_change]
    
    # === C. 거동 능력 ===
    st.markdown("### C. 거동 능력")
    
    mobility_options = {
        "외출 불가, 침대나 의자에서만 생활 가능": 0,
        "외출 불가, 집에서만 활동 가능": 1,
        "외출 가능, 활동 제약 없음": 2
    }
    
    current_mobility_score = data.get('mna_mobility', 2)
    current_mobility_text = [k for k, v in mobility_options.items() if v == current_mobility_score][0] if current_mobility_score in mobility_options.values() else "외출 가능, 활동 제약 없음"
    
    mobility = st.radio(
        "거동 상태",
        options=list(mobility_options.keys()),
        index=list(mobility_options.keys()).index(current_mobility_text),
        key="mna_mobility_radio",
        label_visibility="collapsed"
    )
    mobility_score = mobility_options[mobility]
    
    # === D. 스트레스 또는 급성 질환 ===
    st.markdown("### D. 지난 3개월 동안 정신적 스트레스를 경험했거나 급성 질환을 앓았던 적이 있습니까?")
    
    stress_options = {
        "예": 0,
        "아니오": 2
    }
    
    current_stress_score = data.get('mna_stress_illness', 2)
    current_stress_text = "아니오" if current_stress_score == 2 else "예"
    
    stress_illness = st.radio(
        "스트레스/질환 여부",
        options=list(stress_options.keys()),
        index=list(stress_options.keys()).index(current_stress_text),
        key="mna_stress_radio",
        label_visibility="collapsed"
    )
    stress_score = stress_options[stress_illness]
    
    # === E. 신경정신학적 문제 ===
    st.markdown("### E. 신경 정신과적 문제")
    
    neuro_options = {
        "중증 치매나 우울증": 0,
        "경증 치매": 1,
        "없음": 2
    }
    
    current_neuro_score = data.get('mna_neuropsychological_problem', 2)
    current_neuro_text = [k for k, v in neuro_options.items() if v == current_neuro_score][0] if current_neuro_score in neuro_options.values() else "없음"
    
    neuropsychological = st.radio(
        "정신과적 문제",
        options=list(neuro_options.keys()),
        index=list(neuro_options.keys()).index(current_neuro_text),
        key="mna_neuro_radio",
        label_visibility="collapsed"
    )
    neuro_score = neuro_options[neuropsychological]
    
    # === F. BMI ===
    st.markdown("### F. 체질량지수 → kg / (m 높이)2")
    
    if bmi:
        # BMI 자동 분류
        if bmi < 19:
            bmi_score = 0
            bmi_text = f"BMI < 19 (현재: {bmi:.2f})"
        elif bmi < 21:
            bmi_score = 1
            bmi_text = f"19 ≤ BMI < 21 (현재: {bmi:.2f})"
        elif bmi < 23:
            bmi_score = 2
            bmi_text = f"21 ≤ BMI < 23 (현재: {bmi:.2f})"
        else:
            bmi_score = 3
            bmi_text = f"BMI ≥ 23 (현재: {bmi:.2f})"
        
        st.info(f"📊 {bmi_text}")
    else:
        bmi_options_manual = {
            "BMI < 19": 0,
            "19 ≤ BMI < 21": 1,
            "21 ≤ BMI < 23": 2,
            "BMI ≥ 23": 3
        }
        
        current_bmi_score = data.get('mna_bmi_category', 3)
        current_bmi_text = [k for k, v in bmi_options_manual.items() if v == current_bmi_score][0] if current_bmi_score in bmi_options_manual.values() else "BMI ≥ 23"
        
        bmi_manual = st.radio(
            "BMI 분류",
            options=list(bmi_options_manual.keys()),
            index=list(bmi_options_manual.keys()).index(current_bmi_text),
            key="mna_bmi_radio"
        )
        bmi_score = bmi_options_manual[bmi_manual]
    
    # 총점 계산
    total_score = appetite_score + weight_score + mobility_score + stress_score + neuro_score + bmi_score
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'mna_appetite_change': appetite_score,
        'mna_weight_change': weight_score,
        'mna_mobility': mobility_score,
        'mna_stress_illness': stress_score,
        'mna_neuropsychological_problem': neuro_score,
        'mna_bmi_category': bmi_score,
        'mna_score': total_score
    })
    
    st.markdown("---")
    st.subheader("📊 MNA-SF 결과")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("총점", f"{total_score}점 / 14점")
    
    with col2:
        if total_score >= 12:
            status = "정상 영양 상태"
            color = "green"
        elif total_score >= 8:
            status = "영양불량 위험"
            color = "orange"
        else:
            status = "영양불량"
            color = "red"
        
        st.markdown(f"### :{color}[{status}]")
    
    st.info("""
    **해석 기준:**
    - 12-14점: 정상 영양 상태
    - 8-11점: 영양불량 위험
    - 0-7점: 영양불량
    """)
    
    navigation_buttons()

def show_page7_kmbi():
    """
    페이지 7: K-MBI (한국판 수정 바델 지수) 평가
    항목별 가중치 반영
    """
    st.header("📋 7. K-MBI (한국판 수정 바델 지수)")
    
    st.info("""
    **K-MBI 평가 안내**
    
    각 항목에 대해 대상자의 현재 수행 능력을 평가해주세요.
    
    ⚠️ **보행과 의자차(휠체어)는 둘 중 하나만 선택**합니다.
    - 보행 가능한 경우: 보행 점수 적용 (100점 만점)
    - 의자차(휠체어) 사용하는 경우: 의자차 점수 적용 (90점 만점)
    """)
    
    # K-MBI 항목별 점수 매핑
    kmbi_items = [
        {
            "name": "개인위생", 
            "description": "세수, 머리 빗기, 칫솔질, 면도 등", 
            "key": "kmbi_1",
            "options": [
                "과제를 수행할 수 없는 경우",
                "최대의 도움이 필요한 경우",
                "중등도의 도움이 필요한 경우",
                "최소한의 도움이 필요하거나 감시가 필요한 경우",
                "완전히 독립적인 경우"
            ],
            "scores": [0, 1, 3, 4, 5]
        },
        {
            "name": "목욕하기", 
            "description": "목욕 또는 샤워", 
            "key": "kmbi_2",
            "options": [
                "과제를 수행할 수 없는 경우",
                "최대의 도움이 필요한 경우",
                "중등도의 도움이 필요한 경우",
                "최소한의 도움이 필요하거나 감시가 필요한 경우",
                "완전히 독립적인 경우"
            ],
            "scores": [0, 1, 3, 4, 5]
        },
        {
            "name": "식사하기", 
            "description": "음식을 먹는 동작", 
            "key": "kmbi_3",
            "options": [
                "과제를 수행할 수 없는 경우",
                "최대의 도움이 필요한 경우",
                "중등도의 도움이 필요한 경우",
                "최소한의 도움이 필요하거나 감시가 필요한 경우",
                "완전히 독립적인 경우"
            ],
            "scores": [0, 2, 5, 8, 10]
        },
        {
            "name": "용변처리", 
            "description": "화장실 사용 및 뒤처리", 
            "key": "kmbi_4",
            "options": [
                "과제를 수행할 수 없는 경우",
                "최대의 도움이 필요한 경우",
                "중등도의 도움이 필요한 경우",
                "최소한의 도움이 필요하거나 감시가 필요한 경우",
                "완전히 독립적인 경우"
            ],
            "scores": [0, 2, 5, 8, 10]
        },
        {
            "name": "계단 오르기", 
            "description": "계단 오르고 내리기", 
            "key": "kmbi_5",
            "options": [
                "과제를 수행할 수 없는 경우",
                "최대의 도움이 필요한 경우",
                "중등도의 도움이 필요한 경우",
                "최소한의 도움이 필요하거나 감시가 필요한 경우",
                "완전히 독립적인 경우"
            ],
            "scores": [0, 2, 5, 8, 10]
        },
        {
            "name": "옷 입기", 
            "description": "옷과 신발 착용", 
            "key": "kmbi_6",
            "options": [
                "과제를 수행할 수 없는 경우",
                "최대의 도움이 필요한 경우",
                "중등도의 도움이 필요한 경우",
                "최소한의 도움이 필요하거나 감시가 필요한 경우",
                "완전히 독립적인 경우"
            ],
            "scores": [0, 2, 5, 8, 10]
        },
        {
            "name": "대변조절", 
            "description": "대변 조절 능력", 
            "key": "kmbi_7",
            "options": [
                "과제를 수행할 수 없는 경우",
                "최대의 도움이 필요한 경우",
                "중등도의 도움이 필요한 경우",
                "최소한의 도움이 필요하거나 감시가 필요한 경우",
                "완전히 독립적인 경우"
            ],
            "scores": [0, 2, 5, 8, 10]
        },
        {
            "name": "소변조절", 
            "description": "소변 조절 능력", 
            "key": "kmbi_8",
            "options": [
                "과제를 수행할 수 없는 경우",
                "최대의 도움이 필요한 경우",
                "중등도의 도움이 필요한 경우",
                "최소한의 도움이 필요하거나 감시가 필요한 경우",
                "완전히 독립적인 경우"
            ],
            "scores": [0, 2, 5, 8, 10]
        },
        {
            "name": "보행", 
            "description": "실내외 이동", 
            "key": "kmbi_9",
            "options": [
                "해당 사항 없음",
                "과제를 수행할 수 없는 경우",
                "최대의 도움이 필요한 경우",
                "중등도의 도움이 필요한 경우",
                "최소한의 도움이 필요하거나 감시가 필요한 경우",
                "완전히 독립적인 경우"
            ],
            "scores": [0, 0, 3, 8, 12, 15],
            "has_na": True
        },
        {
            "name": "의자차(휠체어)", 
            "description": "휠체어 사용", 
            "key": "kmbi_10",
            "options": [
                "해당 사항 없음",
                "과제를 수행할 수 없는 경우",
                "최대의 도움이 필요한 경우",
                "중등도의 도움이 필요한 경우",
                "최소한의 도움이 필요하거나 감시가 필요한 경우",
                "완전히 독립적인 경우"
            ],
            "scores": [0, 0, 1, 3, 4, 5],
            "has_na": True
        },
        {
            "name": "의자/침대 이동", 
            "description": "의자나 침대로의 이동", 
            "key": "kmbi_11",
            "options": [
                "과제를 수행할 수 없는 경우",
                "최대의 도움이 필요한 경우",
                "중등도의 도움이 필요한 경우",
                "최소한의 도움이 필요하거나 감시가 필요한 경우",
                "완전히 독립적인 경우"
            ],
            "scores": [0, 3, 8, 12, 15]
        }
    ]
    
    data = st.session_state.basic_data
    
    # 각 항목 평가
    st.subheader("📝 항목별 평가")
    
    for idx, item in enumerate(kmbi_items, 1):
        with st.container():
            st.markdown(f"### {idx}. {item['name']}")
            st.caption(f"📌 {item['description']}")
            
            # 보행/의자차 선택 안내
            if item['key'] in ['kmbi_9', 'kmbi_10']:
                st.warning("⚠️ 보행과 의자차(휠체어) 중 하나만 선택하세요. 다른 하나는 '해당 사항 없음'으로 체크합니다.")
            
            # 기존 값 가져오기 (점수로 저장되어 있을 수 있음)
            current_value = data.get(item['key'])
            
            # 기존 값이 숫자인 경우 옵션 인덱스로 변환
            if isinstance(current_value, (int, float)):
                try:
                    default_index = item['scores'].index(int(current_value))
                except ValueError:
                    default_index = 0
            elif current_value in item['options']:
                default_index = item['options'].index(current_value)
            else:
                default_index = 0
            
            selected = st.radio(
                f"{item['name']} 수행 수준",
                options=item['options'],
                index=default_index,
                key=f"radio_{item['key']}",
                label_visibility="collapsed",
                horizontal=False
            )
            
            # 선택한 옵션에 해당하는 점수 저장
            selected_index = item['options'].index(selected)
            selected_score = item['scores'][selected_index]
            
            data[item['key']] = selected_score
            
            st.divider()
    
    # 총점 계산 (보행/의자차 중 하나만 반영)
    walking_score = data.get('kmbi_9', 0)
    wheelchair_score = data.get('kmbi_10', 0)
    
    # 보행과 의자차 제외한 나머지 항목 점수 (85점 만점)
    base_score = sum(data.get(item['key'], 0) for item in kmbi_items if item['key'] not in ['kmbi_9', 'kmbi_10'])
    
    # 보행 vs 의자차 선택에 따라 총점과 만점 결정
    if walking_score > 0:
        # 보행 사용: 100점 만점
        total_score = base_score + walking_score
        max_score = 100
        mobility_type = "보행"
    elif wheelchair_score > 0:
        # 의자차 사용: 90점 만점
        total_score = base_score + wheelchair_score
        max_score = 90
        mobility_type = "의자차(휠체어)"
    else:
        # 둘 다 0점인 경우
        total_score = base_score
        max_score = 100
        mobility_type = "미선택"
    
    data['k_mbi_score'] = total_score
    data['k_mbi_max_score'] = max_score
    data['mobility_type'] = mobility_type
    
    # 결과 해석
    st.subheader("📊 K-MBI 평가 결과")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총점", f"{total_score}/{max_score}점")
    
    with col2:
        st.metric("이동 수단", mobility_type)
    
    with col3:
        # 백분율로 의존도 계산
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        if percentage >= 91:
            status = "최소 의존(minimal)"
            status_color = "🟢"
        elif percentage >= 75:
            status = "경도 의존(mild)"
            status_color = "🟡"
        elif percentage >= 50:
            status = "중간 의존(moderate)"
            status_color = "🟠"
        elif percentage >= 25:
            status = "대부분 의존(substantial)"
            status_color = "🔴"
        else:
            status = "완전 의존(full)"
            status_color = "⚫"
        
        st.metric("도움의 수준", f"{status_color} {status}")
    
    # 상태별 해석
    st.info(f"""
    **해석 기준** (총점 기준)
    - 0~24점: 완전 의존(full)
    - 25~49점: 대부분 의존(substantial)
    - 50~74점: 중간 의존(moderate)
    - 75~90점: 경도 의존(mild)
    - 91~99점: 최소 의존(minimal)
    
    **현재 평가**: {total_score}/{max_score}점 ({percentage:.1f}%) - {status}
    **이동 방식**: {mobility_type}
    """)
    
    # 항목별 점수 요약
    st.subheader("📋 항목별 점수 요약")
    
    # 점수대별 그룹화
    score_groups = {
        "독립적 (최고점)": [],
        "최소 도움 필요": [],
        "중등도 도움 필요": [],
        "최대 도움 필요": [],
        "수행 불가/해당없음": []
    }
    
    for item in kmbi_items:
        score = data.get(item['key'], 0)
        max_score_item = max(item['scores'])
        
        if score == max_score_item and score > 0:
            score_groups["독립적 (최고점)"].append(f"{item['name']} ({score}점)")
        elif score >= max_score_item * 0.6:
            score_groups["최소 도움 필요"].append(f"{item['name']} ({score}점)")
        elif score >= max_score_item * 0.3:
            score_groups["중등도 도움 필요"].append(f"{item['name']} ({score}점)")
        elif score > 0:
            score_groups["최대 도움 필요"].append(f"{item['name']} ({score}점)")
        else:
            score_groups["수행 불가/해당없음"].append(f"{item['name']} ({score}점)")
    
    # 그룹별 표시
    level_colors = {
        "독립적 (최고점)": "🟢",
        "최소 도움 필요": "🟡",
        "중등도 도움 필요": "🟠",
        "최대 도움 필요": "🔴",
        "수행 불가/해당없음": "⚫"
    }
    
    for level, items in score_groups.items():
        if items:
            st.markdown(f"{level_colors[level]} **{level}**: {', '.join(items)}")
    
    navigation_buttons()
 

def show_page8_mmse():
    """8페이지: K-MMSE~2 (간이정신상태검사 한국판) 평가"""
    st.subheader("K-MMSE~2 (간이정신상태검사 한국판) 평가")
    
    st.info("📝 인지기능을 평가합니다. 각 항목의 점수를 클릭하여 선택하세요.")
    
    data = st.session_state.basic_data
    
    # MMSE-K 평가 항목 (사진 기준)
    mmse_structure = [
        {
            "category": "기억등록",
            "items": [
                {"name": "비행기", "key": "mmse_reg_airplane", "scores": [0, 1]},
                {"name": "연필", "key": "mmse_reg_pencil", "scores": [0, 1]},
                {"name": "소나무", "key": "mmse_reg_pine", "scores": [0, 1]}
            ]
        },
        {
            "category": "시간지남력",
            "items": [
                {"name": "년", "key": "mmse_time_year", "scores": [0, 1]},
                {"name": "월", "key": "mmse_time_month", "scores": [0, 1]},
                {"name": "일", "key": "mmse_time_day", "scores": [0, 1]},
                {"name": "요일", "key": "mmse_time_weekday", "scores": [0, 1]},
                {"name": "계절", "key": "mmse_time_season", "scores": [0, 1]}
            ]
        },
        {
            "category": "장소지남력",
            "items": [
                {"name": "나라", "key": "mmse_place_country", "scores": [0, 1]},
                {"name": "시/도", "key": "mmse_place_city", "scores": [0, 1]},
                {"name": "무엇하는 곳 또는 구/시·군", "key": "mmse_place_type", "scores": [0, 1]},
                {"name": "현재 장소명", "key": "mmse_place_name", "scores": [0, 1]},
                {"name": "몇 층 또는 동(도로명)/읍·면", "key": "mmse_place_floor", "scores": [0, 1]},
            ]
        },
        {
            "category": "기억회상",
            "items": [
                {"name": "비행기", "key": "mmse_recall_airplane", "scores": [0, 1]},
                {"name": "연필", "key": "mmse_recall_pencil", "scores": [0, 1]},
                {"name": "소나무", "key": "mmse_recall_pine", "scores": [0, 1]}
            ]
        },
        {
            "category": "주의집중 및 계산",
            "items": [
                {"name": "100 - 7", "key": "mmse_calc_1", "scores": [0, 1]},
                {"name": "- 7", "key": "mmse_calc_2", "scores": [0, 1]},
                {"name": "- 7", "key": "mmse_calc_3", "scores": [0, 1]},
                {"name": "- 7", "key": "mmse_calc_4", "scores": [0, 1]},
                {"name": "- 7", "key": "mmse_calc_5", "scores": [0, 1]}
            ]
        },
        {
            "category": "언어",
            "subcategories": [
                {
                    "name": "이름대기",
                    "items": [
                        {"name": "눈, 귀", "key": "mmse_naming", "scores": [0, 1, 2]}
                    ]
                },
                {
                    "name": "따라 말하기",
                    "items": [
                        {"name": "백문이 불여일견", "key": "mmse_repetition", "scores": [0, 1]}
                    ]
                },
                {
                    "name": "이해",
                    "items": [
                        {"name": "동그라미를 가리키고,\n네모를 가리킨 다음, 세모를 가리키세요", "key": "mmse_comprehension", "scores": [0, 1, 2, 3]}
                    ]
                },
                {
                    "name": "읽기",
                    "items": [
                        {"name": "(눈을 감으세요)", "key": "mmse_reading", "scores": [0, 1]}
                    ]
                },
                {
                    "name": "쓰기",
                    "items": [
                        {"name": "오늘 날씨를 한 문장으로 써 보세요.", "key": "mmse_writing", "scores": [0, 1]}
                    ]
                }
            ]
        },
        {
            "category": "그리기",
            "items": [
                {"name": "오각형", "key": "mmse_drawing", "scores": [0, 1]}
            ]
        }
    ]
    
    # 스타일 추가
    st.markdown("""
    <style>
    .mmse-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    .mmse-table th {
        background-color: #2c3e50;
        color: white;
        padding: 12px;
        text-align: center;
        font-weight: bold;
    }
    .mmse-table td {
        border: 1px solid #ddd;
        padding: 10px;
        text-align: center;
    }
    .category-cell {
        background-color: #ecf0f1;
        font-weight: bold;
        text-align: center;
    }
    .subcategory-cell {
        background-color: #f8f9fa;
        font-weight: 600;
        text-align: left;
        padding-left: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    total_score = 0
    
    # 테이블 형태로 표시
    for section in mmse_structure:
        st.markdown(f"### {section['category']}")
        
        # 일반 항목 (언어 제외)
        if 'items' in section:
            for item in section['items']:
                col1, col2, col3 = st.columns([3, 4, 3])
                
                with col1:
                    st.write(f"**{item['name']}**")
                
                with col2:
                    st.write("") # 반응 열 (비워둠)
                
                with col3:
                    # 점수 버튼
                    score_cols = st.columns(len(item['scores']))
                    current_value = int(data.get(item['key'], 0))
                    
                    for idx, score in enumerate(item['scores']):
                        with score_cols[idx]:
                            button_type = "primary" if current_value == score else "secondary"
                            if st.button(
                                str(score), 
                                key=f"{item['key']}_{score}",
                                type=button_type,
                                use_container_width=True
                            ):
                                data[item['key']] = score
                                st.rerun()
                    
                    total_score += current_value
        
        # 언어 섹션 (하위 카테고리 있음)
        elif 'subcategories' in section:
            for subcat in section['subcategories']:
                st.markdown(f"#### {subcat['name']}")
                
                for item in subcat['items']:
                    col1, col2, col3 = st.columns([3, 4, 3])
                    
                    with col1:
                        st.write(f"**{item['name']}**")
                    
                    with col2:
                        st.write("") # 반응 열
                    
                    with col3:
                        # 점수 버튼
                        score_cols = st.columns(len(item['scores']))
                        current_value = int(data.get(item['key'], 0))
                        
                        for idx, score in enumerate(item['scores']):
                            with score_cols[idx]:
                                button_type = "primary" if current_value == score else "secondary"
                                if st.button(
                                    str(score), 
                                    key=f"{item['key']}_{score}",
                                    type=button_type,
                                    use_container_width=True
                                ):
                                    data[item['key']] = score
                                    st.rerun()
                        
                        total_score += current_value
        
        st.markdown("---")
    
    # 총점 표시
    st.markdown("### 📊 K-MMSE-2: 표준형 총점")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("총점", f"{total_score} / 30점")
    
    with col2:
        # 교육 수준별 정상 기준
        education = data.get('education', '')
        
        if '무학' in education:
            cutoff = 19
        elif '초등학교' in education:
            cutoff = 22
        elif '중학교' in education or '고등학교' in education:
            cutoff = 24
        else:
            cutoff = 24
        
        if total_score >= cutoff:
            st.success(f"✅ 정상 인지기능 (기준: ≥{cutoff}점)")
        elif total_score >= cutoff - 4:
            st.warning(f"⚠️ 경도 인지장애 의심 (기준: ≥{cutoff}점)")
        else:
            st.error(f"🚨 인지장애 의심 (기준: ≥{cutoff}점)")
    
    # 교육 수준별 기준 안내
    st.info("""
    **교육 수준별 정상 기준**
    - 무학: ≥19점
    - 초등학교 졸업: ≥22점
    - 중학교 이상: ≥24점
    """)
    
    # ✅ 총점 저장
    data['mmse_score'] = total_score
    
    st.caption("※ 대체문항: 집/시·동-통/도·방/작·지명/소록 (대체문항에 관한 자세한 내용은 사용자 지침서를 참고하시기 바랍니다.)")
    
    navigation_buttons()

def show_page9(supabase, elderly_id, surveyor_id, nursing_home_id):
    """9페이지: 시설 특성 및 제출"""
    st.subheader("시설 특성")
    
    data = st.session_state.basic_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        facility_capacity = st.number_input(
            "시설 규모 (어르신 수용 인원(명))",
            min_value=0,
            max_value=1000,
            value=int(data.get('facility_capacity', 0)) if data.get('facility_capacity') else 0,
            key="facility_capacity"
        )
        
        facility_location = st.selectbox(
            "시설 소재지",
            options=["수도권(서울, 경기, 인천)", "충청권(대전, 세종, 충남, 충북)", 
                    "호남권(광주, 전남, 전북)", "영남권(부산, 대구, 울산, 경남, 경북)", 
                    "강원권", "제주권"],
            index=0,
            key="facility_location"
        )
    
    with col2:
        nutritionist_present = st.radio(
            "영양사 배치 여부",
            options=["예", "아니오"],
            index=0 if data.get('nutritionist_present') == True else 1,
            key="nutritionist_present"
        )
    
    # 데이터 저장
    st.session_state.basic_data.update({
        'facility_capacity': facility_capacity,
        'facility_location': facility_location,
        'nutritionist_present': nutritionist_present == "예"
    })
    
    st.markdown("---")
    
    # 평가 점수 요약
    st.subheader("📊 평가 점수 요약")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        kmbi_score = data.get('k_mbi_score', 0)
        st.metric("K-MBI", f"{kmbi_score}점 / 100점")
        
        if kmbi_score >= 90:
            st.success("독립적")
        elif kmbi_score >= 60:
            st.warning("중등도 의존")
        else:
            st.error("중증 의존")
    
    with col2:
        mmse_score = data.get('mmse_score', 0)
        st.metric("MMSE-K", f"{mmse_score}점 / 30점")
        
        education = data.get('education', '')
        if '무학' in education:
            cutoff = 19
        elif '초등학교' in education:
            cutoff = 22
        else:
            cutoff = 24
        
        if mmse_score >= cutoff:
            st.success("정상 인지기능")
        else:
            st.error("인지장애 의심")
    
    with col3:
        mna_score = data.get('mna_score', 0)
        st.metric("MNA-SF", f"{mna_score}점 / 14점")
        
        if mna_score >= 12:
            st.success("정상 영양 상태")
        elif mna_score >= 8:
            st.warning("영양불량 위험")
        else:
            st.error("영양불량")
    
    st.markdown("---")
    
    # 제출 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            st.session_state.basic_page -= 1
            st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
            # 세션 초기화
            if 'basic_data' in st.session_state:
                del st.session_state.basic_data
            if 'basic_page' in st.session_state:
                del st.session_state.basic_page
            st.session_state.current_survey = None
            st.rerun()
    
    with col3:
        if st.button("✅ 제출", use_container_width=True, type="primary"):
            # 필수 항목 검증
            required_fields = ['gender', 'age', 'care_grade', 'k_mbi_score', 'mmse_score', 'mna_score']
            missing = [f for f in required_fields if not st.session_state.basic_data.get(f)]
            
            if missing:
                st.error(f"필수 항목을 입력해주세요: {', '.join(missing)}")
            else:
                save_basic_survey(supabase, elderly_id, surveyor_id, nursing_home_id)

def save_basic_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    """기초 조사 데이터를 Supabase에 저장"""
    try:
        data = st.session_state.basic_data
        
        # === K-MBI 텍스트→점수 매핑 ===
        kmbi_score_mapping = {
            "과제를 수행할 수 없는 경우": 0,
            "최대의 도움이 필요한 경우": 1,
            "중등도의 도움이 필요한 경우": 2,
            "최소한의 도움이 필요하거나 감시가 필요한 경우": 3,
            "완전히 독립적인 경우": 4
        }
        
        # === 1단계: 테이블 스키마 조회 (먼저!) ===
        try:
            schema_check = supabase.table('basic_survey').select('*').limit(1).execute()
            available_columns = set(schema_check.data[0].keys()) if schema_check.data else set()
        except:
            available_columns = {
                'elderly_id', 'surveyor_id', 'nursing_home_id', 'updated_at',
                'gender', 'age', 'care_grade', 'residence_duration', 'education',
                'drinking_smoking', 'diseases', 'medications', 'medication_count',
                'chewing_difficulty', 'swallowing_difficulty', 'food_preparation_method',
                'eating_independence', 'meal_type', 'height', 'weight',
                'waist_circumference', 'systolic_bp', 'diastolic_bp',
                'facility_capacity', 'facility_location', 'nutritionist_present',
                # IPAQ-SF 필드
                'vigorous_activity_days', 'vigorous_activity_time',
                'moderate_activity_days', 'moderate_activity_time',
                'walking_days', 'walking_time', 'sitting_time',
                # MNA-SF 필드
                'mna_appetite_change', 'mna_weight_change', 'mna_mobility',
                'mna_stress_illness', 'mna_neuropsychological_problem',
                'mna_bmi_category', 'mna_score',
                # K-MBI 필드
                'k_mbi_score', 'k_mbi_max_score', 'mobility_type',
                'kmbi_1', 'kmbi_2', 'kmbi_3', 'kmbi_4', 'kmbi_5', 'kmbi_6',
                'kmbi_7', 'kmbi_8', 'kmbi_9', 'kmbi_10', 'kmbi_11',
                # MMSE-K 필드
                'mmse_score',
                'mmse_reg_airplane', 'mmse_reg_pencil', 'mmse_reg_pine',
                'mmse_time_year', 'mmse_time_month', 'mmse_time_day',
                'mmse_time_weekday', 'mmse_time_season',
                'mmse_place_country', 'mmse_place_city', 'mmse_place_type',
                'mmse_place_name', 'mmse_place_floor',
                'mmse_recall_airplane', 'mmse_recall_pencil', 'mmse_recall_pine',
                'mmse_calc_1', 'mmse_calc_2', 'mmse_calc_3', 'mmse_calc_4', 'mmse_calc_5',
                'mmse_naming', 'mmse_repetition', 'mmse_comprehension',
                'mmse_reading', 'mmse_writing', 'mmse_drawing'
            }
        
        # === 2단계: 기본 필수 데이터 ===
        survey_data = {
            'elderly_id': elderly_id,
            'surveyor_id': surveyor_id,
            'nursing_home_id': nursing_home_id,
            'updated_at': get_kst_now()
        }
        
        # === 3단계: 기존 필드 추가 ===
        field_mapping = {
            'gender': 'gender',
            'age': 'age',
            'care_grade': 'care_grade',
            'residence_duration': 'residence_duration',
            'education': 'education',
            'drinking_smoking': 'drinking_smoking',
            'chewing_difficulty': 'chewing_difficulty',
            'swallowing_difficulty': 'swallowing_difficulty',
            'food_preparation_method': 'food_preparation_method',
            'eating_independence': 'eating_independence',
            'meal_type': 'meal_type',
            'height': 'height',
            'weight': 'weight',
            'waist_circumference': 'waist_circumference',
            'systolic_bp': 'systolic_bp',
            'diastolic_bp': 'diastolic_bp',
            'facility_capacity': 'facility_capacity',
            'facility_location': 'facility_location',
            'nutritionist_present': 'nutritionist_present',
            'medication_count': 'medication_count',
            # IPAQ-SF 필드
            'vigorous_activity_days': 'vigorous_activity_days',
            'vigorous_activity_time': 'vigorous_activity_time',
            'moderate_activity_days': 'moderate_activity_days',
            'moderate_activity_time': 'moderate_activity_time',
            'walking_days': 'walking_days',
            'walking_time': 'walking_time',
            'sitting_time': 'sitting_time',
            # MNA-SF 필드
            'mna_appetite_change': 'mna_appetite_change',
            'mna_weight_change': 'mna_weight_change',
            'mna_mobility': 'mna_mobility',
            'mna_stress_illness': 'mna_stress_illness',
            'mna_neuropsychological_problem': 'mna_neuropsychological_problem',
            'mna_bmi_category': 'mna_bmi_category',
            'mna_score': 'mna_score',
            # K-MBI 추가 필드
            'k_mbi_max_score': 'k_mbi_max_score',
            'mobility_type': 'mobility_type',
            'k_mbi_score': 'k_mbi_score'
        }
        
        for field_key, column_name in field_mapping.items():
            if field_key in data and column_name in available_columns:
                survey_data[column_name] = data[field_key]
        
        # === 4단계: JSON 필드 처리 ===
        if 'diseases' in data and 'diseases' in available_columns:
            if isinstance(data['diseases'], str):
                survey_data['diseases'] = data['diseases']
            else:
                survey_data['diseases'] = json.dumps(data['diseases'], ensure_ascii=False)
        
        if 'medications' in data and 'medications' in available_columns:
            if isinstance(data['medications'], str):
                survey_data['medications'] = data['medications']
            else:
                survey_data['medications'] = json.dumps(data['medications'], ensure_ascii=False)
        
        # === 5단계: K-MBI 데이터 (텍스트→숫자 변환 + 정수 변환) ===
        if 'k_mbi_score' in available_columns:
            if 'k_mbi_score' in data:
                survey_data['k_mbi_score'] = int(round(data['k_mbi_score']))
            
            # K-MBI 각 항목 변환 (텍스트 → 점수)
            for i in range(1, 12):
                col_name = f'kmbi_{i}'
                if col_name in available_columns and col_name in data:
                    value = data[col_name]
                    if isinstance(value, str):
                        survey_data[col_name] = kmbi_score_mapping.get(value, 0)
                    else:
                        survey_data[col_name] = int(value) if value is not None else 0
        
        # === 6단계: MMSE-K 개별 항목 저장 ===
        mmse_individual_fields = [
            # 기억등록
            'mmse_reg_airplane', 'mmse_reg_pencil', 'mmse_reg_pine',
            # 시간지남력
            'mmse_time_year', 'mmse_time_month', 'mmse_time_day', 
            'mmse_time_weekday', 'mmse_time_season',
            # 장소지남력
            'mmse_place_country', 'mmse_place_city', 'mmse_place_type',
            'mmse_place_name', 'mmse_place_floor',
            # 기억회상
            'mmse_recall_airplane', 'mmse_recall_pencil', 'mmse_recall_pine',
            # 주의집중 및 계산
            'mmse_calc_1', 'mmse_calc_2', 'mmse_calc_3', 'mmse_calc_4', 'mmse_calc_5',
            # 언어
            'mmse_naming', 'mmse_repetition', 'mmse_comprehension',
            'mmse_reading', 'mmse_writing',
            # 그리기
            'mmse_drawing'
        ]
        
        for field in mmse_individual_fields:
            if field in data and field in available_columns:
                survey_data[field] = int(data[field]) if data[field] is not None else 0
        
        # 총점
        if 'mmse_score' in data and 'mmse_score' in available_columns:
            survey_data['mmse_score'] = int(data['mmse_score'])
        
        # === 7단계: 기존 데이터 확인 ===
        existing = supabase.table('basic_survey') \
            .select('id') \
            .eq('elderly_id', elderly_id) \
            .execute()
        
        # === 8단계: 저장 실행 ===
        if existing.data:
            result = supabase.table('basic_survey') \
                .update(survey_data) \
                .eq('elderly_id', elderly_id) \
                .execute()
        else:
            result = supabase.table('basic_survey') \
                .insert(survey_data) \
                .execute()
        
        # === 9단계: 진행 상태 업데이트 ===
        try:
            supabase.table('survey_progress') \
                .update({
                    'basic_survey_completed': True,
                    'last_updated': get_kst_now()
                }) \
                .eq('elderly_id', elderly_id) \
                .execute()
        except Exception as e:
            st.warning(f"진행 상태 업데이트 실패: {str(e)}")
        
        # === 10단계: 성공 처리 ===
        st.success("✅ 기초 조사가 성공적으로 저장되었습니다!")
        
        # 저장된 필드 요약
        with st.expander("📊 저장된 데이터 항목"):
            saved_fields = [k for k in survey_data.keys() 
                          if k not in ['elderly_id', 'surveyor_id', 'nursing_home_id', 'updated_at']]
            st.write(f"총 {len(saved_fields)}개 항목 저장됨")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'k_mbi_score' in survey_data:
                    st.metric("K-MBI 총점", f"{survey_data['k_mbi_score']}/100점")
            
            with col2:
                if 'mmse_score' in survey_data:
                    st.metric("MMSE-K 총점", f"{survey_data['mmse_score']}/30점")
            
            with col3:
                if 'mna_score' in survey_data:
                    st.metric("MNA-SF 총점", f"{survey_data['mna_score']}/14점")
        
        # 세션 초기화
        if 'basic_data' in st.session_state:
            del st.session_state.basic_data
        if 'basic_page' in st.session_state:
            del st.session_state.basic_page
        st.session_state.current_survey = None
        
        # 대시보드로 돌아가기 버튼
        if st.button("📊 대시보드로 돌아가기", type="primary"):
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ 저장 중 오류 발생: {str(e)}")
        
        with st.expander("🔍 오류 상세 정보"):
            st.write("**오류 메시지:**")
            st.code(str(e))
            
            import traceback
            st.write("**전체 트레이스백:**")
            st.code(traceback.format_exc())

def navigation_buttons():
    """페이지 이동 버튼"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.basic_page > 1:
            if st.button("⬅️ 이전", use_container_width=True):
                st.session_state.basic_page -= 1
                st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
            # 세션 초기화
            if 'basic_data' in st.session_state:
                del st.session_state.basic_data
            if 'basic_page' in st.session_state:
                del st.session_state.basic_page
            st.session_state.current_survey = None
            st.rerun()
    
    with col3:
        if st.session_state.basic_page < 9:
            if st.button("다음 ➡️", use_container_width=True, type="primary"):
                st.session_state.basic_page += 1
                st.rerun()

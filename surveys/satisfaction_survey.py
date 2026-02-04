import streamlit as st
import json
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo('Asia/Seoul')

def get_kst_now():
    """현재 한국 시간 반환"""
    return datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')

def show_satisfaction_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    st.title("😊 3. 만족도 및 선호도 조사표")
    
    # 진행 상태 초기화
    if 'satisfaction_page' not in st.session_state:
        st.session_state.satisfaction_page = 1
    
    # 기존 데이터 불러오기
    if 'satisfaction_data' not in st.session_state:
        try:
            response = supabase.table('satisfaction_survey').select('*').eq('elderly_id', elderly_id).execute()
            if response.data:
                st.session_state.satisfaction_data = response.data[0]
            else:
                st.session_state.satisfaction_data = {}
        except:
            st.session_state.satisfaction_data = {}
    
    # 페이지 진행 표시
    total_pages = 4
    st.progress(st.session_state.satisfaction_page / total_pages)
    st.caption(f"페이지 {st.session_state.satisfaction_page} / {total_pages}")
    
    # 페이지별 내용
    if st.session_state.satisfaction_page == 1:
        show_page1()
    elif st.session_state.satisfaction_page == 2:
        show_page2()
    elif st.session_state.satisfaction_page == 3:
        show_page3()
    elif st.session_state.satisfaction_page == 4:
        show_page4(supabase, elderly_id, surveyor_id, nursing_home_id)

def show_page1():
    """1페이지: 급식 만족도"""
    st.subheader("급식 만족도")
    
    data = st.session_state.satisfaction_data
    
    st.info("📝 현재 제공받는 급식에 대한 만족도를 평가해주세요.")
    
    # === 1. 전반적인 급식 만족도 ===
    st.markdown("### 1. 급식에 대해 전반적으로 얼마나 만족하십니까?")
    
    overall_options = {
        "매우 불만족": 1,
        "불만족": 2,
        "보통": 3,
        "만족": 4,
        "매우 만족": 5
    }
    
    current_overall = data.get('overall_satisfaction', 3)
    current_overall_text = [k for k, v in overall_options.items() if v == current_overall][0] if current_overall in overall_options.values() else "보통"
    
    overall_satisfaction = st.radio(
        "전반적 만족도",
        options=list(overall_options.keys()),
        index=list(overall_options.keys()).index(current_overall_text),
        key="overall_satisfaction_radio",
        horizontal=True,
        label_visibility="collapsed"
    )
    overall_score = overall_options[overall_satisfaction]
    
    # === 2. 급식 양의 적절성 ===
    st.markdown("### 2. 제공되는 급식의 양은 적절합니까?")
    
    portion_options = {
        "매우 부족": 1,
        "부족": 2,
        "적당": 3,
        "많음": 4,
        "매우 많음": 5
    }
    
    current_portion = data.get('portion_adequacy', 3)
    current_portion_text = [k for k, v in portion_options.items() if v == current_portion][0] if current_portion in portion_options.values() else "적당"
    
    portion_adequacy = st.radio(
        "양의 적절성",
        options=list(portion_options.keys()),
        index=list(portion_options.keys()).index(current_portion_text),
        key="portion_adequacy_radio",
        horizontal=True,
        label_visibility="collapsed"
    )
    portion_score = portion_options[portion_adequacy]
    
    # === 3. 급식 품질 만족도 ===
    st.markdown("### 3. 급식의 맛과 품질에 만족하십니까?")
    
    quality_options = {
        "매우 불만족": 1,
        "불만족": 2,
        "보통": 3,
        "만족": 4,
        "매우 만족": 5
    }
    
    current_quality = data.get('food_quality', 3)
    current_quality_text = [k for k, v in quality_options.items() if v == current_quality][0] if current_quality in quality_options.values() else "보통"
    
    food_quality = st.radio(
        "품질 만족도",
        options=list(quality_options.keys()),
        index=list(quality_options.keys()).index(current_quality_text),
        key="food_quality_radio",
        horizontal=True,
        label_visibility="collapsed"
    )
    quality_score = quality_options[food_quality]
    
    # 데이터 저장
    st.session_state.satisfaction_data.update({
        'overall_satisfaction': overall_score,
        'portion_adequacy': portion_score,
        'food_quality': quality_score
    })
    
    # 선택 사항 요약 표시 (optional)
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("전반적 만족도", f"{overall_score}/5")
    with col2:
        st.metric("양의 적절성", f"{portion_score}/5")
    with col3:
        st.metric("품질 만족도", f"{quality_score}/5")
    
    navigation_buttons()

def show_page2():
    """2페이지: 식품 선호도"""
    st.subheader("식품 선호도")
    
    data = st.session_state.satisfaction_data
    
    st.markdown("### 1. 선호하는 식품군 (복수 선택 가능)")
    
    food_groups = [
        "밥⸳죽류",
        "국⸳찌개류",
        "고기류",
        "생선⸳해산물류",
        "채소⸳나물류",
        "두부⸳콩류",
        "채소류",
        "과일",
        "기타",
    ]
    
    existing_food_groups = data.get('preferred_food_groups', [])
    if isinstance(existing_food_groups, str):
        existing_food_groups = json.loads(existing_food_groups) if existing_food_groups else []
    
    selected_food_groups = []
    col1, col2 = st.columns(2)
    
    for i, food_group in enumerate(food_groups):
        with [col1, col2][i % 2]:
            if st.checkbox(food_group, value=food_group in existing_food_groups, key=f"food_group_{i}"):
                selected_food_groups.append(food_group)
    
    st.markdown("---")
    st.markdown("### 2. 선호하는 조리 방법 (복수 선택 가능)")
    
    cooking_methods = [
        "찌기",
        "삶기",
        "굽기",
        "볶기",
        "튀기기",
        "조림",
        "무침",
        "국/탕/찌개",
        "생식 (회, 샐러드 등)"
    ]
    
    existing_cooking = data.get('preferred_cooking_methods', [])
    if isinstance(existing_cooking, str):
        existing_cooking = json.loads(existing_cooking) if existing_cooking else []
    
    selected_cooking = []
    col1, col2 = st.columns(2)
    
    for i, method in enumerate(cooking_methods):
        with [col1, col2][i % 2]:
            if st.checkbox(method, value=method in existing_cooking, key=f"cooking_{i}"):
                selected_cooking.append(method)
    
    st.markdown("---")
    st.markdown("### 3. 급식 개선 사항")
    
    improvement_suggestions = st.text_area(
        "급식에서 개선되었으면 하는 점이 있다면 자유롭게 작성해주세요.",
        value=data.get('improvement_suggestions', ''),
        height=150,
        key="improvement_suggestions"
    )
    
    # 데이터 저장
    st.session_state.satisfaction_data.update({
        'preferred_food_groups': json.dumps(selected_food_groups, ensure_ascii=False),
        'preferred_cooking_methods': json.dumps(selected_cooking, ensure_ascii=False),
        'improvement_suggestions': improvement_suggestions
    })
    
    navigation_buttons()

def show_page3():
    """3페이지: 고령친화우수식품 평가"""
    st.subheader("고령친화우수식품 평가")
    
    st.info("📝 다음 4가지 제품을 시식하고 평가해주세요.")
    
    data = st.session_state.satisfaction_data
    
    # 평가 척도 정의
    taste_options = ["매우 맛없음", "맛없음", "보통", "맛있음", "매우 맛있음"]
    ease_options = ["매우 어려움", "어려움", "보통", "쉬움", "매우 쉬움"]
    satisfaction_options = ["매우 불만족", "불만족", "보통", "만족", "매우 만족"]
    repurchase_options = ["매우 낮음", "낮음", "보통", "높음", "매우 높음"]
    
    products = [
        {
            'name': '오쉐프 간편 고등어구이',
            'prefix': 'product_1'
        },
        {
            'name': '정옥 재첩국',
            'prefix': 'product_2'
        },
        {
            'name': '해물동그랑땡조림',
            'prefix': 'product_3'
        }
    ]
    
    # CSS 스타일
    st.markdown("""
    <style>
    .product-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        font-size: 18px;
        font-weight: bold;
    }
    .evaluation-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    for i, product in enumerate(products):
        st.markdown(f'<div class="product-card">제품 {i+1}: {product["name"]}</div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="evaluation-section">', unsafe_allow_html=True)
            
            # 맛
            st.markdown("##### 1-1. 해당 제품의 맛은 어떠십니까?")
            taste = st.radio(
                "맛 평가",
                options=taste_options,
                index=int(data.get(f"{product['prefix']}_taste", 3)) - 1 if data.get(f"{product['prefix']}_taste") else 2,
                key=f"{product['prefix']}_taste_radio",
                horizontal=True,
                label_visibility="collapsed"
            )
            taste_score = taste_options.index(taste) + 1
            
            st.markdown("---")
            
            # 씹기 편함
            st.markdown("##### 1-2. 해당 제품은 씹기 어떠십니까?")
            chewing = st.radio(
                "씹기 평가",
                options=ease_options,
                index=int(data.get(f"{product['prefix']}_chewing", 3)) - 1 if data.get(f"{product['prefix']}_chewing") else 2,
                key=f"{product['prefix']}_chewing_radio",
                horizontal=True,
                label_visibility="collapsed"
            )
            # 쉬움이 높은 점수가 되도록 역변환
            chewing_score = 6 - (ease_options.index(chewing) + 1)
            
            st.markdown("---")
            
            # 삼키기 편함
            st.markdown("##### 1-3. 해당 제품은 삼키기 어떠십니까?")
            swallowing = st.radio(
                "삼키기 평가",
                options=ease_options,
                index=int(data.get(f"{product['prefix']}_swallowing", 3)) - 1 if data.get(f"{product['prefix']}_swallowing") else 2,
                key=f"{product['prefix']}_swallowing_radio",
                horizontal=True,
                label_visibility="collapsed"
            )
            # 쉬움이 높은 점수가 되도록 역변환
            swallowing_score = 6 - (ease_options.index(swallowing) + 1)
            
            st.markdown("---")
            
            # 전반적 만족도
            st.markdown("##### 1-4. 해당 제품에 전반적으로 만족하십니까?")
            satisfaction = st.radio(
                "만족도 평가",
                options=satisfaction_options,
                index=int(data.get(f"{product['prefix']}_satisfaction", 3)) - 1 if data.get(f"{product['prefix']}_satisfaction") else 2,
                key=f"{product['prefix']}_satisfaction_radio",
                horizontal=True,
                label_visibility="collapsed"
            )
            satisfaction_score = satisfaction_options.index(satisfaction) + 1
            
            st.markdown("---")
            
            # 재구매 의향
            st.markdown("##### 1-5. 해당 제품을 또 드시고 싶으십니까?")
            repurchase = st.radio(
                "재구매 의향",
                options=repurchase_options,
                index=int(data.get(f"{product['prefix']}_repurchase", 3)) - 1 if data.get(f"{product['prefix']}_repurchase") else 2,
                key=f"{product['prefix']}_repurchase_radio",
                horizontal=True,
                label_visibility="collapsed"
            )
            repurchase_score = repurchase_options.index(repurchase) + 1
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 평균 점수 표시
            avg_score = (taste_score + chewing_score + swallowing_score + satisfaction_score + repurchase_score) / 5
            
            # 점수에 따른 색상
            if avg_score >= 4:
                color = "green"
                status = "우수"
            elif avg_score >= 3:
                color = "blue"
                status = "양호"
            else:
                color = "orange"
                status = "보통"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background-color: #f0f2f6; 
                        border-radius: 10px; margin: 15px 0; border-left: 5px solid {color};">
                <h3 style="margin: 0; color: {color};">평균 평점: {avg_score:.1f}점 ({status})</h3>
                <p style="margin: 5px 0 0 0; color: #666;">
                    맛: {taste} | 씹기: {chewing} | 삼키기: {swallowing}<br>
                    만족도: {satisfaction} | 재구매: {repurchase}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # 데이터 저장 (점수로 변환하여 저장)
            st.session_state.satisfaction_data.update({
                f"{product['prefix']}_taste": taste_score,
                f"{product['prefix']}_chewing": chewing_score,
                f"{product['prefix']}_swallowing": swallowing_score,
                f"{product['prefix']}_satisfaction": satisfaction_score,
                f"{product['prefix']}_repurchase": repurchase_score
            })
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    navigation_buttons()

def show_page4(supabase, elderly_id, surveyor_id, nursing_home_id):
    """4페이지: 종합 평가 및 제출"""
    st.subheader("종합 평가")
    
    data = st.session_state.satisfaction_data
    
    st.markdown("### 1. 고령친화우수식품 전반적 만족도")
    
    satisfaction_options = ["매우 불만족", "불만족", "보통", "만족", "매우 만족"]
    
    overall_product_satisfaction = st.radio(
        "시식한 고령친화우수식품에 대해 전반적으로 얼마나 만족하십니까?",
        options=satisfaction_options,
        index=int(data.get('overall_product_satisfaction', 3)) - 1 if data.get('overall_product_satisfaction') else 2,
        key="overall_product_satisfaction_radio",
        horizontal=True
    )
    
    overall_product_satisfaction_score = satisfaction_options.index(overall_product_satisfaction) + 1
    
    st.markdown("---")
    st.markdown("### 2. 드시고 싶은 조리 형태의 수산물 활용 고령친화우수식품을 모두 선택해주세요. (복수 선택 가능)")
    
    cooking_types = [
        "구이",
        "조림",
        "찜",
        "튀김",
        "무침",
        "회",
        "국/탕/찌개",
        "볶음",
        "젓갈",
        "기타"
    ]
    
    existing_cooking_types = data.get('desired_cooking_types', [])
    if isinstance(existing_cooking_types, str):
        existing_cooking_types = json.loads(existing_cooking_types) if existing_cooking_types else []
    
    selected_cooking_types = []
    col1, col2, col3 = st.columns(3)
    
    for i, cooking_type in enumerate(cooking_types):
        with [col1, col2, col3][i % 3]:
            if st.checkbox(cooking_type, value=cooking_type in existing_cooking_types, key=f"cooking_type_{i}"):
                selected_cooking_types.append(cooking_type)
    
    st.markdown("---")
    st.markdown("### 3. 드시고 싶은 종류의 수산물 활용 고령친화우수식품을 모두 선택해주세요. (복수 선택 가능)")
    
    seafood_types = [
        "고등어",
        "갈치",
        "삼치",
        "연어",
        "광어",
        "오징어",
        "낙지",
        "문어",
        "새우",
        "조개류",
        "멸치",
        "명란",
        "기타"
    ]
    
    existing_seafood = data.get('desired_seafood_types', [])
    if isinstance(existing_seafood, str):
        existing_seafood = json.loads(existing_seafood) if existing_seafood else []
    
    selected_seafood = []
    col1, col2, col3 = st.columns(3)
    
    for i, seafood in enumerate(seafood_types):
        with [col1, col2, col3][i % 3]:
            if st.checkbox(seafood, value=seafood in existing_seafood, key=f"seafood_{i}"):
                selected_seafood.append(seafood)
    
    # 데이터 저장
    st.session_state.satisfaction_data.update({
        'overall_product_satisfaction': overall_product_satisfaction_score,
        'desired_cooking_types': json.dumps(selected_cooking_types, ensure_ascii=False),
        'desired_seafood_types': json.dumps(selected_seafood, ensure_ascii=False)
    })
    
    st.markdown("---")
    
    # 응답 요약
    st.subheader("📊 응답 요약")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 급식 만족도")
        satisfaction_level = data.get('overall_satisfaction', 0)
        portion_level = data.get('portion_adequacy', 0)
        quality_level = data.get('food_quality', 0)
        
        st.metric("전반적 만족도", f"{satisfaction_level}점")
        st.metric("양 적절성", f"{portion_level}점")
        st.metric("품질 만족도", f"{quality_level}점")
        
        avg_meal_satisfaction = (satisfaction_level + portion_level + quality_level) / 3
        st.info(f"평균: **{avg_meal_satisfaction:.1f}점**")
    
    with col2:
        st.markdown("#### 제품 평가")
        
        product_names = [
            "고운오징어젓",
            "화덕에 미치다",
            "오쉐프 고등어",
            "해물동그랑땡"
        ]
        
        # 각 제품의 평균 점수 계산
        for i in range(1, 5):
            prefix = f"product_{i}"
            scores = [
                data.get(f"{prefix}_taste", 0),
                data.get(f"{prefix}_chewing", 0),
                data.get(f"{prefix}_swallowing", 0),
                data.get(f"{prefix}_satisfaction", 0),
                data.get(f"{prefix}_repurchase", 0)
            ]
            avg = sum(scores) / len(scores) if scores else 0
            st.metric(product_names[i-1], f"{avg:.1f}점")
        
        st.info(f"전반적 만족도: **{overall_product_satisfaction_score}점**")
    
    # 선호도 요약
    st.markdown("---")
    st.markdown("#### 선호도 요약")
    
    col1, col2 = st.columns(2)
    with col1:
        if selected_cooking_types:
            st.write("**선호 조리법:**", ", ".join(selected_cooking_types))
        else:
            st.write("**선호 조리법:** 선택 안 함")
    
    with col2:
        if selected_seafood:
            st.write("**선호 수산물:**", ", ".join(selected_seafood))
        else:
            st.write("**선호 수산물:** 선택 안 함")
    
    st.markdown("---")
    
    # 제출 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            st.session_state.satisfaction_page -= 1
            st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
            # 세션 초기화
            if 'satisfaction_data' in st.session_state:
                del st.session_state.satisfaction_data
            if 'satisfaction_page' in st.session_state:
                del st.session_state.satisfaction_page
            st.session_state.current_survey = None
            st.rerun()
    
    with col3:
        if st.button("✅ 제출", use_container_width=True, type="primary"):
            save_satisfaction_survey(supabase, elderly_id, surveyor_id, nursing_home_id)

def save_satisfaction_survey(supabase, elderly_id, surveyor_id, nursing_home_id):
    """설문 데이터 저장"""
    try:
        data = st.session_state.satisfaction_data.copy()
        data.update({
            'elderly_id': elderly_id,
            'surveyor_id': surveyor_id,
            'nursing_home_id': nursing_home_id,
            'updated_at': get_kst_now()
        })
        
        # 기존 데이터 확인
        response = supabase.table('satisfaction_survey').select('id').eq('elderly_id', elderly_id).execute()
        
        if response.data:
            # 업데이트
            supabase.table('satisfaction_survey').update(data).eq('elderly_id', elderly_id).execute()
        else:
            # 새로 추가
            supabase.table('satisfaction_survey').insert(data).execute()
        
        # 진행 상황 업데이트
        progress_update = {
            'satisfaction_survey_completed': True,
            'last_updated': get_kst_now()
        }
        
        # 모든 설문 완료 여부 확인
        progress_response = supabase.table('survey_progress').select('*').eq('elderly_id', elderly_id).execute()
        if progress_response.data:
            progress = progress_response.data[0]
            if progress.get('basic_survey_completed') and progress.get('nutrition_survey_completed'):
                progress_update['all_surveys_completed'] = True
        
        supabase.table('survey_progress').update(progress_update).eq('elderly_id', elderly_id).execute()
        
        st.success("✅ 만족도 및 선호도 조사표가 저장되었습니다!")
        
        if progress_update.get('all_surveys_completed'):
            st.success("🎉 모든 설문이 완료되었습니다! 수고하셨습니다!")
        
        # 세션 초기화
        del st.session_state.satisfaction_data
        del st.session_state.satisfaction_page
        st.session_state.current_survey = None
        
        
        if st.button("대시보드로 돌아가기"):
            st.rerun()
        
    except Exception as e:
        st.error(f"저장 중 오류가 발생했습니다: {str(e)}")

def navigation_buttons():
    """페이지 이동 버튼"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.satisfaction_page > 1:
            if st.button("⬅️ 이전", use_container_width=True):
                st.session_state.satisfaction_page -= 1
                st.rerun()
    
    with col2:
        if st.button("🏠 대시보드", use_container_width=True):
            # 세션 초기화
            if 'satisfaction_data' in st.session_state:
                del st.session_state.satisfaction_data
            if 'satisfaction_page' in st.session_state:
                del st.session_state.satisfaction_page
            st.session_state.current_survey = None
            st.rerun()
    
    with col3:
        if st.session_state.satisfaction_page < 4:
            if st.button("다음 ➡️", use_container_width=True, type="primary"):
                st.session_state.satisfaction_page += 1
                st.rerun()

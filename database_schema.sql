-- 요양원 테이블
CREATE TABLE nursing_homes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 조사원 테이블
CREATE TABLE surveyors (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    nursing_home_id TEXT REFERENCES nursing_homes(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 어르신 테이블
CREATE TABLE elderly_residents (
    id TEXT PRIMARY KEY,
    name TEXT,
    nursing_home_id TEXT REFERENCES nursing_homes(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 설문 진행 상황 테이블
CREATE TABLE survey_progress (
    id SERIAL PRIMARY KEY,
    elderly_id TEXT REFERENCES elderly_residents(id) UNIQUE,
    surveyor_id TEXT REFERENCES surveyors(id),
    nursing_home_id TEXT REFERENCES nursing_homes(id),
    basic_survey_completed BOOLEAN DEFAULT FALSE,
    nutrition_survey_completed BOOLEAN DEFAULT FALSE,
    satisfaction_survey_completed BOOLEAN DEFAULT FALSE,
    all_surveys_completed BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- 기초 조사표 데이터
CREATE TABLE basic_survey (
    id SERIAL PRIMARY KEY,
    elderly_id TEXT REFERENCES elderly_residents(id) UNIQUE,
    nursing_home_id TEXT REFERENCES nursing_homes(id),
    surveyor_id TEXT REFERENCES surveyors(id),
    
    -- 인구통계학적 특성
    gender TEXT,
    age INTEGER,
    care_grade TEXT,
    residence_duration TEXT,
    education TEXT,
    drinking_smoking TEXT,
    
    -- 질환 관련
    diseases JSONB,
    medications JSONB,
    medication_count TEXT,
    
    -- 식사 관련
    chewing_difficulty BOOLEAN,
    swallowing_difficulty BOOLEAN,
    food_preparation_method TEXT,
    eating_independence TEXT,
    meal_type TEXT,
    
    -- 기능/건강 상태
    height DECIMAL,
    weight DECIMAL,
    waist_circumference DECIMAL,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    k_mbi_score INTEGER,
    mmse_score INTEGER,
    
    -- 시설 특성
    facility_capacity INTEGER,
    facility_location TEXT,
    nutritionist_present BOOLEAN,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 영양 조사표 데이터
CREATE TABLE nutrition_survey (
    id SERIAL PRIMARY KEY,
    elderly_id TEXT REFERENCES elderly_residents(id) UNIQUE,
    nursing_home_id TEXT REFERENCES nursing_homes(id),
    surveyor_id TEXT REFERENCES surveyors(id),
    
    -- 5일간 식사 데이터 (JSON 형태로 저장)
    meal_portions JSONB,
    plate_waste JSONB,
    
    -- 신체 활동 수준
    vigorous_activity_days INTEGER,
    vigorous_activity_time INTEGER,
    moderate_activity_days INTEGER,
    moderate_activity_time INTEGER,
    walking_days INTEGER,
    walking_time INTEGER,
    sitting_time INTEGER,
    
    -- 영양 상태 평가 (MNA-SF)
    appetite_change INTEGER,
    weight_change INTEGER,
    mobility INTEGER,
    stress_illness INTEGER,
    neuropsychological_problem INTEGER,
    bmi_category INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 만족도 및 선호도 조사표
CREATE TABLE satisfaction_survey (
    id SERIAL PRIMARY KEY,
    elderly_id TEXT REFERENCES elderly_residents(id) UNIQUE,
    nursing_home_id TEXT REFERENCES nursing_homes(id),
    surveyor_id TEXT REFERENCES surveyors(id),
    
    -- 급식 만족도
    overall_satisfaction INTEGER,
    portion_adequacy INTEGER,
    food_quality INTEGER,
    
    -- 식품 선호도
    preferred_food_groups JSONB,
    preferred_cooking_methods JSONB,
    improvement_suggestions TEXT,
    
    -- 블루푸드 선호도
    bluefood_preferences JSONB,
    
    -- 고령친화우수식품 평가
    product_1_name TEXT DEFAULT '고운오징어젓',
    product_1_taste INTEGER,
    product_1_chewing INTEGER,
    product_1_swallowing INTEGER,
    product_1_satisfaction INTEGER,
    product_1_repurchase INTEGER,
    
    product_2_name TEXT DEFAULT '화덕에 미치다 500도 고등어구이',
    product_2_taste INTEGER,
    product_2_chewing INTEGER,
    product_2_swallowing INTEGER,
    product_2_satisfaction INTEGER,
    product_2_repurchase INTEGER,
    
    product_3_name TEXT DEFAULT '오쉐프 간편 고등어구이',
    product_3_taste INTEGER,
    product_3_chewing INTEGER,
    product_3_swallowing INTEGER,
    product_3_satisfaction INTEGER,
    product_3_repurchase INTEGER,
    
    product_4_name TEXT DEFAULT '해물동그랑땡 행복한맛남',
    product_4_taste INTEGER,
    product_4_chewing INTEGER,
    product_4_swallowing INTEGER,
    product_4_satisfaction INTEGER,
    product_4_repurchase INTEGER,
    
    overall_product_satisfaction INTEGER,
    desired_cooking_types JSONB,
    desired_seafood_types JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_survey_progress_elderly ON survey_progress(elderly_id);
CREATE INDEX idx_basic_survey_elderly ON basic_survey(elderly_id);
CREATE INDEX idx_nutrition_survey_elderly ON nutrition_survey(elderly_id);
CREATE INDEX idx_satisfaction_survey_elderly ON satisfaction_survey(elderly_id);

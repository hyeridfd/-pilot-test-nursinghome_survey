# 요양원 건강 및 블루푸드 설문조사 시스템

## 📋 프로젝트 개요

요양원 어르신을 대상으로 한 건강 설문조사 시스템입니다. Streamlit과 Supabase를 활용하여 웹 기반 설문 조사를 수행할 수 있습니다.

### 주요 기능

1. **로그인 시스템**
   - 요양원 ID, 조사원 ID, 어르신 ID 기반 인증
   - 관리자 대시보드 (비밀번호: admin123)

2. **3가지 설문 조사**
   - 기초 조사표 (건강설문): 인구통계, 질환, 식사특성, 건강상태, 시설특성
   - 영양 조사표: 신체활동(IPAQ-SF), 영양상태(MNA-SF)
   - 만족도 및 선호도 조사표: 급식만족도, 식품선호도, 고령친화우수식품 평가

3. **관리자 기능**
   - 요양원/조사원/어르신 관리
   - 설문 진행 현황 모니터링
   - 완료율 통계

## 🚀 설치 방법

### 1. 필수 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)
- Supabase 계정

### 2. 프로젝트 클론 또는 다운로드

```bash
cd survey_app_final
```

### 3. 가상환경 생성 (권장)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 4. 패키지 설치

```bash
pip install -r requirements.txt
```

### 5. Supabase 설정

#### 5.1 Supabase 프로젝트 생성

1. [Supabase](https://supabase.com/)에 로그인
2. 새 프로젝트 생성
3. 프로젝트 URL과 anon/public key 확인

#### 5.2 데이터베이스 스키마 생성

1. Supabase 대시보드 → SQL Editor로 이동
2. `database_schema.sql` 파일의 내용을 복사하여 실행

#### 5.3 초기 데이터 입력

1. `sample_data.sql` 파일의 내용을 SQL Editor에서 실행
2. 또는 관리자 대시보드를 통해 수동으로 데이터 입력

### 6. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 실제 값을 입력:

```bash
cp .env.example .env
```

`.env` 파일 내용:
```
SUPABASE_URL=your_actual_supabase_url
SUPABASE_KEY=your_actual_supabase_anon_key
ADMIN_PASSWORD=admin123
```

### 7. 애플리케이션 실행

```bash
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501` 열림

## 📊 데이터베이스 구조

### 주요 테이블

1. **nursing_homes** - 요양원 정보
2. **surveyors** - 조사원 정보
3. **elderly_residents** - 어르신 정보
4. **survey_progress** - 설문 진행 상황
5. **basic_survey** - 기초 조사표 응답
6. **nutrition_survey** - 영양 조사표 응답
7. **satisfaction_survey** - 만족도 조사표 응답

## 🔐 기본 로그인 정보

### 관리자
- 비밀번호: `admin123`

### 샘플 사용자 (sample_data.sql 실행 후)
- 요양원 ID: `NH001`
- 조사원 ID: `SV001`
- 어르신 ID: `EL001`

## 📝 사용 방법

### 일반 사용자 (조사원)

1. 로그인 페이지에서 요양원 ID, 조사원 ID, 어르신 ID 입력
2. 설문 선택 대시보드에서 원하는 설문 선택
3. 페이지별로 질문에 답변
4. 각 페이지 하단의 "다음" 버튼으로 이동
5. 마지막 페이지에서 "제출" 버튼으로 저장

### 관리자

1. 로그인 페이지 하단 "관리자 로그인" 확장
2. 비밀번호 입력 (기본값: admin123)
3. 대시보드에서 데이터 조회 및 통계 확인

## 🎨 주요 기능 상세

### 기초 조사표 (5페이지)
- **페이지 1**: 성별, 연령, 장기요양등급, 거주기간 등
- **페이지 2**: 질환 정보 및 약물 복용 현황
- **페이지 3**: 식사 관련 특성 (씹기/삼키기 어려움, 식사 독립성 등)
- **페이지 4**: 신체계측 (신장, 체중, 혈압 등), K-MBI, MMSE 점수
- **페이지 5**: 시설 특성 (정원, 소재지, 영양사 배치 등)

### 영양 조사표 (2페이지)
- **페이지 1**: 신체 활동 수준 (IPAQ-SF)
  - 격렬한/중간/걷기 활동 빈도 및 시간
  - MET 자동 계산 및 활동 수준 분류
- **페이지 2**: 영양 상태 평가 (MNA-SF)
  - 6개 항목 평가
  - 자동 점수 계산 및 영양 상태 분류

### 만족도 및 선호도 조사표 (4페이지)
- **페이지 1**: 급식 만족도 (전반적, 양, 품질)
- **페이지 2**: 식품 선호도 및 조리 방법
- **페이지 3**: 고령친화우수식품 4개 제품 평가
  - 고운오징어젓
  - 화덕에 미치다 500도 고등어구이
  - 오쉐프 간편 고등어구이
  - 해물동그랑땡 행복한맛남
- **페이지 4**: 수산물 조리 형태 및 종류 선호도

## 🔧 문제 해결

### Supabase 연결 오류
- `.env` 파일의 URL과 KEY가 정확한지 확인
- Supabase 프로젝트가 활성화되어 있는지 확인

### 데이터 저장 실패
- 데이터베이스 스키마가 올바르게 생성되었는지 확인
- Supabase 대시보드에서 테이블 존재 여부 확인

### 로그인 실패
- 요양원, 조사원, 어르신 데이터가 데이터베이스에 존재하는지 확인
- 각 ID가 올바르게 연결되어 있는지 확인

## 📦 배포

### Streamlit Cloud 배포

1. GitHub에 코드 업로드
2. [Streamlit Cloud](https://streamlit.io/cloud)에서 앱 배포
3. Secrets에 환경 변수 추가:
   ```toml
   SUPABASE_URL = "your_url"
   SUPABASE_KEY = "your_key"
   ADMIN_PASSWORD = "admin123"
   ```

### 로컬 네트워크 공유

```bash
streamlit run app.py --server.address 0.0.0.0
```

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 사용됩니다.

## 👥 기여

문제 발견 시 Issue를 등록하거나 Pull Request를 제출해주세요.

## 📞 지원

기술 지원이 필요한 경우 프로젝트 관리자에게 문의하세요.

# 🚀 빠른 시작 가이드

## 5분 안에 시작하기

### 1단계: 패키지 설치 (1분)

```bash
cd survey_app_final
pip install -r requirements.txt
```

### 2단계: Supabase 설정 (2분)

1. [Supabase](https://supabase.com/) 접속 및 로그인
2. "New Project" 클릭하여 프로젝트 생성
3. 프로젝트 생성 완료 후:
   - Settings → API → Project URL 복사
   - Settings → API → anon/public key 복사

### 3단계: 데이터베이스 생성 (1분)

1. Supabase 대시보드 → SQL Editor
2. `database_schema.sql` 파일 내용 복사 → 붙여넣기 → RUN 클릭
3. `sample_data.sql` 파일 내용 복사 → 붙여넣기 → RUN 클릭

### 4단계: 환경 변수 설정 (30초)

`.env.example` 파일을 `.env`로 복사하고 수정:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

`.env` 파일을 열어서 실제 값 입력:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
ADMIN_PASSWORD=admin123
```

### 5단계: 실행! (30초)

```bash
streamlit run app.py
```

브라우저가 자동으로 열립니다!

---

## 🎯 첫 로그인

### 일반 사용자
- 요양원 ID: `NH001`
- 조사원 ID: `SV001`
- 어르신 ID: `EL001`

### 관리자
- 비밀번호: `admin123`

---

## 📁 파일 구조

```
survey_app_final/
├── app.py                    # 메인 애플리케이션
├── requirements.txt          # 필수 패키지 목록
├── database_schema.sql       # 데이터베이스 스키마
├── sample_data.sql          # 샘플 데이터
├── .env.example             # 환경 변수 템플릿
├── README.md                # 상세 문서
├── QUICKSTART.md            # 이 파일
└── surveys/
    ├── __init__.py
    ├── basic_survey.py      # 기초 조사표
    ├── nutrition_survey.py  # 영양 조사표
    └── satisfaction_survey.py # 만족도 조사표
```

---

## ❓ 문제 해결

### "Module not found" 오류
```bash
pip install -r requirements.txt
```

### "Supabase connection error"
- `.env` 파일의 URL과 KEY 다시 확인
- Supabase 프로젝트가 활성화되어 있는지 확인

### "Table not found"
- `database_schema.sql`을 Supabase SQL Editor에서 실행했는지 확인

### 로그인 안됨
- `sample_data.sql`을 실행했는지 확인
- Supabase 대시보드에서 테이블에 데이터가 있는지 확인

---

## 📞 추가 도움

자세한 내용은 `README.md` 파일을 참조하세요!

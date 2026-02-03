-- 샘플 데이터 삽입
-- 이 파일은 테스트 목적으로 샘플 데이터를 데이터베이스에 추가합니다.

-- 요양원 샘플 데이터
INSERT INTO nursing_homes (id, name) VALUES
('NH001', '서울요양원'),
('NH002', '부산실버케어센터'),
('NH003', '대구행복요양원')
ON CONFLICT (id) DO NOTHING;

-- 조사원 샘플 데이터
INSERT INTO surveyors (id, name, nursing_home_id) VALUES
('SV001', '김조사', 'NH001'),
('SV002', '이조사', 'NH001'),
('SV003', '박조사', 'NH002'),
('SV004', '최조사', 'NH003')
ON CONFLICT (id) DO NOTHING;

-- 어르신 샘플 데이터
INSERT INTO elderly_residents (id, name, nursing_home_id) VALUES
('EL001', '김00', 'NH001'),
('EL002', '이00', 'NH001'),
('EL003', '박00', 'NH001'),
('EL004', '정00', 'NH002'),
('EL005', '최00', 'NH002'),
('EL006', '강00', 'NH003')
ON CONFLICT (id) DO NOTHING;

-- 설문 진행 상황 초기화
INSERT INTO survey_progress (elderly_id, surveyor_id, nursing_home_id)
SELECT e.id, s.id, e.nursing_home_id
FROM elderly_residents e
JOIN surveyors s ON e.nursing_home_id = s.nursing_home_id
ON CONFLICT (elderly_id) DO NOTHING;

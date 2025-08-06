# ASME BPVC 2023 Section II Part D 데이터베이스 프로젝트

## 📋 프로젝트 개요

이 프로젝트는 ASME BPVC 2023 Section II Part D (Customary) 문서에서 재료 데이터를 추출하고, LLM 모델 학습용 데이터셋을 생성하며, MCP 서버를 통해 데이터에 접근할 수 있는 종합적인 시스템입니다.

## 🎯 주요 기능

### 1. 데이터 추출 및 처리
- PDF 문서에서 표와 그래프 자동 추출
- CSV 및 JSON 형태로 데이터 변환
- 데이터 품질 검증 및 정제

### 2. LLM용 데이터 생성
- 종합 데이터베이스 생성 (`llm_comprehensive_data.json`)
- 원본 데이터 보존 (`llm_raw_data.json`)
- 대량 데이터 분석 (`llm_massive_data.json`)
- 학습용 데이터셋 생성 (훈련/검증/테스트 분할)

### 3. MCP 서버
- ASME 재료 데이터 검색 API
- 허용응력값 및 설계응력강도값 조회
- 기계적 특성 및 사용 가이드라인 제공
- 설계 예시 및 권장사항 제공

## 📊 데이터 통계

- **총 표 파일**: 161개 (CSV)
- **총 그래프 파일**: 179개 (JSON)
- **가장 큰 표**: Page_64_Table_1.csv (44행 x 17열 = 748개 셀)
- **큰 표들**: 79개 (5행 이상 또는 10열 이상)
- **LLM 학습용 Q&A 쌍**: 75개

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 데이터 검증
```bash
python data_validation.py
```

### 3. LLM 데이터셋 생성
```bash
python llm_dataset_generator.py
```

### 4. MCP 서버 실행
```bash
python mcp_server.py
```

## 📁 파일 구조

```
asme_database_project/
├── data_validation.py              # 데이터 검증 스크립트
├── llm_dataset_generator.py        # LLM 데이터셋 생성기
├── mcp_server.py                   # MCP 서버
├── llm_comprehensive_data.json     # 종합 데이터베이스
├── llm_raw_data.json              # 원본 데이터
├── llm_massive_data.json          # 대량 데이터 분석
├── llm_dataset_training.json      # 훈련용 데이터셋
├── llm_dataset_validation.json    # 검증용 데이터셋
├── llm_dataset_testing.json       # 테스트용 데이터셋
├── validation_report.json         # 검증 리포트
├── validation_report.md           # 검증 리포트 (마크다운)
├── llm_dataset_summary.md         # 데이터셋 요약
├── output/                        # 추출된 원본 파일들
│   ├── Page_*_Table_*.csv        # 표 데이터
│   └── Page_*_Chart_*.json       # 그래프 데이터
└── scripts/                       # 데이터 추출 스크립트들
```

## 🔧 MCP 서버 API

### 사용 가능한 도구들

1. **search_material** - ASME BPVC 재료 검색
2. **get_allowable_stress** - 재료의 허용응력값 조회
3. **get_design_stress** - 재료의 설계응력강도값 조회
4. **get_mechanical_properties** - 재료의 기계적 특성 조회
5. **get_design_example** - 설계 예시 조회
6. **get_usage_guidelines** - 재료 사용 가이드라인 조회
7. **search_materials_by_property** - 특성별 재료 검색

### 예시 사용법

```python
# 재료 검색
{
    "material_name": "SA-516",
    "material_type": "carbon_steel"
}

# 허용응력값 조회
{
    "material_name": "SA-516_Grade_70",
    "temperature": "400F"
}

# 설계 예시 조회
{
    "design_type": "high_temperature_vessel"
}
```

## 📈 데이터 품질

- **검증 성공률**: 100%
- **총 검증 파일 수**: 340개
- **오류 수**: 0개
- **경고 수**: 98개 (주로 결측값 관련)

## 🎯 활용 방안

### 1. 엔지니어링 설계
- 압력용기 설계 시 재료 선택
- 허용응력값 및 설계응력강도값 조회
- 온도별 재료 특성 분석

### 2. LLM 모델 학습
- ASME 코드 기반 질의응답 모델 훈련
- 엔지니어링 지식 베이스 구축
- 설계 자동화 시스템 개발

### 3. 교육 및 연구
- ASME BPVC 교육 자료 개발
- 재료 공학 연구 데이터 제공
- 설계 가이드라인 연구

## 🔍 검색 가이드라인

### 키워드
- **재료**: Carbon Steel, Alloy Steel, Stainless Steel, SA-516, SA-283, SA-213, Type 304, Type 316
- **특성**: Allowable Stress, Design Stress, Tensile Strength, Yield Strength, Modulus of Elasticity
- **온도**: 100F, 200F, 300F, 400F, 500F, 600F, 700F, 800F
- **형태**: Plate, Pipe, Tube, Bar, Sheet, Weld

### 검색 방법
1. **재료명 검색**: 재료명으로 검색하여 모든 특성 데이터 제공
2. **온도 검색**: 온도로 검색하여 해당 온도에서의 응력 값 제공
3. **특성 검색**: 특성명으로 검색하여 모든 재료별 데이터 제공
4. **형태 검색**: 제품 형태로 검색하여 해당 형태의 재료 정보 제공

## 📝 설계 팁

- **온도 보간**: 표에 없는 온도는 선형 보간 사용
- **안전계수**: 설계 시 적절한 안전계수 적용
- **코드 준수**: ASME BPVC Section VIII Division 1 준수
- **검증**: 최종 설계는 공인된 엔지니어 검토 필요

## 🤝 기여하기

1. 이슈 등록
2. 포크 생성
3. 기능 브랜치 생성
4. 변경사항 커밋
5. 풀 리퀘스트 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트 관련 문의사항은 이슈를 통해 연락해 주세요. 
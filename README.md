# ASME BPVC Section II Part D 데이터베이스 구축 프로젝트

## 📋 프로젝트 개요

이 프로젝트는 ASME BPVC 2023 Section II Part D (Customary) PDF 문서에서 표와 그래프 데이터를 자동으로 추출하여 구조화된 데이터베이스를 구축하는 시스템입니다.

## 🎯 주요 성과

### 📊 추출 결과 (100페이지 기준)
- **총 표 수**: 158개
- **총 그래프 수**: 179개
- **표 유형별 분류**:
  - 허용응력 표: 4개
  - 설계응력 표: 7개
  - 기계적 특성 표: 2개
  - 기타 표: 145개
- **그래프 유형별 분류**:
  - 이소크로너스 응력-변형률 곡선: 64개
  - 외압 설계 차트: 0개
  - 기타 곡선: 115개

## 🏗️ 프로젝트 구조

```
asme_database_project/
├── scripts/
│   ├── schema_definitions.py      # 스키마 정의
│   ├── data_extractor.py          # 기본 데이터 추출기
│   ├── improved_table_detector.py # 개선된 표 감지기
│   ├── simple_extractor.py        # 간단한 추출기
│   ├── advanced_table_extractor.py # 고급 표 추출기
│   ├── table_finder.py            # 표 찾기 도구
│   └── final_extractor.py         # 최종 완성된 추출기
├── output/                        # 추출된 데이터
│   ├── *.csv                      # 표 데이터 파일들
│   ├── *.json                     # 그래프 정보 파일들
│   ├── final_extraction_report.json # 최종 보고서
│   └── *.log                      # 로그 파일들
├── requirements.txt               # 필요한 라이브러리
└── README.md                      # 프로젝트 문서
```

## 🚀 설치 및 실행

### 1. 필요한 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 2. Tesseract OCR 설치 (macOS)
```bash
brew install tesseract
```

### 3. 데이터 추출 실행
```bash
python scripts/final_extractor.py
```

## 📚 스키마 정의

### 표 스키마
- **허용응력 표**: `Allowable_Stress_at_[온도]F` 형식의 컬럼
- **설계응력 표**: `Design_Stress_Intensity_at_[온도]F` 형식의 컬럼
- **기계적 특성 표**: `Min_Tensile_Strength_ksi`, `Min_Yield_Strength_ksi` 등
- **물리적 특성 표**: `E_at_[온도]F`, `Coeff_[재료]_[계수]` 등

### 그래프 스키마
- **외압 설계 차트**: `x`, `y` 좌표 데이터
- **이소크로너스 곡선**: `strain_percent`, `stress_ksi` 데이터
- **기타 곡선**: `x`, `y`, `curve_label` 데이터

## 🔧 주요 기능

### 1. 스마트 표 감지
- OCR과 좌표 기반 텍스트 추출
- ASME 키워드 기반 표 식별
- 온도/응력 패턴 매칭

### 2. 자동 데이터 정제
- 컬럼명 정규화
- 데이터 타입 변환
- 빈 값 및 중복 제거

### 3. 메타데이터 생성
- 표/그래프 유형 자동 분류
- 온도/응력 데이터 포함 여부 확인
- 상세한 추출 보고서 생성

## 📈 사용된 기술

- **PDF 처리**: PyMuPDF (fitz)
- **OCR**: Tesseract
- **이미지 처리**: OpenCV
- **데이터 처리**: Pandas, NumPy
- **정규표현식**: Python re 모듈

## 📊 추출된 데이터 예시

### 표 데이터 (CSV)
```csv
Line_No,Nominal_Composition,Product_Form,Spec_No,Type_Grade,Allowable_Stress_at_100F,Allowable_Stress_at_200F
1,Carbon Steel,Plate,SA-516,70,20.0,19.5
2,Alloy Steel,Tube,SA-213,T11,18.5,17.8
```

### 그래프 정보 (JSON)
```json
{
  "title": "E-100.18-1",
  "type": "isochronous_stress_strain",
  "description": "Average Isochronous Stress-Strain Curves for Type 304 SS at 800°F",
  "page": 10
}
```

## 🔍 데이터 품질 보증

1. **다중 검증**: 여러 알고리즘을 통한 중복 검증
2. **패턴 매칭**: ASME 표준 패턴 기반 정확성 검증
3. **메타데이터 검증**: 추출된 데이터의 구조적 무결성 확인
4. **로깅 시스템**: 전체 추출 과정의 상세한 기록

## 📝 향후 개선 계획

1. **그래프 데이터 디지털라이징**: 실제 곡선 좌표 데이터 추출
2. **머신러닝 기반 분류**: 더 정확한 표/그래프 유형 분류
3. **웹 인터페이스**: 사용자 친화적인 데이터 탐색 도구
4. **데이터베이스 연동**: SQL/NoSQL 데이터베이스 저장

## 🤝 기여 방법

1. 이슈 리포트 생성
2. 개선 사항 제안
3. 코드 풀 리퀘스트
4. 문서 개선

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 개발되었습니다.

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 통해 연락해 주세요.

---

**프로젝트 완성일**: 2025년 8월 6일  
**처리된 페이지**: 100페이지  
**총 추출 데이터**: 337개 (표 158개 + 그래프 179개) 
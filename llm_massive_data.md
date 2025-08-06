# ASME BPVC 2023 Section II Part D - 대량 데이터베이스

## 📊 데이터 개요
- **총 표 파일**: 161개
- **총 그래프 파일**: 179개
- **큰 표 (10행 이상 또는 15열 이상)**: 54개
- **온도 데이터**: 53개
- **응력 데이터**: 16개
- **추출 날짜**: 2025-08-06

## 🏗️ 재료 분포

### 재료 타입별 분포
- **Carbon Steel**: 230회 발견
- **Stainless Steel**: 9회 발견
- **Alloy Steel**: 1회 발견

### 규격 코드별 분포
- **sa-508**: 2회 발견
- **sa-533**: 2회 발견
- **sa-541**: 1회 발견

### 제품 형태별 분포
- **Bar**: 6회 발견
- **Forging**: 14회 발견
- **Plate**: 22회 발견
- **Pipe**: 11회 발견
- **Tube**: 7회 발견
- **Sheet**: 5회 발견

## 📋 온도별 재료 선택 가이드

### Cryogenic
- **온도 범위**: -320°F to -50°F
- **추천 재료**:
  - SA-333 Grade 6 (Carbon Steel)
  - Type 304L SS
  - Type 316L SS
  - 9% Nickel Steel
- **주요 용도**:
  - LNG 저장탱크
  - 극저온용기
  - 액체질소 설비

### Low Temperature
- **온도 범위**: -50°F to 100°F
- **추천 재료**:
  - SA-516 Grade 70 (Carbon Steel)
  - SA-283 Grade C (Carbon Steel)
  - Type 304 SS
  - Type 316 SS
- **주요 용도**:
  - 저온용기
  - 냉장설비
  - 일반 압력용기

### Medium Temperature
- **온도 범위**: 100°F to 600°F
- **추천 재료**:
  - SA-516 Grade 70 (Carbon Steel)
  - SA-285 Grade C (Carbon Steel)
  - Type 304 SS
  - Type 316 SS
- **주요 용도**:
  - 일반 압력용기
  - 열교환기
  - 보일러

### High Temperature
- **온도 범위**: 600°F to 800°F
- **추천 재료**:
  - SA-516 Grade 70 (Carbon Steel)
  - Type 304 SS
  - Type 316 SS
  - Type 321 SS
- **주요 용도**:
  - 고온용기
  - 열교환기
  - 증기관

### Very High Temperature
- **온도 범위**: 800°F to 1200°F
- **추천 재료**:
  - SA-213 T91 (Alloy Steel)
  - SA-213 T92 (Alloy Steel)
  - Type 304 SS
  - Type 316 SS
  - Type 321 SS
- **주요 용도**:
  - 고온 보일러
  - 터빈
  - 고온 파이프

## 🔍 검색 및 활용 방법

### 키워드 검색
- **Materials**: Carbon Steel, Stainless Steel, Alloy Steel, SA-516, SA-283, SA-285, SA-213, SA-312, Type 304, Type 316, Type 321, T91, T92
- **Properties**: Allowable Stress, Design Stress, Tensile Strength, Yield Strength, Modulus of Elasticity, Thermal Expansion, Creep Strength, Fatigue Strength
- **Temperatures**: 100F, 200F, 300F, 400F, 500F, 600F, 700F, 800F, 900F, 1000F, 1100F, 1200F
- **Product_Forms**: Plate, Pipe, Tube, Bar, Sheet, Forging, Fitting, Welded, Seamless

### 사용 시나리오
- **Material Selection**: 온도, 압력, 환경 조건에 따른 재료 선택
- **Stress Calculation**: 온도별 허용응력 값 조회
- **Design Verification**: 기존 설계의 재료 적합성 검토
- **Cost Analysis**: 재료별 경제성 비교 분석

## ⚠️ 주의사항

- 이 데이터는 ASME BPVC 2023 Section II Part D에서 추출되었습니다.
- 실제 설계 시에는 최신 버전의 코드를 참조하시기 바랍니다.
- 온도별 허용응력 값은 온도가 증가할수록 감소합니다.
- 재료 선택 시 사용 환경(온도, 압력, 부식성)을 고려해야 합니다.
- 대량의 데이터가 포함되어 있으므로 필요에 따라 필터링하여 사용하세요.

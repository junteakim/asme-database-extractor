# ASME BPVC 2023 Section II Part D - 실제 추출 데이터

## 📊 데이터 개요
- **총 CSV 파일**: 169개
- **총 JSON 파일**: 184개
- **추출 날짜**: 2025-08-06
- **소스**: ASME BPVC 2023 Section II Part D (Customary)

## 🏗️ 추출된 재료 데이터

### Carbon Steel (탄소강)
- **발견된 표 수**: 3개
- **규격 코드**: 
- **제품 형태**: Bar, Plate

### Stainless Steel (스테인리스강)
- **발견된 표 수**: 3개
- **주요 등급**: Type 304, Type 316, Type 321, Type 347

## 📋 재료 선택 가이드

### High Temperature
- SA-213 T91: 크리프 저항성이 우수한 합금강 (800°F 이상)
- SA-213 T92: 고온 강도가 우수한 합금강 (800°F 이상)
- Type 304 SS: 내산화성이 우수한 스테인리스강 (800°F 이상)

### Low Temperature
- SA-333 Grade 6: 저온 인성이 우수한 탄소강 (-50°F 이하)
- SA-516 Grade 70: 저온용 탄소강 (-50°F 이하)
- Type 304L SS: 저온용 스테인리스강 (-50°F 이하)

### General Purpose
- SA-516 Grade 70: 범용 탄소강 (상온~600°F)
- SA-283 Grade C: 경제적인 탄소강 (상온~600°F)
- Type 304 SS: 범용 스테인리스강 (상온~600°F)

## 🔍 데이터 검색 방법

### 키워드 검색
- **Materials**: Carbon Steel, Alloy Steel, Stainless Steel, SA-516, SA-283, SA-213
- **Properties**: Allowable Stress, Design Stress, Tensile Strength, Yield Strength
- **Temperatures**: 100F, 200F, 300F, 400F, 500F, 600F, 700F, 800F
- **Forms**: Plate, Pipe, Tube, Bar, Sheet

### 파일 패턴
- **Tables**: `Page_*_Table_*.csv`
- **Charts**: `Page_*_Chart_*.json`

## ⚠️ 사용 시 주의사항

- 이 데이터는 ASME BPVC 2023 Section II Part D에서 추출되었습니다.
- 실제 설계 시에는 최신 버전의 코드를 참조하시기 바랍니다.
- 온도별 허용응력 값은 온도가 증가할수록 감소합니다.
- 재료 선택 시 사용 환경(온도, 압력, 부식성)을 고려해야 합니다.

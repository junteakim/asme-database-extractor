# ASME BPVC 2023 Section II Part D - 실제 추출 데이터 (원본)

## 📊 데이터 개요
- **총 표 파일**: 161개
- **총 그래프 파일**: 179개
- **추출 날짜**: 2025-08-06
- **데이터 형태**: 원본 추출 데이터 (요약 없음)

## 📋 사용 가능한 표 데이터

다음 표들이 실제 데이터로 포함되어 있습니다:

 1. **Page_60_Table_1.csv**: 15행 x 12열
 2. **Page_88_Table_3.csv**: 1행 x 21열
 3. **Page_10_Table_1.csv**: 1행 x 2열
 4. **Page_47_Table_2.csv**: 1행 x 5열
 5. **Page_84_Table_5.csv**: 1행 x 15열
 6. **Page_84_Table_4.csv**: 1행 x 15열
 7. **Page_47_Table_3.csv**: 1행 x 5열
 8. **Page_52_Table_1.csv**: 2행 x 3열
 9. **Page_88_Table_2.csv**: 2행 x 17열
10. **Page_60_Table_2.csv**: 4행 x 14열
11. **Page_45_Table_8.csv**: 2행 x 5열
12. **Page_10_Table_2.csv**: 2행 x 14열
13. **Page_47_Table_1.csv**: 1행 x 7열
14. **Page_84_Table_6.csv**: 1행 x 15열
15. **Page_10_Table_3.csv**: 1행 x 7열
16. **Page_88_Table_1.csv**: 1행 x 17열
17. **Page_45_Table_9.csv**: 1행 x 5열
18. **Page_60_Table_3.csv**: 1행 x 13열
19. **Page_10_Table_7.csv**: 4행 x 5열
20. **Page_47_Table_4.csv**: 1행 x 5열
... 및 141개 더

## 📊 실제 데이터 샘플

### 가장 큰 표: Page_64_Table_1.csv
- **크기**: 44행 x 17열
- **컬럼**: 1, Carbon steel, Forgings, SA, –, 765, I, K03046,  …, …...

**실제 데이터 샘플 (처음 5행):**

```json
[
  {
    "1": "2",
    "Carbon steel": "Carbon steel",
    "Forgings": "Plate",
    "SA": "SA",
    "–": "–",
    "765": "515",
    "I": "60",
    "K03046": "K02401",
    " …": " …",
    "…": "…",
    "1.1": "1",
    "1.2": "1",
    "Unnamed: 12": NaN,
    "Unnamed: 13": NaN,
    "Unnamed: 14": NaN,
    "Unnamed: 15": NaN,
    "Unnamed: 16": NaN
  },
  {
    "1": "3",
    "Carbon steel": "Carbon steel",
    "Forgings": "Plate",
    "SA": "SA",
    "–": "–",
    "765": "516",
    "I": "60",
    "K03046": "K02100",
    " …": " …",
    "…": "…",
    "1.1": "1",
    "1.2": "1",
    "Unnamed: 12": NaN,
    "Unnamed: 13": NaN,
    "Unnamed: 14": NaN,
    "Unnamed: 15": NaN,
    "Unnamed: 16": NaN
  },
  {
    "1": "4",
    "Carbon steel": "Carbon steel",
    "Forgings": "Wld. pipe",
    "SA": "SA",
    "–": "–",
    "765": "671",
    "I": "CB60",
    "K03046": "K02401",
    " …": " …",
    "…": "…",
    "1.1": "1",
    "1.2": "1",
    "Unnamed: 12": NaN,
    "Unnamed: 13": NaN,
    "Unnamed: 14": NaN,
    "Unnamed: 15": NaN,
    "Unnamed: 16": NaN
  },
  {
    "1": "5",
    "Carbon steel": "Carbon steel",
    "Forgings": "Wld. pipe",
    "SA": "SA",
    "–": "–",
    "765": "671",
    "I": "CC60",
    "K03046": "K02100",
    " …": " …",
    "…": "…",
    "1.1": "1",
    "1.2": "1",
    "Unnamed: 12": NaN,
    "Unnamed: 13": NaN,
    "Unnamed: 14": NaN,
    "Unnamed: 15": NaN,
    "Unnamed: 16": NaN
  },
  {
    "1": "6",
    "Carbon steel": "Carbon steel",
    "Forgings": "Wld. pipe",
    "SA": "SA",
    "–": "–",
    "765": "671",
    "I": "CE60",
    "K03046": "K02402",
    " …": " …",
    "…": "…",
    "1.1": "1",
    "1.2": "1",
    "Unnamed: 12": NaN,
    "Unnamed: 13": NaN,
    "Unnamed: 14": NaN,
    "Unnamed: 15": NaN,
    "Unnamed: 16": NaN
  }
]
```

## 🔍 데이터 접근 방법

### JSON 데이터에서 표 접근
```python
# 특정 표의 모든 데이터 접근
table_data = raw_data['raw_table_data']['Page_64_Table_1.csv']['data']
table_columns = raw_data['raw_table_data']['Page_64_Table_1.csv']['columns']
table_shape = raw_data['raw_table_data']['Page_64_Table_1.csv']['shape']
```

### 그래프 데이터 접근
```python
# 특정 그래프 데이터 접근
chart_data = raw_data['raw_chart_data']['Page_10_Chart_1.json']
```

## 📝 사용 예시

### 1. Carbon Steel 데이터 찾기
```python
carbon_steel_data = []
for table_name, table_info in raw_data['raw_table_data'].items():
    for row in table_info['data']:
        if 'carbon steel' in str(row).lower():
            carbon_steel_data.append({'table': table_name, 'row': row})
```

### 2. 특정 규격 코드 찾기
```python
sa516_data = []
for table_name, table_info in raw_data['raw_table_data'].items():
    for row in table_info['data']:
        if 'sa-516' in str(row).lower():
            sa516_data.append({'table': table_name, 'row': row})
```

### 3. 온도별 데이터 찾기
```python
temperature_data = []
for table_name, table_info in raw_data['raw_table_data'].items():
    for col in table_info['columns']:
        if '°f' in str(col).lower() or 'f' in str(col).lower():
            temperature_data.append({'table': table_name, 'column': col})
```

## ⚠️ 주의사항

- 이 데이터는 실제 추출된 원본 데이터입니다.
- 요약이나 가공 없이 그대로 제공됩니다.
- 데이터 크기가 클 수 있으므로 필요에 따라 필터링하여 사용하세요.
- 실제 설계 시에는 최신 버전의 ASME 코드를 참조하시기 바랍니다.

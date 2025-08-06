#!/usr/bin/env python3
"""
ASME BPVC 실제 추출 데이터를 요약 없이 그대로 LLM용으로 제공
"""

import pandas as pd
import json
import glob
from pathlib import Path

def extract_all_raw_data():
    """모든 실제 추출 데이터를 그대로 추출"""
    print("🔍 실제 ASME 데이터 추출 시작...")
    
    # 모든 CSV 파일 수집
    csv_files = glob.glob('output/Page_*_Table_*.csv')
    json_files = glob.glob('output/Page_*_Chart_*.json')
    
    print(f"📊 총 파일 수: {len(csv_files)}개 표, {len(json_files)}개 그래프")
    
    # 실제 표 데이터 수집
    all_tables = {}
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            table_name = Path(csv_file).name
            
            # 실제 데이터를 그대로 저장 (요약하지 않음)
            all_tables[table_name] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'data': df.to_dict('records'),  # 모든 행 데이터
                'file_path': csv_file
            }
            
            print(f"✅ {table_name}: {df.shape[0]}행 x {df.shape[1]}열")
            
        except Exception as e:
            print(f"⚠️ 파일 처리 오류 {csv_file}: {e}")
    
    # 실제 그래프 데이터 수집
    all_charts = {}
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                chart_data = json.load(f)
            
            chart_name = Path(json_file).name
            all_charts[chart_name] = chart_data
            
        except Exception as e:
            print(f"⚠️ 그래프 파일 처리 오류 {json_file}: {e}")
    
    return all_tables, all_charts

def create_raw_llm_data():
    """실제 데이터를 그대로 LLM용으로 생성"""
    all_tables, all_charts = extract_all_raw_data()
    
    # 실제 데이터를 그대로 제공
    raw_data = {
        "metadata": {
            "title": "ASME BPVC 2023 Section II Part D - 실제 추출 데이터 (원본)",
            "extraction_date": "2025-08-06",
            "source": "ASME BPVC 2023 Section II Part D (Customary)",
            "total_tables": len(all_tables),
            "total_charts": len(all_charts),
            "version": "raw_data_1.0",
            "description": "요약하지 않은 실제 추출된 ASME BPVC 데이터"
        },
        "raw_table_data": all_tables,  # 모든 표 데이터를 그대로
        "raw_chart_data": all_charts,  # 모든 그래프 데이터를 그대로
        "data_access_guide": {
            "table_access": {
                "description": "표 데이터에 접근하는 방법",
                "example": "raw_table_data['Page_64_Table_1.csv']['data']",
                "available_tables": list(all_tables.keys())
            },
            "chart_access": {
                "description": "그래프 데이터에 접근하는 방법", 
                "example": "raw_chart_data['Page_10_Chart_1.json']",
                "available_charts": list(all_charts.keys())
            }
        }
    }
    
    return raw_data

def save_raw_llm_data():
    """실제 데이터를 그대로 저장"""
    raw_data = create_raw_llm_data()
    
    # JSON 형태로 저장 (실제 데이터 그대로)
    with open('llm_raw_data.json', 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)
    
    # 마크다운 형태로 저장 (실제 데이터 샘플 포함)
    with open('llm_raw_data.md', 'w', encoding='utf-8') as f:
        f.write("# ASME BPVC 2023 Section II Part D - 실제 추출 데이터 (원본)\n\n")
        f.write("## 📊 데이터 개요\n")
        f.write(f"- **총 표 파일**: {raw_data['metadata']['total_tables']}개\n")
        f.write(f"- **총 그래프 파일**: {raw_data['metadata']['total_charts']}개\n")
        f.write(f"- **추출 날짜**: {raw_data['metadata']['extraction_date']}\n")
        f.write(f"- **데이터 형태**: 원본 추출 데이터 (요약 없음)\n\n")
        
        f.write("## 📋 사용 가능한 표 데이터\n\n")
        f.write("다음 표들이 실제 데이터로 포함되어 있습니다:\n\n")
        
        # 상위 20개 표만 나열
        for i, table_name in enumerate(list(raw_data['raw_table_data'].keys())[:20]):
            table_info = raw_data['raw_table_data'][table_name]
            f.write(f"{i+1:2d}. **{table_name}**: {table_info['shape'][0]}행 x {table_info['shape'][1]}열\n")
        
        if len(raw_data['raw_table_data']) > 20:
            f.write(f"... 및 {len(raw_data['raw_table_data']) - 20}개 더\n")
        
        f.write("\n## 📊 실제 데이터 샘플\n\n")
        
        # 가장 큰 표의 실제 데이터 샘플 제공
        largest_table = max(raw_data['raw_table_data'].items(), key=lambda x: x[1]['shape'][0] * x[1]['shape'][1])
        table_name, table_data = largest_table
        
        f.write(f"### 가장 큰 표: {table_name}\n")
        f.write(f"- **크기**: {table_data['shape'][0]}행 x {table_data['shape'][1]}열\n")
        f.write(f"- **컬럼**: {', '.join(table_data['columns'][:10])}{'...' if len(table_data['columns']) > 10 else ''}\n\n")
        
        f.write("**실제 데이터 샘플 (처음 5행):**\n\n")
        f.write("```json\n")
        f.write(json.dumps(table_data['data'][:5], ensure_ascii=False, indent=2))
        f.write("\n```\n\n")
        
        f.write("## 🔍 데이터 접근 방법\n\n")
        f.write("### JSON 데이터에서 표 접근\n")
        f.write("```python\n")
        f.write("# 특정 표의 모든 데이터 접근\n")
        f.write("table_data = raw_data['raw_table_data']['Page_64_Table_1.csv']['data']\n")
        f.write("table_columns = raw_data['raw_table_data']['Page_64_Table_1.csv']['columns']\n")
        f.write("table_shape = raw_data['raw_table_data']['Page_64_Table_1.csv']['shape']\n")
        f.write("```\n\n")
        
        f.write("### 그래프 데이터 접근\n")
        f.write("```python\n")
        f.write("# 특정 그래프 데이터 접근\n")
        f.write("chart_data = raw_data['raw_chart_data']['Page_10_Chart_1.json']\n")
        f.write("```\n\n")
        
        f.write("## 📝 사용 예시\n\n")
        f.write("### 1. Carbon Steel 데이터 찾기\n")
        f.write("```python\n")
        f.write("carbon_steel_data = []\n")
        f.write("for table_name, table_info in raw_data['raw_table_data'].items():\n")
        f.write("    for row in table_info['data']:\n")
        f.write("        if 'carbon steel' in str(row).lower():\n")
        f.write("            carbon_steel_data.append({'table': table_name, 'row': row})\n")
        f.write("```\n\n")
        
        f.write("### 2. 특정 규격 코드 찾기\n")
        f.write("```python\n")
        f.write("sa516_data = []\n")
        f.write("for table_name, table_info in raw_data['raw_table_data'].items():\n")
        f.write("    for row in table_info['data']:\n")
        f.write("        if 'sa-516' in str(row).lower():\n")
        f.write("            sa516_data.append({'table': table_name, 'row': row})\n")
        f.write("```\n\n")
        
        f.write("### 3. 온도별 데이터 찾기\n")
        f.write("```python\n")
        f.write("temperature_data = []\n")
        f.write("for table_name, table_info in raw_data['raw_table_data'].items():\n")
        f.write("    for col in table_info['columns']:\n")
        f.write("        if '°f' in str(col).lower() or 'f' in str(col).lower():\n")
        f.write("            temperature_data.append({'table': table_name, 'column': col})\n")
        f.write("```\n\n")
        
        f.write("## ⚠️ 주의사항\n\n")
        f.write("- 이 데이터는 실제 추출된 원본 데이터입니다.\n")
        f.write("- 요약이나 가공 없이 그대로 제공됩니다.\n")
        f.write("- 데이터 크기가 클 수 있으므로 필요에 따라 필터링하여 사용하세요.\n")
        f.write("- 실제 설계 시에는 최신 버전의 ASME 코드를 참조하시기 바랍니다.\n")
    
    print("✅ 실제 데이터 추출 완료!")
    print("📄 생성된 파일:")
    print("  - llm_raw_data.json (실제 데이터 그대로)")
    print("  - llm_raw_data.md (실제 데이터 샘플 포함)")
    print(f"📊 총 {len(raw_data['raw_table_data'])}개 표, {len(raw_data['raw_chart_data'])}개 그래프 데이터 포함")

if __name__ == "__main__":
    save_raw_llm_data() 
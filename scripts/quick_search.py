"""
빠른 ASME 데이터 검색 도구
명령줄에서 간단하게 특정 값을 검색
"""

import pandas as pd
import json
import re
import sys
import glob
from pathlib import Path

def quick_search(search_term: str, search_type: str = "all"):
    """빠른 검색 함수"""
    data_dir = Path("output")
    
    if not data_dir.exists():
        print("❌ output 디렉토리를 찾을 수 없습니다.")
        print("먼저 데이터 추출을 실행하세요: python scripts/final_extractor.py")
        return
    
    print(f"🔍 '{search_term}' 검색 중...")
    
    # CSV 파일들 검색
    csv_files = glob.glob(str(data_dir / "*.csv"))
    results = []
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            table_name = Path(csv_file).stem
            
            # 검색 타입에 따른 필터링
            if search_type == "material":
                # 재료 관련 검색
                for col in df.columns:
                    if search_term.lower() in str(col).lower():
                        results.append({
                            'file': table_name,
                            'type': 'column_match',
                            'column': col,
                            'sample_data': df.head(3).to_dict('records')
                        })
                
                # 데이터에서 재료명 검색
                for idx, row in df.iterrows():
                    for col in df.columns:
                        if search_term.lower() in str(row[col]).lower():
                            results.append({
                                'file': table_name,
                                'type': 'data_match',
                                'row': idx,
                                'column': col,
                                'value': str(row[col])
                            })
            
            elif search_type == "stress":
                # 응력 값 검색
                for col in df.columns:
                    col_str = str(col).lower()
                    if any(keyword in col_str for keyword in ['stress', 'ksi', 'mpa']):
                        if search_term.lower() in col_str:
                            numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
                            if len(numeric_data) > 0:
                                results.append({
                                    'file': table_name,
                                    'type': 'stress_data',
                                    'column': col,
                                    'min': numeric_data.min(),
                                    'max': numeric_data.max(),
                                    'mean': numeric_data.mean()
                                })
            
            elif search_type == "temperature":
                # 온도 데이터 검색
                for col in df.columns:
                    col_str = str(col).lower()
                    if any(keyword in col_str for keyword in ['°f', 'f', 'temperature']):
                        if search_term.lower() in col_str:
                            results.append({
                                'file': table_name,
                                'type': 'temperature_data',
                                'column': col,
                                'data': df[col].head(5).tolist()
                            })
            
            else:
                # 전체 검색
                for col in df.columns:
                    if search_term.lower() in str(col).lower():
                        results.append({
                            'file': table_name,
                            'type': 'column_match',
                            'column': col,
                            'sample_data': df.head(3).to_dict('records')
                        })
                
                for idx, row in df.iterrows():
                    for col in df.columns:
                        if search_term.lower() in str(row[col]).lower():
                            results.append({
                                'file': table_name,
                                'type': 'data_match',
                                'row': idx,
                                'column': col,
                                'value': str(row[col])
                            })
        
        except Exception as e:
            print(f"⚠️ 파일 읽기 오류: {csv_file} - {e}")
    
    # 결과 표시
    if results:
        print(f"\n✅ {len(results)}개 결과 발견:")
        for i, result in enumerate(results[:10], 1):
            print(f"\n{i}. {result['file']}")
            print(f"   타입: {result['type']}")
            
            if 'column' in result:
                print(f"   컬럼: {result['column']}")
            
            if 'value' in result:
                print(f"   값: {result['value']}")
            
            if 'min' in result:
                print(f"   범위: {result['min']:.2f} ~ {result['max']:.2f} ksi")
                print(f"   평균: {result['mean']:.2f} ksi")
            
            if 'sample_data' in result:
                print(f"   샘플 데이터: {len(result['sample_data'])}행")
        
        if len(results) > 10:
            print(f"\n... 및 {len(results) - 10}개 더")
    else:
        print("❌ 검색 결과가 없습니다.")

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python quick_search.py <검색어>")
        print("  python quick_search.py <검색어> <검색타입>")
        print("\n검색 타입:")
        print("  all        - 전체 검색 (기본값)")
        print("  material   - 재료 검색")
        print("  stress     - 응력 값 검색")
        print("  temperature - 온도 데이터 검색")
        print("\n예시:")
        print("  python quick_search.py 'Carbon Steel'")
        print("  python quick_search.py 'SA-516' material")
        print("  python quick_search.py '100F' temperature")
        print("  python quick_search.py '20.0' stress")
        return
    
    search_term = sys.argv[1]
    search_type = sys.argv[2] if len(sys.argv) > 2 else "all"
    
    quick_search(search_term, search_type)

if __name__ == "__main__":
    main() 
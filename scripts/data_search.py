"""
ASME 데이터베이스 검색 및 탐색 도구
추출된 데이터에서 특정 값을 찾고 탐색하는 기능
"""

import pandas as pd
import json
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import glob

class ASMEDataSearcher:
    """ASME 데이터 검색 클래스"""
    
    def __init__(self, data_dir: str = "output"):
        self.data_dir = Path(data_dir)
        self.tables = {}
        self.charts = {}
        self.load_all_data()
    
    def load_all_data(self):
        """모든 추출된 데이터 로드"""
        print("데이터 로딩 중...")
        
        # CSV 파일들 로드 (표 데이터)
        csv_files = glob.glob(str(self.data_dir / "*.csv"))
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                table_name = Path(csv_file).stem
                self.tables[table_name] = df
            except Exception as e:
                print(f"CSV 파일 로드 실패: {csv_file} - {e}")
        
        # JSON 파일들 로드 (그래프 정보)
        json_files = glob.glob(str(self.data_dir / "*.json"))
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    chart_data = json.load(f)
                chart_name = Path(json_file).stem
                self.charts[chart_name] = chart_data
            except Exception as e:
                print(f"JSON 파일 로드 실패: {json_file} - {e}")
        
        print(f"로드 완료: {len(self.tables)}개 표, {len(self.charts)}개 그래프")
    
    def search_material(self, material_name: str) -> List[Dict]:
        """특정 재료 검색"""
        results = []
        
        for table_name, df in self.tables.items():
            # 모든 컬럼에서 재료명 검색
            for col in df.columns:
                if isinstance(col, str) and material_name.lower() in col.lower():
                    results.append({
                        'type': 'column_match',
                        'table': table_name,
                        'column': col,
                        'data': df.head(5).to_dict('records')
                    })
            
            # 데이터에서 재료명 검색
            for idx, row in df.iterrows():
                for col in df.columns:
                    cell_value = str(row[col])
                    if material_name.lower() in cell_value.lower():
                        results.append({
                            'type': 'data_match',
                            'table': table_name,
                            'row': idx,
                            'column': col,
                            'value': cell_value,
                            'full_row': row.to_dict()
                        })
        
        return results
    
    def search_stress_value(self, stress_type: str = None, temperature: str = None, value_range: Tuple[float, float] = None) -> List[Dict]:
        """응력 값 검색"""
        results = []
        
        for table_name, df in self.tables.items():
            # 응력 관련 컬럼 찾기
            stress_columns = []
            for col in df.columns:
                col_str = str(col).lower()
                if any(keyword in col_str for keyword in ['stress', 'ksi', 'mpa', 'allowable', 'design']):
                    stress_columns.append(col)
            
            if stress_columns:
                for col in stress_columns:
                    # 숫자 데이터 추출
                    numeric_data = pd.to_numeric(df[col], errors='coerce')
                    valid_data = numeric_data.dropna()
                    
                    if len(valid_data) > 0:
                        # 온도 필터링
                        if temperature:
                            if temperature.lower() in str(col).lower():
                                results.append({
                                    'table': table_name,
                                    'column': col,
                                    'min_value': valid_data.min(),
                                    'max_value': valid_data.max(),
                                    'mean_value': valid_data.mean(),
                                    'sample_data': valid_data.head(10).tolist()
                                })
                        else:
                            results.append({
                                'table': table_name,
                                'column': col,
                                'min_value': valid_data.min(),
                                'max_value': valid_data.max(),
                                'mean_value': valid_data.mean(),
                                'sample_data': valid_data.head(10).tolist()
                            })
        
        return results
    
    def search_temperature_data(self, temp_range: Tuple[int, int] = None) -> List[Dict]:
        """온도 데이터 검색"""
        results = []
        
        for table_name, df in self.tables.items():
            # 온도 관련 컬럼 찾기
            temp_columns = []
            for col in df.columns:
                col_str = str(col).lower()
                if any(keyword in col_str for keyword in ['°f', 'f', 'temperature', 'temp']):
                    temp_columns.append(col)
            
            if temp_columns:
                for col in temp_columns:
                    # 온도 값 추출
                    temp_values = []
                    for value in df[col]:
                        if isinstance(value, str):
                            # 온도 패턴 찾기 (예: 100F, 200°F)
                            matches = re.findall(r'(\d+)°?F', value)
                            temp_values.extend([int(match) for match in matches])
                    
                    if temp_values:
                        if temp_range:
                            filtered_temps = [t for t in temp_values if temp_range[0] <= t <= temp_range[1]]
                            if filtered_temps:
                                results.append({
                                    'table': table_name,
                                    'column': col,
                                    'temperature_range': temp_range,
                                    'found_temperatures': filtered_temps
                                })
                        else:
                            results.append({
                                'table': table_name,
                                'column': col,
                                'temperature_range': (min(temp_values), max(temp_values)),
                                'found_temperatures': temp_values
                            })
        
        return results
    
    def search_specification(self, spec_code: str) -> List[Dict]:
        """규격 코드 검색 (예: SA-516, ASTM A516 등)"""
        results = []
        
        for table_name, df in self.tables.items():
            for idx, row in df.iterrows():
                for col in df.columns:
                    cell_value = str(row[col])
                    if spec_code.upper() in cell_value.upper():
                        results.append({
                            'table': table_name,
                            'row': idx,
                            'column': col,
                            'specification': spec_code,
                            'full_row': row.to_dict()
                        })
        
        return results
    
    def get_table_summary(self) -> Dict:
        """모든 표 요약 정보"""
        summary = {}
        
        for table_name, df in self.tables.items():
            summary[table_name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'has_numeric_data': any(pd.to_numeric(df[col], errors='coerce').notna().any() for col in df.columns),
                'has_temperature': any('°f' in str(col).lower() or 'f' in str(col).lower() for col in df.columns),
                'has_stress': any('stress' in str(col).lower() or 'ksi' in str(col).lower() for col in df.columns)
            }
        
        return summary
    
    def interactive_search(self):
        """대화형 검색 인터페이스"""
        print("\n=== ASME 데이터베이스 검색 도구 ===")
        print("1. 재료 검색")
        print("2. 응력 값 검색")
        print("3. 온도 데이터 검색")
        print("4. 규격 코드 검색")
        print("5. 표 요약 보기")
        print("6. 종료")
        
        while True:
            choice = input("\n선택하세요 (1-6): ").strip()
            
            if choice == '1':
                material = input("검색할 재료명을 입력하세요: ").strip()
                if material:
                    results = self.search_material(material)
                    self.display_results(results, f"'{material}' 재료 검색 결과")
            
            elif choice == '2':
                temp = input("온도 범위를 입력하세요 (예: 100F, 200F): ").strip()
                results = self.search_stress_value(temperature=temp)
                self.display_results(results, f"온도 {temp} 응력 값 검색 결과")
            
            elif choice == '3':
                min_temp = input("최소 온도 (F): ").strip()
                max_temp = input("최대 온도 (F): ").strip()
                if min_temp and max_temp:
                    results = self.search_temperature_data((int(min_temp), int(max_temp)))
                    self.display_results(results, f"온도 범위 {min_temp}-{max_temp}°F 검색 결과")
            
            elif choice == '4':
                spec = input("규격 코드를 입력하세요 (예: SA-516): ").strip()
                if spec:
                    results = self.search_specification(spec)
                    self.display_results(results, f"'{spec}' 규격 검색 결과")
            
            elif choice == '5':
                summary = self.get_table_summary()
                self.display_summary(summary)
            
            elif choice == '6':
                print("검색을 종료합니다.")
                break
            
            else:
                print("잘못된 선택입니다. 1-6 중에서 선택하세요.")
    
    def display_results(self, results: List[Dict], title: str):
        """검색 결과 표시"""
        print(f"\n=== {title} ===")
        print(f"총 {len(results)}개 결과")
        
        for i, result in enumerate(results[:10], 1):  # 처음 10개만 표시
            print(f"\n{i}. {result.get('table', 'Unknown')}")
            
            if 'column' in result:
                print(f"   컬럼: {result['column']}")
            
            if 'value' in result:
                print(f"   값: {result['value']}")
            
            if 'min_value' in result:
                print(f"   범위: {result['min_value']:.2f} ~ {result['max_value']:.2f}")
                print(f"   평균: {result['mean_value']:.2f}")
            
            if 'full_row' in result:
                print(f"   전체 행: {result['full_row']}")
        
        if len(results) > 10:
            print(f"\n... 및 {len(results) - 10}개 더")
    
    def display_summary(self, summary: Dict):
        """표 요약 정보 표시"""
        print("\n=== 표 요약 정보 ===")
        
        total_tables = len(summary)
        tables_with_temp = sum(1 for info in summary.values() if info['has_temperature'])
        tables_with_stress = sum(1 for info in summary.values() if info['has_stress'])
        tables_with_numeric = sum(1 for info in summary.values() if info['has_numeric_data'])
        
        print(f"총 표 수: {total_tables}")
        print(f"온도 데이터 포함: {tables_with_temp}")
        print(f"응력 데이터 포함: {tables_with_stress}")
        print(f"숫자 데이터 포함: {tables_with_numeric}")
        
        print("\n=== 주요 표 목록 ===")
        for table_name, info in list(summary.items())[:10]:
            print(f"{table_name}: {info['rows']}행 x {info['columns']}열")
            if info['has_temperature']:
                print("  - 온도 데이터 포함")
            if info['has_stress']:
                print("  - 응력 데이터 포함")

def main():
    """메인 실행 함수"""
    searcher = ASMEDataSearcher()
    
    # 대화형 검색 시작
    searcher.interactive_search()

if __name__ == "__main__":
    main() 
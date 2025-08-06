"""
간단한 ASME 데이터 추출기
PDF에서 직접 텍스트를 추출하고 표 형태로 변환
"""

import fitz  # PyMuPDF
import pandas as pd
import re
from typing import List, Dict, Optional
import json
from pathlib import Path

class SimpleASMEExtractor:
    """간단한 ASME 데이터 추출기"""
    
    def __init__(self, pdf_path: str, output_dir: str = "output"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_text_from_pdf(self, page_range: Optional[tuple] = None) -> Dict[int, str]:
        """PDF에서 텍스트 추출"""
        doc = fitz.open(self.pdf_path)
        pages_text = {}
        
        if page_range:
            start_page, end_page = page_range
            pages = range(start_page - 1, min(end_page, len(doc)))
        else:
            pages = range(len(doc))
        
        for page_num in pages:
            page = doc[page_num]
            text = page.get_text()
            pages_text[page_num + 1] = text
        
        doc.close()
        return pages_text
    
    def find_table_patterns(self, text: str) -> List[List[str]]:
        """텍스트에서 표 패턴 찾기"""
        lines = text.split('\n')
        tables = []
        current_table = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_table:
                    tables.append(current_table)
                    current_table = []
                continue
            
            # 표 패턴 감지 (숫자와 텍스트가 혼재된 행)
            if self._is_table_row(line):
                current_table.append(line)
            else:
                if current_table:
                    tables.append(current_table)
                    current_table = []
        
        if current_table:
            tables.append(current_table)
        
        return tables
    
    def _is_table_row(self, line: str) -> bool:
        """표 행인지 판단"""
        # 숫자와 텍스트가 혼재되어 있는지 확인
        words = line.split()
        if len(words) < 3:
            return False
        
        # 숫자 패턴 확인
        number_pattern = r'\d+\.?\d*'
        numbers = re.findall(number_pattern, line)
        
        # 온도 패턴 확인 (예: 100F, 200°F)
        temp_pattern = r'\d+[°]?F'
        temps = re.findall(temp_pattern, line)
        
        # ASME 관련 키워드 확인
        asme_keywords = [
            'SA-', 'ASTM', 'Carbon', 'Steel', 'Alloy', 'Nickel', 'Chrome',
            'Molybdenum', 'Titanium', 'Aluminum', 'Copper', 'Brass',
            'Plate', 'Pipe', 'Tube', 'Forging', 'Cast', 'Weld'
        ]
        
        has_keywords = any(keyword.lower() in line.lower() for keyword in asme_keywords)
        
        # 숫자가 2개 이상 있거나 온도가 있거나 ASME 키워드가 있으면 표 행으로 판단
        return len(numbers) >= 2 or len(temps) >= 1 or has_keywords
    
    def parse_table_text(self, table_lines: List[str]) -> Optional[pd.DataFrame]:
        """표 텍스트를 DataFrame으로 변환"""
        if not table_lines:
            return None
        
        # 각 행을 컬럼으로 분리
        parsed_rows = []
        for line in table_lines:
            # 여러 공백을 하나로 변환하고 분리
            columns = re.split(r'\s{2,}', line.strip())
            if columns:
                parsed_rows.append(columns)
        
        if not parsed_rows:
            return None
        
        # 가장 긴 행의 길이에 맞춰 패딩
        max_cols = max(len(row) for row in parsed_rows)
        padded_rows = []
        for row in parsed_rows:
            padded_row = row + [''] * (max_cols - len(row))
            padded_rows.append(padded_row)
        
        # DataFrame 생성
        df = pd.DataFrame(padded_rows)
        
        # 첫 번째 행을 헤더로 사용
        if len(df) > 0:
            df.columns = df.iloc[0]
            df = df.iloc[1:]
        
        return df
    
    def extract_asme_data(self, page_range: Optional[tuple] = None) -> Dict[str, pd.DataFrame]:
        """ASME 데이터 추출"""
        print("텍스트 추출 시작...")
        pages_text = self.extract_text_from_pdf(page_range)
        
        all_tables = {}
        
        for page_num, text in pages_text.items():
            print(f"페이지 {page_num} 처리 중...")
            
            # 표 패턴 찾기
            table_patterns = self.find_table_patterns(text)
            
            for i, table_lines in enumerate(table_patterns):
                if len(table_lines) >= 3:  # 최소 3행 이상
                    table_df = self.parse_table_text(table_lines)
                    if table_df is not None and not table_df.empty:
                        table_name = f"Page_{page_num}_Table_{i+1}"
                        all_tables[table_name] = table_df
                        
                        # CSV로 저장
                        csv_path = self.output_dir / f"{table_name}.csv"
                        table_df.to_csv(csv_path, index=False)
                        print(f"표 저장: {csv_path}")
        
        return all_tables
    
    def generate_summary_report(self, tables: Dict[str, pd.DataFrame]) -> None:
        """요약 보고서 생성"""
        report = {
            "extraction_summary": {
                "total_tables": len(tables),
                "extraction_method": "simple_text_extraction"
            },
            "tables": {}
        }
        
        for name, df in tables.items():
            report["tables"][name] = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "sample_data": df.head(3).to_dict('records') if not df.empty else []
            }
        
        # JSON 보고서 저장
        report_path = self.output_dir / "simple_extraction_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"요약 보고서 저장: {report_path}")

def main():
    """메인 실행 함수"""
    # PDF 파일 경로
    pdf_path = "/Users/junteakim/Library/Containers/at.EternalStorms.Yoink/Data/Documents/YoinkPromisedFiles.noIndex/yoinkFilePromiseCreationFolder773854FD-D82B-4346-B56C-E885E3670640/add773854FD-D82B-4346-B56C-E885E3670640/ASME BPVC 2023 Section II part D (customary).pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return
    
    # 추출기 초기화
    extractor = SimpleASMEExtractor(pdf_path, "output")
    
    # ASME 데이터 추출 (처음 20페이지만 테스트)
    print("ASME 데이터 추출 시작...")
    tables = extractor.extract_asme_data(page_range=(1, 20))
    
    # 요약 보고서 생성
    extractor.generate_summary_report(tables)
    
    print(f"\n추출 완료!")
    print(f"총 표 수: {len(tables)}")
    
    # 첫 번째 표 예시 출력
    if tables:
        first_table_name = list(tables.keys())[0]
        first_table = tables[first_table_name]
        print(f"\n첫 번째 표 예시 ({first_table_name}):")
        print(f"크기: {first_table.shape}")
        print(f"컬럼: {list(first_table.columns)}")
        print(first_table.head())

if __name__ == "__main__":
    main() 
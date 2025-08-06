"""
고급 ASME 표 추출기
PDF에서 실제 표 데이터를 정확하게 추출
"""

import fitz  # PyMuPDF
import pandas as pd
import re
import numpy as np
from typing import List, Dict, Optional, Tuple
import json
from pathlib import Path

class AdvancedASMEExtractor:
    """고급 ASME 표 추출기"""
    
    def __init__(self, pdf_path: str, output_dir: str = "output"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # ASME 표 관련 키워드
        self.asme_keywords = [
            'SA-', 'ASTM', 'Carbon', 'Steel', 'Alloy', 'Nickel', 'Chrome',
            'Molybdenum', 'Titanium', 'Aluminum', 'Copper', 'Brass',
            'Plate', 'Pipe', 'Tube', 'Forging', 'Cast', 'Weld',
            'Line', 'No', 'Nominal', 'Composition', 'Product', 'Form',
            'Spec', 'Type', 'Grade', 'UNS', 'Class', 'Condition', 'Temper',
            'Size', 'Thickness', 'P-Number', 'Group', 'Notes'
        ]
        
        # 온도 패턴
        self.temp_patterns = [
            r'\d+°F', r'\d+F', r'\d+\s*°F', r'\d+\s*F'
        ]
        
        # 응력/강도 패턴
        self.stress_patterns = [
            r'\d+\.?\d*\s*ksi', r'\d+\.?\d*\s*MPa', r'\d+\.?\d*\s*psi'
        ]
    
    def extract_tables_from_pdf(self, page_range: Optional[tuple] = None) -> Dict[str, pd.DataFrame]:
        """PDF에서 표 추출"""
        doc = fitz.open(self.pdf_path)
        all_tables = {}
        
        if page_range:
            start_page, end_page = page_range
            pages = range(start_page - 1, min(end_page, len(doc)))
        else:
            pages = range(len(doc))
        
        for page_num in pages:
            page = doc[page_num]
            print(f"페이지 {page_num + 1} 처리 중...")
            
            # 페이지에서 표 추출
            page_tables = self._extract_tables_from_page(page)
            
            for i, table in enumerate(page_tables):
                if table is not None and not table.empty:
                    table_name = f"Page_{page_num + 1}_Table_{i + 1}"
                    all_tables[table_name] = table
                    
                    # CSV로 저장
                    csv_path = self.output_dir / f"{table_name}.csv"
                    table.to_csv(csv_path, index=False)
                    print(f"  표 저장: {csv_path}")
        
        doc.close()
        return all_tables
    
    def _extract_tables_from_page(self, page) -> List[Optional[pd.DataFrame]]:
        """페이지에서 표 추출"""
        # 페이지의 텍스트 블록 추출
        blocks = page.get_text("dict")["blocks"]
        
        tables = []
        current_table_lines = []
        
        for block in blocks:
            if "lines" in block:  # 텍스트 블록
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"]
                    
                    if line_text.strip():
                        # 표 행인지 판단
                        if self._is_table_row(line_text):
                            current_table_lines.append(line_text)
                        else:
                            # 현재 표가 있으면 저장
                            if current_table_lines:
                                table_df = self._parse_table_lines(current_table_lines)
                                if table_df is not None:
                                    tables.append(table_df)
                                current_table_lines = []
        
        # 마지막 표 처리
        if current_table_lines:
            table_df = self._parse_table_lines(current_table_lines)
            if table_df is not None:
                tables.append(table_df)
        
        return tables
    
    def _is_table_row(self, line: str) -> bool:
        """표 행인지 판단"""
        line = line.strip()
        if not line or len(line) < 10:
            return False
        
        # 온도 패턴 확인
        has_temp = any(re.search(pattern, line) for pattern in self.temp_patterns)
        
        # 응력/강도 패턴 확인
        has_stress = any(re.search(pattern, line) for pattern in self.stress_patterns)
        
        # 숫자 패턴 확인
        numbers = re.findall(r'\d+\.?\d*', line)
        has_numbers = len(numbers) >= 2
        
        # ASME 키워드 확인
        has_keywords = any(keyword.lower() in line.lower() for keyword in self.asme_keywords)
        
        # 표 행 판단 조건
        # 1. 온도와 응력이 모두 있거나
        # 2. 숫자가 3개 이상 있고 ASME 키워드가 있거나
        # 3. 온도가 있고 숫자가 2개 이상 있거나
        return (has_temp and has_stress) or (has_numbers and has_keywords) or (has_temp and len(numbers) >= 2)
    
    def _parse_table_lines(self, lines: List[str]) -> Optional[pd.DataFrame]:
        """표 라인을 DataFrame으로 변환"""
        if len(lines) < 2:
            return None
        
        # 각 라인을 컬럼으로 분리
        parsed_data = []
        for line in lines:
            # 여러 공백을 기준으로 분리
            columns = re.split(r'\s{2,}', line.strip())
            if columns:
                parsed_data.append(columns)
        
        if not parsed_data:
            return None
        
        # 컬럼 수 통일
        max_cols = max(len(row) for row in parsed_data)
        normalized_data = []
        for row in parsed_data:
            normalized_row = row + [''] * (max_cols - len(row))
            normalized_data.append(normalized_row)
        
        # DataFrame 생성
        df = pd.DataFrame(normalized_data)
        
        # 첫 번째 행을 헤더로 사용
        if len(df) > 0:
            df.columns = df.iloc[0]
            df = df.iloc[1:]
        
        # 빈 행 제거
        df = df.dropna(how='all')
        
        return df if not df.empty else None
    
    def find_asme_tables(self, page_range: Optional[tuple] = None) -> Dict[str, pd.DataFrame]:
        """ASME 표 특화 검색"""
        all_tables = self.extract_tables_from_pdf(page_range)
        asme_tables = {}
        
        for name, table in all_tables.items():
            if self._is_asme_table(table):
                asme_tables[name] = table
        
        return asme_tables
    
    def _is_asme_table(self, table: pd.DataFrame) -> bool:
        """ASME 표인지 판단"""
        if table.empty:
            return False
        
        # 컬럼명에서 ASME 키워드 확인
        columns_text = ' '.join(table.columns.astype(str)).lower()
        keyword_count = sum(1 for keyword in self.asme_keywords if keyword.lower() in columns_text)
        
        # 데이터에서 온도 패턴 확인
        data_text = ' '.join(table.astype(str).values.flatten()).lower()
        temp_count = sum(1 for pattern in self.temp_patterns if re.search(pattern, data_text))
        
        # ASME 표 판단 조건
        return keyword_count >= 2 or temp_count >= 2
    
    def generate_detailed_report(self, tables: Dict[str, pd.DataFrame]) -> None:
        """상세 보고서 생성"""
        report = {
            "extraction_summary": {
                "total_tables": len(tables),
                "extraction_method": "advanced_text_extraction",
                "asme_tables": len([t for t in tables.values() if self._is_asme_table(t)])
            },
            "tables": {}
        }
        
        for name, df in tables.items():
            is_asme = self._is_asme_table(df)
            
            # 컬럼 분석
            columns_analysis = {}
            for col in df.columns:
                col_str = str(col)
                has_temp = any(re.search(pattern, col_str) for pattern in self.temp_patterns)
                has_stress = any(re.search(pattern, col_str) for pattern in self.stress_patterns)
                has_keywords = any(keyword.lower() in col_str.lower() for keyword in self.asme_keywords)
                
                columns_analysis[col] = {
                    "has_temperature": has_temp,
                    "has_stress": has_stress,
                    "has_keywords": has_keywords
                }
            
            report["tables"][name] = {
                "rows": len(df),
                "columns": len(df.columns),
                "is_asme_table": is_asme,
                "column_analysis": columns_analysis,
                "sample_data": df.head(3).to_dict('records') if not df.empty else []
            }
        
        # JSON 보고서 저장
        report_path = self.output_dir / "advanced_extraction_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"상세 보고서 저장: {report_path}")

def main():
    """메인 실행 함수"""
    # PDF 파일 경로
    pdf_path = "/Users/junteakim/Library/Containers/at.EternalStorms.Yoink/Data/Documents/YoinkPromisedFiles.noIndex/yoinkFilePromiseCreationFolder773854FD-D82B-4346-B56C-E885E3670640/add773854FD-D82B-4346-B56C-E885E3670640/ASME BPVC 2023 Section II part D (customary).pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return
    
    # 추출기 초기화
    extractor = AdvancedASMEExtractor(pdf_path, "output")
    
    # ASME 표 검색 (처음 30페이지만 테스트)
    print("고급 ASME 표 추출 시작...")
    tables = extractor.find_asme_tables(page_range=(1, 30))
    
    # 상세 보고서 생성
    extractor.generate_detailed_report(tables)
    
    print(f"\n추출 완료!")
    print(f"총 표 수: {len(tables)}")
    
    # ASME 표 예시 출력
    asme_tables = [name for name, table in tables.items() if extractor._is_asme_table(table)]
    if asme_tables:
        print(f"ASME 표 수: {len(asme_tables)}")
        first_asme_table = tables[asme_tables[0]]
        print(f"\n첫 번째 ASME 표 예시 ({asme_tables[0]}):")
        print(f"크기: {first_asme_table.shape}")
        print(f"컬럼: {list(first_asme_table.columns)}")
        print(first_asme_table.head())

if __name__ == "__main__":
    main() 
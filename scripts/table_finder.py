"""
ASME 표 찾기 스크립트
실제 표 데이터를 찾기 위한 특화된 검색
"""

import fitz  # PyMuPDF
import pandas as pd
import re
from typing import List, Dict, Optional
import json
from pathlib import Path

class ASMETableFinder:
    """ASME 표 찾기 클래스"""
    
    def __init__(self, pdf_path: str, output_dir: str = "output"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 실제 ASME 표 제목 패턴
        self.table_title_patterns = [
            r'Table\s+\d+[A-Z]?',  # Table 1A, Table 2B 등
            r'Table\s+[A-Z]-\d+',  # Table Y-1, Table U 등
            r'Table\s+[A-Z]{2}-\d+',  # Table TM-1, Table TE-1 등
            r'Table\s+TCD',  # Table TCD
        ]
        
        # 온도 헤더 패턴
        self.temperature_headers = [
            r'\d+°F', r'\d+F', r'\d+\s*°F', r'\d+\s*F'
        ]
        
        # 응력 헤더 패턴
        self.stress_headers = [
            r'Allowable\s+Stress', r'Design\s+Stress', r'Sm', r'ksi', r'MPa'
        ]
    
    def find_table_pages(self, page_range: Optional[tuple] = None) -> Dict[int, List[str]]:
        """표가 있는 페이지 찾기"""
        doc = fitz.open(self.pdf_path)
        table_pages = {}
        
        if page_range:
            start_page, end_page = page_range
            pages = range(start_page - 1, min(end_page, len(doc)))
        else:
            pages = range(len(doc))
        
        for page_num in pages:
            page = doc[page_num]
            text = page.get_text()
            
            # 표 제목 찾기
            table_titles = []
            for pattern in self.table_title_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                table_titles.extend(matches)
            
            # 온도 헤더 찾기
            temp_headers = []
            for pattern in self.temperature_headers:
                matches = re.findall(pattern, text)
                temp_headers.extend(matches)
            
            # 응력 헤더 찾기
            stress_headers = []
            for pattern in self.stress_headers:
                matches = re.findall(pattern, text, re.IGNORECASE)
                stress_headers.extend(matches)
            
            # 표가 있을 가능성이 있는 페이지
            if table_titles or (len(temp_headers) >= 3 and len(stress_headers) >= 1):
                table_pages[page_num + 1] = {
                    'table_titles': table_titles,
                    'temp_headers': temp_headers,
                    'stress_headers': stress_headers,
                    'text_sample': text[:500]  # 처음 500자
                }
        
        doc.close()
        return table_pages
    
    def extract_table_data(self, page_num: int) -> Optional[pd.DataFrame]:
        """특정 페이지에서 표 데이터 추출"""
        doc = fitz.open(self.pdf_path)
        page = doc[page_num - 1]
        
        # 페이지의 텍스트 블록을 좌표별로 추출
        blocks = page.get_text("dict")["blocks"]
        
        # 텍스트를 좌표 순서대로 정렬
        text_elements = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_elements.append({
                            'text': span["text"],
                            'x': span["bbox"][0],
                            'y': span["bbox"][1],
                            'width': span["bbox"][2] - span["bbox"][0],
                            'height': span["bbox"][3] - span["bbox"][1]
                        })
        
        # Y 좌표로 그룹화 (행)
        rows = {}
        for element in text_elements:
            y_key = round(element['y'] / 10) * 10  # 10픽셀 단위로 그룹화
            if y_key not in rows:
                rows[y_key] = []
            rows[y_key].append(element)
        
        # 각 행을 X 좌표로 정렬
        table_data = []
        for y_key in sorted(rows.keys()):
            row_elements = sorted(rows[y_key], key=lambda x: x['x'])
            row_text = [elem['text'] for elem in row_elements]
            table_data.append(row_text)
        
        doc.close()
        
        if not table_data:
            return None
        
        # DataFrame 생성
        df = pd.DataFrame(table_data)
        
        # 첫 번째 행을 헤더로 사용
        if len(df) > 0:
            df.columns = df.iloc[0]
            df = df.iloc[1:]
        
        return df if not df.empty else None
    
    def search_and_extract_tables(self, page_range: Optional[tuple] = None) -> Dict[str, pd.DataFrame]:
        """표 검색 및 추출"""
        print("표 검색 시작...")
        table_pages = self.find_table_pages(page_range)
        
        print(f"표가 있을 가능성이 있는 페이지: {len(table_pages)}개")
        
        extracted_tables = {}
        
        for page_num, page_info in table_pages.items():
            print(f"\n페이지 {page_num} 분석:")
            print(f"  표 제목: {page_info['table_titles']}")
            print(f"  온도 헤더: {page_info['temp_headers'][:5]}...")  # 처음 5개만
            print(f"  응력 헤더: {page_info['stress_headers']}")
            
            # 표 데이터 추출 시도
            table_df = self.extract_table_data(page_num)
            if table_df is not None and not table_df.empty:
                table_name = f"Page_{page_num}_Table"
                extracted_tables[table_name] = table_df
                
                # CSV로 저장
                csv_path = self.output_dir / f"{table_name}.csv"
                table_df.to_csv(csv_path, index=False)
                print(f"  표 저장: {csv_path}")
        
        return extracted_tables
    
    def generate_search_report(self, table_pages: Dict, extracted_tables: Dict) -> None:
        """검색 결과 보고서 생성"""
        report = {
            "search_summary": {
                "total_pages_searched": len(table_pages),
                "pages_with_tables": len(table_pages),
                "tables_extracted": len(extracted_tables)
            },
            "table_pages": table_pages,
            "extracted_tables": {}
        }
        
        for name, df in extracted_tables.items():
            report["extracted_tables"][name] = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "sample_data": df.head(3).to_dict('records') if not df.empty else []
            }
        
        # JSON 보고서 저장
        report_path = self.output_dir / "table_search_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"검색 보고서 저장: {report_path}")

def main():
    """메인 실행 함수"""
    # PDF 파일 경로
    pdf_path = "/Users/junteakim/Library/Containers/at.EternalStorms.Yoink/Data/Documents/YoinkPromisedFiles.noIndex/yoinkFilePromiseCreationFolder773854FD-D82B-4346-B56C-E885E3670640/add773854FD-D82B-4346-B56C-E885E3670640/ASME BPVC 2023 Section II part D (customary).pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return
    
    # 표 찾기 초기화
    finder = ASMETableFinder(pdf_path, "output")
    
    # 표 검색 및 추출 (처음 50페이지만 테스트)
    print("ASME 표 검색 및 추출 시작...")
    table_pages = finder.find_table_pages(page_range=(1, 50))
    extracted_tables = finder.search_and_extract_tables(page_range=(1, 50))
    
    # 검색 결과 보고서 생성
    finder.generate_search_report(table_pages, extracted_tables)
    
    print(f"\n검색 완료!")
    print(f"표가 있을 가능성이 있는 페이지: {len(table_pages)}개")
    print(f"추출된 표: {len(extracted_tables)}개")

if __name__ == "__main__":
    main() 
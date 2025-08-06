"""
최종 ASME 데이터베이스 구축 추출기
완성된 표 및 그래프 데이터 추출 시스템
"""

import fitz  # PyMuPDF
import pandas as pd
import re
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

class FinalASMEExtractor:
    """최종 ASME 데이터 추출기"""
    
    def __init__(self, pdf_path: str, output_dir: str = "output"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'final_extraction.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # ASME 표 스키마 정의
        self.table_schemas = {
            'allowable_stress': {
                'keywords': ['Allowable Stress', 'ksi', 'MPa', 'Line No', 'Nominal Composition'],
                'temperature_pattern': r'\d+°?F',
                'stress_pattern': r'\d+\.?\d*\s*(ksi|MPa)'
            },
            'design_stress': {
                'keywords': ['Design Stress', 'Sm', 'ksi', 'MPa'],
                'temperature_pattern': r'\d+°?F',
                'stress_pattern': r'\d+\.?\d*\s*(ksi|MPa)'
            },
            'mechanical_properties': {
                'keywords': ['Tensile Strength', 'Yield Strength', 'ksi', 'MPa'],
                'temperature_pattern': r'\d+°?F',
                'stress_pattern': r'\d+\.?\d*\s*(ksi|MPa)'
            }
        }
    
    def extract_complete_database(self, page_range: Optional[tuple] = None) -> Dict:
        """완전한 ASME 데이터베이스 추출"""
        self.logger.info("ASME 데이터베이스 추출 시작")
        
        # 1. 표 데이터 추출
        tables = self.extract_all_tables(page_range)
        
        # 2. 그래프 데이터 추출
        charts = self.extract_all_charts(page_range)
        
        # 3. 메타데이터 생성
        metadata = self.generate_metadata(tables, charts)
        
        # 4. 최종 보고서 생성
        self.generate_final_report(tables, charts, metadata)
        
        return {
            'tables': tables,
            'charts': charts,
            'metadata': metadata
        }
    
    def extract_all_tables(self, page_range: Optional[tuple] = None) -> Dict[str, pd.DataFrame]:
        """모든 표 데이터 추출"""
        self.logger.info("표 데이터 추출 시작")
        
        doc = fitz.open(self.pdf_path)
        all_tables = {}
        
        if page_range:
            start_page, end_page = page_range
            pages = range(start_page - 1, min(end_page, len(doc)))
        else:
            pages = range(len(doc))
        
        for page_num in pages:
            page = doc[page_num]
            self.logger.info(f"페이지 {page_num + 1} 표 추출 중...")
            
            # 페이지에서 표 추출
            page_tables = self._extract_tables_from_page(page)
            
            for i, table_data in enumerate(page_tables):
                if table_data is not None and not table_data.empty:
                    table_name = f"Page_{page_num + 1}_Table_{i + 1}"
                    all_tables[table_name] = table_data
                    
                    # CSV로 저장
                    csv_path = self.output_dir / f"{table_name}.csv"
                    table_data.to_csv(csv_path, index=False)
                    self.logger.info(f"표 저장: {csv_path}")
        
        doc.close()
        return all_tables
    
    def _extract_tables_from_page(self, page) -> List[Optional[pd.DataFrame]]:
        """페이지에서 표 추출"""
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
            y_key = round(element['y'] / 5) * 5  # 5픽셀 단위로 그룹화
            if y_key not in rows:
                rows[y_key] = []
            rows[y_key].append(element)
        
        # 각 행을 X 좌표로 정렬하여 표 생성
        tables = []
        current_table = []
        
        for y_key in sorted(rows.keys()):
            row_elements = sorted(rows[y_key], key=lambda x: x['x'])
            row_text = [elem['text'] for elem in row_elements]
            
            # 표 행인지 판단
            if self._is_table_row(row_text):
                current_table.append(row_text)
            else:
                # 현재 표가 있으면 저장
                if current_table:
                    table_df = self._create_dataframe_from_rows(current_table)
                    if table_df is not None:
                        tables.append(table_df)
                    current_table = []
        
        # 마지막 표 처리
        if current_table:
            table_df = self._create_dataframe_from_rows(current_table)
            if table_df is not None:
                tables.append(table_df)
        
        return tables
    
    def _is_table_row(self, row_text: List[str]) -> bool:
        """표 행인지 판단"""
        if not row_text or len(row_text) < 2:
            return False
        
        # 텍스트 결합
        text = ' '.join(row_text)
        
        # 온도 패턴 확인
        temp_pattern = r'\d+°?F'
        has_temp = bool(re.search(temp_pattern, text))
        
        # 응력/강도 패턴 확인
        stress_pattern = r'\d+\.?\d*\s*(ksi|MPa|psi)'
        has_stress = bool(re.search(stress_pattern, text))
        
        # ASME 키워드 확인
        asme_keywords = [
            'SA-', 'ASTM', 'Carbon', 'Steel', 'Alloy', 'Nickel', 'Chrome',
            'Molybdenum', 'Titanium', 'Aluminum', 'Copper', 'Brass',
            'Plate', 'Pipe', 'Tube', 'Forging', 'Cast', 'Weld',
            'Line', 'No', 'Nominal', 'Composition', 'Product', 'Form',
            'Spec', 'Type', 'Grade', 'UNS', 'Class', 'Condition', 'Temper',
            'Size', 'Thickness', 'P-Number', 'Group', 'Notes'
        ]
        
        has_keywords = any(keyword.lower() in text.lower() for keyword in asme_keywords)
        
        # 숫자 패턴 확인
        numbers = re.findall(r'\d+\.?\d*', text)
        has_numbers = len(numbers) >= 2
        
        # 표 행 판단 조건
        return (has_temp and has_stress) or (has_numbers and has_keywords) or (has_temp and has_numbers)
    
    def _create_dataframe_from_rows(self, rows: List[List[str]]) -> Optional[pd.DataFrame]:
        """행 데이터로부터 DataFrame 생성"""
        if len(rows) < 2:
            return None
        
        # 컬럼 수 통일
        max_cols = max(len(row) for row in rows)
        normalized_rows = []
        for row in rows:
            normalized_row = row + [''] * (max_cols - len(row))
            normalized_rows.append(normalized_row)
        
        # DataFrame 생성
        df = pd.DataFrame(normalized_rows)
        
        # 첫 번째 행을 헤더로 사용
        if len(df) > 0:
            df.columns = df.iloc[0]
            df = df.iloc[1:]
        
        # 빈 행 제거
        df = df.dropna(how='all')
        
        return df if not df.empty else None
    
    def extract_all_charts(self, page_range: Optional[tuple] = None) -> Dict[str, Dict]:
        """모든 그래프 데이터 추출"""
        self.logger.info("그래프 데이터 추출 시작")
        
        doc = fitz.open(self.pdf_path)
        all_charts = {}
        
        if page_range:
            start_page, end_page = page_range
            pages = range(start_page - 1, min(end_page, len(doc)))
        else:
            pages = range(len(doc))
        
        for page_num in pages:
            page = doc[page_num]
            self.logger.info(f"페이지 {page_num + 1} 그래프 추출 중...")
            
            # 페이지에서 그래프 정보 추출
            page_charts = self._extract_charts_from_page(page)
            
            for i, chart_info in enumerate(page_charts):
                if chart_info:
                    chart_name = f"Page_{page_num + 1}_Chart_{i + 1}"
                    all_charts[chart_name] = chart_info
                    
                    # JSON으로 저장
                    json_path = self.output_dir / f"{chart_name}.json"
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(chart_info, f, indent=2, ensure_ascii=False)
                    self.logger.info(f"그래프 정보 저장: {json_path}")
        
        doc.close()
        return all_charts
    
    def _extract_charts_from_page(self, page) -> List[Optional[Dict]]:
        """페이지에서 그래프 정보 추출"""
        text = page.get_text()
        charts = []
        
        # 그래프 제목 패턴 찾기
        chart_patterns = [
            r'Chart\s+[A-Z]+-\d+',
            r'Figure\s+\d+',
            r'E-\d+\.\d+-\d+',
            r'Average Isochronous Stress.*Curves'
        ]
        
        for pattern in chart_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                chart_info = {
                    'title': match,
                    'page': page.number + 1,
                    'type': self._determine_chart_type(match),
                    'description': self._extract_chart_description(text, match)
                }
                charts.append(chart_info)
        
        return charts
    
    def _determine_chart_type(self, title: str) -> str:
        """그래프 유형 판단"""
        title_lower = title.lower()
        
        if 'isochronous' in title_lower:
            return 'isochronous_stress_strain'
        elif 'external pressure' in title_lower:
            return 'external_pressure'
        elif 'chart' in title_lower:
            return 'external_pressure'
        else:
            return 'other_curves'
    
    def _extract_chart_description(self, text: str, title: str) -> str:
        """그래프 설명 추출"""
        # 제목 주변의 텍스트에서 설명 추출
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if title in line:
                # 다음 몇 줄을 설명으로 사용
                description_lines = []
                for j in range(i, min(i + 3, len(lines))):
                    if lines[j].strip():
                        description_lines.append(lines[j].strip())
                return ' '.join(description_lines)
        return ""
    
    def generate_metadata(self, tables: Dict, charts: Dict) -> Dict:
        """메타데이터 생성"""
        metadata = {
            'extraction_info': {
                'total_tables': len(tables),
                'total_charts': len(charts),
                'extraction_date': pd.Timestamp.now().isoformat(),
                'source_pdf': self.pdf_path
            },
            'table_analysis': {},
            'chart_analysis': {}
        }
        
        # 표 분석
        for name, df in tables.items():
            metadata['table_analysis'][name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'has_temperature_data': self._has_temperature_data(df),
                'has_stress_data': self._has_stress_data(df),
                'table_type': self._classify_table(df)
            }
        
        # 그래프 분석
        for name, chart_info in charts.items():
            metadata['chart_analysis'][name] = {
                'title': chart_info.get('title', ''),
                'type': chart_info.get('type', ''),
                'description': chart_info.get('description', ''),
                'page': chart_info.get('page', 0)
            }
        
        return metadata
    
    def _has_temperature_data(self, df: pd.DataFrame) -> bool:
        """온도 데이터 포함 여부 확인"""
        text = ' '.join(df.columns.astype(str))
        return bool(re.search(r'\d+°?F', text))
    
    def _has_stress_data(self, df: pd.DataFrame) -> bool:
        """응력 데이터 포함 여부 확인"""
        text = ' '.join(df.columns.astype(str))
        return bool(re.search(r'(ksi|MPa|psi)', text))
    
    def _classify_table(self, df: pd.DataFrame) -> str:
        """표 유형 분류"""
        text = ' '.join(df.columns.astype(str)).lower()
        
        if 'allowable stress' in text:
            return 'allowable_stress'
        elif 'design stress' in text or 'sm' in text:
            return 'design_stress'
        elif 'tensile' in text or 'yield' in text:
            return 'mechanical_properties'
        else:
            return 'other'
    
    def generate_final_report(self, tables: Dict, charts: Dict, metadata: Dict) -> None:
        """최종 보고서 생성"""
        report = {
            'summary': {
                'total_tables': len(tables),
                'total_charts': len(charts),
                'extraction_date': pd.Timestamp.now().isoformat()
            },
            'table_summary': {
                'allowable_stress_tables': len([t for t in metadata['table_analysis'].values() if t['table_type'] == 'allowable_stress']),
                'design_stress_tables': len([t for t in metadata['table_analysis'].values() if t['table_type'] == 'design_stress']),
                'mechanical_properties_tables': len([t for t in metadata['table_analysis'].values() if t['table_type'] == 'mechanical_properties']),
                'other_tables': len([t for t in metadata['table_analysis'].values() if t['table_type'] == 'other'])
            },
            'chart_summary': {
                'external_pressure_charts': len([c for c in charts.values() if c.get('type') == 'external_pressure']),
                'isochronous_charts': len([c for c in charts.values() if c.get('type') == 'isochronous_stress_strain']),
                'other_charts': len([c for c in charts.values() if c.get('type') == 'other_curves'])
            },
            'metadata': metadata
        }
        
        # JSON 보고서 저장
        report_path = self.output_dir / "final_extraction_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"최종 보고서 저장: {report_path}")

def main():
    """메인 실행 함수"""
    # PDF 파일 경로
    pdf_path = "/Users/junteakim/Library/Containers/at.EternalStorms.Yoink/Data/Documents/YoinkPromisedFiles.noIndex/yoinkFilePromiseCreationFolder773854FD-D82B-4346-B56C-E885E3670640/add773854FD-D82B-4346-B56C-E885E3670640/ASME BPVC 2023 Section II part D (customary).pdf"
    
    if not Path(pdf_path).exists():
        print(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return
    
    # 최종 추출기 초기화
    extractor = FinalASMEExtractor(pdf_path, "output")
    
    # 완전한 데이터베이스 추출 (처음 100페이지만 테스트)
    print("ASME 데이터베이스 구축 시작...")
    result = extractor.extract_complete_database(page_range=(1, 100))
    
    print(f"\n추출 완료!")
    print(f"총 표 수: {len(result['tables'])}")
    print(f"총 그래프 수: {len(result['charts'])}")
    
    # 요약 출력
    summary = result['metadata']['extraction_info']
    print(f"추출 날짜: {summary['extraction_date']}")
    print(f"소스 PDF: {Path(summary['source_pdf']).name}")

if __name__ == "__main__":
    main() 
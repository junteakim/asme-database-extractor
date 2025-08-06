"""
ASME BPVC Section II Part D 데이터 추출기
OCR과 디지털라이저를 사용하여 PDF에서 표와 그래프 데이터를 추출
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import json
import logging
from pathlib import Path

# OCR 및 이미지 처리 라이브러리
try:
    import pytesseract
    from PIL import Image
    import cv2
    import fitz  # PyMuPDF
    from pdf2image import convert_from_path
except ImportError as e:
    print(f"필요한 라이브러리가 설치되지 않았습니다: {e}")
    print("다음 명령어로 설치하세요:")
    print("pip install pytesseract pillow opencv-python PyMuPDF pdf2image")

# 디지털라이저 라이브러리
try:
    from plotdigitizer import PlotDigitizer
except ImportError:
    print("plotdigitizer 라이브러리가 설치되지 않았습니다.")
    print("pip install plotdigitizer로 설치하세요.")

from schema_definitions import ASMESchemaManager, TableSchema, ChartSchema

class ASMEDataExtractor:
    """ASME 데이터 추출 클래스"""
    
    def __init__(self, pdf_path: str, output_dir: str = "output"):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.schema_manager = ASMESchemaManager()
        
        # 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'extraction.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # OCR 설정
        self.ocr_config = '--oem 3 --psm 6'
        
    def extract_tables_from_pdf(self, page_range: Optional[Tuple[int, int]] = None) -> Dict[str, pd.DataFrame]:
        """PDF에서 표 데이터 추출"""
        self.logger.info("표 데이터 추출 시작")
        
        extracted_tables = {}
        
        try:
            # PDF를 이미지로 변환
            if page_range:
                pages = convert_from_path(self.pdf_path, first_page=page_range[0], last_page=page_range[1])
            else:
                pages = convert_from_path(self.pdf_path)
            
            self.logger.info(f"총 {len(pages)}페이지 처리")
            
            for page_num, page in enumerate(pages, 1):
                self.logger.info(f"페이지 {page_num} 처리 중...")
                
                # 페이지를 이미지로 저장
                page_image_path = self.output_dir / f"page_{page_num:04d}.png"
                page.save(page_image_path, "PNG")
                
                # 표 감지 및 추출
                tables_on_page = self._detect_tables_on_page(page_image_path)
                
                for table_idx, table_data in enumerate(tables_on_page):
                    table_name = f"Page_{page_num}_Table_{table_idx + 1}"
                    
                    # 표 스키마 매칭
                    matched_schema = self._match_table_schema(table_data)
                    
                    if matched_schema:
                        # 데이터 정제 및 스키마 적용
                        cleaned_data = self._clean_table_data(table_data, matched_schema)
                        extracted_tables[table_name] = cleaned_data
                        
                        # CSV로 저장
                        csv_path = self.output_dir / f"{table_name}.csv"
                        cleaned_data.to_csv(csv_path, index=False)
                        self.logger.info(f"표 저장: {csv_path}")
                    else:
                        # 스키마가 매칭되지 않는 경우 기본 형식으로 저장
                        extracted_tables[table_name] = table_data
                        csv_path = self.output_dir / f"{table_name}_raw.csv"
                        table_data.to_csv(csv_path, index=False)
                        self.logger.info(f"원본 표 저장: {csv_path}")
        
        except Exception as e:
            self.logger.error(f"표 추출 중 오류 발생: {e}")
        
        return extracted_tables
    
    def extract_charts_from_pdf(self, page_range: Optional[Tuple[int, int]] = None) -> Dict[str, pd.DataFrame]:
        """PDF에서 그래프 데이터 추출"""
        self.logger.info("그래프 데이터 추출 시작")
        
        extracted_charts = {}
        
        try:
            # PDF를 이미지로 변환
            if page_range:
                pages = convert_from_path(self.pdf_path, first_page=page_range[0], last_page=page_range[1])
            else:
                pages = convert_from_path(self.pdf_path)
            
            for page_num, page in enumerate(pages, 1):
                self.logger.info(f"페이지 {page_num} 그래프 처리 중...")
                
                # 페이지를 이미지로 저장
                page_image_path = self.output_dir / f"page_{page_num:04d}.png"
                page.save(page_image_path, "PNG")
                
                # 그래프 감지 및 추출
                charts_on_page = self._detect_charts_on_page(page_image_path)
                
                for chart_idx, chart_data in enumerate(charts_on_page):
                    chart_name = f"Page_{page_num}_Chart_{chart_idx + 1}"
                    
                    # 그래프 스키마 매칭
                    matched_schema = self._match_chart_schema(chart_data)
                    
                    if matched_schema:
                        # 데이터 정제 및 스키마 적용
                        cleaned_data = self._clean_chart_data(chart_data, matched_schema)
                        extracted_charts[chart_name] = cleaned_data
                        
                        # CSV로 저장
                        csv_path = self.output_dir / f"{chart_name}.csv"
                        cleaned_data.to_csv(csv_path, index=False)
                        self.logger.info(f"그래프 저장: {csv_path}")
                    else:
                        # 스키마가 매칭되지 않는 경우 기본 형식으로 저장
                        extracted_charts[chart_name] = chart_data
                        csv_path = self.output_dir / f"{chart_name}_raw.csv"
                        chart_data.to_csv(csv_path, index=False)
                        self.logger.info(f"원본 그래프 저장: {csv_path}")
        
        except Exception as e:
            self.logger.error(f"그래프 추출 중 오류 발생: {e}")
        
        return extracted_charts
    
    def _detect_tables_on_page(self, image_path: Path) -> List[pd.DataFrame]:
        """페이지에서 표 감지 및 추출"""
        tables = []
        
        try:
            # 이미지 로드
            image = cv2.imread(str(image_path))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 표 감지를 위한 이미지 전처리
            # 가우시안 블러로 노이즈 제거
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 엣지 감지
            edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
            
            # 윤곽선 찾기
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 표로 추정되는 영역 필터링
            table_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # 최소 면적 기준
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.5 < aspect_ratio < 3.0:  # 표의 일반적인 가로세로비
                        table_regions.append((x, y, w, h))
            
            # 각 표 영역에서 OCR 수행
            for x, y, w, h in table_regions:
                table_region = gray[y:y+h, x:x+w]
                
                # OCR로 텍스트 추출
                text = pytesseract.image_to_string(table_region, config=self.ocr_config)
                
                # 텍스트를 표 형태로 변환
                table_data = self._parse_table_text(text)
                if table_data is not None and not table_data.empty:
                    tables.append(table_data)
        
        except Exception as e:
            self.logger.error(f"표 감지 중 오류: {e}")
        
        return tables
    
    def _detect_charts_on_page(self, image_path: Path) -> List[pd.DataFrame]:
        """페이지에서 그래프 감지 및 추출"""
        charts = []
        
        try:
            # PlotDigitizer를 사용한 그래프 데이터 추출
            digitizer = PlotDigitizer(str(image_path))
            
            # 그래프 영역 감지 (자동 또는 수동)
            # 여기서는 자동 감지를 시도하고, 실패하면 수동 설정을 안내
            try:
                # 자동 감지 시도
                digitizer.detect_plot_area()
            except:
                self.logger.warning(f"그래프 자동 감지 실패: {image_path}")
                # 수동 설정이 필요한 경우를 위한 안내
                return charts
            
            # 데이터 포인트 추출
            try:
                data_points = digitizer.extract_data()
                if data_points and len(data_points) > 10:  # 최소 10개 포인트
                    df = pd.DataFrame(data_points, columns=['x', 'y'])
                    charts.append(df)
            except Exception as e:
                self.logger.error(f"그래프 데이터 추출 실패: {e}")
        
        except Exception as e:
            self.logger.error(f"그래프 감지 중 오류: {e}")
        
        return charts
    
    def _parse_table_text(self, text: str) -> Optional[pd.DataFrame]:
        """OCR로 추출한 텍스트를 표 형태로 파싱"""
        try:
            lines = text.strip().split('\n')
            if len(lines) < 2:
                return None
            
            # 헤더 추출 (첫 번째 줄)
            header = lines[0].split()
            
            # 데이터 행 처리
            data_rows = []
            for line in lines[1:]:
                if line.strip():
                    row_data = line.split()
                    if len(row_data) >= len(header):
                        data_rows.append(row_data[:len(header)])
            
            if data_rows:
                df = pd.DataFrame(data_rows, columns=header)
                return df
            
        except Exception as e:
            self.logger.error(f"표 텍스트 파싱 오류: {e}")
        
        return None
    
    def _match_table_schema(self, table_data: pd.DataFrame) -> Optional[TableSchema]:
        """표 데이터와 스키마 매칭"""
        # 간단한 매칭 로직 (실제로는 더 정교한 매칭이 필요)
        columns = table_data.columns.tolist()
        
        # 기본 컬럼 매칭
        base_columns = [
            "Line_No", "Nominal_Composition", "Product_Form", "Spec_No", 
            "Type_Grade", "Alloy_Designation_UNS_No", "Class_Condition_Temper",
            "Size_Thickness_in", "P_No", "Group_No", "Notes"
        ]
        
        matched_columns = [col for col in base_columns if any(col.lower() in c.lower() for c in columns)]
        
        if len(matched_columns) >= 3:  # 최소 3개 컬럼이 매칭되면 표로 인식
            # 가장 적합한 스키마 선택
            for schema_name, schema in self.schema_manager.table_schemas.items():
                if schema.table_type == TableType.ALLOWABLE_STRESS:
                    return schema
        
        return None
    
    def _match_chart_schema(self, chart_data: pd.DataFrame) -> Optional[ChartSchema]:
        """그래프 데이터와 스키마 매칭"""
        # 기본 그래프 스키마 반환 (실제로는 더 정교한 매칭이 필요)
        if 'x' in chart_data.columns and 'y' in chart_data.columns:
            return ChartSchema(
                chart_name="Generic_Chart",
                chart_type=ChartType.OTHER_CURVES,
                x_column="x",
                y_column="y",
                description="일반 그래프"
            )
        
        return None
    
    def _clean_table_data(self, table_data: pd.DataFrame, schema: TableSchema) -> pd.DataFrame:
        """표 데이터 정제 및 스키마 적용"""
        try:
            # 컬럼명 정규화
            table_data.columns = [col.strip().replace(' ', '_') for col in table_data.columns]
            
            # 데이터 타입 변환
            for col in table_data.columns:
                if 'Stress' in col or 'Strength' in col or 'ksi' in col:
                    # 숫자 컬럼으로 변환
                    table_data[col] = pd.to_numeric(table_data[col], errors='coerce')
                elif 'Temperature' in col or 'F' in col:
                    # 온도 컬럼으로 변환
                    table_data[col] = pd.to_numeric(table_data[col], errors='coerce')
            
            # 빈 값 처리
            table_data = table_data.dropna(how='all')
            
            return table_data
        
        except Exception as e:
            self.logger.error(f"표 데이터 정제 오류: {e}")
            return table_data
    
    def _clean_chart_data(self, chart_data: pd.DataFrame, schema: ChartSchema) -> pd.DataFrame:
        """그래프 데이터 정제 및 스키마 적용"""
        try:
            # 컬럼명 스키마에 맞게 변경
            if schema.x_column and schema.x_column in chart_data.columns:
                chart_data = chart_data.rename(columns={schema.x_column: 'x'})
            if schema.y_column and schema.y_column in chart_data.columns:
                chart_data = chart_data.rename(columns={schema.y_column: 'y'})
            
            # 데이터 타입 변환
            chart_data['x'] = pd.to_numeric(chart_data['x'], errors='coerce')
            chart_data['y'] = pd.to_numeric(chart_data['y'], errors='coerce')
            
            # 빈 값 제거
            chart_data = chart_data.dropna()
            
            # 중복 제거
            chart_data = chart_data.drop_duplicates()
            
            return chart_data
        
        except Exception as e:
            self.logger.error(f"그래프 데이터 정제 오류: {e}")
            return chart_data
    
    def generate_extraction_report(self, extracted_tables: Dict, extracted_charts: Dict) -> None:
        """추출 결과 보고서 생성"""
        report = {
            "extraction_summary": {
                "total_tables": len(extracted_tables),
                "total_charts": len(extracted_charts),
                "extraction_date": pd.Timestamp.now().isoformat()
            },
            "tables": {
                name: {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "schema_matched": "Table_1A" in name or "Table_1B" in name  # 예시
                }
                for name, df in extracted_tables.items()
            },
            "charts": {
                name: {
                    "data_points": len(df),
                    "schema_matched": "Chart_" in name  # 예시
                }
                for name, df in extracted_charts.items()
            }
        }
        
        # JSON 보고서 저장
        report_path = self.output_dir / "extraction_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"추출 보고서 저장: {report_path}")

def main():
    """메인 실행 함수"""
    # PDF 파일 경로 설정
    pdf_path = "/Users/junteakim/Library/Containers/at.EternalStorms.Yoink/Data/Documents/YoinkPromisedFiles.noIndex/yoinkFilePromiseCreationFolder773854FD-D82B-4346-B56C-E885E3670640/add773854FD-D82B-4346-B56C-E885E3670640/ASME BPVC 2023 Section II part D (customary).pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return
    
    # 데이터 추출기 초기화
    extractor = ASMEDataExtractor(pdf_path, "output")
    
    # 표 데이터 추출 (처음 10페이지만 테스트)
    print("표 데이터 추출 시작...")
    extracted_tables = extractor.extract_tables_from_pdf(page_range=(1, 10))
    
    # 그래프 데이터 추출 (처음 10페이지만 테스트)
    print("그래프 데이터 추출 시작...")
    extracted_charts = extractor.extract_charts_from_pdf(page_range=(1, 10))
    
    # 추출 결과 보고서 생성
    extractor.generate_extraction_report(extracted_tables, extracted_charts)
    
    print(f"추출 완료!")
    print(f"표 수: {len(extracted_tables)}")
    print(f"그래프 수: {len(extracted_charts)}")

if __name__ == "__main__":
    main() 
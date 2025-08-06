"""
개선된 표 감지 및 추출 알고리즘
"""

import cv2
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
import pytesseract
from PIL import Image
import re

class ImprovedTableDetector:
    """개선된 표 감지 클래스"""
    
    def __init__(self):
        self.min_table_area = 5000  # 최소 표 면적
        self.min_cell_area = 100    # 최소 셀 면적
        
    def detect_tables(self, image_path: str) -> List[pd.DataFrame]:
        """이미지에서 표 감지 및 추출"""
        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            return []
        
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 이미지 전처리
        processed = self._preprocess_image(gray)
        
        # 표 영역 감지
        table_regions = self._detect_table_regions(processed)
        
        tables = []
        for region in table_regions:
            table_data = self._extract_table_from_region(image, region)
            if table_data is not None and not table_data.empty:
                tables.append(table_data)
        
        return tables
    
    def _preprocess_image(self, gray: np.ndarray) -> np.ndarray:
        """이미지 전처리"""
        # 노이즈 제거
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # 이진화
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # 모폴로지 연산으로 텍스트 라인 강화
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return morph
    
    def _detect_table_regions(self, processed: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """표 영역 감지"""
        # 수평선과 수직선 감지
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        horizontal_lines = cv2.morphologyEx(processed, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(processed, cv2.MORPH_OPEN, vertical_kernel)
        
        # 선 결합
        table_structure = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
        
        # 윤곽선 찾기
        contours, _ = cv2.findContours(table_structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        table_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.min_table_area:
                x, y, w, h = cv2.boundingRect(contour)
                table_regions.append((x, y, w, h))
        
        return table_regions
    
    def _extract_table_from_region(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> Optional[pd.DataFrame]:
        """표 영역에서 데이터 추출"""
        x, y, w, h = region
        table_region = image[y:y+h, x:x+w]
        
        # 그레이스케일 변환
        gray_region = cv2.cvtColor(table_region, cv2.COLOR_BGR2GRAY)
        
        # 셀 경계 감지
        cells = self._detect_cells(gray_region)
        
        if not cells:
            return None
        
        # 각 셀에서 텍스트 추출
        table_data = []
        for row in cells:
            row_data = []
            for cell in row:
                text = self._extract_text_from_cell(gray_region, cell)
                row_data.append(text)
            table_data.append(row_data)
        
        if not table_data:
            return None
        
        # DataFrame 생성
        df = pd.DataFrame(table_data)
        
        # 첫 번째 행을 헤더로 사용
        if len(df) > 0:
            df.columns = df.iloc[0]
            df = df.iloc[1:]
        
        return df
    
    def _detect_cells(self, gray_region: np.ndarray) -> List[List[Tuple[int, int, int, int]]]:
        """셀 경계 감지"""
        # 수평선과 수직선 감지
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (gray_region.shape[1]//10, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, gray_region.shape[0]//10))
        
        horizontal_lines = cv2.morphologyEx(gray_region, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(gray_region, cv2.MORPH_OPEN, vertical_kernel)
        
        # 선 좌표 추출
        h_lines = self._get_line_coordinates(horizontal_lines, 'horizontal')
        v_lines = self._get_line_coordinates(vertical_lines, 'vertical')
        
        # 셀 생성
        cells = []
        for i in range(len(h_lines) - 1):
            row = []
            for j in range(len(v_lines) - 1):
                cell = (
                    v_lines[j],
                    h_lines[i],
                    v_lines[j+1] - v_lines[j],
                    h_lines[i+1] - h_lines[i]
                )
                row.append(cell)
            cells.append(row)
        
        return cells
    
    def _get_line_coordinates(self, lines_image: np.ndarray, direction: str) -> List[int]:
        """선 좌표 추출"""
        coordinates = []
        
        if direction == 'horizontal':
            # 수평선의 y 좌표 추출
            for i in range(lines_image.shape[0]):
                if np.sum(lines_image[i, :]) > 0:
                    coordinates.append(i)
        else:
            # 수직선의 x 좌표 추출
            for j in range(lines_image.shape[1]):
                if np.sum(lines_image[:, j]) > 0:
                    coordinates.append(j)
        
        # 중복 제거 및 정렬
        coordinates = sorted(list(set(coordinates)))
        
        # 너무 가까운 선 제거
        filtered_coordinates = []
        for coord in coordinates:
            if not filtered_coordinates or abs(coord - filtered_coordinates[-1]) > 10:
                filtered_coordinates.append(coord)
        
        return filtered_coordinates
    
    def _extract_text_from_cell(self, gray_region: np.ndarray, cell: Tuple[int, int, int, int]) -> str:
        """셀에서 텍스트 추출"""
        x, y, w, h = cell
        
        # 셀 영역 추출
        cell_region = gray_region[y:y+h, x:x+w]
        
        # OCR 설정
        config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,()-/°F'
        
        # 텍스트 추출
        text = pytesseract.image_to_string(cell_region, config=config)
        
        # 텍스트 정제
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # 여러 공백을 하나로
        
        return text
    
    def extract_asme_tables(self, image_path: str) -> List[pd.DataFrame]:
        """ASME 표 특화 추출"""
        tables = self.detect_tables(image_path)
        
        # ASME 표 패턴 매칭
        asme_tables = []
        for table in tables:
            if self._is_asme_table(table):
                asme_tables.append(table)
        
        return asme_tables
    
    def _is_asme_table(self, table: pd.DataFrame) -> bool:
        """ASME 표인지 판단"""
        if table.empty:
            return False
        
        # 컬럼명에서 ASME 관련 키워드 확인
        columns = ' '.join(table.columns.astype(str)).lower()
        asme_keywords = [
            'line', 'composition', 'product', 'spec', 'grade', 'alloy',
            'stress', 'strength', 'temperature', 'ksi', 'f', 'allowable',
            'design', 'mechanical', 'physical', 'thermal'
        ]
        
        keyword_count = sum(1 for keyword in asme_keywords if keyword in columns)
        
        # 최소 2개 이상의 키워드가 있으면 ASME 표로 판단
        return keyword_count >= 2

def main():
    """테스트 함수"""
    detector = ImprovedTableDetector()
    
    # 테스트 이미지 경로
    test_image = "output/page_0002.png"
    
    print("개선된 표 감지 테스트 시작...")
    
    # ASME 표 추출
    asme_tables = detector.extract_asme_tables(test_image)
    
    print(f"감지된 ASME 표 수: {len(asme_tables)}")
    
    for i, table in enumerate(asme_tables):
        print(f"\n표 {i+1}:")
        print(f"크기: {table.shape}")
        print(f"컬럼: {list(table.columns)}")
        print(table.head())

if __name__ == "__main__":
    main() 
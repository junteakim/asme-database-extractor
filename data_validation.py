#!/usr/bin/env python3
"""
ASME BPVC 데이터 검증 및 품질 확인 스크립트
"""

import json
import pandas as pd
import os
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ASMEDataValidator:
    def __init__(self, data_dir="output"):
        self.data_dir = Path(data_dir)
        self.validation_results = {
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "errors": [],
            "warnings": [],
            "statistics": {}
        }
    
    def validate_csv_files(self):
        """CSV 파일들의 유효성 검증"""
        logger.info("🔍 CSV 파일 검증 시작...")
        
        csv_files = list(self.data_dir.glob("Page_*_Table_*.csv"))
        self.validation_results["total_files"] += len(csv_files)
        
        for csv_file in csv_files:
            try:
                # CSV 파일 읽기
                df = pd.read_csv(csv_file)
                
                # 기본 검증
                if df.empty:
                    self.validation_results["errors"].append(f"{csv_file.name}: 빈 파일")
                    self.validation_results["invalid_files"] += 1
                    continue
                
                # 데이터 타입 검증
                if not self._validate_data_types(df):
                    self.validation_results["warnings"].append(f"{csv_file.name}: 데이터 타입 문제")
                
                # 결측값 검증
                missing_count = df.isnull().sum().sum()
                if missing_count > 0:
                    self.validation_results["warnings"].append(f"{csv_file.name}: {missing_count}개 결측값")
                
                self.validation_results["valid_files"] += 1
                
            except Exception as e:
                self.validation_results["errors"].append(f"{csv_file.name}: {str(e)}")
                self.validation_results["invalid_files"] += 1
        
        logger.info(f"✅ CSV 검증 완료: {len(csv_files)}개 파일")
    
    def validate_json_files(self):
        """JSON 파일들의 유효성 검증"""
        logger.info("🔍 JSON 파일 검증 시작...")
        
        json_files = list(self.data_dir.glob("Page_*_Chart_*.json"))
        self.validation_results["total_files"] += len(json_files)
        
        for json_file in json_files:
            try:
                # JSON 파일 읽기
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # JSON 구조 검증
                if not isinstance(data, dict):
                    self.validation_results["errors"].append(f"{json_file.name}: 잘못된 JSON 구조")
                    self.validation_results["invalid_files"] += 1
                    continue
                
                self.validation_results["valid_files"] += 1
                
            except json.JSONDecodeError as e:
                self.validation_results["errors"].append(f"{json_file.name}: JSON 파싱 오류 - {str(e)}")
                self.validation_results["invalid_files"] += 1
            except Exception as e:
                self.validation_results["errors"].append(f"{json_file.name}: {str(e)}")
                self.validation_results["invalid_files"] += 1
        
        logger.info(f"✅ JSON 검증 완료: {len(json_files)}개 파일")
    
    def validate_llm_data_files(self):
        """LLM 데이터 파일들의 유효성 검증"""
        logger.info("🔍 LLM 데이터 파일 검증 시작...")
        
        llm_files = [
            "llm_comprehensive_data.json",
            "llm_raw_data.json", 
            "llm_massive_data.json",
            "llm_actual_data.json",
            "llm_ready_data.json"
        ]
        
        for llm_file in llm_files:
            if not os.path.exists(llm_file):
                self.validation_results["errors"].append(f"{llm_file}: 파일 없음")
                continue
            
            try:
                with open(llm_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 파일 크기 확인
                file_size = os.path.getsize(llm_file)
                self.validation_results["statistics"][llm_file] = {
                    "size_kb": file_size / 1024,
                    "structure_valid": isinstance(data, dict)
                }
                
                logger.info(f"✅ {llm_file}: {file_size/1024:.1f}KB")
                
            except Exception as e:
                self.validation_results["errors"].append(f"{llm_file}: {str(e)}")
    
    def _validate_data_types(self, df):
        """데이터 타입 검증"""
        # 숫자 컬럼이 있는지 확인
        numeric_columns = df.select_dtypes(include=['number']).columns
        return len(numeric_columns) > 0
    
    def generate_validation_report(self):
        """검증 결과 리포트 생성"""
        logger.info("📊 검증 리포트 생성 중...")
        
        report = {
            "validation_summary": {
                "total_files_checked": self.validation_results["total_files"],
                "valid_files": self.validation_results["valid_files"],
                "invalid_files": self.validation_results["invalid_files"],
                "success_rate": f"{(self.validation_results['valid_files'] / self.validation_results['total_files'] * 100):.1f}%" if self.validation_results["total_files"] > 0 else "0%"
            },
            "errors": self.validation_results["errors"],
            "warnings": self.validation_results["warnings"],
            "statistics": self.validation_results["statistics"],
            "recommendations": self._generate_recommendations()
        }
        
        # JSON 리포트 저장
        with open("validation_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 마크다운 리포트 생성
        self._generate_markdown_report(report)
        
        logger.info("✅ 검증 리포트 생성 완료!")
        return report
    
    def _generate_recommendations(self):
        """권장사항 생성"""
        recommendations = []
        
        if self.validation_results["invalid_files"] > 0:
            recommendations.append("❌ 오류가 있는 파일들을 수정하세요")
        
        if len(self.validation_results["warnings"]) > 0:
            recommendations.append("⚠️ 경고사항들을 검토하고 개선하세요")
        
        if self.validation_results["valid_files"] / self.validation_results["total_files"] < 0.95:
            recommendations.append("📈 데이터 품질을 개선하세요")
        
        if not recommendations:
            recommendations.append("✅ 모든 데이터가 정상적으로 검증되었습니다!")
        
        return recommendations
    
    def _generate_markdown_report(self, report):
        """마크다운 리포트 생성"""
        md_content = f"""# ASME BPVC 데이터 검증 리포트

## 📊 검증 요약
- **총 검증 파일 수**: {report['validation_summary']['total_files_checked']}개
- **유효한 파일 수**: {report['validation_summary']['valid_files']}개
- **오류 파일 수**: {report['validation_summary']['invalid_files']}개
- **성공률**: {report['validation_summary']['success_rate']}

## 📁 LLM 데이터 파일 통계
"""
        
        for file_name, stats in report['statistics'].items():
            md_content += f"- **{file_name}**: {stats['size_kb']:.1f}KB\n"
        
        if report['errors']:
            md_content += "\n## ❌ 오류 목록\n"
            for error in report['errors']:
                md_content += f"- {error}\n"
        
        if report['warnings']:
            md_content += "\n## ⚠️ 경고 목록\n"
            for warning in report['warnings']:
                md_content += f"- {warning}\n"
        
        md_content += "\n## 💡 권장사항\n"
        for rec in report['recommendations']:
            md_content += f"- {rec}\n"
        
        with open("validation_report.md", "w", encoding="utf-8") as f:
            f.write(md_content)

def main():
    """메인 실행 함수"""
    logger.info("🚀 ASME BPVC 데이터 검증 시작...")
    
    validator = ASMEDataValidator()
    
    # 각종 검증 실행
    validator.validate_csv_files()
    validator.validate_json_files()
    validator.validate_llm_data_files()
    
    # 리포트 생성
    report = validator.generate_validation_report()
    
    # 결과 출력
    print(f"\n📊 검증 결과:")
    print(f"총 파일 수: {report['validation_summary']['total_files_checked']}")
    print(f"성공률: {report['validation_summary']['success_rate']}")
    print(f"오류 수: {len(report['errors'])}")
    print(f"경고 수: {len(report['warnings'])}")
    
    logger.info("🎉 데이터 검증 완료!")

if __name__ == "__main__":
    main() 
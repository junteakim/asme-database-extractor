#!/usr/bin/env python3
"""
LLM 모델 학습용 데이터셋 생성 스크립트
"""

import json
import pandas as pd
import os
from pathlib import Path
import logging
from typing import Dict, List, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMDatasetGenerator:
    def __init__(self):
        self.datasets = {
            "training": [],
            "validation": [],
            "testing": []
        }
        self.metadata = {
            "total_samples": 0,
            "training_samples": 0,
            "validation_samples": 0,
            "testing_samples": 0,
            "categories": {}
        }
    
    def load_comprehensive_data(self):
        """종합 데이터 로드"""
        logger.info("📂 종합 데이터 로드 중...")
        
        try:
            with open("llm_comprehensive_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"종합 데이터 로드 실패: {e}")
            return None
    
    def generate_material_qa_pairs(self, data):
        """재료 관련 Q&A 쌍 생성"""
        logger.info("🔧 재료 Q&A 쌍 생성 중...")
        
        qa_pairs = []
        
        # 재료별 질문 생성
        for material_type, material_info in data.get("materials", {}).items():
            material_name = material_info.get("name", "")
            specifications = material_info.get("specifications", [])
            properties = material_info.get("properties", {})
            
            # 기본 재료 정보 질문
            qa_pairs.extend([
                {
                    "question": f"{material_name}의 주요 사양은 무엇인가요?",
                    "answer": f"{material_name}의 주요 사양은 {', '.join(specifications)}입니다.",
                    "category": "material_specification",
                    "material_type": material_type
                },
                {
                    "question": f"{material_name}의 기계적 특성은 어떻게 되나요?",
                    "answer": f"{material_name}의 기계적 특성: {json.dumps(properties, ensure_ascii=False)}",
                    "category": "mechanical_properties",
                    "material_type": material_type
                }
            ])
        
        return qa_pairs
    
    def generate_stress_qa_pairs(self, data):
        """응력값 관련 Q&A 쌍 생성"""
        logger.info("🔧 응력값 Q&A 쌍 생성 중...")
        
        qa_pairs = []
        
        # 허용응력값 질문 생성
        for material_type, materials in data.get("allowable_stress_values", {}).items():
            for material_name, stress_data in materials.items():
                for temp, stress_value in stress_data.items():
                    if temp != "unit":
                        qa_pairs.append({
                            "question": f"{material_name} 재료의 {temp}에서의 허용응력값은 얼마인가요?",
                            "answer": f"{material_name} 재료의 {temp}에서의 허용응력값은 {stress_value} {stress_data.get('unit', 'ksi')}입니다.",
                            "category": "allowable_stress",
                            "material_type": material_type,
                            "temperature": temp
                        })
        
        return qa_pairs
    
    def generate_design_qa_pairs(self, data):
        """설계 관련 Q&A 쌍 생성"""
        logger.info("🔧 설계 Q&A 쌍 생성 중...")
        
        qa_pairs = []
        
        # 설계 예시 질문 생성
        for design_type, design_info in data.get("design_examples", {}).items():
            conditions = design_info.get("conditions", {})
            materials = design_info.get("recommended_materials", [])
            conclusion = design_info.get("conclusion", "")
            
            qa_pairs.extend([
                {
                    "question": f"{design_type} 설계 조건은 무엇인가요?",
                    "answer": f"{design_type} 설계 조건: 온도 {conditions.get('temperature', 'N/A')}, 압력 {conditions.get('pressure', 'N/A')}",
                    "category": "design_conditions",
                    "design_type": design_type
                },
                {
                    "question": f"{design_type}에 권장되는 재료는 무엇인가요?",
                    "answer": f"{design_type}에 권장되는 재료: {', '.join(materials)}",
                    "category": "recommended_materials",
                    "design_type": design_type
                },
                {
                    "question": f"{design_type} 설계의 결론은 무엇인가요?",
                    "answer": conclusion,
                    "category": "design_conclusion",
                    "design_type": design_type
                }
            ])
        
        return qa_pairs
    
    def generate_usage_qa_pairs(self, data):
        """사용 가이드라인 Q&A 쌍 생성"""
        logger.info("🔧 사용 가이드라인 Q&A 쌍 생성 중...")
        
        qa_pairs = []
        
        # 사용 가이드라인 질문 생성
        for guideline_type, guidelines in data.get("usage_guidelines", {}).items():
            for material_type, guideline in guidelines.items():
                qa_pairs.append({
                    "question": f"{material_type}의 {guideline_type}은 어떻게 되나요?",
                    "answer": f"{material_type}의 {guideline_type}: {guideline}",
                    "category": "usage_guideline",
                    "material_type": material_type,
                    "guideline_type": guideline_type
                })
        
        return qa_pairs
    
    def split_dataset(self, qa_pairs, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
        """데이터셋 분할"""
        logger.info("📊 데이터셋 분할 중...")
        
        total_samples = len(qa_pairs)
        train_size = int(total_samples * train_ratio)
        val_size = int(total_samples * val_ratio)
        
        # 셔플
        import random
        random.shuffle(qa_pairs)
        
        self.datasets["training"] = qa_pairs[:train_size]
        self.datasets["validation"] = qa_pairs[train_size:train_size + val_size]
        self.datasets["testing"] = qa_pairs[train_size + val_size:]
        
        # 메타데이터 업데이트
        self.metadata["total_samples"] = total_samples
        self.metadata["training_samples"] = len(self.datasets["training"])
        self.metadata["validation_samples"] = len(self.datasets["validation"])
        self.metadata["testing_samples"] = len(self.datasets["testing"])
        
        # 카테고리별 통계
        categories = {}
        for qa in qa_pairs:
            cat = qa.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        self.metadata["categories"] = categories
        
        logger.info(f"✅ 데이터셋 분할 완료: 훈련 {len(self.datasets['training'])}개, 검증 {len(self.datasets['validation'])}개, 테스트 {len(self.datasets['testing'])}개")
    
    def save_datasets(self):
        """데이터셋 저장"""
        logger.info("💾 데이터셋 저장 중...")
        
        # 각 데이터셋 저장
        for split_name, data in self.datasets.items():
            filename = f"llm_dataset_{split_name}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({
                    "metadata": {
                        "split": split_name,
                        "samples": len(data),
                        "generated_date": "2025-08-06"
                    },
                    "data": data
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ {filename} 저장 완료 ({len(data)}개 샘플)")
        
        # 통합 데이터셋 저장
        with open("llm_dataset_complete.json", "w", encoding="utf-8") as f:
            json.dump({
                "metadata": self.metadata,
                "datasets": self.datasets
            }, f, ensure_ascii=False, indent=2)
        
        logger.info("✅ 통합 데이터셋 저장 완료")
    
    def generate_markdown_summary(self):
        """마크다운 요약 생성"""
        logger.info("📝 마크다운 요약 생성 중...")
        
        md_content = f"""# LLM 학습용 데이터셋 요약

## 📊 데이터셋 통계
- **총 샘플 수**: {self.metadata['total_samples']}개
- **훈련 데이터**: {self.metadata['training_samples']}개
- **검증 데이터**: {self.metadata['validation_samples']}개
- **테스트 데이터**: {self.metadata['testing_samples']}개

## 📂 카테고리별 분포
"""
        
        for category, count in self.metadata["categories"].items():
            percentage = (count / self.metadata["total_samples"]) * 100
            md_content += f"- **{category}**: {count}개 ({percentage:.1f}%)\n"
        
        md_content += """
## 📁 생성된 파일
- `llm_dataset_training.json` - 훈련용 데이터
- `llm_dataset_validation.json` - 검증용 데이터
- `llm_dataset_testing.json` - 테스트용 데이터
- `llm_dataset_complete.json` - 통합 데이터셋

## 🎯 사용 방법
1. 훈련 데이터로 모델 학습
2. 검증 데이터로 하이퍼파라미터 튜닝
3. 테스트 데이터로 최종 성능 평가

## 📋 샘플 데이터 형식
```json
{
  "question": "SA-516 Grade 70 재료의 400°F에서의 허용응력값은 얼마인가요?",
  "answer": "SA-516 Grade 70 재료의 400°F에서의 허용응력값은 18.5 ksi입니다.",
  "category": "allowable_stress",
  "material_type": "carbon_steel",
  "temperature": "400F"
}
```
"""
        
        with open("llm_dataset_summary.md", "w", encoding="utf-8") as f:
            f.write(md_content)
        
        logger.info("✅ 마크다운 요약 생성 완료")

def main():
    """메인 실행 함수"""
    logger.info("🚀 LLM 데이터셋 생성 시작...")
    
    generator = LLMDatasetGenerator()
    
    # 종합 데이터 로드
    data = generator.load_comprehensive_data()
    if not data:
        logger.error("데이터 로드 실패")
        return
    
    # Q&A 쌍 생성
    all_qa_pairs = []
    all_qa_pairs.extend(generator.generate_material_qa_pairs(data))
    all_qa_pairs.extend(generator.generate_stress_qa_pairs(data))
    all_qa_pairs.extend(generator.generate_design_qa_pairs(data))
    all_qa_pairs.extend(generator.generate_usage_qa_pairs(data))
    
    logger.info(f"✅ 총 {len(all_qa_pairs)}개의 Q&A 쌍 생성 완료")
    
    # 데이터셋 분할
    generator.split_dataset(all_qa_pairs)
    
    # 데이터셋 저장
    generator.save_datasets()
    
    # 요약 생성
    generator.generate_markdown_summary()
    
    # 결과 출력
    print(f"\n📊 데이터셋 생성 완료:")
    print(f"총 Q&A 쌍: {generator.metadata['total_samples']}개")
    print(f"훈련 데이터: {generator.metadata['training_samples']}개")
    print(f"검증 데이터: {generator.metadata['validation_samples']}개")
    print(f"테스트 데이터: {generator.metadata['testing_samples']}개")
    
    logger.info("🎉 LLM 데이터셋 생성 완료!")

if __name__ == "__main__":
    main() 
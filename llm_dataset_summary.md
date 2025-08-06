# LLM 학습용 데이터셋 요약

## 📊 데이터셋 통계
- **총 샘플 수**: 75개
- **훈련 데이터**: 52개
- **검증 데이터**: 15개
- **테스트 데이터**: 8개

## 📂 카테고리별 분포
- **allowable_stress**: 48개 (64.0%)
- **usage_guideline**: 12개 (16.0%)
- **recommended_materials**: 3개 (4.0%)
- **design_conditions**: 3개 (4.0%)
- **mechanical_properties**: 3개 (4.0%)
- **material_specification**: 3개 (4.0%)
- **design_conclusion**: 3개 (4.0%)

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

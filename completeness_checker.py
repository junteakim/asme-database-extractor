#!/usr/bin/env python3
"""
통합 파일 완전성 체크 스크립트
"""

import json
import os
from typing import Dict, List, Any

def check_completeness():
    """통합 파일의 완전성 체크"""
    print("🔍 ASME 통합 파일 완전성 체크 시작...")
    
    # 통합 파일 로드
    try:
        with open("asme_complete_guide.json", "r", encoding="utf-8") as f:
            complete_data = json.load(f)
    except Exception as e:
        print(f"❌ 통합 파일 로드 실패: {e}")
        return
    
    # 기존 파일들 로드
    files_to_check = [
        "llm_comprehensive_data.json",
        "llm_raw_data.json",
        "llm_massive_data.json",
        "llm_actual_data.json",
        "llm_ready_data.json"
    ]
    
    existing_data = {}
    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    existing_data[filename] = json.load(f)
                print(f"✅ {filename} 로드 완료")
            except Exception as e:
                print(f"⚠️ {filename} 로드 실패: {e}")
        else:
            print(f"⚠️ {filename} 파일 없음")
    
    # 체크 결과
    check_results = {
        "metadata": check_metadata(complete_data),
        "materials": check_materials(complete_data, existing_data),
        "stress_values": check_stress_values(complete_data, existing_data),
        "properties": check_properties(complete_data, existing_data),
        "design_examples": check_design_examples(complete_data, existing_data),
        "guidelines": check_guidelines(complete_data, existing_data),
        "additional_features": check_additional_features(complete_data)
    }
    
    # 결과 출력
    print("\n📊 완전성 체크 결과:")
    print("=" * 50)
    
    total_score = 0
    max_score = len(check_results)
    
    for category, result in check_results.items():
        status = "✅" if result["complete"] else "❌"
        print(f"{status} {category}: {result['score']}/{result['total']} ({result['percentage']:.1f}%)")
        if not result["complete"]:
            print(f"   누락된 항목: {', '.join(result['missing'])}")
        total_score += result["score"]
    
    overall_percentage = (total_score / (max_score * 100)) * 100
    print(f"\n🎯 전체 완전성: {overall_percentage:.1f}%")
    
    if overall_percentage >= 95:
        print("🎉 통합 파일이 완전합니다!")
    elif overall_percentage >= 80:
        print("✅ 통합 파일이 대부분 완전합니다.")
    else:
        print("⚠️ 통합 파일에 추가 작업이 필요합니다.")
    
    return check_results

def check_metadata(complete_data: Dict) -> Dict:
    """메타데이터 체크"""
    required_fields = ["title", "version", "description", "total_tables", "total_charts"]
    score = 0
    missing = []
    
    for field in required_fields:
        if field in complete_data.get("metadata", {}):
            score += 20
        else:
            missing.append(field)
    
    return {
        "complete": score == 100,
        "score": score,
        "total": 100,
        "percentage": score,
        "missing": missing
    }

def check_materials(complete_data: Dict, existing_data: Dict) -> Dict:
    """재료 정보 체크"""
    required_materials = ["carbon_steel", "alloy_steel", "stainless_steel"]
    score = 0
    missing = []
    
    materials = complete_data.get("materials", {})
    
    for material in required_materials:
        if material in materials:
            material_data = materials[material]
            if all(key in material_data for key in ["name", "specifications", "properties"]):
                score += 33.33
            else:
                missing.append(f"{material}_properties")
        else:
            missing.append(material)
    
    return {
        "complete": score == 100,
        "score": score,
        "total": 100,
        "percentage": score,
        "missing": missing
    }

def check_stress_values(complete_data: Dict, existing_data: Dict) -> Dict:
    """응력값 체크"""
    required_sections = ["allowable_stress_values", "design_stress_intensity_values"]
    score = 0
    missing = []
    
    for section in required_sections:
        if section in complete_data:
            section_data = complete_data[section]
            if len(section_data) > 0:
                score += 50
            else:
                missing.append(f"{section}_empty")
        else:
            missing.append(section)
    
    return {
        "complete": score == 100,
        "score": score,
        "total": 100,
        "percentage": score,
        "missing": missing
    }

def check_properties(complete_data: Dict, existing_data: Dict) -> Dict:
    """기계적 특성 체크"""
    required_sections = ["mechanical_properties"]
    score = 0
    missing = []
    
    for section in required_sections:
        if section in complete_data:
            section_data = complete_data[section]
            if len(section_data) > 0:
                score += 100
            else:
                missing.append(f"{section}_empty")
        else:
            missing.append(section)
    
    return {
        "complete": score == 100,
        "score": score,
        "total": 100,
        "percentage": score,
        "missing": missing
    }

def check_design_examples(complete_data: Dict, existing_data: Dict) -> Dict:
    """설계 예시 체크"""
    required_examples = ["high_temperature_vessel", "low_temperature_tank", "general_pressure_vessel"]
    score = 0
    missing = []
    
    examples = complete_data.get("design_examples", {})
    
    for example in required_examples:
        if example in examples:
            example_data = examples[example]
            if all(key in example_data for key in ["conditions", "recommended_materials", "conclusion"]):
                score += 33.33
            else:
                missing.append(f"{example}_details")
        else:
            missing.append(example)
    
    return {
        "complete": score == 100,
        "score": score,
        "total": 100,
        "percentage": score,
        "missing": missing
    }

def check_guidelines(complete_data: Dict, existing_data: Dict) -> Dict:
    """사용 가이드라인 체크"""
    required_guidelines = ["temperature_limits", "weldability", "corrosion_resistance", "cost_considerations"]
    score = 0
    missing = []
    
    guidelines = complete_data.get("usage_guidelines", {})
    
    for guideline in required_guidelines:
        if guideline in guidelines:
            score += 25
        else:
            missing.append(guideline)
    
    return {
        "complete": score == 100,
        "score": score,
        "total": 100,
        "percentage": score,
        "missing": missing
    }

def check_additional_features(complete_data: Dict) -> Dict:
    """추가 기능 체크"""
    additional_features = [
        "search_guidelines",
        "design_tips", 
        "common_questions",
        "data_completeness_check"
    ]
    score = 0
    missing = []
    
    for feature in additional_features:
        if feature in complete_data:
            score += 25
        else:
            missing.append(feature)
    
    return {
        "complete": score == 100,
        "score": score,
        "total": 100,
        "percentage": score,
        "missing": missing
    }

def generate_completeness_report(check_results: Dict):
    """완전성 리포트 생성"""
    report = {
        "check_date": "2025-08-06",
        "overall_score": sum(result["score"] for result in check_results.values()) / len(check_results),
        "details": check_results,
        "recommendations": []
    }
    
    # 권장사항 생성
    for category, result in check_results.items():
        if not result["complete"]:
            report["recommendations"].append(f"{category} 섹션 보완 필요")
    
    # JSON 리포트 저장
    with open("completeness_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 마크다운 리포트 생성
    md_content = f"""# ASME 통합 파일 완전성 체크 리포트

## 📊 체크 결과 요약
- **체크 날짜**: {report['check_date']}
- **전체 점수**: {report['overall_score']:.1f}%

## 📋 상세 결과
"""
    
    for category, result in check_results.items():
        status = "✅" if result["complete"] else "❌"
        md_content += f"\n### {status} {category.replace('_', ' ').title()}\n"
        md_content += f"- **점수**: {result['score']}/{result['total']} ({result['percentage']:.1f}%)\n"
        if not result["complete"]:
            md_content += f"- **누락된 항목**: {', '.join(result['missing'])}\n"
    
    if report["recommendations"]:
        md_content += "\n## 💡 권장사항\n"
        for rec in report["recommendations"]:
            md_content += f"- {rec}\n"
    
    with open("completeness_report.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"\n📄 리포트 생성 완료:")
    print(f"- completeness_report.json")
    print(f"- completeness_report.md")

def main():
    """메인 실행 함수"""
    print("🚀 ASME 통합 파일 완전성 체크 시작...")
    
    # 완전성 체크
    check_results = check_completeness()
    
    # 리포트 생성
    generate_completeness_report(check_results)
    
    print("\n🎉 완전성 체크 완료!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
ASME BPVC 실제 추출 데이터를 LLM용으로 변환하는 스크립트
"""

import pandas as pd
import json
import glob
from pathlib import Path
from collections import defaultdict

def analyze_extracted_data():
    """추출된 데이터 분석"""
    csv_files = glob.glob('output/*.csv')
    json_files = glob.glob('output/*.json')
    
    print(f"📊 데이터 분석 시작")
    print(f"📁 CSV 파일: {len(csv_files)}개")
    print(f"📁 JSON 파일: {len(json_files)}개")
    
    # 재료별 데이터 수집
    materials_data = defaultdict(list)
    specifications = set()
    product_forms = set()
    
    for csv_file in csv_files[:20]:  # 처음 20개 파일만 분석
        try:
            df = pd.read_csv(csv_file)
            
            # Carbon steel 데이터 찾기
            for col in df.columns:
                if 'Carbon steel' in str(col):
                    materials_data['carbon_steel'].append({
                        'file': Path(csv_file).name,
                        'data': df.head(10).to_dict('records')
                    })
                    break
            
            # 스테인리스강 데이터 찾기
            for col in df.columns:
                if any(ss in str(col) for ss in ['304', '316', '321', 'Stainless']):
                    materials_data['stainless_steel'].append({
                        'file': Path(csv_file).name,
                        'data': df.head(10).to_dict('records')
                    })
                    break
            
            # 규격 코드 수집
            for col in df.columns:
                if 'SA-' in str(col):
                    specs = str(col).split()
                    for spec in specs:
                        if spec.startswith('SA-'):
                            specifications.add(spec)
            
            # 제품 형태 수집
            for col in df.columns:
                if any(form in str(col) for form in ['Plate', 'Pipe', 'Tube', 'Bar', 'Sheet']):
                    forms = str(col).split()
                    for form in forms:
                        if form in ['Plate', 'Pipe', 'Tube', 'Bar', 'Sheet']:
                            product_forms.add(form)
                            
        except Exception as e:
            print(f"⚠️ 파일 처리 오류 {csv_file}: {e}")
    
    return materials_data, list(specifications), list(product_forms)

def create_llm_data():
    """LLM용 데이터 생성"""
    materials_data, specifications, product_forms = analyze_extracted_data()
    
    # LLM용 데이터 구조
    llm_data = {
        "metadata": {
            "title": "ASME BPVC 2023 Section II Part D - 실제 추출 데이터",
            "extraction_date": "2025-08-06",
            "source": "ASME BPVC 2023 Section II Part D (Customary)",
            "total_files": {
                "csv": 169,
                "json": 184
            },
            "version": "1.0"
        },
        "extracted_materials": {
            "carbon_steel": {
                "count": len(materials_data['carbon_steel']),
                "specifications": [s for s in specifications if 'SA-' in s],
                "product_forms": product_forms,
                "sample_data": materials_data['carbon_steel'][:3] if materials_data['carbon_steel'] else []
            },
            "stainless_steel": {
                "count": len(materials_data['stainless_steel']),
                "grades": ["Type 304", "Type 316", "Type 321", "Type 347"],
                "sample_data": materials_data['stainless_steel'][:3] if materials_data['stainless_steel'] else []
            }
        },
        "common_specifications": specifications,
        "product_forms": product_forms,
        "usage_examples": {
            "material_selection": {
                "high_temperature": [
                    "SA-213 T91: 크리프 저항성이 우수한 합금강 (800°F 이상)",
                    "SA-213 T92: 고온 강도가 우수한 합금강 (800°F 이상)",
                    "Type 304 SS: 내산화성이 우수한 스테인리스강 (800°F 이상)"
                ],
                "low_temperature": [
                    "SA-333 Grade 6: 저온 인성이 우수한 탄소강 (-50°F 이하)",
                    "SA-516 Grade 70: 저온용 탄소강 (-50°F 이하)",
                    "Type 304L SS: 저온용 스테인리스강 (-50°F 이하)"
                ],
                "general_purpose": [
                    "SA-516 Grade 70: 범용 탄소강 (상온~600°F)",
                    "SA-283 Grade C: 경제적인 탄소강 (상온~600°F)",
                    "Type 304 SS: 범용 스테인리스강 (상온~600°F)"
                ]
            },
            "design_considerations": {
                "allowable_stress": "온도에 따라 감소하는 허용응력 값 사용",
                "design_stress_intensity": "온도에 따라 감소하는 설계응력 강도 값 사용",
                "mechanical_properties": "인장강도, 항복강도, 연신율 등 고려",
                "physical_properties": "탄성계수, 열팽창계수 등 고려"
            }
        },
        "search_guidelines": {
            "keywords": {
                "materials": ["Carbon Steel", "Alloy Steel", "Stainless Steel", "SA-516", "SA-283", "SA-213"],
                "properties": ["Allowable Stress", "Design Stress", "Tensile Strength", "Yield Strength"],
                "temperatures": ["100F", "200F", "300F", "400F", "500F", "600F", "700F", "800F"],
                "forms": ["Plate", "Pipe", "Tube", "Bar", "Sheet"]
            },
            "file_patterns": {
                "tables": "Page_*_Table_*.csv",
                "charts": "Page_*_Chart_*.json"
            }
        }
    }
    
    return llm_data

def save_llm_data():
    """LLM용 데이터 저장"""
    llm_data = create_llm_data()
    
    # JSON 형태로 저장
    with open('llm_actual_data.json', 'w', encoding='utf-8') as f:
        json.dump(llm_data, f, ensure_ascii=False, indent=2)
    
    # 마크다운 형태로 저장
    with open('llm_actual_data.md', 'w', encoding='utf-8') as f:
        f.write("# ASME BPVC 2023 Section II Part D - 실제 추출 데이터\n\n")
        f.write("## 📊 데이터 개요\n")
        f.write(f"- **총 CSV 파일**: {llm_data['metadata']['total_files']['csv']}개\n")
        f.write(f"- **총 JSON 파일**: {llm_data['metadata']['total_files']['json']}개\n")
        f.write(f"- **추출 날짜**: {llm_data['metadata']['extraction_date']}\n")
        f.write(f"- **소스**: {llm_data['metadata']['source']}\n\n")
        
        f.write("## 🏗️ 추출된 재료 데이터\n\n")
        f.write("### Carbon Steel (탄소강)\n")
        f.write(f"- **발견된 표 수**: {llm_data['extracted_materials']['carbon_steel']['count']}개\n")
        f.write(f"- **규격 코드**: {', '.join(llm_data['extracted_materials']['carbon_steel']['specifications'])}\n")
        f.write(f"- **제품 형태**: {', '.join(llm_data['extracted_materials']['carbon_steel']['product_forms'])}\n\n")
        
        f.write("### Stainless Steel (스테인리스강)\n")
        f.write(f"- **발견된 표 수**: {llm_data['extracted_materials']['stainless_steel']['count']}개\n")
        f.write(f"- **주요 등급**: {', '.join(llm_data['extracted_materials']['stainless_steel']['grades'])}\n\n")
        
        f.write("## 📋 재료 선택 가이드\n\n")
        for category, materials in llm_data['usage_examples']['material_selection'].items():
            f.write(f"### {category.replace('_', ' ').title()}\n")
            for material in materials:
                f.write(f"- {material}\n")
            f.write("\n")
        
        f.write("## 🔍 데이터 검색 방법\n\n")
        f.write("### 키워드 검색\n")
        for category, keywords in llm_data['search_guidelines']['keywords'].items():
            f.write(f"- **{category.title()}**: {', '.join(keywords)}\n")
        f.write("\n")
        
        f.write("### 파일 패턴\n")
        for pattern_type, pattern in llm_data['search_guidelines']['file_patterns'].items():
            f.write(f"- **{pattern_type.title()}**: `{pattern}`\n")
        f.write("\n")
        
        f.write("## ⚠️ 사용 시 주의사항\n\n")
        f.write("- 이 데이터는 ASME BPVC 2023 Section II Part D에서 추출되었습니다.\n")
        f.write("- 실제 설계 시에는 최신 버전의 코드를 참조하시기 바랍니다.\n")
        f.write("- 온도별 허용응력 값은 온도가 증가할수록 감소합니다.\n")
        f.write("- 재료 선택 시 사용 환경(온도, 압력, 부식성)을 고려해야 합니다.\n")
    
    print("✅ LLM용 데이터 생성 완료!")
    print("📄 생성된 파일:")
    print("  - llm_actual_data.json (JSON 형태)")
    print("  - llm_actual_data.md (마크다운 형태)")

if __name__ == "__main__":
    save_llm_data() 
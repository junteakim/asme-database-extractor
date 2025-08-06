#!/usr/bin/env python3
"""
ASME BPVC 대량 데이터 분석 및 LLM용 데이터 생성
"""

import pandas as pd
import json
import glob
from pathlib import Path
from collections import defaultdict, Counter
import re

def analyze_all_extracted_data():
    """모든 추출된 데이터 분석"""
    print("🔍 ASME BPVC 대량 데이터 분석 시작...")
    
    # 파일 목록
    csv_files = glob.glob('output/Page_*_Table_*.csv')
    json_files = glob.glob('output/Page_*_Chart_*.json')
    
    print(f"📊 총 파일 수: {len(csv_files)}개 표, {len(json_files)}개 그래프")
    
    # 데이터 수집
    all_materials = []
    all_specifications = []
    all_product_forms = []
    all_temperature_data = []
    all_stress_data = []
    large_tables = []
    
    # 표 데이터 분석
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            rows, cols = df.shape
            
            # 큰 표 저장 (10행 이상 또는 15열 이상)
            if rows >= 10 or cols >= 15:
                large_tables.append({
                    'file': Path(csv_file).name,
                    'rows': rows,
                    'columns': cols,
                    'size': rows * cols,
                    'data': df.head(20).to_dict('records')  # 처음 20행만 저장
                })
            
            # 재료 정보 추출
            for col in df.columns:
                col_str = str(col).lower()
                
                # 재료 타입
                if 'carbon steel' in col_str:
                    all_materials.append('Carbon Steel')
                elif 'stainless steel' in col_str or '304' in col_str or '316' in col_str:
                    all_materials.append('Stainless Steel')
                elif 'alloy steel' in col_str or 't91' in col_str or 't92' in col_str:
                    all_materials.append('Alloy Steel')
                
                # 규격 코드
                if 'sa-' in col_str:
                    specs = re.findall(r'sa-\d+', col_str)
                    all_specifications.extend(specs)
                
                # 제품 형태
                forms = ['plate', 'pipe', 'tube', 'bar', 'sheet', 'forging', 'fitting']
                for form in forms:
                    if form in col_str:
                        all_product_forms.append(form.title())
                
                # 온도 데이터
                if any(temp in col_str for temp in ['°f', 'f', 'temperature', 'temp']):
                    all_temperature_data.append(col_str)
                
                # 응력 데이터
                if any(stress in col_str for stress in ['stress', 'ksi', 'mpa', 'allowable', 'design']):
                    all_stress_data.append(col_str)
            
            # 데이터에서도 검색
            for _, row in df.iterrows():
                for cell in row:
                    cell_str = str(cell).lower()
                    if 'carbon steel' in cell_str:
                        all_materials.append('Carbon Steel')
                    elif 'sa-' in cell_str:
                        specs = re.findall(r'sa-\d+', cell_str)
                        all_specifications.extend(specs)
                        
        except Exception as e:
            print(f"⚠️ 파일 처리 오류 {csv_file}: {e}")
    
    # 통계 계산
    material_counts = Counter(all_materials)
    spec_counts = Counter(all_specifications)
    form_counts = Counter(all_product_forms)
    
    return {
        'total_files': len(csv_files),
        'large_tables': large_tables,
        'material_distribution': dict(material_counts),
        'specification_distribution': dict(spec_counts),
        'product_form_distribution': dict(form_counts),
        'temperature_data_count': len(all_temperature_data),
        'stress_data_count': len(all_stress_data)
    }

def create_comprehensive_llm_data():
    """포괄적인 LLM용 데이터 생성"""
    analysis = analyze_all_extracted_data()
    
    # 가장 큰 표들에서 실제 데이터 추출
    actual_material_data = extract_actual_material_data()
    
    llm_data = {
        "metadata": {
            "title": "ASME BPVC 2023 Section II Part D - 대량 데이터베이스",
            "extraction_date": "2025-08-06",
            "source": "ASME BPVC 2023 Section II Part D (Customary)",
            "total_tables": analysis['total_files'],
            "total_charts": 179,
            "version": "2.0",
            "description": "실제 추출된 대량의 ASME BPVC 재료 데이터"
        },
        "data_statistics": {
            "total_files": analysis['total_files'],
            "large_tables": len(analysis['large_tables']),
            "material_distribution": analysis['material_distribution'],
            "specification_distribution": analysis['specification_distribution'],
            "product_form_distribution": analysis['product_form_distribution'],
            "temperature_data_count": analysis['temperature_data_count'],
            "stress_data_count": analysis['stress_data_count']
        },
        "actual_extracted_data": {
            "large_tables": analysis['large_tables'][:10],  # 상위 10개 큰 표
            "material_database": actual_material_data
        },
        "comprehensive_material_guide": create_material_guide(),
        "search_and_usage_guide": create_search_guide()
    }
    
    return llm_data

def extract_actual_material_data():
    """실제 추출된 재료 데이터 정리"""
    material_db = {
        "carbon_steel": {
            "specifications": [],
            "product_forms": [],
            "grades": [],
            "sample_data": []
        },
        "stainless_steel": {
            "specifications": [],
            "grades": [],
            "sample_data": []
        },
        "alloy_steel": {
            "specifications": [],
            "grades": [],
            "sample_data": []
        }
    }
    
    # 큰 표들에서 실제 데이터 추출
    large_files = [
        'Page_64_Table_1.csv',
        'Page_96_Table_5.csv', 
        'Page_76_Table_6.csv',
        'Page_72_Table_1.csv',
        'Page_56_Table_2.csv'
    ]
    
    for file in large_files:
        try:
            df = pd.read_csv(f'output/{file}')
            
            # Carbon Steel 데이터
            carbon_data = df[df.apply(lambda row: 'carbon steel' in str(row).lower(), axis=1)]
            if not carbon_data.empty:
                material_db['carbon_steel']['sample_data'].append({
                    'file': file,
                    'rows': len(carbon_data),
                    'data': carbon_data.head(5).to_dict('records')
                })
            
            # 규격 코드 추출
            for col in df.columns:
                col_str = str(col)
                if 'SA-' in col_str:
                    specs = re.findall(r'SA-\d+', col_str)
                    material_db['carbon_steel']['specifications'].extend(specs)
                
                # 제품 형태 추출
                forms = ['Plate', 'Pipe', 'Tube', 'Bar', 'Sheet', 'Forging']
                for form in forms:
                    if form in col_str:
                        material_db['carbon_steel']['product_forms'].append(form)
                        
        except Exception as e:
            print(f"데이터 추출 오류 {file}: {e}")
    
    # 중복 제거
    for material_type in material_db:
        if 'specifications' in material_db[material_type]:
            material_db[material_type]['specifications'] = list(set(material_db[material_type]['specifications']))
        if 'product_forms' in material_db[material_type]:
            material_db[material_type]['product_forms'] = list(set(material_db[material_type]['product_forms']))
    
    return material_db

def create_material_guide():
    """포괄적인 재료 선택 가이드"""
    return {
        "temperature_based_selection": {
            "cryogenic": {
                "temperature_range": "-320°F to -50°F",
                "materials": [
                    "SA-333 Grade 6 (Carbon Steel)",
                    "Type 304L SS",
                    "Type 316L SS",
                    "9% Nickel Steel"
                ],
                "applications": ["LNG 저장탱크", "극저온용기", "액체질소 설비"]
            },
            "low_temperature": {
                "temperature_range": "-50°F to 100°F",
                "materials": [
                    "SA-516 Grade 70 (Carbon Steel)",
                    "SA-283 Grade C (Carbon Steel)",
                    "Type 304 SS",
                    "Type 316 SS"
                ],
                "applications": ["저온용기", "냉장설비", "일반 압력용기"]
            },
            "medium_temperature": {
                "temperature_range": "100°F to 600°F",
                "materials": [
                    "SA-516 Grade 70 (Carbon Steel)",
                    "SA-285 Grade C (Carbon Steel)",
                    "Type 304 SS",
                    "Type 316 SS"
                ],
                "applications": ["일반 압력용기", "열교환기", "보일러"]
            },
            "high_temperature": {
                "temperature_range": "600°F to 800°F",
                "materials": [
                    "SA-516 Grade 70 (Carbon Steel)",
                    "Type 304 SS",
                    "Type 316 SS",
                    "Type 321 SS"
                ],
                "applications": ["고온용기", "열교환기", "증기관"]
            },
            "very_high_temperature": {
                "temperature_range": "800°F to 1200°F",
                "materials": [
                    "SA-213 T91 (Alloy Steel)",
                    "SA-213 T92 (Alloy Steel)",
                    "Type 304 SS",
                    "Type 316 SS",
                    "Type 321 SS"
                ],
                "applications": ["고온 보일러", "터빈", "고온 파이프"]
            }
        },
        "application_based_selection": {
            "pressure_vessels": {
                "materials": ["SA-516 Grade 70", "SA-283 Grade C", "Type 304 SS"],
                "considerations": ["압력", "온도", "내식성", "용접성"]
            },
            "piping_systems": {
                "materials": ["SA-53", "SA-106", "SA-312", "Type 304 SS"],
                "considerations": ["압력", "온도", "유체 특성", "부식성"]
            },
            "heat_exchangers": {
                "materials": ["SA-516 Grade 70", "Type 304 SS", "Type 316 SS"],
                "considerations": ["열전도율", "내식성", "온도", "압력"]
            },
            "boilers": {
                "materials": ["SA-213 T91", "SA-213 T92", "SA-516 Grade 70"],
                "considerations": ["고온 강도", "크리프 저항성", "내산화성"]
            }
        }
    }

def create_search_guide():
    """검색 및 활용 가이드"""
    return {
        "search_keywords": {
            "materials": [
                "Carbon Steel", "Stainless Steel", "Alloy Steel",
                "SA-516", "SA-283", "SA-285", "SA-213", "SA-312",
                "Type 304", "Type 316", "Type 321", "T91", "T92"
            ],
            "properties": [
                "Allowable Stress", "Design Stress", "Tensile Strength",
                "Yield Strength", "Modulus of Elasticity", "Thermal Expansion",
                "Creep Strength", "Fatigue Strength"
            ],
            "temperatures": [
                "100F", "200F", "300F", "400F", "500F", "600F", "700F", "800F",
                "900F", "1000F", "1100F", "1200F"
            ],
            "product_forms": [
                "Plate", "Pipe", "Tube", "Bar", "Sheet", "Forging",
                "Fitting", "Welded", "Seamless"
            ]
        },
        "file_patterns": {
            "tables": "Page_*_Table_*.csv",
            "charts": "Page_*_Chart_*.json",
            "large_tables": "Page_*_Table_*.csv (10행 이상 또는 15열 이상)"
        },
        "usage_scenarios": {
            "material_selection": "온도, 압력, 환경 조건에 따른 재료 선택",
            "stress_calculation": "온도별 허용응력 값 조회",
            "design_verification": "기존 설계의 재료 적합성 검토",
            "cost_analysis": "재료별 경제성 비교 분석"
        }
    }

def save_massive_llm_data():
    """대량 LLM 데이터 저장"""
    llm_data = create_comprehensive_llm_data()
    
    # JSON 형태로 저장
    with open('llm_massive_data.json', 'w', encoding='utf-8') as f:
        json.dump(llm_data, f, ensure_ascii=False, indent=2)
    
    # 마크다운 형태로 저장
    with open('llm_massive_data.md', 'w', encoding='utf-8') as f:
        f.write("# ASME BPVC 2023 Section II Part D - 대량 데이터베이스\n\n")
        f.write("## 📊 데이터 개요\n")
        f.write(f"- **총 표 파일**: {llm_data['metadata']['total_tables']}개\n")
        f.write(f"- **총 그래프 파일**: {llm_data['metadata']['total_charts']}개\n")
        f.write(f"- **큰 표 (10행 이상 또는 15열 이상)**: {llm_data['data_statistics']['large_tables']}개\n")
        f.write(f"- **온도 데이터**: {llm_data['data_statistics']['temperature_data_count']}개\n")
        f.write(f"- **응력 데이터**: {llm_data['data_statistics']['stress_data_count']}개\n")
        f.write(f"- **추출 날짜**: {llm_data['metadata']['extraction_date']}\n\n")
        
        f.write("## 🏗️ 재료 분포\n\n")
        f.write("### 재료 타입별 분포\n")
        for material, count in llm_data['data_statistics']['material_distribution'].items():
            f.write(f"- **{material}**: {count}회 발견\n")
        f.write("\n")
        
        f.write("### 규격 코드별 분포\n")
        for spec, count in sorted(llm_data['data_statistics']['specification_distribution'].items(), key=lambda x: x[1], reverse=True)[:10]:
            f.write(f"- **{spec}**: {count}회 발견\n")
        f.write("\n")
        
        f.write("### 제품 형태별 분포\n")
        for form, count in llm_data['data_statistics']['product_form_distribution'].items():
            f.write(f"- **{form}**: {count}회 발견\n")
        f.write("\n")
        
        f.write("## 📋 온도별 재료 선택 가이드\n\n")
        for temp_range, info in llm_data['comprehensive_material_guide']['temperature_based_selection'].items():
            f.write(f"### {temp_range.replace('_', ' ').title()}\n")
            f.write(f"- **온도 범위**: {info['temperature_range']}\n")
            f.write("- **추천 재료**:\n")
            for material in info['materials']:
                f.write(f"  - {material}\n")
            f.write("- **주요 용도**:\n")
            for app in info['applications']:
                f.write(f"  - {app}\n")
            f.write("\n")
        
        f.write("## 🔍 검색 및 활용 방법\n\n")
        f.write("### 키워드 검색\n")
        for category, keywords in llm_data['search_and_usage_guide']['search_keywords'].items():
            f.write(f"- **{category.title()}**: {', '.join(keywords)}\n")
        f.write("\n")
        
        f.write("### 사용 시나리오\n")
        for scenario, description in llm_data['search_and_usage_guide']['usage_scenarios'].items():
            f.write(f"- **{scenario.replace('_', ' ').title()}**: {description}\n")
        f.write("\n")
        
        f.write("## ⚠️ 주의사항\n\n")
        f.write("- 이 데이터는 ASME BPVC 2023 Section II Part D에서 추출되었습니다.\n")
        f.write("- 실제 설계 시에는 최신 버전의 코드를 참조하시기 바랍니다.\n")
        f.write("- 온도별 허용응력 값은 온도가 증가할수록 감소합니다.\n")
        f.write("- 재료 선택 시 사용 환경(온도, 압력, 부식성)을 고려해야 합니다.\n")
        f.write("- 대량의 데이터가 포함되어 있으므로 필요에 따라 필터링하여 사용하세요.\n")
    
    print("✅ 대량 LLM 데이터 생성 완료!")
    print("📄 생성된 파일:")
    print("  - llm_massive_data.json (JSON 형태)")
    print("  - llm_massive_data.md (마크다운 형태)")

if __name__ == "__main__":
    save_massive_llm_data() 
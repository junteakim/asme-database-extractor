"""
ASME BPVC Section II Part D 데이터베이스 스키마 정의
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Union
from enum import Enum

class TableType(Enum):
    """표 유형 정의"""
    ALLOWABLE_STRESS = "allowable_stress"
    DESIGN_STRESS = "design_stress"
    MECHANICAL_PROPERTIES = "mechanical_properties"
    PHYSICAL_PROPERTIES = "physical_properties"
    THERMAL_EXPANSION = "thermal_expansion"
    THERMAL_CONDUCTIVITY = "thermal_conductivity"

class ChartType(Enum):
    """그래프 유형 정의"""
    EXTERNAL_PRESSURE = "external_pressure"
    ISOCHRONOUS_STRESS_STRAIN = "isochronous_stress_strain"
    OTHER_CURVES = "other_curves"

@dataclass
class TableSchema:
    """표 스키마 정의"""
    table_name: str
    table_type: TableType
    base_columns: List[str]
    temperature_columns: List[str]
    stress_columns: List[str]
    description: str

@dataclass
class ChartSchema:
    """그래프 스키마 정의"""
    chart_name: str
    chart_type: ChartType
    x_column: str
    y_column: str
    curve_label_column: Optional[str] = None
    description: str = ""

class ASMESchemaManager:
    """ASME 스키마 관리 클래스"""
    
    def __init__(self):
        self.table_schemas = self._initialize_table_schemas()
        self.chart_schemas = self._initialize_chart_schemas()
    
    def _initialize_table_schemas(self) -> Dict[str, TableSchema]:
        """표 스키마 초기화"""
        schemas = {}
        
        # 허용 응력/설계 응력 표 (Tables 1A, 1B, 2A, 2B, 3, 4, 5A, 5B, 6A, 6B, 6C, 6D)
        base_columns = [
            "Line_No", "Nominal_Composition", "Product_Form", "Spec_No", 
            "Type_Grade", "Alloy_Designation_UNS_No", "Class_Condition_Temper",
            "Size_Thickness_in", "P_No", "Group_No", "Notes"
        ]
        
        # 온도 범위 (100°F ~ 1500°F, 50°F 또는 100°F 간격)
        temperature_range = list(range(100, 1501, 50))  # 100°F ~ 1500°F, 50°F 간격
        temperature_columns = [f"Allowable_Stress_at_{temp}F" for temp in temperature_range]
        
        for table_name in ["1A", "1B", "2A", "2B", "3", "4", "5A", "5B", "6A", "6B", "6C", "6D"]:
            schemas[f"Table_{table_name}"] = TableSchema(
                table_name=f"Table_{table_name}",
                table_type=TableType.ALLOWABLE_STRESS,
                base_columns=base_columns,
                temperature_columns=temperature_columns,
                stress_columns=temperature_columns,
                description=f"허용 응력 표 {table_name}"
            )
        
        # 기계적 강도 표 (Table Y-1, U)
        yield_strength_columns = [f"Yield_Strength_ksi_at_{temp}F" for temp in temperature_range]
        
        schemas["Table_Y-1"] = TableSchema(
            table_name="Table_Y-1",
            table_type=TableType.MECHANICAL_PROPERTIES,
            base_columns=["Line_No", "Size_Thickness_in", "Min_Tensile_Strength_ksi", "Min_Yield_Strength_ksi", "Notes"],
            temperature_columns=yield_strength_columns,
            stress_columns=yield_strength_columns,
            description="항복강도 표"
        )
        
        schemas["Table_U"] = TableSchema(
            table_name="Table_U",
            table_type=TableType.MECHANICAL_PROPERTIES,
            base_columns=base_columns[:-3],  # P_No, Group_No, Notes 제외
            temperature_columns=[],
            stress_columns=["Min_Tensile_Strength_ksi", "Min_Yield_Strength_ksi"],
            description="인장강도 표"
        )
        
        # 물리적 특성 표 (TM, TE, TCD 시리즈)
        # Modulus of Elasticity (TM-tables)
        tm_temperature_range = [-325, -200, -100, 70, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500]
        tm_columns = [f"E_at_{temp}F" for temp in tm_temperature_range]
        
        for table_name in ["TM-1", "TM-2"]:
            schemas[f"Table_{table_name}"] = TableSchema(
                table_name=f"Table_{table_name}",
                table_type=TableType.PHYSICAL_PROPERTIES,
                base_columns=["Material"],
                temperature_columns=tm_columns,
                stress_columns=tm_columns,
                description=f"탄성계수 표 {table_name}"
            )
        
        # Thermal Expansion (TE-tables)
        te_base_columns = ["Temperature_F"]
        te_coefficient_columns = []
        
        # 예시: 5Cr-11Mo Steels, 5Ni-½Mo Steels, 7Ni Steels
        material_groups = ["5Cr_11Mo", "5Ni_0_5Mo", "7Ni"]
        for material in material_groups:
            for coeff in ["A", "B", "C"]:
                te_coefficient_columns.append(f"Coeff_{material}_{coeff}")
        
        for table_name in ["TE-1", "TE-2", "TE-3", "TE-4", "TE-5"]:
            schemas[f"Table_{table_name}"] = TableSchema(
                table_name=f"Table_{table_name}",
                table_type=TableType.THERMAL_EXPANSION,
                base_columns=te_base_columns,
                temperature_columns=te_coefficient_columns,
                stress_columns=te_coefficient_columns,
                description=f"열팽창 계수 표 {table_name}"
            )
        
        # Thermal Conductivity/Diffusivity (TCD)
        tcd_base_columns = ["Temperature_F"]
        tcd_coefficient_columns = []
        
        for group in ["A", "B", "C", "D", "E"]:
            tcd_coefficient_columns.extend([f"TC_Group_{group}", f"TD_Group_{group}"])
        
        schemas["Table_TCD"] = TableSchema(
            table_name="Table_TCD",
            table_type=TableType.THERMAL_CONDUCTIVITY,
            base_columns=tcd_base_columns,
            temperature_columns=tcd_coefficient_columns,
            stress_columns=tcd_coefficient_columns,
            description="열전도도/확산도 표"
        )
        
        return schemas
    
    def _initialize_chart_schemas(self) -> Dict[str, ChartSchema]:
        """그래프 스키마 초기화"""
        schemas = {}
        
        # 외압 설계용 차트
        external_pressure_charts = [
            "G", "CS-1", "CS-2", "CS-3", "CS-4", "CS-5", "CS-6",
            "HT-1", "HT-2", "HA-1", "HA-2", "HA-3", "HA-4", "HA-5",
            "HA-6", "HA-7", "HA-8", "HA-9", "HA-10", "CI-1",
            "CD-1", "CD-2", "NFA-1", "NFA-2", "NFA-3", "NFA-4",
            "NFA-5", "NFA-6", "NFA-7", "NFA-8", "NFA-9", "NFA-10",
            "NFA-11", "NFA-12", "NFA-13", "NFC-1", "NFC-2", "NFC-3",
            "NFC-4", "NFC-5", "NFC-6", "NFC-7", "NFC-8", "NFN-1",
            "NFN-2", "NFN-3", "NFN-4", "NFN-5", "NFN-6", "NFN-7",
            "NFN-8", "NFN-9", "NFN-10", "NFN-11", "NFN-12", "NFN-13",
            "NFN-14", "NFN-15", "NFN-16", "NFN-17", "NFN-18", "NFN-19",
            "NFN-20", "NFN-21", "NFN-22", "NFN-23", "NFN-24", "NFN-25",
            "NFN-26", "NFN-27", "NFT-1", "NFT-2", "NFT-3", "NFT-4",
            "NFT-5", "NFT-6", "NFZ-1", "NFZ-2"
        ]
        
        for chart_name in external_pressure_charts:
            schemas[f"Chart_{chart_name}"] = ChartSchema(
                chart_name=f"Chart_{chart_name}",
                chart_type=ChartType.EXTERNAL_PRESSURE,
                x_column="x",
                y_column="y",
                description=f"외압 설계용 차트 {chart_name}"
            )
        
        # 이소크로너스 응력-변형률 곡선 (부록 E)
        for i in range(1, 101):  # E-100.x-y 시리즈 (예시로 100개)
            schemas[f"E-100.{i}"] = ChartSchema(
                chart_name=f"E-100.{i}",
                chart_type=ChartType.ISOCHRONOUS_STRESS_STRAIN,
                x_column="strain_percent",
                y_column="stress_ksi",
                description=f"이소크로너스 응력-변형률 곡선 E-100.{i}"
            )
        
        # 기타 곡선
        other_curves = ["TM-curve", "TE-curve", "TCD-curve"]
        for curve_name in other_curves:
            schemas[f"Fig_{curve_name}"] = ChartSchema(
                chart_name=f"Fig_{curve_name}",
                chart_type=ChartType.OTHER_CURVES,
                x_column="x",
                y_column="y",
                curve_label_column="curve_label",
                description=f"기타 곡선 {curve_name}"
            )
        
        return schemas
    
    def get_table_schema(self, table_name: str) -> Optional[TableSchema]:
        """표 스키마 조회"""
        return self.table_schemas.get(table_name)
    
    def get_chart_schema(self, chart_name: str) -> Optional[ChartSchema]:
        """그래프 스키마 조회"""
        return self.chart_schemas.get(chart_name)
    
    def list_all_table_schemas(self) -> List[str]:
        """모든 표 스키마 목록 반환"""
        return list(self.table_schemas.keys())
    
    def list_all_chart_schemas(self) -> List[str]:
        """모든 그래프 스키마 목록 반환"""
        return list(self.chart_schemas.keys())
    
    def get_schema_summary(self) -> Dict:
        """스키마 요약 정보 반환"""
        return {
            "total_tables": len(self.table_schemas),
            "total_charts": len(self.chart_schemas),
            "table_types": {table_type.value: len([s for s in self.table_schemas.values() if s.table_type == table_type]) 
                           for table_type in TableType},
            "chart_types": {chart_type.value: len([s for s in self.chart_schemas.values() if s.chart_type == chart_type]) 
                           for chart_type in ChartType}
        }

if __name__ == "__main__":
    # 스키마 매니저 테스트
    schema_manager = ASMESchemaManager()
    
    print("=== ASME 스키마 정의 테스트 ===")
    print(f"총 표 수: {len(schema_manager.table_schemas)}")
    print(f"총 그래프 수: {len(schema_manager.chart_schemas)}")
    
    print("\n=== 스키마 요약 ===")
    summary = schema_manager.get_schema_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print("\n=== 표 스키마 예시 ===")
    table_example = schema_manager.get_table_schema("Table_1A")
    if table_example:
        print(f"표 이름: {table_example.table_name}")
        print(f"표 유형: {table_example.table_type.value}")
        print(f"기본 컬럼 수: {len(table_example.base_columns)}")
        print(f"온도 컬럼 수: {len(table_example.temperature_columns)}")
    
    print("\n=== 그래프 스키마 예시 ===")
    chart_example = schema_manager.get_chart_schema("Chart_G")
    if chart_example:
        print(f"그래프 이름: {chart_example.chart_name}")
        print(f"그래프 유형: {chart_example.chart_type.value}")
        print(f"X축 컬럼: {chart_example.x_column}")
        print(f"Y축 컬럼: {chart_example.y_column}") 
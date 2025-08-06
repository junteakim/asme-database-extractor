#!/usr/bin/env python3
"""
ASME BPVC 데이터베이스 MCP 서버
"""

import json
import asyncio
import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ASMEMCPServer:
    def __init__(self):
        self.server = Server("asme-bpvc-server")
        self.data_cache = {}
        self.setup_tools()
    
    def setup_tools(self):
        """도구 설정"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """사용 가능한 도구 목록 반환"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="search_material",
                        description="ASME BPVC 재료 검색",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "material_name": {
                                    "type": "string",
                                    "description": "검색할 재료명 (예: SA-516, Type 304)"
                                },
                                "material_type": {
                                    "type": "string",
                                    "description": "재료 타입 (carbon_steel, alloy_steel, stainless_steel)",
                                    "enum": ["carbon_steel", "alloy_steel", "stainless_steel"]
                                }
                            },
                            "required": ["material_name"]
                        }
                    ),
                    Tool(
                        name="get_allowable_stress",
                        description="재료의 허용응력값 조회",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "material_name": {
                                    "type": "string",
                                    "description": "재료명 (예: SA-516_Grade_70)"
                                },
                                "temperature": {
                                    "type": "string",
                                    "description": "온도 (예: 400F, 600F)"
                                }
                            },
                            "required": ["material_name"]
                        }
                    ),
                    Tool(
                        name="get_design_stress",
                        description="재료의 설계응력강도값 조회",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "material_name": {
                                    "type": "string",
                                    "description": "재료명 (예: SA-516_Grade_70)"
                                },
                                "temperature": {
                                    "type": "string",
                                    "description": "온도 (예: 400F, 600F)"
                                }
                            },
                            "required": ["material_name"]
                        }
                    ),
                    Tool(
                        name="get_mechanical_properties",
                        description="재료의 기계적 특성 조회",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "material_name": {
                                    "type": "string",
                                    "description": "재료명 (예: SA-516_Grade_70, Type_304)"
                                }
                            },
                            "required": ["material_name"]
                        }
                    ),
                    Tool(
                        name="get_design_example",
                        description="설계 예시 조회",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "design_type": {
                                    "type": "string",
                                    "description": "설계 타입",
                                    "enum": ["high_temperature_vessel", "low_temperature_tank", "general_pressure_vessel"]
                                }
                            },
                            "required": ["design_type"]
                        }
                    ),
                    Tool(
                        name="get_usage_guidelines",
                        description="재료 사용 가이드라인 조회",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "material_type": {
                                    "type": "string",
                                    "description": "재료 타입",
                                    "enum": ["carbon_steel", "alloy_steel", "stainless_steel"]
                                },
                                "guideline_type": {
                                    "type": "string",
                                    "description": "가이드라인 타입",
                                    "enum": ["temperature_limits", "weldability", "corrosion_resistance", "cost_considerations"]
                                }
                            },
                            "required": ["material_type"]
                        }
                    ),
                    Tool(
                        name="search_materials_by_property",
                        description="특성별 재료 검색",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "property": {
                                    "type": "string",
                                    "description": "검색할 특성",
                                    "enum": ["high_temperature", "low_temperature", "corrosion_resistance", "cost_effective"]
                                }
                            },
                            "required": ["property"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """도구 호출 처리"""
            try:
                if name == "search_material":
                    return await self.search_material(arguments)
                elif name == "get_allowable_stress":
                    return await self.get_allowable_stress(arguments)
                elif name == "get_design_stress":
                    return await self.get_design_stress(arguments)
                elif name == "get_mechanical_properties":
                    return await self.get_mechanical_properties(arguments)
                elif name == "get_design_example":
                    return await self.get_design_example(arguments)
                elif name == "get_usage_guidelines":
                    return await self.get_usage_guidelines(arguments)
                elif name == "search_materials_by_property":
                    return await self.search_materials_by_property(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"알 수 없는 도구: {name}")]
                    )
            except Exception as e:
                logger.error(f"도구 호출 오류: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"오류 발생: {str(e)}")]
                )
    
    async def load_data(self):
        """데이터 로드"""
        try:
            with open("llm_comprehensive_data.json", "r", encoding="utf-8") as f:
                self.data_cache = json.load(f)
            logger.info("✅ ASME 데이터 로드 완료")
        except Exception as e:
            logger.error(f"데이터 로드 실패: {e}")
            self.data_cache = {}
    
    async def search_material(self, arguments: Dict[str, Any]) -> CallToolResult:
        """재료 검색"""
        material_name = arguments.get("material_name", "")
        material_type = arguments.get("material_type")
        
        results = []
        
        # 재료 타입별 검색
        if material_type and material_type in self.data_cache.get("materials", {}):
            material_info = self.data_cache["materials"][material_type]
            if material_name.lower() in material_info.get("name", "").lower():
                results.append(f"**{material_info['name']}**")
                results.append(f"사양: {', '.join(material_info.get('specifications', []))}")
                results.append(f"특성: {json.dumps(material_info.get('properties', {}), ensure_ascii=False)}")
        
        # 모든 재료에서 검색
        if not results:
            for mat_type, mat_info in self.data_cache.get("materials", {}).items():
                if material_name.lower() in mat_info.get("name", "").lower():
                    results.append(f"**{mat_info['name']}** ({mat_type})")
                    results.append(f"사양: {', '.join(mat_info.get('specifications', []))}")
        
        if not results:
            return CallToolResult(
                content=[TextContent(type="text", text=f"재료 '{material_name}'을 찾을 수 없습니다.")]
            )
        
        return CallToolResult(
            content=[TextContent(type="text", text="\n".join(results))]
        )
    
    async def get_allowable_stress(self, arguments: Dict[str, Any]) -> CallToolResult:
        """허용응력값 조회"""
        material_name = arguments.get("material_name", "")
        temperature = arguments.get("temperature", "")
        
        stress_data = self.data_cache.get("allowable_stress_values", {})
        
        for mat_type, materials in stress_data.items():
            if material_name in materials:
                material_stress = materials[material_name]
                if temperature:
                    if temperature in material_stress:
                        stress_value = material_stress[temperature]
                        unit = material_stress.get("unit", "ksi")
                        return CallToolResult(
                            content=[TextContent(type="text", text=f"{material_name}의 {temperature}에서의 허용응력값: {stress_value} {unit}")]
                        )
                    else:
                        return CallToolResult(
                            content=[TextContent(type="text", text=f"온도 {temperature}에 대한 데이터가 없습니다. 사용 가능한 온도: {list(material_stress.keys())}")]
                        )
                else:
                    # 모든 온도 데이터 반환
                    result = f"**{material_name} 허용응력값**\n"
                    for temp, stress in material_stress.items():
                        if temp != "unit":
                            result += f"- {temp}: {stress} {material_stress.get('unit', 'ksi')}\n"
                    return CallToolResult(content=[TextContent(type="text", text=result)])
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"재료 '{material_name}'의 허용응력값을 찾을 수 없습니다.")]
        )
    
    async def get_design_stress(self, arguments: Dict[str, Any]) -> CallToolResult:
        """설계응력강도값 조회"""
        material_name = arguments.get("material_name", "")
        temperature = arguments.get("temperature", "")
        
        stress_data = self.data_cache.get("design_stress_intensity_values", {})
        
        for mat_type, materials in stress_data.items():
            if material_name in materials:
                material_stress = materials[material_name]
                if temperature:
                    if temperature in material_stress:
                        stress_value = material_stress[temperature]
                        unit = material_stress.get("unit", "ksi")
                        return CallToolResult(
                            content=[TextContent(type="text", text=f"{material_name}의 {temperature}에서의 설계응력강도값: {stress_value} {unit}")]
                        )
                    else:
                        return CallToolResult(
                            content=[TextContent(type="text", text=f"온도 {temperature}에 대한 데이터가 없습니다.")]
                        )
                else:
                    result = f"**{material_name} 설계응력강도값**\n"
                    for temp, stress in material_stress.items():
                        if temp != "unit":
                            result += f"- {temp}: {stress} {material_stress.get('unit', 'ksi')}\n"
                    return CallToolResult(content=[TextContent(type="text", text=result)])
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"재료 '{material_name}'의 설계응력강도값을 찾을 수 없습니다.")]
        )
    
    async def get_mechanical_properties(self, arguments: Dict[str, Any]) -> CallToolResult:
        """기계적 특성 조회"""
        material_name = arguments.get("material_name", "")
        
        properties_data = self.data_cache.get("mechanical_properties", {})
        
        for mat_type, materials in properties_data.items():
            if material_name in materials:
                props = materials[material_name]
                result = f"**{material_name} 기계적 특성**\n"
                for prop_name, prop_value in props.items():
                    result += f"- {prop_name}: {prop_value}\n"
                return CallToolResult(content=[TextContent(type="text", text=result)])
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"재료 '{material_name}'의 기계적 특성을 찾을 수 없습니다.")]
        )
    
    async def get_design_example(self, arguments: Dict[str, Any]) -> CallToolResult:
        """설계 예시 조회"""
        design_type = arguments.get("design_type", "")
        
        design_examples = self.data_cache.get("design_examples", {})
        
        if design_type in design_examples:
            example = design_examples[design_type]
            result = f"**{design_type} 설계 예시**\n"
            result += f"조건: 온도 {example.get('conditions', {}).get('temperature', 'N/A')}, 압력 {example.get('conditions', {}).get('pressure', 'N/A')}\n"
            result += f"권장 재료: {', '.join(example.get('recommended_materials', []))}\n"
            result += f"결론: {example.get('conclusion', 'N/A')}\n"
            return CallToolResult(content=[TextContent(type="text", text=result)])
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"설계 타입 '{design_type}'을 찾을 수 없습니다.")]
        )
    
    async def get_usage_guidelines(self, arguments: Dict[str, Any]) -> CallToolResult:
        """사용 가이드라인 조회"""
        material_type = arguments.get("material_type", "")
        guideline_type = arguments.get("guideline_type")
        
        guidelines = self.data_cache.get("usage_guidelines", {})
        
        if guideline_type:
            if guideline_type in guidelines:
                guideline = guidelines[guideline_type].get(material_type, "데이터 없음")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"{material_type}의 {guideline_type}: {guideline}")]
                )
        else:
            result = f"**{material_type} 사용 가이드라인**\n"
            for g_type, g_data in guidelines.items():
                if material_type in g_data:
                    result += f"- {g_type}: {g_data[material_type]}\n"
            return CallToolResult(content=[TextContent(type="text", text=result)])
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"가이드라인을 찾을 수 없습니다.")]
        )
    
    async def search_materials_by_property(self, arguments: Dict[str, Any]) -> CallToolResult:
        """특성별 재료 검색"""
        property_name = arguments.get("property", "")
        
        materials = self.data_cache.get("materials", {})
        results = []
        
        for mat_type, mat_info in materials.items():
            usage = mat_info.get("usage", {})
            if property_name == "high_temperature" and usage.get("high_temperature"):
                results.append(f"**{mat_info['name']}** - 고온용")
            elif property_name == "low_temperature" and usage.get("low_temperature"):
                results.append(f"**{mat_info['name']}** - 저온용")
            elif property_name == "corrosion_resistance" and mat_type == "stainless_steel":
                results.append(f"**{mat_info['name']}** - 우수한 내식성")
            elif property_name == "cost_effective" and usage.get("cost") == "경제적":
                results.append(f"**{mat_info['name']}** - 경제적")
        
        if not results:
            return CallToolResult(
                content=[TextContent(type="text", text=f"특성 '{property_name}'에 맞는 재료를 찾을 수 없습니다.")]
            )
        
        return CallToolResult(
            content=[TextContent(type="text", text="\n".join(results))]
        )

async def main():
    """메인 함수"""
    server = ASMEMCPServer()
    
    # 데이터 로드
    await server.load_data()
    
    # 서버 실행
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="asme-bpvc-server",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 
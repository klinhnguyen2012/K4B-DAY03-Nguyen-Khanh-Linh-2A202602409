"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()


def _prompt_with_observations(
    prompt: str, observations: Optional[List[Dict[str, Any]]]
) -> str:
    if not observations:
        return prompt
    observation_text = json.dumps(observations, ensure_ascii=False)
    return (
        f"{prompt}\n\nCác Observation từ những bước trước:\n{observation_text}\n"
        "Hãy dùng dữ liệu này để chọn công cụ tiếp theo hoặc trả lời cuối cùng."
    )

class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(
        self,
        prompt: str,
        tools_schema: List[Dict[str, Any]],
        system_prompt: str = "",
        observations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return (
            "[Mock Chatbot Response]: Tôi có thể hướng dẫn chuẩn bị hồ sơ học bổng "
            "ở mức tổng quát, nhưng không có công cụ tra cứu dữ liệu thời gian thực."
        )

    def generate_with_tools(
        self,
        prompt: str,
        tools_schema: List[Dict[str, Any]],
        system_prompt: str = "",
        observations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        observations = observations or []

        if observations:
            last_observation = observations[-1]
            last_tool = last_observation.get("tool_name")
            result = last_observation.get("result", {})
            status = result.get("status")

            if status == "NOT_FOUND":
                return {
                    "type": "text",
                    "content": (
                        "Không tìm thấy hồ sơ hoặc học bổng theo yêu cầu. Vui lòng "
                        "cung cấp GPA kèm thang điểm, chứng chỉ, ngành học, kỳ nhập "
                        "học, khu vực mong muốn và nhu cầu tài chính."
                    ),
                    "thought": "Observation trả NOT_FOUND nên tôi không được bịa dữ liệu.",
                }

            if last_tool == "profile_query":
                if "hb_test_01" in prompt_lower or "checklist" in prompt_lower:
                    return {
                        "type": "tool_call",
                        "tool_name": "scholarship_details",
                        "arguments": {"scholarship_id": "HB_TEST_01", "intake": "2027"},
                        "thought": "Đã có hồ sơ; cần đọc điều kiện và deadline của HB_TEST_01.",
                    }
                profile = result.get("data", {})
                return {
                    "type": "text",
                    "content": (
                        "Hồ sơ đã tra cứu: "
                        f"GPA {profile.get('gpa')}/{profile.get('gpa_scale')}; "
                        f"chứng chỉ {json.dumps(profile.get('certificates', []), ensure_ascii=False)}; "
                        f"hoạt động {json.dumps(profile.get('activities', []), ensure_ascii=False)}. "
                        "Cần kiểm tra thêm yêu cầu riêng của từng học bổng trước khi kết luận."
                    ),
                    "thought": "Đã có hồ sơ và câu hỏi chỉ yêu cầu liệt kê thông tin.",
                }

            if last_tool == "scholarship_search":
                scholarships = result.get("data", [])
                if not scholarships:
                    return {
                        "type": "text",
                        "content": "Không tìm thấy lựa chọn phù hợp trong dữ liệu thử nghiệm.",
                        "thought": "Kết quả tìm kiếm rỗng nên cần dừng và báo rõ.",
                    }
                return {
                    "type": "tool_call",
                    "tool_name": "scholarship_details",
                    "arguments": {
                        "scholarship_id": scholarships[0]["scholarship_id"],
                        "intake": scholarships[0].get("intake", "2027"),
                    },
                    "thought": "Đã có danh sách; cần đọc điều kiện của lựa chọn đầu tiên.",
                }

            if last_tool == "scholarship_details":
                if "checklist" in prompt_lower and "sv2026001" in prompt_lower:
                    return {
                        "type": "tool_call",
                        "tool_name": "study_plan_save",
                        "arguments": {
                            "student_id": "SV2026001",
                            "scholarship_id": result.get("scholarship_id", "HB_TEST_01"),
                            "tasks": [
                                {
                                    "title": "Nâng IELTS từ 6.0 lên tối thiểu 6.5",
                                    "due_date": "2026-11-30",
                                    "priority": "high",
                                },
                                {
                                    "title": "Hoàn thiện CV, bảng điểm và bài luận",
                                    "due_date": "2026-12-20",
                                    "priority": "high",
                                },
                                {
                                    "title": "Xin hai thư giới thiệu",
                                    "due_date": "2027-01-10",
                                    "priority": "medium",
                                },
                            ],
                        },
                        "thought": "Đã biết deadline và yêu cầu; có thể tạo checklist để lưu.",
                    }
                details = result.get("data", {})
                requirements = details.get("requirements", {})
                return {
                    "type": "text",
                    "content": (
                        f"Lựa chọn thử nghiệm: {details.get('name', '')} tại "
                        f"{details.get('university', '')}, hạn {details.get('deadline', '')}. "
                        "GPA 3.5/4.0 đáp ứng mức tối thiểu 3.2, nhưng IELTS 6.0 "
                        f"chưa đạt mức {requirements.get('minimum_english_score', 6.5)}. "
                        "Nên thi lại IELTS trước 30/11/2026, hoàn thiện CV và bài luận "
                        "trước 20/12/2026, xin thư giới thiệu trước 10/01/2027 và "
                        "nộp trước deadline ít nhất 7 ngày. Dữ liệu này chỉ dùng thử nghiệm."
                    ),
                    "thought": "Đã có chi tiết để phân tích khoảng thiếu và tạo timeline.",
                }

            if last_tool == "study_plan_save":
                return {
                    "type": "text",
                    "content": result.get(
                        "message", "Đã lưu checklist và timeline thử nghiệm thành công."
                    ),
                    "thought": "Tool lưu kế hoạch đã trả kết quả; có thể phản hồi cuối cùng.",
                }

        if "có thể hỗ trợ" in prompt_lower or "cần cung cấp" in prompt_lower:
            return {
                "type": "text",
                "content": (
                    "Tôi hỗ trợ phân tích hồ sơ, tìm trường và học bổng, chỉ ra yêu "
                    "cầu còn thiếu, rồi tạo checklist và timeline. Bạn nên cung cấp "
                    "GPA kèm thang điểm, chứng chỉ, hoạt động, ngành, bậc học, khu "
                    "vực, kỳ nhập học và nhu cầu tài chính."
                ),
                "thought": "Đây là câu hỏi giới thiệu nên không cần gọi công cụ.",
            }

        if "sv9999999" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "profile_query",
                "arguments": {"student_id": "SV9999999"},
                "thought": "Cần xác minh hồ sơ SV9999999 trước khi đề xuất học bổng.",
            }

        if "sv2026001" in prompt_lower:
            return {
                "type": "tool_call",
                "tool_name": "profile_query",
                "arguments": {"student_id": "SV2026001"},
                "thought": "Cần tra cứu hồ sơ SV2026001 trước khi đánh giá hoặc lập kế hoạch.",
            }

        if "gpa" in prompt_lower and ("học bổng" in prompt_lower or "thạc sĩ" in prompt_lower):
            return {
                "type": "tool_call",
                "tool_name": "scholarship_search",
                "arguments": {
                    "degree_level": "Thạc sĩ",
                    "major": "Công nghệ thông tin",
                    "regions": ["Việt Nam", "Quốc tế"],
                    "intake": "2027",
                    "funding_need": "Hỗ trợ học phí",
                },
                "thought": "Hồ sơ và mục tiêu đã có trong câu hỏi; cần tìm học bổng phù hợp.",
            }

        return {
            "type": "text",
            "content": "Vui lòng cung cấp thêm hồ sơ và mục tiêu học bổng để tôi hỗ trợ.",
            "thought": "Chưa đủ thông tin để chọn công cụ phù hợp.",
        }


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"

    def generate_with_tools(
        self,
        prompt: str,
        tools_schema: List[Dict[str, Any]],
        system_prompt: str = "",
        observations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("ℹ️ [Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(
                prompt, tools_schema, system_prompt, observations
            )
        
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            
            # Chuẩn hóa function declarations cho Gemini SDK
            function_declarations = []
            for tool in tools_schema:
                # Bỏ qua các tool schema chưa được định nghĩa hoàn chỉnh
                if not tool.get("name") or not tool.get("parameters"):
                    continue
                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                })

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                tools=[{"function_declarations": function_declarations}] if function_declarations else None,
                temperature=0.2
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=_prompt_with_observations(prompt, observations),
                config=config
            )

            # Kiểm tra xem Gemini có trả về Tool Call không
            if response.function_calls:
                call = response.function_calls[0]
                args = dict(call.args) if hasattr(call, 'args') and call.args else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": f"Gemini quyết định gọi công cụ '{call.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": response.text or "",
                    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }

        except Exception as e:
            print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(
                prompt, tools_schema, system_prompt, observations
            )


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"

    def generate_with_tools(
        self,
        prompt: str,
        tools_schema: List[Dict[str, Any]],
        system_prompt: str = "",
        observations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(
                prompt, tools_schema, system_prompt, observations
            )

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append(
                {
                    "role": "user",
                    "content": _prompt_with_observations(prompt, observations),
                }
            )

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(
                prompt, tools_schema, system_prompt, observations
            )


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()

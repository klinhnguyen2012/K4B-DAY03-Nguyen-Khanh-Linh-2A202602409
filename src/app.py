"""CLI và ReAct loop cho Scholarship Planning Agent."""

import json
import os
import sys
import time
from typing import Any, Dict, List

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from mcp_server import MCPScholarshipServer
from prompts import CHATBOT_BASELINE_PROMPT, MAX_ITERATIONS, REACT_AGENT_SYSTEM_PROMPT
from providers import get_llm_provider


load_dotenv()


def load_test_cases() -> List[Dict[str, Any]]:
    """Tải bộ test cá nhân hoặc dùng file mẫu khi chưa có."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    if not os.path.exists(config_path):
        config_path = os.path.join(base_dir, "config", "test_cases.example.json")
        print("⚠️ Chưa thấy config/test_cases.json; đang dùng file mẫu.")
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_waterfall_trace(trace_data: List[Dict[str, Any]]) -> None:
    """Ghi Waterfall Trace Log ra docs/trace_waterfall.json."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    trace_path = os.path.join(base_dir, "docs", "trace_waterfall.json")
    os.makedirs(os.path.dirname(trace_path), exist_ok=True)
    with open(trace_path, "w", encoding="utf-8") as file:
        json.dump(trace_data, file, ensure_ascii=False, indent=2)
    print(f"📊 Đã lưu {len(trace_data)} sự kiện tại '{trace_path}'.")


def run_baseline_chatbot(user_query: str, provider: Any) -> None:
    """Chạy chatbot không có công cụ."""
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot phản hồi:\n{response}")


def _provider_label(provider: Any) -> str:
    model_name = getattr(provider, "model_name", "unknown-model")
    return f"{provider.__class__.__name__}:{model_name}"


def run_react_agent(
    user_query: str, provider: Any, mcp_server: MCPScholarshipServer
) -> List[Dict[str, Any]]:
    """Chạy Thought -> Action -> Observation cho tới câu trả lời cuối cùng."""
    print(f"\n🤖 [SCHOLARSHIP PLANNING AGENT] Câu hỏi: {user_query}")

    trace_logs: List[Dict[str, Any]] = []
    observations: List[Dict[str, Any]] = []
    tools_list = mcp_server.list_tools()
    provider_label = _provider_label(provider)

    for step in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- 🔄 ReAct Loop (Step {step}/{MAX_ITERATIONS}) ---")
        provider_started = time.perf_counter()
        llm_response = provider.generate_with_tools(
            user_query,
            tools_list,
            system_prompt=REACT_AGENT_SYSTEM_PROMPT,
            observations=observations,
        )
        provider_latency_ms = round((time.perf_counter() - provider_started) * 1000, 2)
        thought = llm_response.get("thought", "Đang suy luận...")
        print(f"🧠 [Thought]: {thought}")

        if llm_response.get("type") == "text":
            final_content = llm_response.get("content", "")
            print(f"🏁 [Final Answer]: {final_content}")
            trace_logs.append(
                {
                    "step": step,
                    "query": user_query,
                    "provider": provider_label,
                    "action_type": "FINAL_ANSWER",
                    "thought": thought,
                    "output": final_content,
                    "latency_ms": provider_latency_ms,
                }
            )
            return trace_logs

        if llm_response.get("type") != "tool_call":
            error_message = "Provider trả về loại phản hồi không hợp lệ."
            trace_logs.append(
                {
                    "step": step,
                    "query": user_query,
                    "provider": provider_label,
                    "action_type": "FINAL_ANSWER",
                    "thought": thought,
                    "output": error_message,
                    "latency_ms": provider_latency_ms,
                }
            )
            print(f"🏁 [Final Answer]: {error_message}")
            return trace_logs

        tool_name = llm_response.get("tool_name", "")
        arguments = llm_response.get("arguments", {})
        print(f"🛠️ [Action]: {tool_name}({arguments})")

        tool_started = time.perf_counter()
        mcp_result = mcp_server.call_tool(tool_name, arguments)
        tool_latency_ms = round((time.perf_counter() - tool_started) * 1000, 2)
        observation = mcp_result.get("result", {})
        print(f"👁️ [Observation]: {json.dumps(observation, ensure_ascii=False)}")

        trace_logs.append(
            {
                "step": step,
                "query": user_query,
                "provider": provider_label,
                "action_type": "TOOL_EXECUTION",
                "thought": thought,
                "tool_name": tool_name,
                "arguments": arguments,
                "observation": observation,
                "provider_latency_ms": provider_latency_ms,
                "tool_latency_ms": tool_latency_ms,
                "latency_ms": round(provider_latency_ms + tool_latency_ms, 2),
            }
        )
        observations.append(
            {"tool_name": tool_name, "arguments": arguments, "result": observation}
        )

    limit_message = (
        f"Agent đã đạt giới hạn {MAX_ITERATIONS} bước và chưa thể hoàn tất yêu cầu. "
        "Vui lòng thu hẹp yêu cầu hoặc thử lại."
    )
    trace_logs.append(
        {
            "step": MAX_ITERATIONS + 1,
            "query": user_query,
            "provider": provider_label,
            "action_type": "FINAL_ANSWER",
            "thought": "Dừng an toàn khi đạt giới hạn vòng lặp.",
            "output": limit_message,
            "latency_ms": 0.0,
        }
    )
    print(f"🏁 [Final Answer]: {limit_message}")
    return trace_logs


def main() -> None:
    print("==========================================================")
    print("🎓 SCHOLARSHIP PLANNING AGENT — REACT + MCP")
    print("==========================================================")

    provider = get_llm_provider()
    mcp_server = MCPScholarshipServer()
    tests = load_test_cases()

    print(f"🔌 LLM Provider: {_provider_label(provider)}")
    print(f"🌐 MCP Server: {mcp_server.server_name}")
    print(f"✅ Đã tải {len(tests)} test case.\n")

    if "--interactive" in sys.argv:
        print("🎮 Nhập câu hỏi về hồ sơ, trường hoặc học bổng; gõ exit để thoát.")
        while True:
            try:
                user_input = input("👤 Bạn hỏi: ").strip()
                if not user_input or user_input.lower() in {"exit", "quit"}:
                    print("👋 Kết thúc phiên trò chuyện.")
                    break
                save_waterfall_trace(run_react_agent(user_input, provider, mcp_server))
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Đã thoát phiên tương tác.")
                break
        return

    if "--all" in sys.argv:
        print("🚀 [TEST SUITE MODE] Kiểm tra 5 test case:")
        completed_count = 0
        todo_count = 0
        all_traces: List[Dict[str, Any]] = []
        for test_case in tests:
            print("\n==================================================")
            print(
                f"🧪 [{test_case['id']}] {test_case['type']} "
                f"({test_case['complexity']})"
            )
            print(f"📌 Kỳ vọng: {test_case['expected_behavior']}")
            if test_case["question"].strip().startswith("TODO"):
                print("⏸️ Test case chưa có câu hỏi.")
                todo_count += 1
                continue
            all_traces.extend(
                run_react_agent(test_case["question"], provider, mcp_server)
            )
            completed_count += 1

        print("\n==================================================")
        print(
            f"📊 [KẾT QUẢ TEST SUITE]: Đã thực thi {completed_count}/{len(tests)} "
            f"Test Cases | {todo_count} Test Cases đang chờ điền câu hỏi (TODO)"
        )
        save_waterfall_trace(all_traces)
        return

    print("ℹ️ Chạy `python src/app.py --all` hoặc `python src/app.py --interactive`.")
    sample_query = tests[1]["question"]
    save_waterfall_trace(run_react_agent(sample_query, provider, mcp_server))


if __name__ == "__main__":
    main()

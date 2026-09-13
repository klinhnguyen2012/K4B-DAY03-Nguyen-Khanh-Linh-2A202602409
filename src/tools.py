"""Tool schemas và backend Mock cho Scholarship Planning Agent."""

import json
from typing import Any, Dict, List


TOOLS_SCHEMA = [
    {
        "name": "profile_query",
        "description": "Tra cứu hồ sơ người học để đánh giá mức phù hợp với học bổng.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "Mã học sinh hoặc sinh viên, ví dụ SV2026001",
                }
            },
            "required": ["student_id"],
        },
    },
    {
        "name": "scholarship_search",
        "description": "Tìm trường, chương trình và học bổng thử nghiệm phù hợp.",
        "parameters": {
            "type": "object",
            "properties": {
                "degree_level": {
                    "type": "string",
                    "description": "Bậc học mong muốn, ví dụ Cử nhân hoặc Thạc sĩ",
                },
                "major": {"type": "string", "description": "Ngành học mong muốn"},
                "regions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Các quốc gia hoặc khu vực mong muốn",
                },
                "intake": {"type": "string", "description": "Kỳ nhập học dự kiến"},
                "funding_need": {
                    "type": "string",
                    "description": "Nhu cầu hỗ trợ tài chính",
                },
            },
            "required": ["degree_level", "major", "regions", "intake", "funding_need"],
        },
    },
    {
        "name": "scholarship_details",
        "description": "Tra cứu điều kiện, tài liệu và deadline của một học bổng thử nghiệm.",
        "parameters": {
            "type": "object",
            "properties": {
                "scholarship_id": {"type": "string", "description": "Mã học bổng"},
                "intake": {"type": "string", "description": "Kỳ nhập học cần kiểm tra"},
            },
            "required": ["scholarship_id", "intake"],
        },
    },
    {
        "name": "study_plan_save",
        "description": "Lưu checklist và timeline chuẩn bị hồ sơ cho học bổng đã chọn.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "string", "description": "Mã học sinh hoặc sinh viên"},
                "scholarship_id": {"type": "string", "description": "Mã học bổng đã chọn"},
                "tasks": {
                    "type": "array",
                    "description": "Danh sách công việc cần hoàn thành",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Tên công việc"},
                            "due_date": {
                                "type": "string",
                                "description": "Hạn hoàn thành theo YYYY-MM-DD",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["high", "medium", "low"],
                            },
                        },
                        "required": ["title", "due_date", "priority"],
                    },
                },
            },
            "required": ["student_id", "scholarship_id", "tasks"],
        },
    },
]


STUDENT_PROFILES = {
    "SV2026001": {
        "full_name": "Nguyễn Văn An",
        "gpa": 3.5,
        "gpa_scale": 4.0,
        "certificates": [{"name": "IELTS", "score": 6.0, "expires_on": "2027-06-30"}],
        "activities": ["Thành viên Câu lạc bộ Công nghệ"],
        "target_degree": "Thạc sĩ",
        "desired_major": "Công nghệ thông tin",
        "preferred_regions": ["Việt Nam", "Quốc tế"],
        "intake": "2027",
        "funding_need": "Hỗ trợ học phí",
    },
    "SV2026002": {
        "full_name": "Trần Thị Bình",
        "gpa": 3.8,
        "gpa_scale": 4.0,
        "certificates": [{"name": "IELTS", "score": 7.0, "expires_on": "2028-03-01"}],
        "activities": ["Trưởng nhóm dự án cộng đồng"],
        "target_degree": "Cử nhân",
        "desired_major": "Khoa học dữ liệu",
        "preferred_regions": ["Việt Nam"],
        "intake": "2027",
        "funding_need": "Toàn phần",
    },
}


SCHOLARSHIPS = {
    "HB_TEST_01": {
        "scholarship_id": "HB_TEST_01",
        "name": "Mock Technology Excellence Scholarship",
        "university": "Đại học Công nghệ Mẫu",
        "country": "Việt Nam",
        "degree_level": "Thạc sĩ",
        "majors": ["Công nghệ thông tin", "Khoa học máy tính"],
        "intakes": ["2027"],
        "funding": "Hỗ trợ 75% học phí",
        "funding_category": "Hỗ trợ học phí",
        "requirements": {
            "minimum_gpa": 3.2,
            "gpa_scale": 4.0,
            "english_certificate": "IELTS",
            "minimum_english_score": 6.5,
            "activities": "Ưu tiên dự án hoặc hoạt động liên quan đến công nghệ",
        },
        "required_documents": [
            "CV",
            "Bảng điểm",
            "Bài luận",
            "Hai thư giới thiệu",
            "Chứng chỉ ngoại ngữ",
        ],
        "deadline": "2027-01-31T23:59:00+07:00",
        "source": "Dữ liệu thử nghiệm nội bộ — không dùng để nộp hồ sơ thật",
    },
    "HB_TEST_02": {
        "scholarship_id": "HB_TEST_02",
        "name": "Mock Global Computing Scholarship",
        "university": "International Sample University",
        "country": "Úc",
        "degree_level": "Thạc sĩ",
        "majors": ["Công nghệ thông tin", "Khoa học máy tính"],
        "intakes": ["2027"],
        "funding": "Toàn bộ học phí",
        "funding_category": "Toàn phần",
        "requirements": {
            "minimum_gpa": 3.6,
            "gpa_scale": 4.0,
            "english_certificate": "IELTS",
            "minimum_english_score": 7.0,
            "activities": "Có dự án kỹ thuật hoặc hoạt động lãnh đạo",
        },
        "required_documents": ["CV", "Bảng điểm", "Bài luận", "Hai thư giới thiệu"],
        "deadline": "2026-12-15T23:59:00+11:00",
        "source": "Dữ liệu thử nghiệm nội bộ — không dùng để nộp hồ sơ thật",
    },
    "HB_TEST_03": {
        "scholarship_id": "HB_TEST_03",
        "name": "Mock Data Futures Scholarship",
        "university": "Viện Đại học Mẫu Việt Nam",
        "country": "Việt Nam",
        "degree_level": "Cử nhân",
        "majors": ["Khoa học dữ liệu"],
        "intakes": ["2027"],
        "funding": "Toàn phần",
        "funding_category": "Toàn phần",
        "requirements": {
            "minimum_gpa": 3.7,
            "gpa_scale": 4.0,
            "english_certificate": "IELTS",
            "minimum_english_score": 6.5,
            "activities": "Có hoạt động cộng đồng hoặc thành tích học thuật",
        },
        "required_documents": ["CV", "Bảng điểm", "Bài luận", "Chứng chỉ ngoại ngữ"],
        "deadline": "2027-02-28T23:59:00+07:00",
        "source": "Dữ liệu thử nghiệm nội bộ — không dùng để nộp hồ sơ thật",
    },
}


SAVED_PLANS: Dict[str, Dict[str, Any]] = {}


def _json_response(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _normalize(value: Any) -> str:
    return str(value).strip().casefold()


def execute_profile_query(student_id: str) -> str:
    normalized_id = str(student_id).strip().upper()
    if not normalized_id:
        return _json_response({"status": "INVALID_ARGUMENTS", "message": "student_id không được để trống."})
    profile = STUDENT_PROFILES.get(normalized_id)
    if profile is None:
        return _json_response({"status": "NOT_FOUND", "message": f"Không tìm thấy hồ sơ có mã '{normalized_id}'."})
    return _json_response({"status": "SUCCESS", "student_id": normalized_id, "data": profile})


def _matches_region(scholarship: Dict[str, Any], regions: List[str]) -> bool:
    normalized_regions = {_normalize(region) for region in regions}
    country = _normalize(scholarship["country"])
    return country in normalized_regions or (
        country != _normalize("Việt Nam") and _normalize("Quốc tế") in normalized_regions
    )


def execute_scholarship_search(
    degree_level: str,
    major: str,
    regions: List[str],
    intake: str,
    funding_need: str,
) -> str:
    if not all([str(degree_level).strip(), str(major).strip(), str(intake).strip()]):
        return _json_response({"status": "INVALID_ARGUMENTS", "message": "Bậc học, ngành học và kỳ nhập học không được để trống."})
    if not isinstance(regions, list) or not regions:
        return _json_response({"status": "INVALID_ARGUMENTS", "message": "regions phải là danh sách không rỗng."})

    matches = []
    for scholarship in SCHOLARSHIPS.values():
        if _normalize(scholarship["degree_level"]) != _normalize(degree_level):
            continue
        if not any(
            _normalize(major) in _normalize(item) or _normalize(item) in _normalize(major)
            for item in scholarship["majors"]
        ):
            continue
        if str(intake).strip() not in scholarship["intakes"]:
            continue
        if not _matches_region(scholarship, regions):
            continue
        matches.append(
            {
                "scholarship_id": scholarship["scholarship_id"],
                "name": scholarship["name"],
                "university": scholarship["university"],
                "country": scholarship["country"],
                "degree_level": scholarship["degree_level"],
                "funding": scholarship["funding"],
                "intake": str(intake).strip(),
                "deadline": scholarship["deadline"],
                "source": scholarship["source"],
                "funding_match": _normalize(funding_need)
                in _normalize(scholarship["funding"] + " " + scholarship["funding_category"]),
            }
        )
    message = (
        f"Tìm thấy {len(matches)} học bổng thử nghiệm phù hợp."
        if matches
        else "Không tìm thấy học bổng thử nghiệm phù hợp; hãy điều chỉnh tiêu chí tìm kiếm."
    )
    return _json_response({"status": "SUCCESS", "data": matches, "message": message})


def execute_scholarship_details(scholarship_id: str, intake: str) -> str:
    normalized_id = str(scholarship_id).strip().upper()
    scholarship = SCHOLARSHIPS.get(normalized_id)
    if scholarship is None or str(intake).strip() not in scholarship["intakes"]:
        return _json_response(
            {
                "status": "NOT_FOUND",
                "message": f"Không tìm thấy học bổng '{normalized_id}' cho kỳ nhập học '{str(intake).strip()}'.",
            }
        )
    return _json_response(
        {
            "status": "SUCCESS",
            "scholarship_id": normalized_id,
            "intake": str(intake).strip(),
            "data": scholarship,
        }
    )


def _validate_tasks(tasks: Any) -> str:
    if not isinstance(tasks, list) or not tasks:
        return "tasks phải là danh sách không rỗng."
    required_fields = {"title", "due_date", "priority"}
    allowed_priorities = {"high", "medium", "low"}
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict) or not required_fields.issubset(task):
            return f"Công việc số {index} phải có title, due_date và priority."
        if not str(task["title"]).strip() or not str(task["due_date"]).strip():
            return f"Công việc số {index} có title hoặc due_date rỗng."
        if task["priority"] not in allowed_priorities:
            return f"Công việc số {index} có priority không hợp lệ."
    return ""


def execute_study_plan_save(
    student_id: str, scholarship_id: str, tasks: List[Dict[str, str]]
) -> str:
    normalized_student_id = str(student_id).strip().upper()
    normalized_scholarship_id = str(scholarship_id).strip().upper()
    if normalized_student_id not in STUDENT_PROFILES:
        return _json_response({"status": "NOT_FOUND", "message": "Không tìm thấy hồ sơ để lưu kế hoạch."})
    if normalized_scholarship_id not in SCHOLARSHIPS:
        return _json_response({"status": "NOT_FOUND", "message": "Không tìm thấy học bổng để lưu kế hoạch."})
    validation_error = _validate_tasks(tasks)
    if validation_error:
        return _json_response({"status": "INVALID_ARGUMENTS", "message": validation_error})

    plan_id = f"PLAN-{normalized_student_id}-{normalized_scholarship_id}"
    plan = {
        "plan_id": plan_id,
        "student_id": normalized_student_id,
        "scholarship_id": normalized_scholarship_id,
        "tasks": tasks,
    }
    SAVED_PLANS[plan_id] = plan
    return _json_response(
        {"status": "SUCCESS", **plan, "message": "Đã lưu checklist và timeline thử nghiệm thành công."}
    )


TOOL_ROUTER = {
    "profile_query": execute_profile_query,
    "scholarship_search": execute_scholarship_search,
    "scholarship_details": execute_scholarship_details,
    "study_plan_save": execute_study_plan_save,
}


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    executor = TOOL_ROUTER.get(tool_name)
    if executor is None:
        return _json_response({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại."})
    try:
        return executor(**arguments)
    except TypeError as exc:
        return _json_response({"status": "INVALID_ARGUMENTS", "error": str(exc)})
    except Exception as exc:
        return _json_response({"status": "EXECUTION_ERROR", "error": str(exc)})

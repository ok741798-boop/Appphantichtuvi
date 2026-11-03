"""Diễn giải lá số bằng OpenAI, có fallback về văn bản rule-based.

Fallback được dùng khi không có OPENAI_API_KEY, chưa cài gói openai hoặc API
lỗi. Kết quả cache trong bộ nhớ theo hash(lá số + năm + khía cạnh), nên khởi
động lại server sẽ mất cache. Họ tên và ngày sinh không được gửi lên OpenAI.
"""

import hashlib
import json
import logging
import os
import time
from typing import Dict, List, Optional

from calendar_utils import get_can_chi_year
from interpreter import analyze_current, cung_at, year_context

logger = logging.getLogger(__name__)

ASPECT_LABELS = {
    "summary": "tổng quan",
    "career": "sự nghiệp",
    "wealth": "tài lộc",
    "love": "tình cảm",
    "health": "sức khỏe",
}

MAX_ATTEMPTS = 3
BACKOFF_BASE_SECONDS = 1.0
REQUEST_TIMEOUT_SECONDS = 20.0

SYSTEM_PROMPT = """Bạn là chuyên gia tử vi Việt Nam nhiều năm kinh nghiệm.
Hãy luận giải bằng tiếng Việt, giọng tích cực, khách quan và thực tế.

Quy tắc:
- Viết một đoạn văn 100-150 từ, không dùng tiêu đề hay gạch đầu dòng.
- Chỉ dựa trên dữ liệu lá số được cung cấp, không tự thêm sao.
- Trình bày như xu hướng để tham khảo, không khẳng định chắc chắn về tương lai.
- Tránh mê tín cực đoan: không dọa tai họa, không khuyên cúng giải hạn.
- Về sức khỏe: không chẩn đoán bệnh, khuyến khích hỏi ý kiến bác sĩ khi cần.
- Kết thúc bằng một lời khuyên cụ thể, làm được ngay."""

# Mỗi khía cạnh có một cặp ví dụ để định hình giọng văn và độ dài.
FEW_SHOTS: Dict[str, Dict[str, str]] = {
    "summary": {
        "user": "Năm 2026 (Bính Ngọ), tuổi âm 36. Đại vận tại Quan Lộc có Vũ Khúc, Thất Sát. "
                "Tiểu hạn tại Tài Bạch có Thiên Phủ. Hãy luận tổng quan.",
        "assistant": "Năm Bính Ngọ mở ra giai đoạn khá vững vàng cho bạn. Đại vận đang đi qua "
                     "cung Quan Lộc với Vũ Khúc và Thất Sát, cho thấy đây là chặng đường đòi hỏi "
                     "kỷ luật cao, nhưng cũng là lúc năng lực thực sự được ghi nhận. Tiểu hạn tại "
                     "Tài Bạch gặp Thiên Phủ giúp cân bằng lại áp lực đó, vì sao này thiên về tích "
                     "lũy và giữ gìn thành quả. Nói cách khác, bạn có xu hướng làm nhiều trong năm "
                     "nay, và phần thưởng đến từ sự bền bỉ hơn là một bước nhảy lớn. Những quyết "
                     "định có kế hoạch rõ ràng thường cho kết quả tốt, còn những việc làm theo cảm "
                     "hứng nhất thời nên được cân nhắc thêm. Lời khuyên cho năm nay: chọn ra ba "
                     "mục tiêu quan trọng nhất, viết xuống và rà soát tiến độ mỗi quý.",
    },
    "career": {
        "user": "Năm 2027 (Đinh Mùi). Lưu Quan Lộc tại Dần có Thiên Cơ, Thái Âm, kèm Tả Phù. "
                "Hãy luận sự nghiệp.",
        "assistant": "Về sự nghiệp, năm Đinh Mùi cho thấy xu hướng thuận lợi với những công việc "
                     "cần tư duy và sự tỉ mỉ. Thiên Cơ gợi ý rằng trí tuệ và khả năng thích nghi là "
                     "thế mạnh của bạn lúc này, còn Thái Âm giúp bạn làm việc cẩn thận, kín đáo và "
                     "có chiều sâu. Sự xuất hiện của Tả Phù là dấu hiệu tích cực: bạn dễ nhận được "
                     "hỗ trợ từ đồng nghiệp hoặc cấp trên, nên những dự án có sự phối hợp sẽ suôn "
                     "sẻ hơn làm một mình. Tuy vậy, Thiên Cơ cũng khiến kế hoạch dễ thay đổi, vì "
                     "thế cần chốt rõ ưu tiên trước khi bắt tay vào việc. Lời khuyên cụ thể: "
                     "trong tháng này, hãy chủ động trao đổi với một người đi trước về hướng phát "
                     "triển của bạn trong hai năm tới.",
    },
    "wealth": {
        "user": "Năm 2028 (Mậu Thân). Lưu Tài Bạch tại Tý có Tham Lang, kèm Địa Kiếp. "
                "Hãy luận tài lộc.",
        "assistant": "Về tài lộc, năm Mậu Thân có nhiều cơ hội nhưng cũng cần sự tỉnh táo. Tham "
                     "Lang mang đến khả năng kiếm tiền qua giao tiếp, kinh doanh và các mối quan "
                     "hệ, nên bạn có thể thấy nhiều lời mời hợp tác hơn thường lệ. Địa Kiếp đi cùng "
                     "lại nhắc rằng dòng tiền năm nay dễ biến động, và những khoản đầu tư hứa hẹn "
                     "lợi nhuận quá nhanh cần được xem xét kỹ. Đây không phải dấu hiệu xấu, mà là "
                     "lời nhắc nên ưu tiên sự an toàn trước khi nghĩ đến mở rộng. Nếu giữ được kỷ "
                     "luật chi tiêu, bạn vẫn có thể kết thúc năm với tình hình tài chính tốt hơn. Lời khuyên "
                     "cụ thể: lập một khoản dự phòng tương đương ba tháng chi tiêu, sau đó mới "
                     "tính tới những cơ hội mới.",
    },
    "love": {
        "user": "Năm 2029 (Kỷ Dậu). Lưu Phu Thê tại Ngọ có Thái Dương, kèm Hồng Loan. "
                "Hãy luận tình cảm.",
        "assistant": "Về tình cảm, năm Kỷ Dậu mang không khí ấm áp và cởi mở. Thái Dương khiến "
                     "bạn chủ động, rộng lượng và dễ thể hiện sự quan tâm, còn Hồng Loan là sao "
                     "của nhân duyên, gợi ý những tin vui trong chuyện tình cảm. Với người đang độc "
                     "thân, đây là khoảng thời gian thuận lợi để mở rộng các mối quan hệ, nhất là "
                     "qua công việc hoặc bạn bè chung. Với người đã có đôi, năm nay phù hợp để bàn "
                     "tới những kế hoạch dài hạn của hai người. Điều cần lưu ý là Thái Dương đôi "
                     "khi làm bạn dành quá nhiều năng lượng ra bên ngoài, khiến người bên cạnh cảm "
                     "thấy bị bỏ quên. Lời khuyên cụ thể: hãy dành riêng một buổi mỗi tuần cho người "
                     "thương, không điện thoại và không bàn chuyện công việc.",
    },
    "health": {
        "user": "Năm 2030 (Canh Tuất). Lưu Tật Ách tại Thân có Thiên Đồng, kèm Thiên Hình. "
                "Hãy luận sức khỏe.",
        "assistant": "Về sức khỏe, năm Canh Tuất nhìn chung khá ổn định. Thiên Đồng là phúc tinh, "
                     "gợi ý tinh thần lạc quan và khả năng hồi phục tốt, đây là nền tảng rất đáng "
                     "quý. Thiên Hình đi cùng nhắc bạn nên có thái độ chủ động và kỷ luật hơn với "
                     "việc chăm sóc cơ thể, thay vì chờ tới khi có vấn đề mới quan tâm. Những thói "
                     "quen nhỏ như ngủ đủ giấc, ăn uống đúng bữa và vận động đều đặn có thể tạo ra "
                     "khác biệt lớn trong năm nay. Lá số chỉ phản ánh xu hướng và không "
                     "thay thế được ý kiến chuyên môn, vì vậy nếu có triệu chứng bất thường, hãy "
                     "đến gặp bác sĩ sớm. Lời khuyên cụ thể: đặt lịch khám sức khỏe tổng quát và "
                     "duy trì ba mươi phút đi bộ mỗi ngày.",
    },
}

_cache: Dict[str, str] = {}


def _cache_key(chart: Dict, aspect: str, year: int) -> str:
    """Tạo khóa cache: cùng lá số, cùng năm, cùng khía cạnh thì dùng lại kết quả."""
    payload = json.dumps({"cung": chart["cung"], "year": year, "aspect": aspect},
                         sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _palace_line(palace: Dict) -> str:
    """Mô tả một cung thành một dòng văn bản để đưa vào prompt."""
    stars = ", ".join(palace["chinh_tinh"]) or "vô chính diệu"
    extras = ", ".join(palace["phu_tinh"])
    hoa = ", ".join(f"{h['star']} {h['hoa']}" for h in palace["tu_hoa"])
    line = f"- {palace['name']} tại {palace['position']}: {stars}"
    if extras:
        line += f"; phụ tinh: {extras}"
    if hoa:
        line += f"; {hoa}"
    return line


def build_prompt(chart: Dict, aspect: str, year: int) -> str:
    """Soạn nội dung gửi cho mô hình. Chỉ gồm dữ liệu sao, không có thông tin cá nhân."""
    context = year_context(chart, year)
    dai_van = context["dai_van"]
    tieu_han = context["tieu_han"]
    luu_tinh = ", ".join(f"{name} tại {cung_at(chart, p)['position']}"
                         for name, p in context["luu_tinh"].items())
    lines = [
        f"Năm xem: {year} ({get_can_chi_year(year)}), tuổi âm {context['age']}.",
        f"{chart['am_duong']}, bản mệnh {chart['ban_menh']}, {chart['cuc']['name']}.",
        f"Đại vận: {dai_van['name'] if dai_van else 'chưa nhập đại vận'}.",
        f"Tiểu hạn: {tieu_han['name']} tại {tieu_han['position']}.",
        f"Lưu niên: {luu_tinh}.",
        "Lá số:",
        *[_palace_line(palace) for palace in chart["cung"]],
        f"Hãy luận {ASPECT_LABELS[aspect]} của năm {year}.",
    ]
    return "\n".join(lines)


def _build_messages(chart: Dict, aspect: str, year: int) -> List[Dict[str, str]]:
    """Ghép system prompt, ví dụ mẫu và câu hỏi thực tế."""
    example = FEW_SHOTS[aspect]
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": example["user"]},
        {"role": "assistant", "content": example["assistant"]},
        {"role": "user", "content": build_prompt(chart, aspect, year)},
    ]


def _get_client() -> Optional[object]:
    """Tạo OpenAI client; trả về None nếu chưa cấu hình key hoặc chưa cài gói."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("Chưa cài gói openai, dùng văn bản rule-based")
        return None
    # Tắt retry của thư viện để không nhân số lần thử với vòng lặp bên dưới.
    return OpenAI(api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS, max_retries=0)


def _is_retryable(error: Exception) -> bool:
    """Chỉ thử lại lỗi tạm thời; lỗi như sai key thì thử lại cũng vô ích."""
    status = getattr(error, "status_code", None)
    if status is None:
        # Lỗi kết nối và timeout không có mã HTTP.
        return type(error).__name__ in ("APIConnectionError", "APITimeoutError")
    return status == 429 or status >= 500


def _call_openai(client: object, messages: List[Dict[str, str]]) -> Optional[str]:
    """Gọi API, thử tối đa 3 lần với thời gian chờ tăng theo cấp số nhân."""
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )
            content = response.choices[0].message.content
            return content.strip() if content else None
        except Exception as error:  # SDK có nhiều loại lỗi, lỗi nào cũng phải về được fallback.
            logger.warning("Gọi OpenAI lỗi (lần %d): %s", attempt + 1, type(error).__name__)
            if attempt == MAX_ATTEMPTS - 1 or not _is_retryable(error):
                return None
            time.sleep(BACKOFF_BASE_SECONDS * 2 ** attempt)
    return None


def generate_narrative(chart: Dict, aspect: str, year: Optional[int] = None) -> str:
    """Sinh lời luận cho một khía cạnh.

    Args:
        chart: Lá số từ build_chart.
        aspect: Một trong summary, career, wealth, love, health.
        year: Năm xem hạn; mặc định là năm dương lịch hiện tại.

    Returns:
        Lời luận từ OpenAI, hoặc văn bản rule-based nếu không gọi được.
    """
    if aspect not in ASPECT_LABELS:
        raise ValueError(f"Khía cạnh không hợp lệ: {aspect}")
    year = year if year is not None else time.localtime().tm_year

    key = _cache_key(chart, aspect, year)
    if key in _cache:
        return _cache[key]

    client = _get_client()
    narrative = _call_openai(client, _build_messages(chart, aspect, year)) if client else None
    if narrative is None:
        # Không cache fallback để lần sau còn thử lại AI.
        return analyze_current(chart, year)[aspect]
    _cache[key] = narrative
    return narrative

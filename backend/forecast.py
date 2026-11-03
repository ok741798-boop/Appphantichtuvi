"""Dự đoán vận hạn 10 năm dựa trên luận giải rule-based."""

from typing import Dict, List

from interpreter import analyze_year

# Ngưỡng trùng với màu thẻ năm trên giao diện: từ 7 là xanh, dưới 4 là đỏ.
NGUONG_KHOI_SU = 7
NGUONG_THAN_TRONG = 4


def year_verdict(rating: int) -> str:
    """Đổi điểm năm thành lời gợi ý ngắn: nên khởi sự hay cần thận trọng."""
    if rating >= NGUONG_KHOI_SU:
        return "Tốt để khởi sự"
    if rating < NGUONG_THAN_TRONG:
        return "Cần thận trọng"
    return "Giữ nhịp ổn định"


def forecast_10_years(chart: Dict, start_year: int) -> List[Dict]:
    """Dự đoán 10 năm liên tiếp, bắt đầu từ start_year.

    Mỗi phần tử gồm year, can_chi, age, rating (số nguyên 1-10), verdict,
    short_summary (cho thẻ năm), summary, aspect_ratings và các khía cạnh
    career, wealth, love, health.
    """
    results = []
    for offset in range(10):
        year_result = analyze_year(chart, start_year + offset)
        year_result["rating"] = round(year_result["rating"])
        year_result["verdict"] = year_verdict(year_result["rating"])
        year_result["short_summary"] = (f"Tiểu hạn tại cung {year_result['tieu_han']}, "
                                        f"tổng thể {year_result['tone']}.")
        results.append(year_result)
    return results

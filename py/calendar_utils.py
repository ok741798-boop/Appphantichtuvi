"""Tiện ích lịch: chuyển Dương lịch sang Âm lịch Việt Nam và tính Can Chi.

Âm lịch ở đây được tính bằng thiên văn theo múi giờ GMT+7 (thuật toán của
Hồ Ngọc Đức). Không dùng bảng Tết của Trung Quốc vì lịch hai nước có thể lệch
nhau: Tết 1985 ở Việt Nam là 21/1, ở Trung Quốc là 20/2; Tết 2007 là 17/2 so
với 18/2.
"""

import math
import sys
from datetime import date, timedelta
from typing import Dict, Tuple

CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# Múi giờ Việt Nam, ảnh hưởng tới ngày Sóc và ngày Trung khí.
TIME_ZONE = 7

HOUR_LABELS = [
    "Tý (23h-1h)", "Sửu (1h-3h)", "Dần (3h-5h)", "Mão (5h-7h)",
    "Thìn (7h-9h)", "Tỵ (9h-11h)", "Ngọ (11h-13h)", "Mùi (13h-15h)",
    "Thân (15h-17h)", "Dậu (17h-19h)", "Tuất (19h-21h)", "Hợi (21h-23h)",
]

# 30 nạp âm, mỗi nạp âm ứng với 2 cặp Can Chi liên tiếp trong vòng 60 Giáp Tý.
NAP_AM = [
    "Hải Trung Kim", "Lư Trung Hỏa", "Đại Lâm Mộc", "Lộ Bàng Thổ", "Kiếm Phong Kim",
    "Sơn Đầu Hỏa", "Giản Hạ Thủy", "Thành Đầu Thổ", "Bạch Lạp Kim", "Dương Liễu Mộc",
    "Tuyền Trung Thủy", "Ốc Thượng Thổ", "Tích Lịch Hỏa", "Tùng Bách Mộc", "Trường Lưu Thủy",
    "Sa Trung Kim", "Sơn Hạ Hỏa", "Bình Địa Mộc", "Bích Thượng Thổ", "Kim Bạch Kim",
    "Phúc Đăng Hỏa", "Thiên Hà Thủy", "Đại Trạch Thổ", "Thoa Xuyến Kim", "Tang Đố Mộc",
    "Đại Khê Thủy", "Sa Trung Thổ", "Thiên Thượng Hỏa", "Thạch Lựu Mộc", "Đại Hải Thủy",
]


# ==================== CAN CHI ====================

def get_can_chi_year(year: int) -> str:
    """Tính Can Chi của năm: (year-4)%10 cho Can, (year-4)%12 cho Chi.

    Ví dụ: get_can_chi_year(1984) -> "Giáp Tý".
    """
    return f"{CAN[(year - 4) % 10]} {CHI[(year - 4) % 12]}"


def get_can_chi_month(lunar_year: int, lunar_month: int) -> str:
    """Tính Can Chi tháng âm lịch.

    Chi tháng cố định: tháng 1 là Dần, tháng 2 là Mão... Can tháng suy từ Can
    năm theo phép Ngũ Hổ Độn, ví dụ năm Giáp có tháng 1 là Bính Dần.
    """
    year_can = (lunar_year - 4) % 10
    return f"{CAN[(year_can * 2 + lunar_month + 1) % 10]} {CHI[(lunar_month + 1) % 12]}"


def get_can_chi_day(solar_date: date) -> str:
    """Tính Can Chi ngày dương lịch theo số ngày Julius.

    Vòng Can Chi ngày không bị ngắt quãng nên chỉ cần lấy JDN + 49 mod 60.
    Ví dụ: 10/2/2024 (mùng 1 Tết) là ngày Giáp Thìn.
    """
    index = (_jd_from_date(solar_date.day, solar_date.month, solar_date.year) + 49) % 60
    return f"{CAN[index % 10]} {CHI[index % 12]}"


def get_hour_chi_index(hour_24h: int) -> int:
    """Đổi giờ 24h sang chỉ số Chi của giờ: Tý=0 (23h-1h), Sửu=1 (1h-3h)..."""
    return ((hour_24h + 1) // 2) % 12


def get_can_chi_hour(day_can_chi: str, hour_24h: int) -> str:
    """Tính Can Chi giờ theo phép Ngũ Thử Độn.

    Can của giờ phụ thuộc Can ngày nên cần truyền thêm Can Chi ngày; ví dụ
    ngày Giáp có giờ Tý là Giáp Tý, ngày Ất có giờ Tý là Bính Tý.
    """
    day_can = CAN.index(day_can_chi.split()[0])
    chi = get_hour_chi_index(hour_24h)
    return f"{CAN[(day_can * 2 + chi) % 10]} {CHI[chi]}"


def get_nap_am(can_index: int, chi_index: int) -> str:
    """Lấy nạp âm của một cặp Can Chi, ví dụ Giáp Tý -> "Hải Trung Kim"."""
    # Tìm vị trí trong vòng 60: số x thỏa x%10 = can và x%12 = chi.
    cycle_index = (6 * can_index - 5 * chi_index) % 60
    return NAP_AM[cycle_index // 2]


# ==================== TÍNH TOÁN THIÊN VĂN ====================

def _jd_from_date(day: int, month: int, year: int) -> int:
    """Đổi ngày dương lịch sang số ngày Julius."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _new_moon_day(k: int) -> int:
    """Tìm ngày Sóc (mùng 1) của lần trăng mới thứ k, tính từ 1/1/1900."""
    t = k / 1236.85
    t2 = t * t
    t3 = t2 * t
    dr = math.pi / 180
    jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * t2 - 0.000000155 * t3
    jd1 += 0.00033 * math.sin((166.56 + 132.87 * t - 0.009173 * t2) * dr)
    m = 359.2242 + 29.10535608 * k - 0.0000333 * t2 - 0.00000347 * t3
    mpr = 306.0253 + 385.81691806 * k + 0.0107306 * t2 + 0.00001236 * t3
    f = 21.2964 + 390.67050646 * k - 0.0016528 * t2 - 0.00000239 * t3
    c1 = (0.1734 - 0.000393 * t) * math.sin(m * dr) + 0.0021 * math.sin(2 * dr * m)
    c1 += -0.4068 * math.sin(mpr * dr) + 0.0161 * math.sin(dr * 2 * mpr)
    c1 -= 0.0004 * math.sin(dr * 3 * mpr)
    c1 += 0.0104 * math.sin(dr * 2 * f) - 0.0051 * math.sin(dr * (m + mpr))
    c1 += -0.0074 * math.sin(dr * (m - mpr)) + 0.0004 * math.sin(dr * (2 * f + m))
    c1 += -0.0004 * math.sin(dr * (2 * f - m)) - 0.0006 * math.sin(dr * (2 * f + mpr))
    c1 += 0.0010 * math.sin(dr * (2 * f - mpr)) + 0.0005 * math.sin(dr * (2 * mpr + m))
    if t < -11:
        delta_t = 0.001 + 0.000839 * t + 0.0002261 * t2 - 0.00000845 * t3 - 0.000000081 * t * t3
    else:
        delta_t = -0.000278 + 0.000265 * t + 0.000262 * t2
    return math.floor(jd1 + c1 - delta_t + 0.5 + TIME_ZONE / 24)


def _sun_longitude_sector(jd: int) -> int:
    """Xác định Mặt Trời ở cung Hoàng đạo nào (0-11, mỗi cung 30 độ) trong ngày jd."""
    t = (jd - 2451545.5 - TIME_ZONE / 24) / 36525
    t2 = t * t
    dr = math.pi / 180
    m = 357.52910 + 35999.05030 * t - 0.0001559 * t2 - 0.00000048 * t * t2
    l0 = 280.46645 + 36000.76983 * t + 0.0003032 * t2
    dl = (1.914600 - 0.004817 * t - 0.000014 * t2) * math.sin(dr * m)
    dl += (0.019993 - 0.000101 * t) * math.sin(dr * 2 * m) + 0.000290 * math.sin(dr * 3 * m)
    longitude = (l0 + dl) * dr
    longitude -= 2 * math.pi * math.floor(longitude / (2 * math.pi))
    return math.floor(longitude / math.pi * 6)


def _lunar_month_11(year: int) -> int:
    """Tìm ngày đầu tháng 11 âm lịch, tức tháng chứa Đông Chí của năm dương lịch."""
    offset = _jd_from_date(31, 12, year) - 2415021
    k = math.floor(offset / 29.530588853)
    new_moon = _new_moon_day(k)
    if _sun_longitude_sector(new_moon) >= 9:
        new_moon = _new_moon_day(k - 1)
    return new_moon


def _leap_month_offset(month_11: int) -> int:
    """Tìm tháng nhuận: tháng đầu tiên sau tháng 11 không chứa Trung khí."""
    k = math.floor((month_11 - 2415021.076998695) / 29.530588853 + 0.5)
    i = 1
    sector = _sun_longitude_sector(_new_moon_day(k + i))
    while True:
        last = sector
        i += 1
        sector = _sun_longitude_sector(_new_moon_day(k + i))
        if sector == last or i >= 14:
            return i - 1


def _solar_to_lunar_tuple(year: int, month: int, day: int) -> Tuple[int, int, int, bool]:
    """Trả về (ngày, tháng, năm âm lịch, có phải tháng nhuận không)."""
    day_number = _jd_from_date(day, month, year)
    k = math.floor((day_number - 2415021.076998695) / 29.530588853)
    month_start = _new_moon_day(k + 1)
    if month_start > day_number:
        month_start = _new_moon_day(k)

    a11 = _lunar_month_11(year)
    b11 = a11
    if a11 >= month_start:
        lunar_year = year
        a11 = _lunar_month_11(year - 1)
    else:
        lunar_year = year + 1
        b11 = _lunar_month_11(year + 1)

    lunar_day = day_number - month_start + 1
    diff = (month_start - a11) // 29
    is_leap = False
    lunar_month = diff + 11
    # Năm có 13 tháng khi khoảng cách giữa hai tháng 11 dài hơn 365 ngày.
    if b11 - a11 > 365:
        leap_diff = _leap_month_offset(a11)
        if diff >= leap_diff:
            lunar_month = diff + 10
            is_leap = diff == leap_diff
    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1
    return lunar_day, lunar_month, lunar_year, is_leap


def solar_to_lunar(year: int, month: int, day: int) -> Dict:
    """Chuyển ngày dương lịch sang âm lịch Việt Nam.

    Ví dụ: solar_to_lunar(2024, 2, 10) -> mùng 1 tháng 1 năm 2024.

    Returns:
        Dict gồm lunar_day, lunar_month, lunar_year, is_leap.
    """
    lunar_day, lunar_month, lunar_year, is_leap = _solar_to_lunar_tuple(year, month, day)
    return {
        "lunar_day": lunar_day,
        "lunar_month": lunar_month,
        "lunar_year": lunar_year,
        "is_leap": is_leap,
    }


def get_full_can_chi(year: int, month: int, day: int, hour: int) -> Dict:
    """Tính đầy đủ âm lịch và Can Chi năm/tháng/ngày/giờ của một thời điểm sinh.

    Giờ Tý bắt đầu từ 23h nên người sinh từ 23h-24h được tính sang ngày hôm
    sau, theo thông lệ của tử vi. Trường day_rollover đánh dấu trường hợp này.
    """
    day_rollover = hour == 23
    effective = date(year, month, day) + timedelta(days=1 if day_rollover else 0)
    lunar = solar_to_lunar(effective.year, effective.month, effective.day)
    day_cc = get_can_chi_day(effective)
    return {
        "lunar": lunar,
        "day_rollover": day_rollover,
        "can_chi": {
            "year": get_can_chi_year(lunar["lunar_year"]),
            "month": get_can_chi_month(lunar["lunar_year"], lunar["lunar_month"]),
            "day": day_cc,
            "hour": get_can_chi_hour(day_cc, hour),
        },
    }


if __name__ == "__main__":
    # Tự kiểm tra nhanh: python calendar_utils.py
    # 10/2/2024 -> 1/1/2024, năm Giáp Thìn, ngày Giáp Thìn
    # 21/1/1985 -> 1/1/1985, năm Ất Sửu (Tết Việt Nam sớm hơn Trung Quốc 1 tháng)
    # 23/3/2023 -> 2 nhuận/2023, năm Quý Mão
    sys.stdout.reconfigure(encoding="utf-8")
    for sample in [(2024, 2, 10, 12), (1985, 1, 21, 8), (2023, 3, 23, 0)]:
        print(sample, get_full_can_chi(*sample))

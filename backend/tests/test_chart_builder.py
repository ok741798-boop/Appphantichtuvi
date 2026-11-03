"""Kiểm tra lịch âm và các quy tắc an sao bằng những giá trị đã biết."""

import pytest

from calendar_utils import CHI, get_can_chi_day, get_can_chi_year, get_full_can_chi, get_nap_am, solar_to_lunar
from chart_builder import build_chart, find_menh, find_than, find_tu_vi, palace_can, place_chinh_tinh
from datetime import date

SUU, DAN, THIN, TI, NGO, DAU, HOI = 1, 2, 4, 5, 6, 9, 11


@pytest.mark.parametrize("solar, expected", [
    ((2024, 2, 10), (1, 1, 2024, False)),
    ((1985, 1, 21), (1, 1, 1985, False)),  # Tết Việt Nam sớm hơn Trung Quốc một tháng
    ((2007, 2, 17), (1, 1, 2007, False)),  # Tết Việt Nam sớm hơn Trung Quốc một ngày
    ((2023, 3, 22), (1, 2, 2023, True)),   # Mùng 1 tháng 2 nhuận, Sóc lúc 00:23 GMT+7
    ((1991, 2, 15), (1, 1, 1991, False)),  # Sóc lúc 00:32 GMT+7, dễ lệch sang hôm trước
])
def test_solar_to_lunar(solar, expected):
    lunar = solar_to_lunar(*solar)
    assert (lunar["lunar_day"], lunar["lunar_month"], lunar["lunar_year"], lunar["is_leap"]) == expected


def test_can_chi():
    assert get_can_chi_year(1984) == "Giáp Tý"
    assert get_can_chi_day(date(2024, 2, 10)) == "Giáp Thìn"


def test_gio_ty_sau_23h_tinh_sang_ngay_hom_sau():
    before = get_full_can_chi(2024, 2, 9, 22)
    after = get_full_can_chi(2024, 2, 9, 23)
    assert before["lunar"]["lunar_year"] == 2023
    assert after["lunar"]["lunar_day"] == 1 and after["lunar"]["lunar_year"] == 2024
    assert after["day_rollover"] is True


@pytest.mark.parametrize("can, chi, expected", [
    (0, 0, "Hải Trung Kim"), (2, 2, "Lư Trung Hỏa"), (9, 11, "Đại Hải Thủy"), (6, 6, "Lộ Bàng Thổ"),
])
def test_nap_am(can, chi, expected):
    assert get_nap_am(can, chi) == expected


def test_can_cung_theo_ngu_ho_don():
    assert palace_can(0, DAN) == 2  # Năm Giáp, cung Dần là Bính Dần
    assert palace_can(4, DAN) == 0  # Năm Mậu, cung Dần là Giáp Dần
    assert palace_can(0, SUU) == 3  # Năm Giáp, cung Sửu là Đinh Sửu


def test_menh_than():
    assert find_menh(1, 0) == DAN and find_than(1, 0) == DAN
    assert find_menh(3, 2) == DAN
    assert find_than(3, 2) == 6


@pytest.mark.parametrize("day, cuc, expected", [
    (1, 2, SUU), (2, 2, DAN), (1, 3, THIN), (1, 4, HOI), (1, 5, NGO), (1, 6, DAU),
])
def test_tu_vi_mung_1_theo_cuc(day, cuc, expected):
    assert find_tu_vi(day, cuc) == expected


def test_chinh_tinh_tu_vi_tai_ty():
    stars = place_chinh_tinh(0)
    assert stars["Thiên Phủ"] == THIN
    assert stars["Liêm Trinh"] == THIN
    assert stars["Thiên Cơ"] == HOI
    assert stars["Phá Quân"] == DAN
    assert len(stars) == 14


@pytest.mark.parametrize("year", [1900, 1950, 1984, 1990, 2000, 2024])
@pytest.mark.parametrize("gender", ["Nam", "Nữ"])
def test_la_so_day_du(year, gender):
    chart = build_chart({"full_name": "A", "gender": gender, "day": 15, "month": 5,
                         "year": year, "hour": 10})
    assert sorted(c["position_index"] for c in chart["cung"]) == list(range(12))
    assert sum(len(c["chinh_tinh"]) for c in chart["cung"]) == 14
    assert sum(1 for c in chart["cung"] if c["is_than"]) == 1
    assert sum(1 for c in chart["cung"] if c["tuan"]) == 2
    assert sum(1 for c in chart["cung"] if c["triet"]) == 2
    assert len(chart["tu_hoa"]) == 4
    assert sorted(c["dai_van_start"] for c in chart["cung"]) == [
        chart["cuc"]["number"] + 10 * step for step in range(12)
    ]
    assert chart["menh_position"] in CHI

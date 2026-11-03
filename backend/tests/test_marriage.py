"""Kiểm tra module Duyên Số: phân tích, dự đoán, so sánh và giới hạn tuổi."""

import random
from datetime import date

import pytest

from app import app, charts
from chart_builder import build_chart
from destiny_predictor import (_age_candidate, compare_charts, element_relation, love_month,
                               love_score)
from marriage_analyzer import analyze_marriage, calculate_fate_percentage
from stars_data import CHINH_TINH, PHU_TINH

YEAR = 2026
BIRTH = {"full_name": "Nguyễn Văn A", "gender": "Nam", "day": 15, "month": 5,
         "year": 1990, "hour": 9, "birth_place": "Hà Nội"}
PARTNER = {"full_name": "Trần Thị B", "gender": "Nữ", "day": 2, "month": 3,
           "year": 1993, "hour": 7}


@pytest.fixture
def client():
    charts.clear()
    return app.test_client()


@pytest.fixture
def chart_id(client):
    return client.post("/api/chart/build", json=BIRTH).get_json()["chart_id"]


def _random_charts(count):
    rng = random.Random(11)
    for _ in range(count):
        yield build_chart({"full_name": "A", "gender": rng.choice(["Nam", "Nữ"]),
                           "day": rng.randint(1, 28), "month": rng.randint(1, 12),
                           "year": rng.randint(1940, 2008), "hour": rng.randint(0, 23)})


def test_phan_tich_du_truong_tren_nhieu_la_so():
    for chart in _random_charts(150):
        result = analyze_marriage(chart, YEAR)
        assert result["partner_term"] == ("vợ" if chart["info"]["gender"] == "Nam" else "chồng")
        assert result["partner_appearance"]["face"]
        assert result["partner_personality"]["traits"]
        assert result["partner_career"]["groups"]
        assert 0 <= result["fate_percentage"] <= 100
        assert all(0 <= value <= 100 for value in result["harmony"].values())
        assert len(result["timeline"]) == 6
        assert result["timeline"][0]["year"] == YEAR
        assert 1 <= result["meeting_time"]["month"] <= 12
        assert YEAR <= result["meeting_time"]["year"] < YEAR + 8


def test_cac_moc_tuong_lai_dung_thu_tu():
    for chart in _random_charts(150):
        result = analyze_marriage(chart, YEAR)
        years = [item["year"] for item in result["future_timeline"]]
        assert years == sorted(years)
        assert result["marriage_age"]["best_year"] > result["meeting_time"]["year"]
        assert result["marriage_age"]["from_age"] <= result["marriage_age"]["best_age"]
        assert result["marriage_age"]["best_age"] <= result["marriage_age"]["to_age"]


def test_tuoi_khi_gap_nhau_nhat_quan():
    for chart in _random_charts(150):
        result = analyze_marriage(chart, YEAR)
        ages = result["meeting_ages"]
        assert ages["you_age"] == result["meeting_time"]["age"]
        assert ages["partner_age_from"] <= ages["partner_age"] <= ages["partner_age_to"]
        assert 1 <= len(ages["candidates"]) <= 3
        assert ages["name_hints"]
        for item in ages["candidates"]:
            assert item["age_at_meeting"] == ages["meeting_year"] - item["birth_year"] + 1


def test_nguoi_ay_du_tuoi_khi_khoang_chenh_cho_phep():
    chart = build_chart({**BIRTH, "year": 2007})
    for item in analyze_marriage(chart, YEAR)["meeting_ages"]["candidates"]:
        assert item["age_at_meeting"] >= 19


def test_nam_sinh_goi_y_khop_can_chi_va_ban_menh():
    item = _age_candidate(build_chart(BIRTH), 2004, 2031)
    assert item["can_chi"] == "Giáp Thân"
    assert item["ban_menh"] == "Tuyền Trung Thủy"
    assert item["zodiac"] == "Thân"
    assert item["age_at_meeting"] == 28


def test_gia_dinh_hai_ben_co_du_truong():
    for chart in _random_charts(150):
        result = analyze_marriage(chart, YEAR)
        for family in (result["your_family"], result["partner_family"]):
            assert family["wealth"] and family["siblings"] and family["parents"]
        assert result["family_match"]["relation"] in ("tương sinh", "bình hòa", "tương khắc")
        assert result["family_match"]["text"]


def test_gia_dinh_nguoi_xem_doc_tu_cung_phu_mau_cua_chinh_ho():
    chart = build_chart(BIRTH)
    phu_mau = next(c for c in chart["cung"] if c["name"] == "Phụ Mẫu")
    phu_mau.update({"tuan": True, "triet": False, "phu_tinh": []})
    assert analyze_marriage(chart, YEAR)["your_family"]["parents"] == "Bố mẹ có lúc bất đồng"
    phu_mau.update({"tuan": False})
    assert analyze_marriage(chart, YEAR)["your_family"]["parents"] == "Bố mẹ khá hòa thuận"


def test_so_sanh_co_gia_dinh_hai_ben_tu_la_so_that():
    result = compare_charts(build_chart(BIRTH), build_chart(PARTNER))
    assert {"Gia đình", "Bố mẹ", "Anh chị em"} <= {row["label"] for row in result["rows"]}
    assert result["family_text"]


def test_khong_tra_ve_ho_ten_du_doan():
    result = analyze_marriage(build_chart(BIRTH), YEAR)
    assert "partner_name" not in result
    assert "full_name" not in result["meeting_ages"]


def test_ket_qua_on_dinh_voi_cung_la_so():
    chart = build_chart(BIRTH)
    assert analyze_marriage(chart, YEAR) == analyze_marriage(chart, YEAR)


def test_diem_thuan_duyen_tinh_tuan_triet_va_hoa():
    chart = build_chart(BIRTH)
    phu_the = next(c for c in chart["cung"] if c["name"] == "Phu Thê")
    phu_the.update({"chinh_tinh": [], "phu_tinh": ["Hồng Loan"], "tu_hoa": [], "tuan": False, "triet": False})
    assert calculate_fate_percentage(chart) == 58
    phu_the.update({"tuan": True, "tu_hoa": [{"star": "Hồng Loan", "hoa": "Hóa Kỵ"}]})
    assert calculate_fate_percentage(chart) == 35


def test_love_score_cong_diem_khi_tieu_han_vao_phu_the():
    chart = build_chart(BIRTH)
    scores = [love_score(chart, year) for year in range(YEAR, YEAR + 12)]
    assert any("tiểu hạn vào cung Phu Thê" in item["reasons"] for item in scores)


def test_thang_giua_cac_nam_cach_nhau_theo_chi():
    chart = build_chart(BIRTH)
    assert (love_month(chart, YEAR) - love_month(chart, YEAR + 1)) % 12 == 1


@pytest.mark.parametrize("first, second, expected", [
    ("Kim", "Kim", "bình hòa"), ("Kim", "Thủy", "tương sinh"), ("Thủy", "Kim", "tương sinh"),
    ("Kim", "Mộc", "tương khắc"), ("Hỏa", "Thủy", "tương khắc"),
])
def test_quan_he_ngu_hanh(first, second, expected):
    assert element_relation(first, second) == expected


def test_so_sanh_hai_la_so():
    result = compare_charts(build_chart(BIRTH), build_chart(PARTNER))
    assert 0 <= result["overall"] <= 100
    assert result["partner_name"] == PARTNER["full_name"]
    assert result["warnings"] and result["advice"]


def test_api_phan_tich(client, chart_id):
    response = client.post("/api/marriage/analyze", json={"chart_id": chart_id})
    assert response.status_code == 200
    assert "fate_percentage" in response.get_json()


def test_api_so_sanh_khong_luu_la_so_nguoi_ay(client, chart_id):
    response = client.post("/api/marriage/compare", json={"chart_id": chart_id, "partner": PARTNER})
    assert response.status_code == 200
    assert list(charts) == [chart_id]


def test_api_khong_tim_thay_la_so(client):
    assert client.post("/api/marriage/analyze", json={"chart_id": "x"}).status_code == 404


def test_api_chan_nguoi_chua_du_tuoi(client):
    today = date.today()
    minor = {**BIRTH, "year": today.year - 17}
    minor_id = client.post("/api/chart/build", json=minor).get_json()["chart_id"]
    response = client.post("/api/marriage/analyze", json={"chart_id": minor_id})
    assert response.status_code == 403


def test_api_chan_so_sanh_voi_nguoi_chua_du_tuoi(client, chart_id):
    partner = {**PARTNER, "year": date.today().year - 16}
    response = client.post("/api/marriage/compare", json={"chart_id": chart_id, "partner": partner})
    assert response.status_code == 403


def test_api_so_sanh_thieu_thong_tin(client, chart_id):
    response = client.post("/api/marriage/compare", json={"chart_id": chart_id})
    assert response.status_code == 400


@pytest.mark.parametrize("path", ["/", "/marriage.html", "/js/main.js", "/css/style.css"])
def test_frontend_buoc_kiem_tra_lai_ban_moi(client, path):
    assert "no-cache" in client.get(path).headers["Cache-Control"]


def test_so_sao_tren_trang_chu_khop_du_lieu(client):
    html = client.get("/").get_data(as_text=True)
    assert f"{len(CHINH_TINH)} chính tinh, {len(PHU_TINH)} phụ tinh" in html


def test_trang_marriage_duoc_phuc_vu(client):
    assert client.get("/marriage").status_code == 200
    assert client.get("/marriage.html").status_code == 200

"""Kiểm tra API, độ dài lời luận, fallback AI và xuất PDF."""

import random
from types import SimpleNamespace

import pytest

import ai_narrator
from app import app, charts
from chart_builder import build_chart
from forecast import forecast_10_years, year_verdict
from interpreter import ASPECTS, MAX_ASPECT_WORDS, MIN_ASPECT_WORDS, analyze_current

BIRTH = {"full_name": "Nguyễn Văn A", "gender": "Nam", "day": 15, "month": 5,
         "year": 1990, "hour": 9, "birth_place": "Hà Nội"}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    charts.clear()
    return app.test_client()


@pytest.fixture
def chart_id(client):
    return client.post("/api/chart/build", json=BIRTH).get_json()["chart_id"]


def _random_charts(count):
    rng = random.Random(7)
    for _ in range(count):
        yield build_chart({"full_name": "A", "gender": rng.choice(["Nam", "Nữ"]),
                           "day": rng.randint(1, 28), "month": rng.randint(1, 12),
                           "year": rng.randint(1900, 2025), "hour": rng.randint(0, 23)})


def test_build_va_doc_lai_chart(client, chart_id):
    response = client.get(f"/api/chart/{chart_id}")
    assert response.status_code == 200
    assert len(response.get_json()["cung"]) == 12


@pytest.mark.parametrize("change, message", [
    ({"full_name": "  "}, "họ tên"),
    ({"gender": "X"}, "Giới tính"),
    ({"hour": 24}, "Giờ sinh"),
    ({"month": 13}, "Ngày sinh"),
    ({"year": 1899}, "1900"),
    ({"year": "1990"}, "số nguyên"),
])
def test_tu_choi_du_lieu_sai(client, change, message):
    response = client.post("/api/chart/build", json={**BIRTH, **change})
    assert response.status_code == 400
    assert message in response.get_json()["error"]


def test_chart_khong_ton_tai(client):
    assert client.get("/api/chart/khong-co").status_code == 404
    assert client.post("/api/analysis/current", json={"chart_id": "khong-co"}).status_code == 404


def test_phan_tich_hien_tai(client, chart_id):
    data = client.post("/api/analysis/current", json={"chart_id": chart_id}).get_json()
    assert data["dai_van"]["cung"] and data["tieu_han"]["cung"]
    for aspect in ASPECTS:
        assert data[aspect] and 1 <= data["aspect_ratings"][aspect] <= 10


def test_du_doan_10_nam(client, chart_id):
    data = client.post("/api/analysis/forecast", json={"chart_id": chart_id}).get_json()["forecast"]
    assert len(data) == 10
    assert [item["year"] for item in data] == list(range(data[0]["year"], data[0]["year"] + 10))
    for item in data:
        assert 1 <= item["rating"] <= 10 and item["verdict"] and item["short_summary"]
        assert set(item["aspect_ratings"]) == set(ASPECTS)


def test_loi_luan_du_do_dai():
    for chart in _random_charts(1500):
        result = analyze_current(chart, 2026)
        for aspect in ASPECTS:
            assert MIN_ASPECT_WORDS <= len(result[aspect].split()) <= MAX_ASPECT_WORDS, result[aspect]


def test_diem_nam_co_du_ca_ba_muc():
    verdicts = {item["verdict"] for chart in _random_charts(60)
                for item in forecast_10_years(chart, 2026)}
    assert verdicts == {year_verdict(9), year_verdict(5), year_verdict(2)}


def test_be_sinh_truoc_dai_van_dau_tien():
    chart = build_chart({**BIRTH, "year": 2025})
    assert analyze_current(chart, 2026)["dai_van"]["cung"] == "Chưa nhập đại vận"


def test_xuat_pdf(client, chart_id):
    response = client.get(f"/api/chart/{chart_id}/pdf")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")


def test_khong_co_key_thi_dung_rule_based(client):
    chart = build_chart(BIRTH)
    assert ai_narrator.generate_narrative(chart, "career", 2026) == analyze_current(chart, 2026)["career"]


def test_co_key_thi_dung_ai_va_cache(monkeypatch):
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        message = SimpleNamespace(content=" Lời luận từ AI. ")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    fake = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(ai_narrator, "_get_client", lambda: fake)
    ai_narrator._cache.clear()
    chart = build_chart(BIRTH)
    assert ai_narrator.generate_narrative(chart, "love", 2026) == "Lời luận từ AI."
    assert ai_narrator.generate_narrative(chart, "love", 2026) == "Lời luận từ AI."
    assert len(calls) == 1
    assert "Nguyễn Văn A" not in str(calls[0]["messages"])


def test_ai_loi_thi_quay_ve_rule_based(monkeypatch):
    def create(**kwargs):
        raise ValueError("lỗi giả")

    fake = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(ai_narrator, "_get_client", lambda: fake)
    ai_narrator._cache.clear()
    chart = build_chart(BIRTH)
    assert ai_narrator.generate_narrative(chart, "wealth", 2026) == analyze_current(chart, 2026)["wealth"]


def test_vi_du_ai_khong_vuot_do_dai():
    for example in ai_narrator.FEW_SHOTS.values():
        assert len(example["assistant"].split()) <= 150

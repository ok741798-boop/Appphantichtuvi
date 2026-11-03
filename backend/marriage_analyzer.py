"""Phân tích cung Phu Thê cho module Duyên Số Định Mệnh.

Người bạn đời được suy từ cung Phu Thê: cung này đóng vai Mệnh của người ấy, các
cung khác của người ấy tính theo khoảng cách như trên lá số gốc (an nghịch).
"""

from typing import Dict, List

from destiny_predictor import (build_future_timeline, build_meeting_timeline, ban_menh_element,
                               describe_family, element_relation, family_match,
                               find_conflict_years, find_palace, palace_stars,
                               predict_child_years, predict_marriage_age, predict_meeting_ages,
                               predict_meeting_circumstance, predict_meeting_place,
                               predict_meeting_time)
from interpreter import cung_at, main_stars, score_palace
from marriage_templates import (CAUTION_DEFAULT, CAUTION_RULES, DEFAULT_PROFILE,
                                ELEMENT_RELATION_SCORE, FATE_BASE, FATE_HOA, FATE_LEVELS, FATE_STARS,
                                FATE_TRIET, FATE_TUAN, MAU_HOP, PARTNER_TERM, PHU_TINH_FEATURE,
                                POSITIVE_DEFAULT, POSITIVE_RULES, SAO_DUONG, STABILITY_LEVELS,
                                STAR_PROFILE)
from stars_data import get_star

# Khoảng cách từ Mệnh đến các cung của người bạn đời, đi nghịch như khi an cung.
OFFSET_HUYNH_DE = 1
OFFSET_PHU_MAU = -1
OFFSET_TAI_BACH = 4
OFFSET_QUAN_LOC = 8

DIEM_GIAU_CO = 8
DIEM_KHA_GIA = 6
HE_SO_THANG_100 = 10
MAX_FEATURES = 3
MAX_CAREERS = 5


def _profile(chart: Dict, palace: Dict) -> Dict:
    """Lấy hồ sơ của chính tinh đầu tiên trong cung, không có thì dùng hồ sơ mặc định."""
    stars = main_stars(chart, palace)
    return STAR_PROFILE[stars[0]] if stars else DEFAULT_PROFILE


def _partner_palace(chart: Dict, phu_the: Dict, offset: int) -> Dict:
    """Lấy một cung của người bạn đời theo khoảng cách từ cung Phu Thê."""
    return cung_at(chart, phu_the["position_index"] - offset)


def analyze_appearance(chart: Dict, phu_the: Dict) -> Dict:
    """Phân tích ngoại hình người bạn đời."""
    profile = _profile(chart, phu_the)
    features = [profile["feature"]]
    features += [text for star, text in PHU_TINH_FEATURE.items() if star in phu_the["phu_tinh"]]
    return {"height": profile["height"], "face": profile["face"], "skin": profile["skin"],
            "style": profile["style"], "features": features[:MAX_FEATURES]}


def analyze_personality(chart: Dict, phu_the: Dict) -> Dict:
    """Phân tích tính cách người bạn đời."""
    traits: List[str] = []
    for star in main_stars(chart, phu_the):
        traits += [trait for trait in STAR_PROFILE[star]["traits"] if trait not in traits]
    traits = traits or list(DEFAULT_PROFILE["traits"])
    love_notes = [get_star(star)["love"] for star in main_stars(chart, phu_the)]
    return {"traits": traits, "summary": ". ".join(note.capitalize() for note in love_notes)
            or "Người ấy coi trọng sự chân thành trong tình cảm"}


def analyze_career(chart: Dict, phu_the: Dict) -> Dict:
    """Phân tích nghề nghiệp từ cung Phu Thê và cung Quan Lộc của người ấy."""
    careers: List[str] = []
    for palace in (phu_the, _partner_palace(chart, phu_the, OFFSET_QUAN_LOC)):
        careers += [c for c in _profile(chart, palace)["careers"] if c not in careers]
    wealth_score = score_palace(chart, _partner_palace(chart, phu_the, OFFSET_TAI_BACH))
    if wealth_score >= DIEM_GIAU_CO:
        income = "Giàu có"
    else:
        income = "Khá giả" if wealth_score >= DIEM_KHA_GIA else "Trung bình"
    return {"groups": careers[:MAX_CAREERS], "income": income}


def analyze_family(chart: Dict, phu_the: Dict) -> Dict:
    """Phân tích hoàn cảnh gia đình người bạn đời."""
    parents = _partner_palace(chart, phu_the, OFFSET_PHU_MAU)
    siblings = _partner_palace(chart, phu_the, OFFSET_HUYNH_DE)
    has_ma = "Thiên Mã" in palace_stars(find_palace(chart, "Thiên Di"))
    return {**describe_family(chart, parents, siblings),
            "hometown": "Có thể ở xa quê bạn" if has_ma else "Quê không quá xa bạn"}


def analyze_your_family(chart: Dict) -> Dict:
    """Mô tả gia đình người xem từ chính cung Phụ Mẫu và Huynh Đệ trên lá số."""
    return describe_family(chart, find_palace(chart, "Phụ Mẫu"), find_palace(chart, "Huynh Đệ"))


def analyze_family_match(chart: Dict, phu_the: Dict) -> Dict:
    """So sánh gia đình người xem với gia đình người bạn đời suy từ cung Phu Thê."""
    return family_match(chart, find_palace(chart, "Phụ Mẫu"), chart,
                        _partner_palace(chart, phu_the, OFFSET_PHU_MAU))


def analyze_age_gap(chart: Dict, phu_the: Dict) -> str:
    """Dự đoán chênh lệch tuổi so với người xem."""
    return str(_profile(chart, phu_the)["gap"])


def calculate_fate_percentage(chart: Dict) -> int:
    """Tính điểm thuận duyên, thang 0-100. Đây là thang quy ước, không phải xác suất."""
    phu_the = find_palace(chart, "Phu Thê")
    score = FATE_BASE + sum(FATE_STARS.get(star, 0) for star in palace_stars(phu_the))
    score += sum(FATE_HOA[item["hoa"]] for item in phu_the["tu_hoa"])
    score += FATE_TUAN if phu_the["tuan"] else 0
    score += FATE_TRIET if phu_the["triet"] else 0
    return max(0, min(100, score))


def _fate_text(score: int) -> Dict:
    """Đổi điểm thuận duyên thành mức đánh giá và lời mô tả."""
    level, note = next((label, text) for floor, label, text in FATE_LEVELS if score >= floor)
    return {"level": level, "text": f"Điểm thuận duyên {score}/100, mức {level}. {note}"}


def calculate_harmony(chart: Dict, fate: int) -> Dict:
    """Tính 4 chỉ số hòa hợp và điểm tổng, thang 0-100."""
    phu_the = find_palace(chart, "Phu Thê")
    personality = round(score_palace(chart, phu_the) * HE_SO_THANG_100)
    menh_stars = main_stars(chart, find_palace(chart, "Mệnh"))
    partner_stars = main_stars(chart, phu_the)
    relation = "bình hòa"
    if menh_stars and partner_stars:
        relation = element_relation(get_star(menh_stars[0])["ngu_hanh"],
                                    get_star(partner_stars[0])["ngu_hanh"])
    ngu_hanh = ELEMENT_RELATION_SCORE[relation]
    goals = round((score_palace(chart, find_palace(chart, "Quan Lộc"))
                   + score_palace(chart, find_palace(chart, "Phúc Đức"))) / 2 * HE_SO_THANG_100)
    return {
        "overall": round((personality + ngu_hanh + goals + fate) / 4),
        "personality": personality,
        "ngu_hanh": ngu_hanh,
        "goals": goals,
        "love": fate,
    }


def analyze_stability(chart: Dict) -> Dict:
    """Đánh giá độ bền của hôn nhân từ điểm cung Phu Thê."""
    phu_the = find_palace(chart, "Phu Thê")
    score = score_palace(chart, phu_the)
    label, text = next((name, note) for floor, name, note in STABILITY_LEVELS if score >= floor)
    if phu_the["tuan"] or phu_the["triet"]:
        text += " Cung này gặp Tuần hoặc Triệt nên giai đoạn đầu có thể nhiều trở ngại."
    return {"level": label, "text": text}


def _matched(rules: List[Dict], stars: List[str]) -> List[str]:
    """Lọc các lời luận có sao khớp; rule có all=True cần đủ mọi sao."""
    results = []
    for rule in rules:
        found = [star in stars for star in rule["stars"]]
        if all(found) if rule.get("all") else any(found):
            results.append(str(rule["text"]))
    return results


def analyze_life(chart: Dict) -> Dict:
    """Dự đoán cuộc sống hôn nhân: điểm tích cực, điểm cần lưu ý, người quyết định."""
    phu_the = find_palace(chart, "Phu Thê")
    stars = palace_stars(phu_the) + main_stars(chart, phu_the)
    positives = _matched(POSITIVE_RULES, stars) or [POSITIVE_DEFAULT]
    cautions = _matched(CAUTION_RULES, stars) or [CAUTION_DEFAULT]
    if score_palace(chart, phu_the) > score_palace(chart, find_palace(chart, "Mệnh")):
        decision = "Người ấy có xu hướng giữ vai trò quyết định nhiều hơn"
    else:
        decision = "Bạn có xu hướng giữ vai trò quyết định nhiều hơn"
    finance_score = score_palace(chart, find_palace(chart, "Tài Bạch"))
    finance = "Tài chính gia đình khá ổn định" if finance_score >= DIEM_KHA_GIA else (
        "Tài chính cần được lập kế hoạch cẩn thận")
    return {"positives": positives, "cautions": cautions, "decision": decision, "finance": finance}


def analyze_children(chart: Dict, marriage_year: int) -> Dict:
    """Dự đoán xu hướng con cái từ cung Tử Tức."""
    tu_tuc = find_palace(chart, "Tử Tức")
    stars = main_stars(chart, tu_tuc)
    count = "2-3 con" if score_palace(chart, tu_tuc) >= DIEM_KHA_GIA else "1-2 con"
    first = "con trai" if stars and stars[0] in SAO_DUONG else "con gái"
    years = predict_child_years(chart, marriage_year)
    return {"count": count, "first": first, "years": years,
            "text": (f"Cung Tử Tức gợi ý khoảng {count}, xu hướng {first} trước. "
                     f"Năm thuận: {', '.join(str(year) for year in years)}.")}


def generate_warnings(chart: Dict, current_year: int) -> List[Dict]:
    """Liệt kê các năm cần lưu ý trong chuyện tình cảm."""
    return [{"year": item["year"],
             "text": f"Năm {item['year']}: {item['reason']}, nên kiên nhẫn và tránh quyết định vội."}
            for item in find_conflict_years(chart, current_year)]


def generate_advice(chart: Dict) -> List[str]:
    """Sinh lời khuyên, gồm màu hợp theo bản mệnh."""
    element = ban_menh_element(chart)
    return [
        f"Bản mệnh hành {element}, có thể chọn tông màu {MAU_HOP[element]} cho những dịp quan trọng.",
        "Chủ động mở rộng các mối quan hệ lành mạnh trong những năm được đánh dấu.",
        "Hiểu rõ giá trị và mục tiêu của mình trước khi quyết định chuyện lâu dài.",
    ]


def analyze_marriage(chart: Dict, current_year: int) -> Dict:
    """Phân tích đầy đủ cho trang Duyên Số Định Mệnh."""
    phu_the = find_palace(chart, "Phu Thê")
    meeting = predict_meeting_time(chart, current_year)
    circumstances = predict_meeting_circumstance(chart)
    marriage = predict_marriage_age(chart, current_year, meeting["year"])
    children = analyze_children(chart, marriage["best_year"])
    fate = calculate_fate_percentage(chart)
    return {
        "partner_term": PARTNER_TERM[chart["info"]["gender"]],
        "palace": {"position": phu_the["position"], "chinh_tinh": phu_the["chinh_tinh"],
                   "phu_tinh": phu_the["phu_tinh"]},
        "partner_appearance": analyze_appearance(chart, phu_the),
        "partner_personality": analyze_personality(chart, phu_the),
        "partner_career": analyze_career(chart, phu_the),
        "partner_family": analyze_family(chart, phu_the),
        "your_family": analyze_your_family(chart),
        "family_match": analyze_family_match(chart, phu_the),
        "age_difference": analyze_age_gap(chart, phu_the),
        "meeting_time": meeting,
        "meeting_ages": predict_meeting_ages(chart, meeting),
        "meeting_place": predict_meeting_place(chart),
        "meeting_circumstance": circumstances,
        "timeline": build_meeting_timeline(chart, current_year, circumstances),
        "marriage_age": marriage,
        "marriage_stability": analyze_stability(chart),
        "marriage_life": analyze_life(chart),
        "children": children,
        "fate_percentage": fate,
        "fate": _fate_text(fate),
        "harmony": calculate_harmony(chart, fate),
        "warnings": generate_warnings(chart, current_year),
        "advice": generate_advice(chart),
        "future_timeline": build_future_timeline(meeting, marriage, children["years"]),
    }

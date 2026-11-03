"""Dự đoán duyên số: thời điểm gặp, hoàn cảnh, tuổi kết hôn và so sánh 2 lá số.

Điểm tình duyên của từng năm là quy ước của ứng dụng để so sánh tương đối giữa
các năm, không phải xác suất một sự kiện sẽ xảy ra.
"""

from typing import Dict, List, Optional

from calendar_utils import CHI, get_can_chi_year, get_hour_chi_index, get_nap_am
from interpreter import age_in_year, cung_at, main_stars, score_palace, year_context
from marriage_templates import (AGE_GAP_RANGE, CIRCUMSTANCE_DEFAULT, CIRCUMSTANCE_RULES,
                                DEFAULT_AGE_GAP, ELEMENT_RELATION_SCORE, HUONG_NGU_HANH,
                                MARRIAGE_AGE_RANGE, MAX_CIRCUMSTANCES, STAR_PROFILE, TEN_THEO_HANH,
                                TIMING_SHIFT)
from stars_data import get_star

# Số năm xét tìm thời điểm gặp, tính cả năm hiện tại.
MEETING_WINDOW = 8
# Timeline gặp gỡ hiển thị năm hiện tại và 5 năm tới.
TIMELINE_YEARS = 6
WARNING_WINDOW = 10
CHILD_WINDOW = 6
MAX_CHILD_YEARS = 2
MIN_GAP_MEET_TO_WED = 1

LOVE_STAR_POINTS = {"Hồng Loan": 3, "Thiên Hỷ": 3, "Đào Hoa": 2, "Tham Lang": 1, "Thái Âm": 1}
DIEM_TIEU_HAN_PHU_THE = 3
DIEM_DAI_VAN_PHU_THE = 2
DIEM_THAI_TUE_PHU_THE = 2
DIEM_LUU_LOC = 1
DIEM_LUU_KY = -2
NGUONG_CAO = 6
NGUONG_TRUNG_BINH = 3

# Trong năm xem hạn, cung tình duyên cách cung tiểu hạn 2 cung theo chiều nghịch.
OFFSET_LOVE_PALACE = 2
# Tam hợp cách nhau 4 Chi, lục xung cách nhau 6 Chi.
CHI_TAM_HOP = 4
CHI_LUC_XUNG = 6
DIEM_TAM_HOP = 15
DIEM_LUC_XUNG = -15

# Người ấy phải đủ 18 tuổi thật khi gặp, tức từ 19 tuổi âm.
MIN_PARTNER_LUNAR_AGE = 19
MAX_AGE_CANDIDATES = 3

# Ngưỡng điểm cung Phụ Mẫu khi mô tả điều kiện gia đình.
DIEM_GIA_DINH_KHA_GIA = 8
DIEM_GIA_DINH_DU_DAY = 6
# Điểm Phụ Mẫu hai bên chênh không quá mức này thì coi là tương xứng.
CHENH_GIA_DINH_TUONG_XUNG = 1.5

NGU_HANH_SINH = {"Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc"}
NGU_HANH_KHAC = {"Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc"}


def find_palace(chart: Dict, name: str) -> Dict:
    """Tìm một cung theo tên."""
    return next(palace for palace in chart["cung"] if palace["name"] == name)


def palace_stars(palace: Dict) -> List[str]:
    """Liệt kê chính tinh và phụ tinh của một cung."""
    return palace["chinh_tinh"] + palace["phu_tinh"]


def ban_menh_element(chart: Dict) -> str:
    """Lấy hành của bản mệnh, là từ cuối trong tên nạp âm."""
    return chart["ban_menh"].split()[-1]


def element_relation(first: str, second: str) -> str:
    """Xác định quan hệ ngũ hành giữa 2 hành."""
    if first == second:
        return "bình hòa"
    if second == NGU_HANH_SINH[first] or first == NGU_HANH_SINH[second]:
        return "tương sinh"
    return "tương khắc"


def love_score(chart: Dict, year: int) -> Dict:
    """Chấm điểm tình duyên một năm và ghi lại các lý do."""
    context = year_context(chart, year)
    phu_the = find_palace(chart, "Phu Thê")
    tieu_han = context["tieu_han"]
    love_palace = cung_at(chart, tieu_han["position_index"] - OFFSET_LOVE_PALACE)
    score = 0
    reasons: List[str] = []

    for star, points in LOVE_STAR_POINTS.items():
        if star in palace_stars(tieu_han):
            score += points
            reasons.append(f"tiểu hạn gặp {star}")
        elif star in palace_stars(love_palace):
            score += 1
            reasons.append(f"cung tình duyên của năm có {star}")
    if tieu_han["name"] == "Phu Thê":
        score += DIEM_TIEU_HAN_PHU_THE
        reasons.append("tiểu hạn vào cung Phu Thê")
    if context["dai_van"] and context["dai_van"]["name"] == "Phu Thê":
        score += DIEM_DAI_VAN_PHU_THE
        reasons.append("đại vận đi qua cung Phu Thê")
    if context["luu_tinh"]["Thái Tuế"] == phu_the["position_index"]:
        score += DIEM_THAI_TUE_PHU_THE
        reasons.append("Thái Tuế chiếu cung Phu Thê")
    if context["luu_hoa"]["Hóa Lộc"] in palace_stars(phu_the):
        score += DIEM_LUU_LOC
        reasons.append("lưu Hóa Lộc vào cung Phu Thê")
    conflict = context["luu_hoa"]["Hóa Kỵ"] in palace_stars(phu_the)
    if conflict:
        score += DIEM_LUU_KY
    return {"year": year, "age": context["age"], "can_chi": context["can_chi"],
            "score": score, "reasons": reasons, "conflict": conflict}


def love_month(chart: Dict, year: int) -> int:
    """Tìm tháng âm lịch nguyệt hạn đi vào cung Phu Thê.

    Dùng phép Đẩu Quân: từ cung Thái Tuế đếm nghịch đến tháng sinh, rồi đếm thuận
    đến giờ sinh để được cung tháng Giêng; các tháng sau đi thuận.
    """
    year_chi = (year - 4) % 12
    hour_chi = get_hour_chi_index(chart["info"]["hour"])
    first_month = year_chi - (chart["chart_month"] - 1) + hour_chi
    return (find_palace(chart, "Phu Thê")["position_index"] - first_month) % 12 + 1


def _probability(score: int) -> str:
    """Đổi điểm tình duyên thành mức khả năng."""
    if score >= NGUONG_CAO:
        return "cao"
    return "trung bình" if score >= NGUONG_TRUNG_BINH else "thấp"


def _best_year(items: List[Dict]) -> Dict:
    """Chọn năm điểm cao nhất, không có Hóa Kỵ thì được ưu tiên, hòa điểm lấy năm sớm hơn."""
    return max(items, key=lambda item: (item["score"], not item["conflict"], -item["year"]))


def predict_meeting_time(chart: Dict, current_year: int) -> Dict:
    """Dự đoán năm thuận duyên nhất để gặp người ấy."""
    years = [love_score(chart, current_year + offset) for offset in range(MEETING_WINDOW)]
    best = _best_year(years)
    month = love_month(chart, best["year"])
    return {
        "year": best["year"],
        "age": best["age"],
        "month": month,
        "probability": _probability(best["score"]),
        "text": (f"Năm thuận duyên nhất trong {MEETING_WINDOW} năm tới là {best['year']} "
                 f"({best['age']} tuổi âm), đặc biệt quanh tháng {month} âm lịch."),
    }


def build_meeting_timeline(chart: Dict, current_year: int, circumstances: List[str]) -> List[Dict]:
    """Dựng timeline gặp gỡ từ năm hiện tại đến 5 năm tới."""
    timeline = []
    for offset in range(TIMELINE_YEARS):
        item = love_score(chart, current_year + offset)
        probability = _probability(item["score"])
        reason = ", ".join(item["reasons"]) or "không có sao tình duyên nổi bật"
        timeline.append({
            "year": item["year"],
            "age": item["age"],
            "can_chi": item["can_chi"],
            "probability": probability,
            "highlight": probability == "cao",
            "text": f"Khả năng gặp gỡ {probability}: {reason}.",
        })
    first_highlight = next((item for item in timeline if item["highlight"]), None)
    if first_highlight:
        first_highlight["text"] += f" Có thể gặp {circumstances[0]}."
    return timeline


def predict_meeting_circumstance(chart: Dict) -> List[str]:
    """Suy ra hoàn cảnh gặp gỡ từ các sao ở Phu Thê, Thiên Di và Quan Lộc."""
    stars = set()
    for name in ("Phu Thê", "Thiên Di", "Quan Lộc"):
        stars.update(palace_stars(find_palace(chart, name)))
    found = [rule["text"] for rule in CIRCUMSTANCE_RULES if stars.intersection(rule["stars"])]
    return found[:MAX_CIRCUMSTANCES] or [CIRCUMSTANCE_DEFAULT]


def predict_meeting_place(chart: Dict) -> Dict:
    """Suy ra địa điểm gặp từ cung Thiên Di."""
    thien_di = find_palace(chart, "Thiên Di")
    stars = main_stars(chart, thien_di)
    element = get_star(stars[0])["ngu_hanh"] if stars else "Thổ"
    direction = HUONG_NGU_HANH[element]
    has_ma = "Thiên Mã" in palace_stars(thien_di) + palace_stars(find_palace(chart, "Phu Thê"))
    if has_ma and score_palace(chart, thien_di) >= 7:
        distance = "Có thể xa quê, thậm chí ở nước ngoài"
    elif has_ma:
        distance = "Người ấy có thể khác quê với bạn"
    else:
        distance = "Người ấy nhiều khả năng ở không quá xa quê bạn"
    return {"direction": direction, "distance": distance,
            "text": f"{distance}, thiên về {direction}."}


def predict_marriage_age(chart: Dict, current_year: int, meeting_year: int) -> Dict:
    """Dự đoán khoảng tuổi và năm đẹp nhất để kết hôn."""
    low, high = MARRIAGE_AGE_RANGE[chart["info"]["gender"]]
    stars = main_stars(chart, find_palace(chart, "Phu Thê"))
    timing = STAR_PROFILE[stars[0]]["timing"] if stars else "vừa"
    if timing == "sớm":
        low, high = low - TIMING_SHIFT, high - TIMING_SHIFT
    elif timing == "muộn":
        low, high = low + TIMING_SHIFT, high + TIMING_SHIFT

    birth_year = chart["lunar"]["lunar_year"]
    first_year = max(birth_year + low - 1, meeting_year + MIN_GAP_MEET_TO_WED)
    last_year = max(birth_year + high - 1, first_year + MIN_GAP_MEET_TO_WED)
    best = _best_year([love_score(chart, year) for year in range(first_year, last_year + 1)])
    first_age, last_age = age_in_year(chart, first_year), age_in_year(chart, last_year)
    return {
        "from_age": first_age,
        "to_age": last_age,
        "best_year": best["year"],
        "best_age": best["age"],
        "timing": timing,
        "text": (f"Khoảng tuổi thuận lợi để kết hôn là {first_age}-{last_age} tuổi âm, "
                 f"năm đẹp nhất là {best['year']} ({best['age']} tuổi âm)."),
    }


def predict_child_years(chart: Dict, marriage_year: int) -> List[int]:
    """Chọn các năm thuận cho chuyện con cái sau năm kết hôn."""
    tu_tuc = find_palace(chart, "Tử Tức")
    scored = []
    for offset in range(1, CHILD_WINDOW + 1):
        context = year_context(chart, marriage_year + offset)
        score = 2 if context["tieu_han"]["name"] == "Tử Tức" else 0
        score += 1 if context["luu_tinh"]["Thái Tuế"] == tu_tuc["position_index"] else 0
        score += 1 if context["luu_hoa"]["Hóa Lộc"] in palace_stars(tu_tuc) else 0
        scored.append((score, context["year"]))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return sorted(year for _, year in scored[:MAX_CHILD_YEARS])


def find_conflict_years(chart: Dict, current_year: int) -> List[Dict]:
    """Tìm các năm dễ có mâu thuẫn tình cảm trong 10 năm tới."""
    phu_the = find_palace(chart, "Phu Thê")
    results = []
    for offset in range(WARNING_WINDOW):
        context = year_context(chart, current_year + offset)
        reasons = []
        if context["luu_hoa"]["Hóa Kỵ"] in palace_stars(phu_the):
            reasons.append("lưu Hóa Kỵ vào cung Phu Thê")
        reasons += [f"{name} chiếu cung Phu Thê" for name in ("Tang Môn", "Bạch Hổ")
                    if context["luu_tinh"][name] == phu_the["position_index"]]
        if reasons:
            results.append({"year": context["year"], "reason": ", ".join(reasons)})
    return results


def build_future_timeline(meeting: Dict, marriage: Dict, child_years: List[int]) -> List[Dict]:
    """Dựng các mốc gặp gỡ, yêu, cưới, sinh con theo đúng thứ tự thời gian."""
    love_year = meeting["year"] if marriage["best_year"] == meeting["year"] + 1 else meeting["year"] + 1
    milestones = [
        {"icon": "✨", "title": "Gặp gỡ", "year": meeting["year"],
         "text": "Năm thuận duyên nhất để gặp người ấy."},
        {"icon": "💞", "title": "Yêu nhau", "year": love_year,
         "text": "Giai đoạn tìm hiểu và gắn bó."},
        {"icon": "💍", "title": "Kết hôn", "year": marriage["best_year"],
         "text": "Năm đẹp nhất trong khoảng tuổi thuận lợi."},
    ]
    if child_years:
        milestones.append({"icon": "👶", "title": "Đón con", "year": child_years[0],
                           "text": "Năm thuận cho chuyện con cái."})
    return milestones


def describe_family(chart: Dict, parents: Dict, siblings: Dict) -> Dict:
    """Mô tả gia đình từ cung Phụ Mẫu và cung Huynh Đệ của một người."""
    score = score_palace(chart, parents)
    if score >= DIEM_GIA_DINH_KHA_GIA:
        wealth = "Gia đình khá giả"
    else:
        wealth = "Gia đình bình dân, đủ đầy" if score >= DIEM_GIA_DINH_DU_DAY else "Gia đình bình dân"
    has_conflict = parents["tuan"] or parents["triet"] or any(
        get_star(star)["rating"] <= 3 for star in parents["phu_tinh"])
    count = len(siblings["chinh_tinh"])
    return {
        "wealth": wealth,
        "siblings": "Ít anh chị em" if count == 0 else f"Khoảng {count + 1}-{count + 2} anh chị em",
        "parents": "Bố mẹ có lúc bất đồng" if has_conflict else "Bố mẹ khá hòa thuận",
    }


def family_match(chart: Dict, parents: Dict, other: Dict, other_parents: Dict) -> Dict:
    """So sánh gia đình hai bên từ cung Phụ Mẫu của mỗi người."""
    stars, other_stars = main_stars(chart, parents), main_stars(other, other_parents)
    relation = "bình hòa"
    if stars and other_stars:
        relation = element_relation(get_star(stars[0])["ngu_hanh"], get_star(other_stars[0])["ngu_hanh"])
    gap = abs(score_palace(chart, parents) - score_palace(other, other_parents))
    level = ("Điều kiện hai bên khá tương xứng" if gap <= CHENH_GIA_DINH_TUONG_XUNG
             else "Điều kiện hai bên có khác biệt")
    notes = {
        "tương sinh": "hai gia đình dễ hòa hợp và ủng hộ nhau",
        "bình hòa": "hai gia đình có thể cư xử êm đẹp khi hiểu nhau hơn",
        "tương khắc": "nếp sống hai bên có thể khác nhau, nên giới thiệu dần và tôn trọng thói quen của nhau",
    }
    return {"relation": relation, "text": f"{level}, {notes[relation]}."}


def _chi_index(chart: Dict) -> int:
    """Lấy chỉ số Địa Chi của năm sinh."""
    return CHI.index(chart["can_chi"]["year"].split()[1])


def _age_candidate(chart: Dict, birth_year: int, meeting_year: int) -> Dict:
    """Đánh giá một năm sinh khả dĩ của người ấy so với lá số người xem."""
    can_index, chi_index = (birth_year - 4) % 10, (birth_year - 4) % 12
    ban_menh = get_nap_am(can_index, chi_index)
    element = ban_menh.split()[-1]
    relation = element_relation(ban_menh_element(chart), element)
    chi_gap = (_chi_index(chart) - chi_index) % 12
    score = ELEMENT_RELATION_SCORE[relation]
    tuoi = "không xung không hợp"
    if chi_gap in (CHI_TAM_HOP, 12 - CHI_TAM_HOP):
        score, tuoi = score + DIEM_TAM_HOP, "tam hợp"
    elif chi_gap == CHI_LUC_XUNG:
        score, tuoi = score + DIEM_LUC_XUNG, "lục xung"
    return {
        "birth_year": birth_year,
        "can_chi": get_can_chi_year(birth_year),
        "zodiac": CHI[chi_index],
        "ban_menh": ban_menh,
        "element": element,
        "age_at_meeting": meeting_year - birth_year + 1,
        "relation": relation,
        "tuoi": tuoi,
        "score": score,
    }


def predict_meeting_ages(chart: Dict, meeting: Dict) -> Dict:
    """Dự đoán tuổi hai người lúc gặp và các năm sinh khả dĩ của người ấy.

    Khoảng chênh tuổi lấy từ chính tinh tại Phu Thê. Trong khoảng đó, năm sinh nào
    tam hợp và có bản mệnh hợp với người xem hơn thì được xếp trước. Tên chỉ là gợi
    ý theo hành, vì lá số không suy ra được tên thật.
    """
    stars = main_stars(chart, find_palace(chart, "Phu Thê"))
    low, high = AGE_GAP_RANGE[stars[0]] if stars else DEFAULT_AGE_GAP
    birth_year = chart["lunar"]["lunar_year"]
    adult = [_age_candidate(chart, birth_year - gap, meeting["year"]) for gap in range(low, high + 1)]
    adult = [item for item in adult if item["age_at_meeting"] >= MIN_PARTNER_LUNAR_AGE]
    # Người xem còn trẻ và khoảng chênh toàn nhỏ tuổi hơn thì lấy bằng tuổi làm mặc định.
    candidates = adult or [_age_candidate(chart, birth_year, meeting["year"])]
    ranked = sorted(candidates, key=lambda item: (-item["score"], abs(item["birth_year"] - birth_year)))
    best = ranked[0]
    ages = [item["age_at_meeting"] for item in candidates]
    partner_gender = "Nữ" if chart["info"]["gender"] == "Nam" else "Nam"
    gap = best["age_at_meeting"] - meeting["age"]
    gap_text = f"lớn hơn bạn {gap} tuổi" if gap > 0 else (
        f"nhỏ hơn bạn {-gap} tuổi" if gap < 0 else "bằng tuổi bạn")
    return {
        "meeting_year": meeting["year"],
        "you_age": meeting["age"],
        "partner_age_from": min(ages),
        "partner_age_to": max(ages),
        "partner_age": best["age_at_meeting"],
        "gap_text": gap_text,
        "candidates": ranked[:MAX_AGE_CANDIDATES],
        "name_element": best["element"],
        "name_hints": TEN_THEO_HANH[partner_gender][best["element"]],
        "text": (f"Năm {meeting['year']}, bạn {meeting['age']} tuổi âm, người ấy khoảng "
                 f"{min(ages)}-{max(ages)} tuổi âm. Hợp nhất là {best['age_at_meeting']} tuổi âm, "
                 f"sinh năm {best['birth_year']} ({best['can_chi']}), {gap_text}."),
    }


def _first_element(chart: Dict, palace_name: str) -> Optional[str]:
    """Lấy hành của chính tinh đầu tiên tại một cung."""
    stars = main_stars(chart, find_palace(chart, palace_name))
    return get_star(stars[0])["ngu_hanh"] if stars else None


def _relation_score(first: Optional[str], second: Optional[str]) -> int:
    """Đổi quan hệ 2 hành thành điểm; thiếu dữ liệu thì tính là bình hòa."""
    if not first or not second:
        return ELEMENT_RELATION_SCORE["bình hòa"]
    return ELEMENT_RELATION_SCORE[element_relation(first, second)]


def compare_charts(chart: Dict, other: Dict) -> Dict:
    """So sánh 2 lá số, trả về điểm hòa hợp, bảng so sánh, cảnh báo và lời khuyên."""
    element, other_element = ban_menh_element(chart), ban_menh_element(other)
    relation = element_relation(element, other_element)
    ngu_hanh = ELEMENT_RELATION_SCORE[relation]

    stars_menh = set(main_stars(chart, find_palace(chart, "Mệnh")))
    other_menh = set(main_stars(other, find_palace(other, "Mệnh")))
    wanted = set(main_stars(chart, find_palace(chart, "Phu Thê")))
    other_wanted = set(main_stars(other, find_palace(other, "Phu Thê")))
    matches_partner = bool(wanted & other_menh) or bool(other_wanted & stars_menh)
    personality = _relation_score(_first_element(chart, "Mệnh"), _first_element(other, "Mệnh"))
    personality = min(100, personality + (12 if matches_partner else 0))

    goals = _relation_score(_first_element(chart, "Quan Lộc"), _first_element(other, "Quan Lộc"))

    chi_gap = (_chi_index(chart) - _chi_index(other)) % 12
    tuoi_text = "Hai tuổi không xung không hợp"
    tuoi_bonus = 0
    if chi_gap in (CHI_TAM_HOP, 12 - CHI_TAM_HOP):
        tuoi_text, tuoi_bonus = "Hai tuổi tam hợp, dễ đồng lòng", DIEM_TAM_HOP
    elif chi_gap == CHI_LUC_XUNG:
        tuoi_text, tuoi_bonus = "Hai tuổi lục xung, dễ khác quan điểm", DIEM_LUC_XUNG

    average = (ngu_hanh + personality + goals) / 3
    overall = max(0, min(100, round(average + tuoi_bonus / 2)))

    warnings = []
    if relation == "tương khắc":
        warnings.append(f"Bản mệnh {element} và {other_element} tương khắc, hai người dễ khác nhịp "
                        "sống và cách xử lý vấn đề.")
    if chi_gap == CHI_LUC_XUNG:
        warnings.append("Hai tuổi lục xung, nên tránh đối đầu khi chưa bình tĩnh.")
    if goals < ELEMENT_RELATION_SCORE["bình hòa"]:
        warnings.append("Định hướng công việc có thể khác nhau, nên bàn trước các mục tiêu lớn.")
    if not warnings:
        warnings.append("Chưa thấy xung đột lớn trên lá số, vẫn nên chú ý những khác biệt nhỏ hằng ngày.")

    advice = ["Dành thời gian trò chuyện về tiền bạc, gia đình và kế hoạch dài hạn."]
    if personality < ELEMENT_RELATION_SCORE["tương sinh"]:
        advice.append("Tôn trọng cách làm của nhau thay vì cố thay đổi đối phương.")
    if ngu_hanh >= ELEMENT_RELATION_SCORE["tương sinh"]:
        advice.append("Tận dụng điểm tương sinh: làm chung một việc nhỏ để thêm gắn kết.")

    parents, other_parents = find_palace(chart, "Phụ Mẫu"), find_palace(other, "Phụ Mẫu")
    family = describe_family(chart, parents, find_palace(chart, "Huynh Đệ"))
    other_family = describe_family(other, other_parents, find_palace(other, "Huynh Đệ"))

    return {
        "partner_name": other["info"]["full_name"],
        "overall": overall,
        "scores": {"ngu_hanh": ngu_hanh, "personality": personality, "goals": goals},
        "rows": [
            {"label": "Bản mệnh", "you": chart["ban_menh"], "partner": other["ban_menh"]},
            {"label": "Năm sinh", "you": chart["can_chi"]["year"], "partner": other["can_chi"]["year"]},
            {"label": "Chính tinh Mệnh", "you": ", ".join(sorted(stars_menh)),
             "partner": ", ".join(sorted(other_menh))},
            {"label": "Gia đình", "you": family["wealth"], "partner": other_family["wealth"]},
            {"label": "Bố mẹ", "you": family["parents"], "partner": other_family["parents"]},
            {"label": "Anh chị em", "you": family["siblings"], "partner": other_family["siblings"]},
        ],
        "family_text": family_match(chart, parents, other, other_parents)["text"],
        "ngu_hanh_text": f"Bản mệnh {element} và {other_element}: {relation}.",
        "tuoi_text": tuoi_text + ".",
        "warnings": warnings,
        "advice": advice,
    }

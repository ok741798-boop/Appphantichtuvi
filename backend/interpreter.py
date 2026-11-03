"""Luận giải rule-based: chấm điểm cung, xác định đại vận, tiểu hạn, lưu niên.

Thang điểm là quy ước của ứng dụng để so sánh tương đối giữa các năm, không
phải kết luận chắc chắn về tương lai. Điểm chưa xét độ miếu, vượng, hãm của sao.
"""

from typing import Dict, List, Optional

from calendar_utils import CAN, CHI, get_can_chi_year
from chart_builder import tieu_han_position
from stars_data import DIEM_TU_HOA, LUU_TINH, TEN_TU_HOA, TU_HOA, TU_HOA_INFO, get_star

ASPECTS = ["career", "wealth", "love", "health"]

# Trong năm xem hạn, cung tiểu hạn đóng vai Mệnh của năm đó. Các cung còn lại
# của năm suy từ nó theo khoảng cách như trên lá số gốc (an nghịch).
ASPECT_OFFSET = {"career": 8, "wealth": 4, "love": 2, "health": 5}
ASPECT_CUNG = {"career": "Quan Lộc", "wealth": "Tài Bạch", "love": "Phu Thê", "health": "Tật Ách"}
ASPECT_TITLE = {"career": "sự nghiệp", "wealth": "tài lộc", "love": "tình cảm", "health": "sức khỏe"}

# Độ dài mỗi đoạn luận khía cạnh, tính theo số từ cách nhau bởi khoảng trắng.
MIN_ASPECT_WORDS = 100
MAX_ASPECT_WORDS = 120
# Câu ngắn để lấp phần thiếu khi các câu chung đều quá dài so với chỗ còn lại.
CAU_DEM = "Hãy xem đây là gợi ý để cân nhắc thêm."

# Điều chỉnh điểm cho các yếu tố đặc biệt trong một cung
DIEM_TUAN = -0.4
DIEM_TRIET = -0.6
DIEM_VO_CHINH_DIEU = -0.5
# Mức ảnh hưởng của 1 phụ tinh so với chính tinh
HE_SO_PHU_TINH = 0.2
# Trọng số của 3 tầng vận hạn khi chấm điểm một năm
TRONG_SO_DAI_VAN = 0.35
TRONG_SO_TIEU_HAN = 0.40
TRONG_SO_THAI_TUE = 0.25
DIEM_LUU_HUNG = -0.7
DIEM_LUU_HOA = 0.6
# Điểm thô của một năm tập trung quanh 6.8 trong dải hẹp; giãn ra để các năm khác
# nhau rõ rệt hơn, nếu không gần như không năm nào rơi vào mức "cần thận trọng".
TAM_DIEM_NAM = 6.8
DIEM_NAM_TRUNG_BINH = 5.5
HE_SO_GIAN_DIEM_NAM = 1.8

TONE = [
    (7.5, "rất thuận lợi", "Đây là lúc nên chủ động nắm bắt cơ hội và mở rộng kế hoạch."),
    (6.0, "khá thuận lợi", "Cứ giữ nhịp đều đặn, kết quả sẽ đến từ sự kiên trì."),
    (4.5, "có thuận có nghịch", "Nên ưu tiên việc chắc chắn và chuẩn bị phương án dự phòng."),
    (0.0, "cần thận trọng", "Nên đi chậm, củng cố nền tảng và tham khảo người có kinh nghiệm."),
]


# Lời khuyên riêng của từng khía cạnh, theo đúng thứ tự 4 mức trong TONE.
ASPECT_ADVICE = {
    "career": [
        "Đây là thời điểm phù hợp để nhận thêm trách nhiệm, đề xuất ý tưởng mới hoặc khởi động dự án đã ấp ủ từ lâu.",
        "Hãy tập trung nâng cao chuyên môn và hoàn thành tốt việc đang làm, vì sự ghi nhận thường đến từ kết quả thực tế.",
        "Nên chia nhỏ mục tiêu, làm rõ vai trò với đồng nghiệp và giữ lại phương án dự phòng trước khi thay đổi lớn.",
        "Chưa nên vội đổi việc hay mở rộng; hãy ưu tiên ổn định, ghi chép đầy đủ và hỏi ý kiến người có kinh nghiệm.",
    ],
    "wealth": [
        "Có thể cân nhắc mở rộng nguồn thu, nhưng vẫn nên đặt giới hạn rủi ro rõ ràng cho từng khoản đầu tư.",
        "Hãy duy trì thói quen tích lũy đều đặn và theo dõi chi tiêu hằng tháng để giữ vững thành quả đã có.",
        "Nên giữ một khoản dự phòng, đọc kỹ giấy tờ và tránh quyết định tài chính lớn khi chưa đủ thông tin.",
        "Nên ưu tiên giữ tiền, hạn chế vay mượn hay cho vay lớn và tránh những lời mời hứa hẹn lợi nhuận nhanh.",
    ],
    "love": [
        "Đây là lúc tốt để mở lòng, chủ động gặp gỡ hoặc cùng người thương bàn những kế hoạch lâu dài.",
        "Hãy dành thời gian chất lượng cho nhau, lắng nghe nhiều hơn và vun đắp những thói quen nhỏ mỗi tuần.",
        "Khi có khác biệt, nên trao đổi thẳng thắn nhưng nhẹ nhàng, tránh để những khúc mắc nhỏ tích tụ lâu ngày.",
        "Nên kiên nhẫn, tránh nói lời nóng giận hay quyết định vội, và cho nhau không gian khi cần bình tĩnh lại.",
    ],
    "health": [
        "Hãy tận dụng giai đoạn này để xây dựng thói quen vận động đều đặn và chế độ ăn uống cân bằng.",
        "Nên giữ nếp ngủ đủ giấc, vận động vừa sức và dành thời gian thư giãn sau những ngày làm việc căng thẳng.",
        "Nên giảm bớt làm việc quá sức, ăn uống đúng bữa và để ý những thay đổi nhỏ của cơ thể.",
        "Nên ưu tiên nghỉ ngơi, sắp xếp lịch khám sức khỏe định kỳ và hỏi bác sĩ sớm khi thấy điều bất thường.",
    ],
}

# Câu chung, chỉ dùng khi lá số có ít sao khiến đoạn luận chưa đủ độ dài.
ASPECT_GENERAL = {
    "career": [
        "Trong công việc, mức độ thuận lợi còn phụ thuộc nhiều vào sự chuẩn bị, kỹ năng và các mối quan hệ bạn đã xây dựng từ trước.",
        "Vì vậy, hãy xem đây là xu hướng để lập kế hoạch, thay vì là kết luận chắc chắn về kết quả.",
    ],
    "wealth": [
        "Về tiền bạc, kết quả thực tế còn phụ thuộc vào thói quen chi tiêu, kế hoạch tích lũy và cách bạn quản lý rủi ro.",
        "Vì vậy, hãy xem đây là gợi ý để sắp xếp tài chính, thay vì là lời khẳng định về thu nhập.",
    ],
    "love": [
        "Trong chuyện tình cảm, sự chân thành, lắng nghe và tôn trọng lẫn nhau luôn quan trọng hơn bất kỳ dấu hiệu nào trên lá số.",
        "Vì vậy, hãy xem đây là gợi ý để hiểu mình và hiểu người, thay vì là lời phán về duyên phận.",
    ],
    "health": [
        "Về sức khỏe, thói quen ngủ nghỉ, ăn uống và vận động hằng ngày có tác động rõ ràng hơn nhiều so với vận hạn.",
        "Vì vậy, hãy xem đây là lời nhắc chăm sóc bản thân, thay vì là dự báo về thể trạng.",
    ],
}


def _tone(score: float) -> Dict[str, object]:
    """Đổi điểm số thành mức đánh giá, lời khuyên và số thứ tự của mức."""
    for level, (threshold, label, advice) in enumerate(TONE):
        if score >= threshold:
            return {"level": level, "label": label, "advice": advice}
    return {"level": len(TONE) - 1, "label": TONE[-1][1], "advice": TONE[-1][2]}


def cung_at(chart: Dict, position: int) -> Dict:
    """Lấy cung tại một vị trí Địa Chi (Tý=0, ..., Hợi=11)."""
    return next(c for c in chart["cung"] if c["position_index"] == position % 12)


def main_stars(chart: Dict, palace: Dict) -> List[str]:
    """Lấy chính tinh của cung; cung vô chính diệu mượn sao ở cung đối diện."""
    return palace["chinh_tinh"] or cung_at(chart, palace["position_index"] + 6)["chinh_tinh"]


def score_palace(chart: Dict, palace: Dict) -> float:
    """Chấm điểm một cung, từ 1 đến 10.

    Lấy trung bình rating chính tinh, rồi cộng thêm ảnh hưởng của phụ tinh, Tứ
    Hóa, Tuần, Triệt. Cung vô chính diệu bị trừ nhẹ vì phải mượn sao đối cung.
    """
    stars = main_stars(chart, palace)
    score = sum(get_star(s)["rating"] for s in stars) / len(stars)
    if not palace["chinh_tinh"]:
        score += DIEM_VO_CHINH_DIEU
    score += sum((get_star(s)["rating"] - 5) * HE_SO_PHU_TINH for s in palace["phu_tinh"])
    score += sum(DIEM_TU_HOA[h["hoa"]] for h in palace["tu_hoa"])
    score += DIEM_TUAN if palace["tuan"] else 0
    score += DIEM_TRIET if palace["triet"] else 0
    return round(max(1.0, min(10.0, score)), 1)


def analyze_sao(chart: Dict, cung_data: Dict) -> Dict:
    """Luận giải một cung dựa trên các sao trong cung.

    Returns:
        Dict gồm score, label (mức đánh giá) và text (mô tả ngắn).
    """
    score = score_palace(chart, cung_data)
    tone = _tone(score)
    stars = main_stars(chart, cung_data)
    verb = "có" if cung_data["chinh_tinh"] else "vô chính diệu, mượn"
    text = (f"Cung {cung_data['name']} tại {cung_data['position']} {verb} "
            f"{', '.join(stars)}: {tone['label']}.")
    return {"score": score, "label": tone["label"], "text": text}


def age_in_year(chart: Dict, year: int) -> int:
    """Tính tuổi âm (tuổi mụ) trong một năm."""
    return max(1, year - chart["lunar"]["lunar_year"] + 1)


def find_dai_van(chart: Dict, age: int) -> Optional[Dict]:
    """Tìm đại vận chứa một tuổi; trả về None nếu chưa tới đại vận đầu tiên.

    Mỗi đại vận kéo dài 10 năm và lặp lại sau 120 tuổi.
    """
    first = chart["cuc"]["number"]
    if age < first:
        return None
    start = first + (age - first) % 120 // 10 * 10
    return next(c for c in chart["cung"] if c["dai_van_start"] == start)


def year_context(chart: Dict, year: int) -> Dict:
    """Gom các yếu tố vận hạn của một năm: đại vận, tiểu hạn, lưu niên."""
    age = age_in_year(chart, year)
    year_can = CAN[(year - 4) % 10]
    year_chi = (year - 4) % 12
    tieu_han = cung_at(chart, tieu_han_position(chart, age))
    return {
        "year": year,
        "can_chi": get_can_chi_year(year),
        "age": age,
        "dai_van": find_dai_van(chart, age),
        "tieu_han": tieu_han,
        # Thái Tuế đứng tại Chi của năm; Tang Môn cách +2, Bạch Hổ cách +8.
        "luu_tinh": {"Thái Tuế": year_chi, "Tang Môn": (year_chi + 2) % 12,
                     "Bạch Hổ": (year_chi + 8) % 12},
        "luu_hoa": dict(zip(TEN_TU_HOA, TU_HOA[year_can])),
    }


def _luu_tinh_at_tieu_han(context: Dict) -> List[str]:
    """Liệt kê các lưu tinh rơi đúng vào cung tiểu hạn."""
    position = context["tieu_han"]["position_index"]
    return [name for name, p in context["luu_tinh"].items() if p == position]


def _luu_hoa_at_tieu_han(context: Dict) -> Dict[str, str]:
    """Liệt kê lưu Tứ Hóa của năm rơi vào cung tiểu hạn, dạng {tên hóa: sao}."""
    palace = context["tieu_han"]
    stars = palace["chinh_tinh"] + palace["phu_tinh"]
    return {hoa: star for hoa, star in context["luu_hoa"].items() if star in stars}


def evaluate_context(chart: Dict, context: Dict) -> float:
    """Chấm điểm một năm từ các yếu tố vận hạn đã gom sẵn."""
    menh = cung_at(chart, chart["cung"][0]["position_index"])
    dai_van = context["dai_van"] or menh
    score = (
        TRONG_SO_DAI_VAN * score_palace(chart, dai_van)
        + TRONG_SO_TIEU_HAN * score_palace(chart, context["tieu_han"])
        + TRONG_SO_THAI_TUE * score_palace(chart, cung_at(chart, context["luu_tinh"]["Thái Tuế"]))
    )
    for name in _luu_tinh_at_tieu_han(context):
        if name != "Thái Tuế":
            score += DIEM_LUU_HUNG
    for hoa in _luu_hoa_at_tieu_han(context):
        if hoa == "Hóa Lộc":
            score += DIEM_LUU_HOA
        elif hoa == "Hóa Kỵ":
            score -= DIEM_LUU_HOA
    score = DIEM_NAM_TRUNG_BINH + (score - TAM_DIEM_NAM) * HE_SO_GIAN_DIEM_NAM
    return round(max(1.0, min(10.0, score)), 1)


def evaluate_year(chart: Dict, year: int) -> float:
    """Chấm điểm vận hạn của một năm, thang 1-10."""
    return evaluate_context(chart, year_context(chart, year))


def _aspect_palace(chart: Dict, context: Dict, aspect: str) -> Dict:
    """Tìm cung phụ trách một khía cạnh trong năm xem hạn."""
    return cung_at(chart, context["tieu_han"]["position_index"] - ASPECT_OFFSET[aspect])


def aspect_text(chart: Dict, context: Dict, aspect: str) -> str:
    """Sinh đoạn luận giải một khía cạnh của năm."""
    palace = _aspect_palace(chart, context, aspect)
    score = score_palace(chart, palace)
    tone = _tone(score)
    opening = (f"Về {ASPECT_TITLE[aspect]}, năm {context['year']} ({context['can_chi']}) lưu "
               f"{ASPECT_CUNG[aspect]} đóng tại cung {palace['position']}, tức cung "
               f"{palace['name']} trên lá số gốc, xu hướng chung {tone['label']} "
               f"({score}/10).")
    closing = [ASPECT_ADVICE[aspect][tone["level"]]]
    if aspect == "health":
        closing.append("Nội dung này không thay thế tư vấn y tế.")
    return _fit_length([opening], _aspect_details(chart, context, palace, aspect), closing,
                       ASPECT_GENERAL[aspect] + [CAU_DEM])


def _aspect_details(chart: Dict, context: Dict, palace: Dict, aspect: str) -> List[str]:
    """Liệt kê các câu chi tiết của một khía cạnh, câu quan trọng đứng trước."""
    details = [f"Sao {name} cho thấy: {get_star(name)[aspect]}."
               for name in main_stars(chart, palace)[:2]]
    if not palace["chinh_tinh"]:
        details.append("Cung này vô chính diệu nên mượn sao ở cung đối diện, ảnh hưởng thường "
                       "không ổn định bằng cung có chính tinh.")
    details += [f"{item['star']} mang {item['hoa']}: {TU_HOA_INFO[item['hoa']]}"
                for item in palace["tu_hoa"]]
    by_strength = sorted(palace["phu_tinh"], key=lambda s: get_star(s)["rating"], reverse=True)
    details += [f"Điểm cần lưu ý là {name}: {get_star(name)[aspect]}."
                for name in reversed(by_strength) if get_star(name)["rating"] < 5][:2]
    details += [f"Trợ lực đến từ {name}: {get_star(name)[aspect]}."
                for name in by_strength if get_star(name)["rating"] > 5][:2]
    if palace["triet"]:
        details.append("Cung này gặp Triệt nên việc dễ bị cản ở bước đầu, cần kiên nhẫn hơn dự tính.")
    if palace["tuan"]:
        details.append("Cung này gặp Tuần nên ảnh hưởng của các sao giảm bớt, kết quả có thể đến chậm.")
    dai_van = context["dai_van"]
    if dai_van:
        details.append(f"Nền chung của giai đoạn này là đại vận tại cung {dai_van['name']} "
                       f"({score_palace(chart, dai_van)}/10).")
    return details


def _fit_length(opening: List[str], details: List[str], closing: List[str],
                fillers: List[str]) -> str:
    """Ghép đoạn luận sao cho số từ nằm trong khoảng MIN_ASPECT_WORDS-MAX_ASPECT_WORDS.

    Câu chi tiết nào làm đoạn văn vượt mức tối đa thì bỏ qua; nếu sau đó vẫn
    thiếu từ thì thêm các câu chung trong fillers.
    """
    def word_count(sentences: List[str]) -> int:
        """Đếm số từ của một danh sách câu."""
        return len(" ".join(sentences).split())

    body: List[str] = []
    for sentence in details:
        if word_count(opening + body + [sentence] + closing) <= MAX_ASPECT_WORDS:
            body.append(sentence)
    for sentence in fillers:
        current = opening + body + closing
        fits = word_count(current + [sentence]) <= MAX_ASPECT_WORDS
        if word_count(current) < MIN_ASPECT_WORDS and fits:
            body.append(sentence)
    return " ".join(opening + body + closing)


def summary_text(chart: Dict, context: Dict, score: float) -> str:
    """Sinh đoạn tổng quan của năm."""
    tieu_han = context["tieu_han"]
    dai_van = context["dai_van"]
    tone = _tone(score)
    dai_van_text = (f"đại vận tại cung {dai_van['name']} ({dai_van['dai_van_age']} tuổi)"
                    if dai_van else "chưa bước vào đại vận đầu tiên")
    text = (f"Năm {context['year']} ({context['can_chi']}), {context['age']} tuổi âm, "
            f"{dai_van_text}, tiểu hạn tại cung {tieu_han['name']} ({tieu_han['position']}). "
            f"Tổng thể {tone['label']}. {tone['advice']}")
    for name in _luu_tinh_at_tieu_han(context):
        text += f" Tiểu hạn gặp {name}: {LUU_TINH[name]}"
    for hoa, star in _luu_hoa_at_tieu_han(context).items():
        text += f" Lưu {hoa} tại {star}."
    return text


def analyze_year(chart: Dict, year: int) -> Dict:
    """Luận giải đầy đủ một năm, dùng chung cho tab Hiện tại và tab Tương lai."""
    context = year_context(chart, year)
    score = evaluate_context(chart, context)
    result = {
        "year": year,
        "can_chi": context["can_chi"],
        "age": context["age"],
        "rating": score,
        "summary": summary_text(chart, context, score),
        "tieu_han": context["tieu_han"]["name"],
        "tone": _tone(score)["label"],
        "aspect_ratings": _aspect_ratings(chart, context),
    }
    for aspect in ASPECTS:
        result[aspect] = aspect_text(chart, context, aspect)
    return result


def _aspect_ratings(chart: Dict, context: Dict) -> Dict[str, float]:
    """Chấm điểm 4 khía cạnh của một năm, thang 1-10."""
    return {aspect: score_palace(chart, _aspect_palace(chart, context, aspect))
            for aspect in ASPECTS}


def analyze_current(chart: Dict, current_year: int) -> Dict:
    """Phân tích vận hạn của năm hiện tại."""
    context = year_context(chart, current_year)
    result = analyze_year(chart, current_year)
    dai_van = context["dai_van"]
    tieu_han = context["tieu_han"]
    return {
        "year": current_year,
        "can_chi": context["can_chi"],
        "age": context["age"],
        "dai_van": {
            "cung": dai_van["name"] if dai_van else "Chưa nhập đại vận",
            "position": dai_van["position"] if dai_van else "",
            "age_range": dai_van["dai_van_age"] if dai_van else f"1-{chart['cuc']['number'] - 1}",
            "rating": score_palace(chart, dai_van) if dai_van else None,
        },
        "tieu_han": {
            "cung": tieu_han["name"],
            "position": tieu_han["position"],
            "rating": score_palace(chart, tieu_han),
        },
        "luu_nien": {
            name: CHI[position] for name, position in context["luu_tinh"].items()
        },
        "aspect_ratings": result["aspect_ratings"],
        "overall_rating": result["rating"],
        "summary": result["summary"],
        **{aspect: result[aspect] for aspect in ASPECTS},
    }

"""Lập lá số tử vi: an 12 cung, 14 chính tinh, phụ tinh, Tứ Hóa, Tuần, Triệt.

Quy ước vị trí: mỗi cung là một số từ 0 đến 11 theo Địa Chi (Tý=0, Sửu=1, ...,
Hợi=11). "Thuận" là tiến theo chiều tăng của Địa Chi, "nghịch" là lùi lại.

Thứ tự an sao:
    1. Cung Mệnh: từ Dần đếm thuận theo tháng sinh, rồi đếm nghịch theo giờ sinh.
       Cung Thân: cũng từ tháng sinh nhưng đếm thuận theo giờ sinh.
    2. Cục: lấy Can của cung Mệnh (Ngũ Hổ Độn) ghép với Chi của cung Mệnh, tra
       nạp âm rồi đổi ra Thủy Nhị, Mộc Tam, Kim Tứ, Thổ Ngũ, Hỏa Lục.
    3. Tử Vi: tìm theo ngày sinh âm lịch và số Cục.
    4. Từ Tử Vi suy ra 5 sao còn lại của chòm Tử Vi và Thiên Phủ; từ Thiên Phủ
       suy ra 7 sao còn lại của chòm Thiên Phủ.
    5. Phụ tinh: theo tháng, giờ, Can năm, Chi năm.
    6. Tứ Hóa: theo Can năm.
    7. Tuần, Triệt: theo Can Chi năm.
"""

import sys
import uuid
from typing import Dict, List, Optional, Tuple

from calendar_utils import CAN, CHI, HOUR_LABELS, get_full_can_chi, get_hour_chi_index, get_nap_am
from stars_data import TEN_TU_HOA, TU_HOA, TU_HOA_INFO, get_star

TY, SUU, DAN, MAO, THIN, TI, NGO, MUI, THAN, DAU, TUAT, HOI = range(12)

# 12 cung theo thứ tự an nghịch từ cung Mệnh.
CUNG_NAMES = [
    "Mệnh", "Huynh Đệ", "Phu Thê", "Tử Tức", "Tài Bạch", "Tật Ách",
    "Thiên Di", "Nô Bộc", "Quan Lộc", "Điền Trạch", "Phúc Đức", "Phụ Mẫu",
]

CUC_BY_ELEMENT = {
    "Thủy": (2, "Thủy Nhị Cục"),
    "Mộc": (3, "Mộc Tam Cục"),
    "Kim": (4, "Kim Tứ Cục"),
    "Thổ": (5, "Thổ Ngũ Cục"),
    "Hỏa": (6, "Hỏa Lục Cục"),
}

# Khoảng cách tới Tử Vi của chòm Tử Vi (đều đếm nghịch).
CHOM_TU_VI = {"Tử Vi": 0, "Thiên Cơ": -1, "Thái Dương": -3, "Vũ Khúc": -4,
              "Thiên Đồng": -5, "Liêm Trinh": -8}
# Khoảng cách tới Thiên Phủ của chòm Thiên Phủ (đều đếm thuận).
CHOM_THIEN_PHU = {"Thiên Phủ": 0, "Thái Âm": 1, "Tham Lang": 2, "Cự Môn": 3,
                  "Thiên Tướng": 4, "Thiên Lương": 5, "Thất Sát": 6, "Phá Quân": 10}

LOC_TON = {"Giáp": DAN, "Ất": MAO, "Bính": TI, "Đinh": NGO, "Mậu": TI,
           "Kỷ": NGO, "Canh": THAN, "Tân": DAU, "Nhâm": HOI, "Quý": TY}
KHOI_VIET = {"Giáp": (SUU, MUI), "Mậu": (SUU, MUI), "Ất": (TY, THAN), "Kỷ": (TY, THAN),
             "Bính": (HOI, DAU), "Đinh": (HOI, DAU), "Canh": (NGO, DAN), "Tân": (NGO, DAN),
             "Nhâm": (MAO, TI), "Quý": (MAO, TI)}
TRIET = {"Giáp": (THAN, DAU), "Kỷ": (THAN, DAU), "Ất": (NGO, MUI), "Canh": (NGO, MUI),
         "Bính": (THIN, TI), "Tân": (THIN, TI), "Đinh": (DAN, MAO), "Nhâm": (DAN, MAO),
         "Mậu": (TY, SUU), "Quý": (TY, SUU)}

# Các sao an theo nhóm tam hợp của Chi năm sinh, tra bằng CHI_NHOM.
CHI_NHOM = {TY: 0, THIN: 0, THAN: 0, DAN: 1, NGO: 1, TUAT: 1,
            TI: 2, DAU: 2, SUU: 2, HOI: 3, MAO: 3, MUI: 3}
THIEN_MA = [DAN, THAN, HOI, TI]
DAO_HOA = [DAU, MAO, NGO, TY]
# Nhóm năm -> cung khởi của Hỏa Tinh và Linh Tinh.
HOA_LINH_KHOI = [(DAN, TUAT), (SUU, MAO), (MAO, TUAT), (DAU, TUAT)]
# Nhóm năm -> cung khởi tiểu hạn ở tuổi 1.
TIEU_HAN_KHOI = [TUAT, THIN, MUI, SUU]

TRANG_SINH = ["Tràng Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng", "Suy",
              "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"]
TRANG_SINH_KHOI = {"Thủy": THAN, "Thổ": THAN, "Mộc": HOI, "Kim": TI, "Hỏa": DAN}

MENH_CHU = {TY: "Tham Lang", SUU: "Cự Môn", DAN: "Lộc Tồn", MAO: "Văn Khúc", THIN: "Liêm Trinh",
            TI: "Vũ Khúc", NGO: "Phá Quân", MUI: "Vũ Khúc", THAN: "Liêm Trinh",
            DAU: "Văn Khúc", TUAT: "Lộc Tồn", HOI: "Cự Môn"}
THAN_CHU = {TY: "Hỏa Tinh", SUU: "Thiên Tướng", DAN: "Thiên Lương", MAO: "Thiên Đồng",
            THIN: "Văn Xương", TI: "Thiên Cơ", NGO: "Hỏa Tinh", MUI: "Thiên Tướng",
            THAN: "Thiên Lương", DAU: "Thiên Đồng", TUAT: "Văn Xương", HOI: "Thiên Cơ"}


def find_menh(lunar_month: int, hour_chi: int) -> int:
    """An cung Mệnh: từ Dần thuận theo tháng sinh, rồi nghịch theo giờ sinh."""
    return (DAN + lunar_month - 1 - hour_chi) % 12


def find_than(lunar_month: int, hour_chi: int) -> int:
    """An cung Thân: từ Dần thuận theo tháng sinh, rồi thuận theo giờ sinh."""
    return (DAN + lunar_month - 1 + hour_chi) % 12


def palace_can(year_can: int, position: int) -> int:
    """Tìm Can của một cung theo Ngũ Hổ Độn.

    Năm Giáp/Kỷ có cung Dần là Bính Dần, Ất/Canh là Mậu Dần, Bính/Tân là Canh
    Dần, Đinh/Nhâm là Nhâm Dần, Mậu/Quý là Giáp Dần. Từ Dần đếm thuận tới Sửu.
    """
    can_dan = (year_can * 2 + 2) % 10
    return (can_dan + (position - DAN) % 12) % 10


def find_cuc(year_can: int, menh: int) -> Tuple[int, str, str]:
    """Xác định Cục từ nạp âm của cung Mệnh.

    Returns:
        (số Cục, tên Cục, hành của Cục).
    """
    element = get_nap_am(palace_can(year_can, menh), menh).split()[-1]
    number, name = CUC_BY_ELEMENT[element]
    return number, name, element


def find_tu_vi(lunar_day: int, cuc: int) -> int:
    """An sao Tử Vi theo ngày sinh âm lịch và số Cục.

    Tìm số x nhỏ nhất để (ngày + x) chia hết cho Cục, gọi q là thương. Từ Dần
    đếm thuận q-1 cung, sau đó x lẻ thì lùi x cung, x chẵn thì tiến x cung.
    Ví dụ Thủy Nhị Cục, mùng 1: x=1, q=1, từ Dần lùi 1 ra Sửu.
    """
    x = -lunar_day % cuc
    q = (lunar_day + x) // cuc
    position = DAN + q - 1
    position += -x if x % 2 else x
    return position % 12


def place_chinh_tinh(tu_vi: int) -> Dict[str, int]:
    """An 14 chính tinh.

    Thiên Phủ đối xứng với Tử Vi qua trục Dần-Thân, nên vị trí của hai sao
    luôn có tổng bằng 4 (mod 12); Tử Vi ở Dần hoặc Thân thì đồng cung Thiên Phủ.
    """
    thien_phu = (4 - tu_vi) % 12
    stars = {name: (tu_vi + offset) % 12 for name, offset in CHOM_TU_VI.items()}
    stars.update({name: (thien_phu + offset) % 12 for name, offset in CHOM_THIEN_PHU.items()})
    return stars


def place_phu_tinh(month: int, hour_chi: int, year_can: str, year_chi: int,
                   hoa_linh_thuan: bool) -> Dict[str, int]:
    """An các phụ tinh theo tháng, giờ, Can năm và Chi năm sinh."""
    month_index = month - 1
    group = CHI_NHOM[year_chi]
    loc_ton = LOC_TON[year_can]
    khoi, viet = KHOI_VIET[year_can]
    hoa_khoi, linh_khoi = HOA_LINH_KHOI[group]
    # Dương Nam, Âm Nữ: Hỏa thuận Linh nghịch; Âm Nam, Dương Nữ thì ngược lại.
    direction = 1 if hoa_linh_thuan else -1
    return {
        # Theo tháng sinh
        "Tả Phù": (THIN + month_index) % 12,
        "Hữu Bật": (TUAT - month_index) % 12,
        "Thiên Hình": (DAU + month_index) % 12,
        "Thiên Riêu": (SUU + month_index) % 12,
        # Theo giờ sinh
        "Văn Xương": (TUAT - hour_chi) % 12,
        "Văn Khúc": (THIN + hour_chi) % 12,
        "Địa Không": (HOI - hour_chi) % 12,
        "Địa Kiếp": (HOI + hour_chi) % 12,
        # Theo Can năm sinh
        "Lộc Tồn": loc_ton,
        "Kình Dương": (loc_ton + 1) % 12,
        "Đà La": (loc_ton - 1) % 12,
        "Thiên Khôi": khoi,
        "Thiên Việt": viet,
        # Theo Chi năm sinh
        "Thiên Mã": THIEN_MA[group],
        "Đào Hoa": DAO_HOA[group],
        "Long Trì": (THIN + year_chi) % 12,
        "Phượng Các": (TUAT - year_chi) % 12,
        "Thiên Khốc": (NGO - year_chi) % 12,
        "Thiên Hư": (NGO + year_chi) % 12,
        "Hồng Loan": (MAO - year_chi) % 12,
        "Thiên Hỷ": (MAO - year_chi + 6) % 12,
        # Theo Chi năm sinh và giờ sinh
        "Hỏa Tinh": (hoa_khoi + direction * hour_chi) % 12,
        "Linh Tinh": (linh_khoi - direction * hour_chi) % 12,
    }


def find_tuan(year_can: int, year_chi: int) -> Tuple[int, int]:
    """An Tuần: hai Chi bị thiếu trong tuần Giáp chứa năm sinh.

    Mỗi tuần Giáp có 10 năm nên dư 2 Chi. Ví dụ tuần Giáp Tý thiếu Tuất, Hợi.
    """
    giap_chi = (year_chi - year_can) % 12
    return (giap_chi + 10) % 12, (giap_chi + 11) % 12


def tieu_han_position(chart: Dict, age: int) -> int:
    """Tìm cung tiểu hạn ở một tuổi âm: khởi theo Chi năm, Nam thuận, Nữ nghịch."""
    return (chart["tieu_han_khoi"] + chart["tieu_han_chieu"] * (age - 1)) % 12


def _average_rating(chinh_tinh: Dict[str, int], phu_tinh: Dict[str, int],
                    position: int) -> Optional[float]:
    """Tính trung bình rating các sao trong một cung; cung không có sao trả về None."""
    ratings = [get_star(name)["rating"] for stars in (chinh_tinh, phu_tinh)
               for name, star_position in stars.items() if star_position == position]
    return round(sum(ratings) / len(ratings), 1) if ratings else None


def build_palaces(lunar_day: int, lunar_month: int, can_chi_year: str, hour_chi: int,
                  gender: str) -> Dict:
    """Lập 12 cung từ thông tin âm lịch.

    Args:
        lunar_day: Ngày âm lịch (1-30).
        lunar_month: Tháng âm lịch dùng để an sao (1-12).
        can_chi_year: Can Chi năm sinh, ví dụ "Canh Ngọ".
        hour_chi: Chỉ số Chi của giờ sinh (Tý=0, ..., Hợi=11).
        gender: "Nam" hoặc "Nữ".

    Returns:
        Dict gồm cung (12 cung theo thứ tự CUNG_NAMES) và các thông tin chung.
    """
    can_name, chi_name = can_chi_year.split()
    year_can, year_chi = CAN.index(can_name), CHI.index(chi_name)
    duong = year_can % 2 == 0
    nam = gender == "Nam"
    # Dương Nam, Âm Nữ đi thuận; Âm Nam, Dương Nữ đi nghịch.
    thuan = duong == nam
    direction = 1 if thuan else -1

    menh = find_menh(lunar_month, hour_chi)
    than = find_than(lunar_month, hour_chi)
    cuc_number, cuc_name, cuc_element = find_cuc(year_can, menh)
    tu_vi = find_tu_vi(lunar_day, cuc_number)

    chinh_tinh = place_chinh_tinh(tu_vi)
    phu_tinh = place_phu_tinh(lunar_month, hour_chi, can_name, year_chi, thuan)
    all_stars = {**chinh_tinh, **phu_tinh}

    tu_hoa = [{"star": star, "hoa": hoa, "position": all_stars[star]}
              for star, hoa in zip(TU_HOA[can_name], TEN_TU_HOA)]
    tuan = find_tuan(year_can, year_chi)
    triet = TRIET[can_name]
    trang_sinh_khoi = TRANG_SINH_KHOI[cuc_element]

    cung: List[Dict] = []
    for index, name in enumerate(CUNG_NAMES):
        # Các cung an nghịch từ Mệnh; đại vận đi theo chiều Âm Dương từ Mệnh.
        position = (menh - index) % 12
        dai_van_step = (direction * (position - menh)) % 12
        dai_van_start = cuc_number + 10 * dai_van_step
        cung.append({
            "name": name,
            "cung_name": name,
            "position": CHI[position],
            "chi": CHI[position],
            "position_index": position,
            "can": CAN[palace_can(year_can, position)],
            "chinh_tinh": [s for s, p in chinh_tinh.items() if p == position],
            "phu_tinh": [s for s, p in phu_tinh.items() if p == position],
            "tu_hoa": [{"star": h["star"], "hoa": h["hoa"]} for h in tu_hoa
                       if h["position"] == position],
            "trang_sinh": TRANG_SINH[(direction * (position - trang_sinh_khoi)) % 12],
            "tuan": position in tuan,
            "triet": position in triet,
            "is_than": position == than,
            "dai_van_age": f"{dai_van_start}-{dai_van_start + 9}",
            "dai_van_start": dai_van_start,
            "rating": _average_rating(chinh_tinh, phu_tinh, position),
        })

    return {
        "cung": cung,
        "menh_cung": CUNG_NAMES[0],
        "menh_position": CHI[menh],
        "than_position": CHI[than],
        "than_cu": next(c["name"] for c in cung if c["is_than"]),
        "cuc": {"number": cuc_number, "name": cuc_name},
        "am_duong": f"{'Dương' if duong else 'Âm'} {gender}",
        "chieu_dai_van": "Thuận" if thuan else "Nghịch",
        "ban_menh": get_nap_am(year_can, year_chi),
        "menh_chu": MENH_CHU[year_chi],
        "than_chu": THAN_CHU[year_chi],
        "tu_hoa": [{"star": h["star"], "hoa": h["hoa"], "cung": CHI[h["position"]]}
                   for h in tu_hoa],
        "tuan": [CHI[p] for p in tuan],
        "triet": [CHI[p] for p in triet],
        "tieu_han_khoi": TIEU_HAN_KHOI[CHI_NHOM[year_chi]],
        "tieu_han_chieu": 1 if nam else -1,
    }


def _star_info(cung: List[Dict]) -> Dict[str, Dict]:
    """Gom ý nghĩa các sao có trong lá số để frontend hiện tooltip."""
    info: Dict[str, Dict] = {}
    for palace in cung:
        for name in palace["chinh_tinh"] + palace["phu_tinh"]:
            star = get_star(name)
            info[name] = {"y_nghia": star["y_nghia"], "ngu_hanh": star["ngu_hanh"],
                          "rating": star["rating"]}
    for name, meaning in TU_HOA_INFO.items():
        info[name] = {"y_nghia": meaning, "ngu_hanh": "", "rating": None}
    return info


def build_chart(birth_info: Dict) -> Dict:
    """Lập lá số đầy đủ từ thông tin sinh theo dương lịch.

    Args:
        birth_info: {"full_name": str, "gender": "Nam"|"Nữ", "day": int,
            "month": int, "year": int, "hour": int (0-23)}. Có thể kèm birth_place.

    Returns:
        Dict gồm chart_id, info, lunar, can_chi và 12 cung trong khóa "cung".
    """
    year, month, day, hour = (birth_info[k] for k in ("year", "month", "day", "hour"))
    calendar = get_full_can_chi(year, month, day, hour)
    lunar = calendar["lunar"]
    hour_chi = get_hour_chi_index(hour)

    # Tháng nhuận: từ ngày 16 trở đi tính sang tháng sau, thông lệ phổ biến.
    chart_month = lunar["lunar_month"]
    if lunar["is_leap"] and lunar["lunar_day"] > 15:
        chart_month = chart_month % 12 + 1

    palaces = build_palaces(lunar["lunar_day"], chart_month, calendar["can_chi"]["year"],
                            hour_chi, birth_info["gender"])
    return {
        "chart_id": str(uuid.uuid4()),
        "info": birth_info,
        "lunar": lunar,
        "can_chi": calendar["can_chi"],
        "day_rollover": calendar["day_rollover"],
        "gio_sinh": HOUR_LABELS[hour_chi],
        "chart_month": chart_month,
        "star_info": _star_info(palaces["cung"]),
        **palaces,
    }


if __name__ == "__main__":
    # Ví dụ: Nam, sinh 15/5/1990 lúc 10h. Xem thêm tests/test_chart_builder.py
    sys.stdout.reconfigure(encoding="utf-8")
    sample = build_chart({"full_name": "Mẫu", "gender": "Nam", "day": 15, "month": 5,
                          "year": 1990, "hour": 10})
    print(sample["lunar"], sample["can_chi"], sample["cuc"]["name"])
    for palace in sample["cung"]:
        print(f"{palace['name']:<11}{palace['position']:<6}{palace['dai_van_age']:<8}"
              f"{', '.join(palace['chinh_tinh'])} | {', '.join(palace['phu_tinh'])}")

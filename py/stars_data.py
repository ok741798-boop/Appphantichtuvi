"""Dữ liệu sao tử vi: 14 chính tinh, 23 phụ tinh, lưu tinh và Tứ Hóa.

Trường rating (1-10) là thang điểm cát/hung dùng cho luận giải rule-based:
trên 5 thiên về cát, dưới 5 thiên về hung. Đây là thang quy ước của ứng dụng,
không phải số liệu trong sách tử vi cổ.

Lời luận cố ý tránh khẳng định tai họa hay bệnh tật cụ thể: mỗi sao chỉ mô tả
xu hướng để người dùng tham khảo.
"""

from typing import Dict, List, Optional

StarInfo = Dict[str, object]

CHINH_TINH: Dict[str, StarInfo] = {
    "Tử Vi": {
        "ngu_hanh": "Thổ",
        "y_nghia": "Đế tinh: vua, quyền quý, khả năng lãnh đạo",
        "career": "có tố chất tổ chức và lãnh đạo, hợp vai trò quản lý, điều hành",
        "wealth": "tài lộc ổn định, thường đến từ địa vị và uy tín",
        "love": "coi trọng gia đạo, cần tránh áp đặt ý mình lên người thương",
        "health": "thể trạng khá tốt, nên chú ý tiêu hóa",
        "rating": 9,
    },
    "Thiên Cơ": {
        "ngu_hanh": "Mộc",
        "y_nghia": "Mưu trí, linh hoạt, giỏi tính toán và thích nghi",
        "career": "hợp công việc cần tư duy như kế hoạch, tư vấn, kỹ thuật, giáo dục",
        "wealth": "tiền bạc đến nhờ trí tuệ, thu nhập có thể thay đổi theo giai đoạn",
        "love": "tình cảm nhiều suy tư, cần chia sẻ thẳng thắn để tránh nghĩ quá nhiều",
        "health": "dễ căng thẳng thần kinh, nên giữ giấc ngủ điều độ",
        "rating": 7,
    },
    "Thái Dương": {
        "ngu_hanh": "Hỏa",
        "y_nghia": "Mặt Trời: danh tiếng, sự rộng lượng, tinh thần cống hiến",
        "career": "dễ được biết đến, hợp môi trường công khai, giao tiếp, cống hiến",
        "wealth": "tài lộc đi cùng danh tiếng, rộng rãi nên cần biết giữ lại",
        "love": "ấm áp, chủ động và hay bao bọc người thương",
        "health": "nên chú ý mắt, huyết áp và cân bằng công việc",
        "rating": 8,
    },
    "Vũ Khúc": {
        "ngu_hanh": "Kim",
        "y_nghia": "Tài tinh: tài chính, kỷ luật, tính quyết đoán",
        "career": "hợp tài chính, kỹ thuật, công việc cần kỷ luật và kết quả rõ ràng",
        "wealth": "giỏi kiếm và quản lý tiền, tích lũy tốt nếu có kế hoạch",
        "love": "ít bộc lộ cảm xúc, cần chủ động thể hiện sự quan tâm",
        "health": "nên chú ý hô hấp và tránh làm việc quá sức",
        "rating": 8,
    },
    "Thiên Đồng": {
        "ngu_hanh": "Thủy",
        "y_nghia": "Phúc tinh: hiền hòa, lạc quan, biết hưởng thụ",
        "career": "hợp môi trường ôn hòa như dịch vụ, chăm sóc, giáo dục",
        "wealth": "tài lộc vừa đủ, an nhàn, cần thêm tính kỷ luật để tích lũy",
        "love": "dịu dàng, dễ gần, biết vun vén không khí gia đình",
        "health": "thể trạng ổn, nên duy trì vận động đều đặn",
        "rating": 8,
    },
    "Liêm Trinh": {
        "ngu_hanh": "Hỏa",
        "y_nghia": "Nguyên tắc, nhiệt huyết, có cả nét đào hoa lẫn nét nghiêm cẩn",
        "career": "hợp pháp lý, hành chính, kỹ thuật hoặc lĩnh vực cần nguyên tắc",
        "wealth": "kiếm tiền bằng năng lực, nên minh bạch trong hợp tác",
        "love": "tình cảm sâu đậm nhưng dễ căng thẳng, cần mềm mỏng hơn",
        "health": "nên chú ý tim mạch, máu huyết và tránh nóng nảy",
        "rating": 6,
    },
    "Thiên Phủ": {
        "ngu_hanh": "Thổ",
        "y_nghia": "Kho trời: tích lũy, bảo thủ tích cực, sự vững vàng",
        "career": "hợp quản trị, tài chính, những vị trí cần sự ổn định và tin cậy",
        "wealth": "giữ tiền tốt, tài sản tăng dần theo thời gian",
        "love": "chín chắn, thực tế, tạo cảm giác an toàn cho bạn đời",
        "health": "thể trạng tốt, nên chú ý chế độ ăn uống",
        "rating": 9,
    },
    "Thái Âm": {
        "ngu_hanh": "Thủy",
        "y_nghia": "Mặt Trăng: nhu hòa, tinh tế, gắn với điền sản và tích lũy",
        "career": "hợp công việc tỉ mỉ, sáng tạo, tài chính hoặc bất động sản",
        "wealth": "tích lũy đều đặn, có duyên với nhà đất",
        "love": "nhạy cảm, giàu tình cảm, cần được lắng nghe",
        "health": "nên chú ý nội tiết và giữ tinh thần thư thái",
        "rating": 8,
    },
    "Tham Lang": {
        "ngu_hanh": "Thủy",
        "y_nghia": "Đào hoa tinh: ham học hỏi, khéo giao tiếp, nhiều ham muốn",
        "career": "hợp kinh doanh, truyền thông, nghệ thuật, giao tế",
        "wealth": "cơ hội tài chính nhiều nhưng biến động, cần kiểm soát chi tiêu",
        "love": "duyên dáng, nhiều mối quan hệ, cần sự chân thành và rõ ràng",
        "health": "nên điều độ ăn uống, sinh hoạt",
        "rating": 5,
    },
    "Cự Môn": {
        "ngu_hanh": "Thủy",
        "y_nghia": "Ám tinh: ăn nói sắc sảo, hay hoài nghi, dễ gặp thị phi",
        "career": "hợp nghề dùng lời nói như luật, giảng dạy, truyền thông, tư vấn",
        "wealth": "tài lộc đến nhờ chuyên môn, nên có hợp đồng rõ ràng",
        "love": "dễ hiểu lầm vì lời nói, nên trao đổi nhẹ nhàng và lắng nghe",
        "health": "nên chú ý tiêu hóa, răng miệng",
        "rating": 5,
    },
    "Thiên Tướng": {
        "ngu_hanh": "Thủy",
        "y_nghia": "Ấn tinh: trợ giúp, trung thực, có trách nhiệm",
        "career": "hợp vai trò phụ tá, hành chính, tham mưu, được cấp trên tin cậy",
        "wealth": "tài lộc ổn định, thường có người hỗ trợ khi cần",
        "love": "chu đáo, có trách nhiệm, coi trọng sự hòa thuận",
        "health": "thể trạng ổn, nên chú ý da và đường tiết niệu",
        "rating": 8,
    },
    "Thiên Lương": {
        "ngu_hanh": "Mộc",
        "y_nghia": "Ấm tinh: che chở, nhân hậu, biến hung thành lành",
        "career": "hợp y tế, giáo dục, tư vấn, công việc giúp ích cho người khác",
        "wealth": "tài lộc từ uy tín, không nên chạy theo cơ hội mạo hiểm",
        "love": "bao dung, hay chăm lo, nên tránh tính bảo ban quá mức",
        "health": "có phúc khí, nên khám sức khỏe định kỳ để yên tâm",
        "rating": 8,
    },
    "Thất Sát": {
        "ngu_hanh": "Kim",
        "y_nghia": "Tướng tinh: dũng mãnh, quyết liệt, thích thử thách",
        "career": "hợp môi trường cạnh tranh, khởi nghiệp, kỹ thuật, quân sự",
        "wealth": "tài lộc theo từng đợt, cần dự phòng cho giai đoạn biến động",
        "love": "thẳng thắn, mạnh mẽ, cần học cách nhường nhịn",
        "health": "nên chú ý an toàn khi di chuyển và vận động mạnh",
        "rating": 6,
    },
    "Phá Quân": {
        "ngu_hanh": "Thủy",
        "y_nghia": "Hao tinh: phá cũ dựng mới, thích đổi thay",
        "career": "hợp đổi mới, khởi nghiệp, tái cấu trúc công việc",
        "wealth": "thu chi lớn và biến động, nên tách riêng khoản dự phòng",
        "love": "cần không gian riêng, mối quan hệ bền khi có sự tôn trọng",
        "health": "nên chú ý nghỉ ngơi, tránh làm việc thất thường",
        "rating": 5,
    },
}


def _phu(ngu_hanh: str, y_nghia: str, rating: int, career: str, wealth: str, love: str,
         health: str) -> StarInfo:
    """Gom dữ liệu một phụ tinh về cùng cấu trúc với chính tinh."""
    return {
        "ngu_hanh": ngu_hanh, "y_nghia": y_nghia, "rating": rating,
        "career": career, "wealth": wealth, "love": love, "health": health,
    }


PHU_TINH: Dict[str, StarInfo] = {
    # Lục cát và các sao trợ lực
    "Tả Phù": _phu("Thổ", "Trợ lực, có người giúp đỡ", 8,
                   "được đồng nghiệp hỗ trợ", "có người chung vốn hoặc giúp sức",
                   "được người thân ủng hộ", "có người chăm lo khi cần"),
    "Hữu Bật": _phu("Thủy", "Trợ lực, hòa giải khéo léo", 8,
                    "có quý nhân nâng đỡ", "được giúp đỡ về tiền bạc",
                    "dễ hàn gắn bất hòa", "có người chăm lo khi cần"),
    "Văn Xương": _phu("Kim", "Học vấn, thi cử, văn chương", 7,
                      "thuận lợi cho học tập, bằng cấp", "kiếm tiền nhờ kiến thức",
                      "tình cảm tao nhã", "tinh thần minh mẫn"),
    "Văn Khúc": _phu("Thủy", "Tài năng, khẩu tài, nghệ thuật", 7,
                     "ăn nói có duyên, có năng khiếu", "có lộc từ tài năng",
                     "lãng mạn, tinh tế", "tinh thần linh hoạt"),
    "Thiên Khôi": _phu("Hỏa", "Quý nhân dương, cơ hội được nâng đỡ", 8,
                       "gặp quý nhân là bậc trên", "có người mở đường tài lộc",
                       "được người lớn tuổi vun vén", "gặp thầy gặp thuốc"),
    "Thiên Việt": _phu("Hỏa", "Quý nhân âm, sự hỗ trợ kín đáo", 8,
                       "được giúp đỡ thầm lặng", "có lộc từ quan hệ",
                       "dễ gặp người tử tế", "gặp thầy gặp thuốc"),
    "Lộc Tồn": _phu("Thổ", "Bổng lộc, sự no đủ và tích lũy", 9,
                    "có bổng lộc ổn định", "giữ tiền tốt, có của ăn của để",
                    "cuộc sống đủ đầy", "ăn ngon ngủ yên"),
    "Thiên Mã": _phu("Hỏa", "Di chuyển, thay đổi, năng động", 7,
                     "có cơ hội đi xa, đổi môi trường", "tiền bạc đến nhờ năng động",
                     "dễ có giai đoạn xa cách", "nên chú ý an toàn khi đi lại"),
    "Long Trì": _phu("Thủy", "Vẻ thanh tao, may mắn nhẹ nhàng", 7,
                     "được quý mến", "có lộc nhỏ", "tình cảm êm đềm", "tinh thần thư thái"),
    "Phượng Các": _phu("Mộc", "Danh giá, vẻ đẹp, hỷ sự", 7,
                       "có tiếng tốt", "có lộc từ danh tiếng", "có tin vui", "tinh thần phấn chấn"),
    "Hồng Loan": _phu("Thủy", "Hỷ tinh về nhân duyên", 8,
                      "có quý nhân khác giới", "có tin vui về tiền",
                      "thuận lợi cho hôn nhân, tình duyên", "tinh thần vui vẻ"),
    "Thiên Hỷ": _phu("Thủy", "Hỷ tinh về tin vui", 8,
                     "có tin mừng trong công việc", "có khoản thu vui",
                     "có thể có hỷ sự", "tinh thần lạc quan"),
    "Đào Hoa": _phu("Mộc", "Sức hút, nhân duyên, giao tiếp", 7,
                    "dễ được yêu mến", "có lộc nhờ quan hệ", "nhiều duyên, cần rõ ràng",
                    "nên giữ sinh hoạt điều độ"),
    # Lục sát và các sao cần lưu ý
    "Kình Dương": _phu("Kim", "Sát tinh: cứng rắn, cạnh tranh, dễ xung đột", 4,
                       "phải cạnh tranh nhiều", "nên thận trọng khi hợp tác",
                       "tránh lời nói nóng nảy", "nên cẩn thận với vật sắc nhọn"),
    "Đà La": _phu("Kim", "Sát tinh: trì hoãn, vướng mắc kéo dài", 3,
                  "tiến độ có thể chậm", "tiền về chậm hơn dự tính",
                  "dễ giữ khúc mắc trong lòng", "nên xử lý sớm các vấn đề âm ỉ"),
    "Hỏa Tinh": _phu("Hỏa", "Sát tinh: nóng vội, bùng phát nhanh", 3,
                     "nên tránh quyết định vội", "chi tiêu dễ bốc đồng",
                     "tránh nóng giận", "nên giữ bình tĩnh, nghỉ ngơi đủ"),
    "Linh Tinh": _phu("Hỏa", "Sát tinh: bất ngờ, âm ỉ, dễ bất an", 3,
                      "có thể có thay đổi đột ngột", "nên có khoản dự phòng",
                      "dễ nghĩ ngợi một mình", "nên giải tỏa căng thẳng"),
    "Địa Không": _phu("Hỏa", "Không vong: ý tưởng lạ, dễ hụt hẫng", 2,
                      "hợp sáng tạo, tránh kỳ vọng ảo", "tránh đầu tư theo cảm hứng",
                      "dễ thấy khoảng trống trong lòng", "nên giữ tinh thần ổn định"),
    "Địa Kiếp": _phu("Hỏa", "Kiếp sát: biến động, dễ hao tổn", 2,
                     "có thể phải làm lại từ đầu", "nên tránh rủi ro lớn về tiền",
                     "nên kiên nhẫn khi gặp sóng gió", "nên giữ sức, tránh làm quá tải"),
    "Thiên Hình": _phu("Hỏa", "Kỷ luật, pháp lý, sự nghiêm khắc", 4,
                       "hợp pháp lý, y khoa, kỹ thuật", "nên tuân thủ giấy tờ",
                       "tránh quá nghiêm khắc", "nên khám định kỳ"),
    "Thiên Riêu": _phu("Thủy", "Sức hấp dẫn kèm thị phi nhỏ", 4,
                       "tránh chuyện đồn đoán", "tránh chi tiêu theo cảm xúc",
                       "nên rõ ràng trong các mối quan hệ", "nên giữ vệ sinh, nghỉ ngơi"),
    "Thiên Khốc": _phu("Thủy", "Nỗi buồn, sự lo nghĩ sâu", 4,
                       "lo nghĩ nhiều về công việc", "cẩn trọng khoản hao nhỏ",
                       "dễ buồn vu vơ", "nên chia sẻ, thư giãn"),
    "Thiên Hư": _phu("Thủy", "Trống trải, cảm giác thiếu thực chất", 4,
                     "tránh làm việc chỉ để lấy tiếng", "tránh phô trương",
                     "dễ thấy cô đơn", "nên giữ nếp sinh hoạt đều"),
}

# Sao lưu niên: đổi vị trí theo Chi của từng năm xem hạn.
LUU_TINH: Dict[str, str] = {
    "Thái Tuế": "Sao đứng năm: nhiều việc, dễ thay đổi, nên giữ chữ tín và làm việc đúng phép.",
    "Tang Môn": "Dễ có chuyện buồn phiền, nên quan tâm người thân và giữ tinh thần vững vàng.",
    "Bạch Hổ": "Năm nhiều xáo động, nên cẩn trọng khi đi lại và khi ra quyết định lớn.",
}

# Tứ Hóa theo Can, thứ tự: Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ.
# Các trường phái khác nhau ở vài Can; đây là bảng thông dụng trong tử vi Việt Nam.
TU_HOA: Dict[str, List[str]] = {
    "Giáp": ["Liêm Trinh", "Phá Quân", "Vũ Khúc", "Thái Dương"],
    "Ất": ["Thiên Cơ", "Thiên Lương", "Tử Vi", "Thái Âm"],
    "Bính": ["Thiên Đồng", "Thiên Cơ", "Văn Xương", "Liêm Trinh"],
    "Đinh": ["Thái Âm", "Thiên Đồng", "Thiên Cơ", "Cự Môn"],
    "Mậu": ["Tham Lang", "Thái Âm", "Hữu Bật", "Thiên Cơ"],
    "Kỷ": ["Vũ Khúc", "Tham Lang", "Thiên Lương", "Văn Khúc"],
    "Canh": ["Thái Dương", "Vũ Khúc", "Thái Âm", "Thiên Đồng"],
    "Tân": ["Cự Môn", "Thái Dương", "Văn Khúc", "Văn Xương"],
    "Nhâm": ["Thiên Lương", "Tử Vi", "Tả Phù", "Vũ Khúc"],
    "Quý": ["Phá Quân", "Cự Môn", "Thái Âm", "Tham Lang"],
}
TEN_TU_HOA: List[str] = ["Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"]

# Điểm cộng/trừ của Tứ Hóa khi rơi vào một cung.
DIEM_TU_HOA: Dict[str, float] = {
    "Hóa Lộc": 1.0, "Hóa Quyền": 0.7, "Hóa Khoa": 0.5, "Hóa Kỵ": -1.0,
}

TU_HOA_INFO: Dict[str, str] = {
    "Hóa Lộc": "Thêm tài lộc, cơ hội và sự hanh thông cho sao được hóa.",
    "Hóa Quyền": "Thêm quyền hành, ảnh hưởng và sức quyết đoán.",
    "Hóa Khoa": "Thêm danh tiếng, học vấn và quý nhân giải ách.",
    "Hóa Kỵ": "Dễ vướng bận, nên thận trọng ở việc mà sao này chủ quản.",
}


def get_star(name: str) -> Optional[StarInfo]:
    """Tìm dữ liệu của một sao theo tên, trả về None nếu không có."""
    return CHINH_TINH.get(name) or PHU_TINH.get(name)


if __name__ == "__main__":
    print(f"{len(CHINH_TINH)} chính tinh, {len(PHU_TINH)} phụ tinh")

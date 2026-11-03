"""Dữ liệu luận giải cho module Duyên Số Định Mệnh.

Toàn bộ bảng dưới đây là quy ước của ứng dụng, tổng hợp theo ý nghĩa phổ biến của
sao, không phải số liệu thống kê. Lời luận chỉ mô tả xu hướng để tham khảo, cố ý
tránh khẳng định chắc chắn về chuyện đổ vỡ, ngoại tình hay con cái.
"""

from typing import Dict, List, Tuple

PARTNER_TERM: Dict[str, str] = {"Nam": "vợ", "Nữ": "chồng"}

# Độ tuổi kết hôn phổ biến theo giới, tính theo tuổi âm.
MARRIAGE_AGE_RANGE: Dict[str, List[int]] = {"Nam": [27, 35], "Nữ": [24, 30]}
# Sao muộn hoặc sao sớm tại cung Phu Thê làm lệch khoảng tuổi này.
TIMING_SHIFT = 2

DEFAULT_PROFILE: Dict[str, object] = {
    "face": "Trái xoan, hài hòa",
    "skin": "Sáng vừa phải",
    "height": "Trung bình",
    "style": "Thanh lịch, gọn gàng",
    "feature": "Vẻ ngoài dễ gần",
    "traits": ["hiền hòa", "biết lắng nghe"],
    "careers": ["văn phòng", "dịch vụ"],
    "gap": "bằng tuổi hoặc chênh 1-3 tuổi",
    "timing": "vừa",
}

STAR_PROFILE: Dict[str, Dict[str, object]] = {
    "Tử Vi": {
        "face": "Vuông đầy đặn, phúc hậu", "skin": "Sáng hồng", "height": "Khá cao",
        "style": "Chỉn chu, sang trọng", "feature": "Dáng vẻ đĩnh đạc, có uy",
        "traits": ["tự tin", "có chính kiến", "thích làm chủ"],
        "careers": ["quản lý", "nhà nước", "điều hành doanh nghiệp"],
        "gap": "lớn hơn bạn khoảng 3-5 tuổi", "timing": "vừa",
    },
    "Thiên Cơ": {
        "face": "Thanh tú, hơi dài", "skin": "Sáng", "height": "Trung bình, dáng gọn",
        "style": "Gọn gàng, thông minh", "feature": "Đôi mắt nhanh nhẹn",
        "traits": ["thông minh", "linh hoạt", "hay suy nghĩ"],
        "careers": ["kỹ sư", "lập trình", "tư vấn", "giáo viên"],
        "gap": "chênh 1-3 tuổi", "timing": "vừa",
    },
    "Thái Dương": {
        "face": "Tròn sáng, rạng rỡ", "skin": "Hồng hào", "height": "Khá cao",
        "style": "Năng động, nổi bật", "feature": "Nụ cười ấm áp",
        "traits": ["cởi mở", "rộng lượng", "nhiệt tình"],
        "careers": ["truyền thông", "giảng dạy", "công việc đối ngoại"],
        "gap": "lớn hơn bạn khoảng 1-3 tuổi", "timing": "sớm",
    },
    "Vũ Khúc": {
        "face": "Cương nghị, góc cạnh", "skin": "Hơi ngăm", "height": "Trung bình, dáng chắc",
        "style": "Đơn giản, thực tế", "feature": "Ánh mắt dứt khoát",
        "traits": ["kỷ luật", "thực tế", "ít bộc lộ cảm xúc"],
        "careers": ["tài chính", "ngân hàng", "kỹ thuật", "kinh doanh"],
        "gap": "lớn hơn bạn khoảng 3-5 tuổi", "timing": "muộn",
    },
    "Thiên Đồng": {
        "face": "Tròn trịa, phúc hậu", "skin": "Trắng, dễ nhìn", "height": "Trung bình",
        "style": "Đơn giản, thoải mái", "feature": "Vẻ mặt hiền, trẻ hơn tuổi",
        "traits": ["hiền hòa", "lạc quan", "thích an nhàn"],
        "careers": ["giáo viên", "dịch vụ", "chăm sóc khách hàng", "y tế"],
        "gap": "nhỏ hơn bạn hoặc bằng tuổi", "timing": "sớm",
    },
    "Liêm Trinh": {
        "face": "Sắc nét, đôi mày rõ", "skin": "Hơi ngăm hoặc hồng", "height": "Trung bình",
        "style": "Có gu, chú trọng hình ảnh", "feature": "Nét cuốn hút riêng",
        "traits": ["nguyên tắc", "nhiệt huyết", "tình cảm sâu đậm"],
        "careers": ["pháp lý", "hành chính", "kỹ thuật", "nhà nước"],
        "gap": "chênh 1-3 tuổi", "timing": "vừa",
    },
    "Thiên Phủ": {
        "face": "Vuông tròn, đầy đặn", "skin": "Sáng", "height": "Trung bình khá",
        "style": "Đứng đắn, chững chạc", "feature": "Tạo cảm giác an toàn",
        "traits": ["chín chắn", "tiết kiệm", "biết lo xa"],
        "careers": ["tài chính", "quản trị", "bất động sản", "nhà nước"],
        "gap": "lớn hơn bạn khoảng 1-3 tuổi", "timing": "vừa",
    },
    "Thái Âm": {
        "face": "Dịu dàng, thanh tú", "skin": "Trắng mịn", "height": "Trung bình, dáng mảnh",
        "style": "Nhẹ nhàng, tinh tế", "feature": "Đôi mắt đẹp, giọng nói êm",
        "traits": ["dịu dàng", "tinh tế", "giàu tình cảm"],
        "careers": ["nghệ thuật", "bất động sản", "tài chính", "thiết kế"],
        "gap": "nhỏ hơn bạn hoặc bằng tuổi", "timing": "vừa",
    },
    "Tham Lang": {
        "face": "Sắc sảo, quyến rũ", "skin": "Sáng hồng", "height": "Khá cao",
        "style": "Hợp thời, thu hút", "feature": "Có nét đẹp nổi bật",
        "traits": ["đa tài", "khéo léo", "giỏi giao tiếp"],
        "careers": ["kinh doanh", "truyền thông", "nghệ thuật", "ngoại giao"],
        "gap": "chênh 3-5 tuổi", "timing": "sớm",
    },
    "Cự Môn": {
        "face": "Hơi dài, miệng rộng", "skin": "Hơi ngăm", "height": "Trung bình",
        "style": "Giản dị, có cá tính", "feature": "Giọng nói ấn tượng",
        "traits": ["khéo nói", "hay tranh luận", "sắc sảo"],
        "careers": ["luật", "giảng dạy", "truyền thông", "tư vấn"],
        "gap": "chênh 3-5 tuổi", "timing": "muộn",
    },
    "Thiên Tướng": {
        "face": "Đầy đặn, cân đối", "skin": "Trắng hồng", "height": "Trung bình khá",
        "style": "Lịch sự, chỉn chu", "feature": "Phong thái đáng tin",
        "traits": ["trọng danh dự", "cẩn thận", "có trách nhiệm"],
        "careers": ["hành chính", "nhà nước", "tham mưu", "nhân sự"],
        "gap": "chênh 1-3 tuổi", "timing": "vừa",
    },
    "Thiên Lương": {
        "face": "Hiền, trán cao", "skin": "Sáng", "height": "Khá cao",
        "style": "Giản dị, chín chắn", "feature": "Vẻ chững chạc hơn tuổi",
        "traits": ["nhân hậu", "bao dung", "hay chăm lo"],
        "careers": ["bác sĩ", "giáo viên", "tư vấn", "công tác xã hội"],
        "gap": "lớn hơn bạn khoảng 5-10 tuổi", "timing": "muộn",
    },
    "Thất Sát": {
        "face": "Góc cạnh, mạnh mẽ", "skin": "Hơi ngăm", "height": "Khá cao, dáng rắn rỏi",
        "style": "Gọn gàng, dứt khoát", "feature": "Ánh mắt sắc",
        "traits": ["mạnh mẽ", "quyết đoán", "thẳng thắn"],
        "careers": ["khởi nghiệp", "kỹ thuật", "quân đội", "công an"],
        "gap": "lớn hơn bạn khoảng 3-5 tuổi", "timing": "muộn",
    },
    "Phá Quân": {
        "face": "Cá tính, khó đoán", "skin": "Hơi ngăm", "height": "Trung bình khá",
        "style": "Phá cách, không theo khuôn mẫu", "feature": "Phong thái khác biệt",
        "traits": ["thích đổi mới", "cá tính", "độc lập"],
        "careers": ["khởi nghiệp", "công nghệ", "sáng tạo", "vận tải"],
        "gap": "chênh 3-5 tuổi", "timing": "muộn",
    },
}

# Khoảng chênh tuổi của người ấy so với người xem: số dương là lớn hơn, số âm là nhỏ hơn.
# Bảng này đi cùng trường gap trong STAR_PROFILE.
DEFAULT_AGE_GAP = (-3, 3)
AGE_GAP_RANGE: Dict[str, Tuple[int, int]] = {
    "Tử Vi": (3, 5), "Thiên Cơ": (-3, 3), "Thái Dương": (1, 3), "Vũ Khúc": (3, 5),
    "Thiên Đồng": (-3, 0), "Liêm Trinh": (-3, 3), "Thiên Phủ": (1, 3), "Thái Âm": (-3, 0),
    "Tham Lang": (-5, 5), "Cự Môn": (-5, 5), "Thiên Tướng": (-3, 3), "Thiên Lương": (5, 10),
    "Thất Sát": (3, 5), "Phá Quân": (-5, 5),
}

# Tên mang hành tương ứng theo cách đặt tên phổ biến, chỉ để gợi ý cho vui.
# Lá số không có dữ liệu nào suy ra được tên thật của một người.
TEN_THEO_HANH: Dict[str, Dict[str, List[str]]] = {
    "Nữ": {
        "Kim": ["Ngân", "Kim", "Xuyến"], "Mộc": ["Lan", "Mai", "Trúc", "Thảo"],
        "Thủy": ["Hà", "Giang", "Thủy", "Băng"], "Hỏa": ["Ánh", "Dương", "Hồng", "Hạ"],
        "Thổ": ["Ngọc", "Châu", "Bích", "Diệp"],
    },
    "Nam": {
        "Kim": ["Cương", "Phong", "Kiếm"], "Mộc": ["Tùng", "Lâm", "Bách", "Quý"],
        "Thủy": ["Hải", "Giang", "Trường", "Thắng"], "Hỏa": ["Quang", "Huy", "Đăng", "Nhật"],
        "Thổ": ["Sơn", "Kiên", "Thành", "Bảo"],
    },
}

# Phụ tinh tại Phu Thê bổ sung một nét ngoại hình hoặc thần thái.
PHU_TINH_FEATURE: Dict[str, str] = {
    "Hồng Loan": "Có nét duyên, dễ tạo thiện cảm",
    "Thiên Hỷ": "Hay cười, mang lại không khí vui",
    "Đào Hoa": "Có sức hút với người xung quanh",
    "Long Trì": "Dáng vẻ thanh tao",
    "Phượng Các": "Có gu thẩm mỹ tốt",
    "Văn Xương": "Vẻ thư sinh, có học thức",
    "Văn Khúc": "Ăn nói có duyên",
    "Thiên Riêu": "Có vẻ quyến rũ riêng",
}

# Hoàn cảnh gặp gỡ theo thứ tự ưu tiên, sao đứng trước được nói đến trước.
CIRCUMSTANCE_RULES: List[Dict[str, object]] = [
    {"stars": ["Tả Phù", "Hữu Bật"], "text": "qua bạn bè hoặc người quen giới thiệu"},
    {"stars": ["Văn Xương", "Văn Khúc"], "text": "ở trường học, lớp học hoặc một khóa đào tạo"},
    {"stars": ["Thiên Mã"], "text": "trong một chuyến du lịch hoặc công tác xa nhà"},
    {"stars": ["Hồng Loan", "Thiên Hỷ"], "text": "ở đám cưới, tiệc hoặc một dịp vui"},
    {"stars": ["Thiên Cơ", "Cự Môn", "Đào Hoa"], "text": "qua mạng xã hội hoặc trao đổi trực tuyến"},
    {"stars": ["Thiên Lương", "Địa Không"], "text": "ở nơi yên tĩnh như chùa, đền hoặc hoạt động thiện nguyện"},
]
CIRCUMSTANCE_DEFAULT = "trong môi trường công việc hằng ngày"
MAX_CIRCUMSTANCES = 3

# Phương vị theo ngũ hành, dùng hành của chính tinh tại Thiên Di.
HUONG_NGU_HANH: Dict[str, str] = {
    "Thủy": "phía Bắc", "Hỏa": "phía Nam", "Mộc": "phía Đông", "Kim": "phía Tây",
    "Thổ": "khu vực gần nơi bạn sống",
}

# Màu và hướng hợp theo hành bản mệnh, lấy hành sinh ra bản mệnh và chính nó.
MAU_HOP: Dict[str, str] = {
    "Kim": "trắng, ánh kim, vàng nhạt", "Mộc": "xanh lá, xanh nước biển, đen",
    "Thủy": "đen, xanh nước biển, trắng", "Hỏa": "đỏ, hồng, xanh lá",
    "Thổ": "vàng, nâu, đỏ cam",
}

# Thang điểm thuận duyên, là quy ước để so sánh chứ không phải xác suất thật.
FATE_BASE = 50
FATE_STARS: Dict[str, int] = {
    "Tử Vi": 15, "Thiên Phủ": 12, "Thiên Đồng": 10, "Thái Âm": 8, "Thiên Tướng": 8,
    "Hồng Loan": 8, "Thiên Hỷ": 8, "Thiên Lương": 6, "Tả Phù": 4, "Hữu Bật": 4,
    "Long Trì": 3, "Phượng Các": 3,
    "Địa Không": -10, "Địa Kiếp": -10, "Kình Dương": -6, "Đà La": -6,
    "Hỏa Tinh": -5, "Linh Tinh": -5, "Thiên Khốc": -3, "Thiên Hư": -3,
}
FATE_HOA: Dict[str, int] = {"Hóa Lộc": 10, "Hóa Quyền": 6, "Hóa Khoa": 6, "Hóa Kỵ": -8}
FATE_TUAN = -15
FATE_TRIET = -15

FATE_LEVELS = [
    (80, "rất cao", "Đường đến với nhau khá thuận, hai người dễ tìm được tiếng nói chung."),
    (65, "khá cao", "Có thể có một vài lần giận hời hoặc tạm xa nhau trước khi về chung một nhà."),
    (45, "trung bình", "Duyên có nhưng cần thời gian, sự kiên nhẫn của cả hai quyết định nhiều hơn."),
    (0, "cần vun đắp nhiều", "Con đường có thể nhiều thử thách, nên đi chậm và tìm hiểu kỹ trước khi quyết định."),
]

STABILITY_LEVELS = [
    (7.0, "Khá bền vững", "Nền tảng của cung Phu Thê khá vững, hôn nhân dễ giữ được sự ổn định lâu dài."),
    (5.0, "Tương đối ổn định", "Hôn nhân có nền tảng ổn, cần chủ động vun đắp để không nguội lạnh theo thời gian."),
    (0.0, "Cần vun đắp", "Cung Phu Thê có nhiều biến động, cả hai cần trao đổi thẳng thắn và kiên nhẫn hơn."),
]

# Sao tại Tử Tức nghiêng về con trai, các sao còn lại nghiêng về con gái.
SAO_DUONG: List[str] = ["Tử Vi", "Thái Dương", "Vũ Khúc", "Liêm Trinh", "Thất Sát", "Phá Quân", "Tham Lang"]

# Cặp sao cần lưu ý trong hôn nhân: sao hoặc cụm sao và lời nhắc đi kèm.
CAUTION_RULES: List[Dict[str, object]] = [
    {"stars": ["Đào Hoa", "Tham Lang"], "all": True,
     "text": "Cả hai đều có nhiều mối quan hệ xã giao, nên giữ ranh giới rõ ràng và minh bạch với nhau."},
    {"stars": ["Tả Phù", "Hữu Bật"], "all": True,
     "text": "Dễ có người ngoài tác động vào chuyện hai người, nên tự giải quyết việc riêng với nhau trước."},
    {"stars": ["Cự Môn"], "text": "Dễ hiểu lầm vì lời nói, nên trao đổi nhẹ nhàng và tránh tranh thắng thua."},
    {"stars": ["Thiên Mã"], "text": "Có thể có giai đoạn phải xa nhau vì công việc, nên giữ liên lạc đều đặn."},
    {"stars": ["Kình Dương", "Hỏa Tinh"], "text": "Khi nóng giận dễ nói lời khó rút lại, nên tạm dừng rồi nói chuyện sau."},
    {"stars": ["Đà La"], "text": "Khúc mắc dễ bị giữ trong lòng, nên nói ra sớm thay vì để lâu."},
    {"stars": ["Địa Không", "Địa Kiếp"], "text": "Có thể có biến động lớn về tiền bạc hoặc công việc, nên có khoản dự phòng chung."},
]

POSITIVE_RULES: List[Dict[str, object]] = [
    {"stars": ["Thiên Đồng", "Thái Âm"], "text": "Không khí gia đình dễ êm ấm, hai người biết chăm sóc nhau."},
    {"stars": ["Tử Vi", "Thiên Phủ"], "text": "Gia đình có nền tảng vững, người ấy có khả năng lo toan việc lớn."},
    {"stars": ["Thiên Tướng", "Thiên Lương"], "text": "Người ấy có trách nhiệm, biết che chở và giữ lời."},
    {"stars": ["Hồng Loan", "Thiên Hỷ"], "text": "Cuộc sống chung có nhiều niềm vui và tin mừng."},
    {"stars": ["Lộc Tồn"], "text": "Kinh tế gia đình có xu hướng no đủ, biết tích lũy."},
    {"stars": ["Văn Xương", "Văn Khúc"], "text": "Hai người có thể trò chuyện và chia sẻ sở thích tinh thần."},
]
POSITIVE_DEFAULT = "Hai người có cơ hội cùng nhau xây dựng cuộc sống bằng sự chân thành và nỗ lực chung."
CAUTION_DEFAULT = "Hãy dành thời gian cho nhau đều đặn để những chuyện nhỏ không tích tụ."

ELEMENT_RELATION_SCORE: Dict[str, int] = {"tương sinh": 88, "bình hòa": 72, "tương khắc": 45}

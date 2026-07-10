"""Taxonomy intent CỐ ĐỊNH (PRD §7.1) — nhúng vào prompt Agent 1.

Agent 1 phân loại từ MESSAGE + taxonomy này (mô tả + ví dụ mỗi intent) — KHÔNG retrieval (đó là việc Agent 2,
PRD §7.2). Entity schema theo intent để LLM trích đúng. Nội dung lấy từ intents-guide (nay không upload nữa).
"""

from __future__ import annotations

# intent -> {description, examples, entities-schema}
TAXONOMY: dict[str, dict] = {
    "product_price": {
        "description": "Khách hỏi GIÁ sản phẩm — bao nhiêu tiền, giá niêm yết, giá sỉ/lẻ, giá theo màu/size.",
        "examples": ["Áo này bao nhiêu tiền vậy shop?", "Quần jean ống rộng giá nhiêu ạ?", "Mua 3 cái có giá sỉ không?"],
        "entities": ["product_name", "color"],
    },
    "product_information": {
        "description": "Khách hỏi THÔNG TIN sản phẩm (không phải giá) — chất liệu, màu, còn hàng, form dáng, xuất xứ.",
        "examples": ["Áo này còn màu trắng không shop?", "Chất vải cái đầm này là gì vậy?", "Áo thun này còn hàng không?"],
        "entities": ["product_name", "color"],
    },
    "size_consulting": {
        "description": "Khách nhờ TƯ VẤN CHỌN SIZE dựa trên cân nặng/chiều cao/số đo; hỏi size nào vừa.",
        "examples": ["Mình cao 1m60 nặng 50kg thì mặc size gì?", "Áo size M vừa người 55kg không?", "Vòng eo 68 chọn size mấy?"],
        "entities": ["height", "weight", "size"],
    },
    "shipping": {
        "description": "Khách hỏi VẬN CHUYỂN — phí ship, thời gian giao, giao tỉnh, ship COD, đơn vị vận chuyển.",
        "examples": ["Ship về Đà Nẵng bao nhiêu tiền?", "Mấy ngày thì hàng tới nơi?", "Shop có giao COD không?"],
        "entities": ["destination", "order_id"],
    },
    "order_status": {
        "description": "Khách hỏi TRẠNG THÁI ĐƠN đã đặt — đơn tới đâu rồi, đã giao chưa, mã vận đơn, khi nào nhận.",
        "examples": ["Đơn 1234 của mình tới đâu rồi?", "Em đặt 3 ngày rồi mà chưa thấy giao", "Cho xin mã vận đơn với ạ"],
        "entities": ["order_id"],
    },
    "refund": {
        "description": "Khách muốn TRẢ HÀNG / HOÀN TIỀN — chính sách hoàn tiền, điều kiện trả, hoàn tiền về đâu.",
        "examples": ["Mình muốn trả lại áo và lấy lại tiền", "Sản phẩm lỗi cho em hoàn tiền được không?", "Chính sách hoàn tiền thế nào?"],
        "entities": ["order_id"],
    },
    "exchange": {
        "description": "Khách muốn ĐỔI HÀNG — đổi size, đổi màu, đổi mẫu khác; điều kiện & thời hạn đổi.",
        "examples": ["Cho mình đổi sang size L được không?", "Áo bị chật, muốn đổi cái to hơn", "Đổi màu khác có được không?"],
        "entities": ["order_id"],
    },
    "complaint": {
        "description": "Khách KHIẾU NẠI / PHÀN NÀN — hàng lỗi/sai, thái độ phục vụ, giao chậm, bức xúc, đòi gặp quản lý.",
        "examples": ["Shop giao sai màu rồi, xử lý sao?", "Áo rách chỉ khi vừa nhận, quá tệ", "Nhân viên thái độ, tôi muốn gặp quản lý"],
        "entities": ["order_id"],
    },
    "promotion": {
        "description": "Khách hỏi KHUYẾN MÃI — mã giảm giá, chương trình sale, ưu đãi thành viên, quà tặng kèm.",
        "examples": ["Shop có chương trình giảm giá nào không?", "Có mã giảm cho khách mới không?", "Mua 2 tặng 1 còn áp dụng không?"],
        "entities": ["promo_code"],
    },
    "other": {
        "description": "Câu KHÔNG thuộc các nhóm trên hoặc ngoài phạm vi shop — chào hỏi, cảm ơn, hỏi lan man, spam.",
        "examples": ["Alo shop ơi", "Cảm ơn shop nhiều nha", "Shop mở cửa mấy giờ vậy?"],
        "entities": [],
    },
}


def render_taxonomy() -> str:
    """Kết xuất taxonomy thành text để nhúng vào system prompt Agent 1."""
    lines: list[str] = []
    for intent, spec in TAXONOMY.items():
        ents = ", ".join(spec["entities"]) or "(không có)"
        examples = " | ".join(spec["examples"])
        lines.append(f"- {intent}: {spec['description']}\n    entities: {ents}\n    ví dụ: {examples}")
    return "\n".join(lines)

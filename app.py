
import os
import re
import unicodedata
from datetime import datetime

import requests
import streamlit as st


# ==================================================
# 1. CẤU HÌNH
# ==================================================
st.set_page_config(
    page_title="Milk Tea Order - Út Thảo",
    page_icon="🧋",
    layout="centered"
)

LOGO = "B1C6BACF-D2A3-4CBE-9079-F30567711538.png"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

if os.path.exists(LOGO):
    st.image(LOGO, use_container_width=True)


# ==================================================
# 2. MENU VÀ GIÁ BÁN
# ==================================================
TRA_SUA = {
    "Trà sữa truyền thống": 30000,
    "Trà sữa trân châu đường đen": 35000,
    "Trà sữa matcha": 35000,
    "Trà sữa ô long": 32000,
    "Trà sữa khoai môn": 35000,
    "Trà sữa socola": 35000,
    "Trà sữa dâu": 32000,
    "Trà sữa thái xanh": 30000,
    "Trà sữa thái đỏ": 30000,
    "Trà đào": 30000,
    "Trà vải": 30000,
    "Trà chanh": 20000,
}

TOPPING = {
    "Trân châu đen": 5000,
    "Trân châu trắng": 7000,
    "Thạch trái cây": 5000,
    "Thạch cà phê": 5000,
    "Pudding trứng": 7000,
    "Flan": 8000,
    "Kem cheese": 10000,
    "Sương sáo": 5000,
}

MON_AN = {
    "Bánh flan": 12000,
    "Bánh mì phô mai": 20000,
    "Khoai tây chiên": 25000,
    "Xúc xích": 15000,
    "Bánh tiramisu": 30000,
}

SIZE = {"M": 0, "L": 5000, "XL": 10000}

GOI_Y_TOPPING = {
    "Trà sữa truyền thống": ["Trân châu đen", "Pudding trứng", "Flan"],
    "Trà sữa trân châu đường đen": ["Trân châu đen", "Pudding trứng"],
    "Trà sữa matcha": ["Trân châu trắng", "Pudding trứng", "Kem cheese"],
    "Trà sữa ô long": ["Trân châu trắng", "Sương sáo", "Kem cheese"],
    "Trà sữa khoai môn": ["Trân châu trắng", "Pudding trứng", "Flan"],
    "Trà sữa socola": ["Trân châu đen", "Flan", "Kem cheese"],
    "Trà sữa dâu": ["Thạch trái cây", "Trân châu trắng", "Pudding trứng"],
    "Trà sữa thái xanh": ["Trân châu trắng", "Pudding trứng", "Thạch cà phê"],
    "Trà sữa thái đỏ": ["Trân châu đen", "Pudding trứng", "Flan"],
    "Trà đào": ["Thạch trái cây", "Trân châu trắng"],
    "Trà vải": ["Thạch trái cây", "Trân châu trắng"],
    "Trà chanh": ["Thạch trái cây", "Sương sáo"],
}

DO_NGOT = {
    "Trà sữa trân châu đường đen": "Ngọt đậm",
    "Trà sữa socola": "Ngọt béo",
    "Trà sữa khoai môn": "Ngọt béo",
    "Trà sữa truyền thống": "Ngọt vừa",
    "Trà sữa thái đỏ": "Ngọt vừa đến đậm",
    "Trà sữa thái xanh": "Ngọt vừa",
    "Trà sữa dâu": "Ngọt trái cây",
    "Trà sữa matcha": "Béo, có vị trà",
    "Trà sữa ô long": "Thơm trà, thường ít ngọt hơn",
    "Trà đào": "Ngọt thanh",
    "Trà vải": "Ngọt thanh",
    "Trà chanh": "Chua ngọt",
}


# ==================================================
# 3. SESSION STATE
# ==================================================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "invoice" not in st.session_state:
    st.session_state.invoice = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ==================================================
# 4. HÀM HỖ TRỢ
# ==================================================
def tien_vnd(so_tien):
    return f"{so_tien:,.0f}đ".replace(",", ".")


def chuan_hoa(text):
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )
    return text.replace("đ", "d")


def lay_secret(ten, mac_dinh=""):
    """Đọc cấu hình từ Streamlit secrets hoặc biến môi trường."""
    try:
        gia_tri = st.secrets.get(ten, mac_dinh)
    except Exception:
        gia_tri = mac_dinh

    return gia_tri or os.getenv(ten, mac_dinh)


def tim_mon_trong_cau(text, menu):
    cau = chuan_hoa(text)

    for ten_mon in sorted(menu, key=len, reverse=True):
        if chuan_hoa(ten_mon) in cau:
            return ten_mon

    tu_dong = {
        "matcha": "Trà sữa matcha",
        "khoai mon": "Trà sữa khoai môn",
        "socola": "Trà sữa socola",
        "truyen thong": "Trà sữa truyền thống",
        "duong den": "Trà sữa trân châu đường đen",
        "thai xanh": "Trà sữa thái xanh",
        "thai do": "Trà sữa thái đỏ",
        "o long": "Trà sữa ô long",
        "tra dao": "Trà đào",
        "tra vai": "Trà vải",
        "tra chanh": "Trà chanh",
    }

    for tu, ten_mon in tu_dong.items():
        if tu in cau and ten_mon in menu:
            return ten_mon

    return None


def tao_du_lieu_menu():
    """Tạo dữ liệu menu để AI tư vấn đúng giá của quán."""
    dong = ["MENU QUÁN TRÀ SỮA ÚT THẢO"]

    dong.append("\nTRÀ SỮA VÀ TRÀ:")
    for ten, gia in TRA_SUA.items():
        dong.append(f"- {ten}: {tien_vnd(gia)}")

    dong.append("\nTOPPING:")
    for ten, gia in TOPPING.items():
        dong.append(f"- {ten}: {tien_vnd(gia)}")

    dong.append("\nMÓN ĂN THÊM:")
    for ten, gia in MON_AN.items():
        dong.append(f"- {ten}: {tien_vnd(gia)}")

    dong.append("\nPHỤ THU SIZE:")
    for ten, gia in SIZE.items():
        dong.append(f"- Size {ten}: cộng {tien_vnd(gia)}")

    dong.append("\nGỢI Ý TOPPING:")
    for ten, ds in GOI_Y_TOPPING.items():
        dong.append(f"- {ten}: {', '.join(ds)}")

    dong.append("\nGỢI Ý HƯƠNG VỊ:")
    for ten, vi in DO_NGOT.items():
        dong.append(f"- {ten}: {vi}")

    dong.append(
        "\nMức đường khách có thể chọn: 0%, 30%, 50%, 70%, 100%. "
        "Mức đá: Không đá, 30%, 50%, 70%, 100%."
    )

    dong.append(
        "\nGiá trong menu là giá cơ bản. Trà sữa/trà cộng phụ thu size "
        "và topping nếu khách chọn. Mỗi topping được tính một lần "
        "trên mỗi ly. Món ăn thêm không có phụ thu size."
    )

    return "\n".join(dong)


# ==================================================
# 5. CHATBOT DỰ PHÒNG KHI AI KHÔNG KẾT NỐI ĐƯỢC
# ==================================================
def chatbot_du_phong(cau_hoi):
    cau = chuan_hoa(cau_hoi)

    if not cau:
        return "Bạn hãy nhập câu hỏi để mình tư vấn nhé! 🧋"

    if any(tu in cau for tu in [
        "xin chao", "chao shop", "hello", "hi ban"
    ]):
        return (
            "Xin chào! 🧋 Mình là trợ lý của Trà Sữa Út Thảo. "
            "Bạn có thể hỏi giá, topping, hương vị hoặc chọn món "
            "theo ngân sách nhé!"
        )

    hoi_cao = any(tu in cau for tu in [
        "cao nhat", "dat nhat", "mac nhat", "gia cao"
    ])
    hoi_re = any(tu in cau for tu in [
        "re nhat", "thap nhat", "gia re", "gia thap"
    ])

    if hoi_cao:
        gia = max(TRA_SUA.values())
        ds = [ten for ten, g in TRA_SUA.items() if g == gia]
        return (
            f"Món có giá cơ bản cao nhất là {tien_vnd(gia)}:\n\n"
            + "\n".join(f"- {ten}" for ten in ds)
            + "\n\nChưa bao gồm phụ thu size và topping."
        )

    if hoi_re:
        gia = min(TRA_SUA.values())
        ds = [ten for ten, g in TRA_SUA.items() if g == gia]
        return (
            f"Món có giá cơ bản thấp nhất là {tien_vnd(gia)}:\n\n"
            + "\n".join(f"- {ten}" for ten in ds)
            + "\n\nChưa bao gồm phụ thu size và topping."
        )

    if any(tu in cau for tu in [
        "bang gia", "menu gia", "danh sach gia", "gia tung mon"
    ]):
        return (
            "**Bảng giá trà sữa và trà:**\n\n"
            + "\n".join(
                f"- {ten}: {tien_vnd(gia)}"
                for ten, gia in TRA_SUA.items()
            )
            + "\n\nGiá cơ bản, chưa bao gồm size và topping."
        )

    if any(tu in cau for tu in [
        "mon an", "do an", "an vat", "banh", "xuc xich"
    ]):
        return (
            "**Menu món ăn thêm:**\n\n"
            + "\n".join(
                f"- {ten}: {tien_vnd(gia)}"
                for ten, gia in MON_AN.items()
            )
        )

    if any(tu in cau for tu in [
        "it ngot", "khong ngot", "giam ngot", "thanh mat"
    ]):
        return (
            "Bạn có thể tham khảo Trà chanh (chua ngọt), Trà đào "
            "(ngọt thanh) hoặc Trà sữa ô long (hương trà nổi bật). "
            "Có thể thử mức đường 0% hoặc 30%. Lưu ý, mức đường "
            "tùy chọn không nhất thiết đồng nghĩa không có đường "
            "trong các nguyên liệu khác."
        )

    if any(tu in cau for tu in ["ngot nhat", "ngot dam", "thich ngot"]):
        return (
            "Nếu thích vị ngọt đậm, bạn có thể thử Trà sữa trân châu "
            "đường đen. Nếu thích vị ngọt béo, có thể tham khảo "
            "Trà sữa socola hoặc khoai môn. Đây là gợi ý hương vị, "
            "không phải kết quả đo lượng đường."
        )

    ten_mon = tim_mon_trong_cau(cau_hoi, TRA_SUA)

    if ten_mon:
        gia = TRA_SUA[ten_mon]

        if "topping" in cau or "ket hop" in cau or "hop voi gi" in cau:
            ds = GOI_Y_TOPPING.get(ten_mon, [])
            return (
                f"Với **{ten_mon}**, bạn có thể thử:\n\n"
                + "\n".join(
                    f"- {t} (+{tien_vnd(TOPPING[t])})"
                    for t in ds
                )
            )

        if "gia" in cau or "bao nhieu" in cau or "tien" in cau:
            return (
                f"**{ten_mon}** có giá cơ bản {tien_vnd(gia)}. "
                f"Size L cộng {tien_vnd(SIZE['L'])}, size XL cộng "
                f"{tien_vnd(SIZE['XL'])}. Topping tính thêm theo menu."
            )

        return (
            f"**{ten_mon}**\n\n"
            f"- Giá cơ bản: {tien_vnd(gia)}\n"
            f"- Hương vị dự kiến: {DO_NGOT.get(ten_mon, 'Tùy công thức')}\n"
            f"- Topping gợi ý: {', '.join(GOI_Y_TOPPING.get(ten_mon, []))}"
        )

    so_tien = re.search(
        r"(\d+(?:[.,]\d+)?)\s*(k|nghin|ngan|trieu|tr)?",
        cau
    )

    if any(tu in cau for tu in [
        "duoi", "toi da", "ngan sach", "khong qua", "tam gia"
    ]) and so_tien:
        gia = float(so_tien.group(1).replace(",", "."))
        don_vi = so_tien.group(2) or ""

        if don_vi in ("k", "nghin", "ngan"):
            gia *= 1000
        elif don_vi in ("trieu", "tr"):
            gia *= 1000000
        elif gia < 1000:
            gia *= 1000

        ds = [
            (ten, g) for ten, g in TRA_SUA.items()
            if g <= gia
        ]

        if ds:
            return (
                f"Các món có giá cơ bản không quá {tien_vnd(gia)}:\n\n"
                + "\n".join(
                    f"- {ten}: {tien_vnd(g)}" for ten, g in ds
                )
                + "\n\nSize lớn và topping có thể làm tổng tiền tăng."
            )

        return "Chưa có món phù hợp với ngân sách này. Bạn thử tăng ngân sách nhé!"

    return (
        "Mình chưa hiểu rõ câu hỏi. Bạn có thể hỏi về giá món, "
        "menu, topping, độ ngọt, món ăn thêm hoặc ngân sách nhé! 🧋"
    )


# ==================================================
# 6. KẾT NỐI CHATBOT AI
# ==================================================
def chatbot_ai(cau_hoi):
    api_key = lay_secret("OPENROUTER_API_KEY")
    model = lay_secret("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    if not api_key or api_key == "DAN_API_KEY_MOI_CUA_BAN_VAO_DAY":
        return (
            chatbot_du_phong(cau_hoi)
            + "\n\n---\n"
            "ℹ️ Chatbot hiện đang dùng chế độ dự phòng vì chưa cấu hình "
            "API key. Hãy thêm OPENROUTER_API_KEY vào "
            "`.streamlit/secrets.toml` để bật AI."
        )

    system_prompt = f"""
Bạn là trợ lý tư vấn thân thiện của Quán Trà Sữa Út Thảo.
Hãy trả lời bằng tiếng Việt tự nhiên, dễ hiểu, lịch sự và có thể
dùng emoji vừa phải.

DỮ LIỆU MENU CHÍNH THỨC:
{tao_du_lieu_menu()}

QUY TẮC:
1. Chỉ khẳng định giá và món có trong dữ liệu menu ở trên.
2. Không tự bịa món, giá, chương trình khuyến mãi hoặc thành phần.
3. Khi tính giá, tính đúng giá cơ bản + phụ thu size + topping,
   rồi nhân số lượng nếu khách cung cấp đủ thông tin.
4. Nếu thiếu thông tin để tính tổng tiền, hỏi lại khách.
5. Có thể tư vấn món theo khẩu vị, topping, ngân sách và so sánh món.
6. Các mô tả độ ngọt chỉ là gợi ý hương vị, không phải số liệu đo đường.
7. Nếu được hỏi nội dung ngoài phạm vi quán, trả lời ngắn gọn và
   hướng khách quay lại các câu hỏi về menu.
8. Không nói rằng bạn đã nhận đơn hoặc thanh toán cho khách.
   Việc đặt món và thanh toán thực hiện ở tab Đặt món & thanh toán.
9. Trả lời có cấu trúc khi cần, không quá dài nếu câu hỏi đơn giản.
"""

    # Gửi lịch sử gần đây để AI có thể hiểu ngữ cảnh.
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(st.session_state.chat_history[-12:])

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-OpenRouter-Title": "Ut Thao Milk Tea",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 700,
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()

        answer = data["choices"][0]["message"]["content"]

        if isinstance(answer, str) and answer.strip():
            return answer.strip()

        return chatbot_du_phong(cau_hoi)

    except requests.exceptions.Timeout:
        return (
            "AI phản hồi hơi chậm, bạn vui lòng thử lại nhé. 🧋\n\n"
            "Gợi ý nhanh:\n" + chatbot_du_phong(cau_hoi)
        )

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "không rõ"
        if status in (401, 403):
            return (
                "Không thể xác thực API key. Bạn hãy kiểm tra key trong "
                "`.streamlit/secrets.toml` và chắc chắn key còn hoạt động.\n\n"
                + chatbot_du_phong(cau_hoi)
            )
        if status == 429:
            return (
                "Dịch vụ AI đang giới hạn lượt gọi hoặc không đủ hạn mức. "
                "Bạn thử lại sau nhé.\n\n"
                + chatbot_du_phong(cau_hoi)
            )
        return (
            f"AI hiện gặp lỗi kết nối (HTTP {status}). "
            "Bạn có thể thử lại sau.\n\n"
            + chatbot_du_phong(cau_hoi)
        )

    except (requests.exceptions.RequestException, KeyError, ValueError, IndexError):
        return (
            "Hiện chưa kết nối được với AI. Mình sẽ hỗ trợ bạn bằng "
            "chế độ tư vấn cơ bản nhé!\n\n"
            + chatbot_du_phong(cau_hoi)
        )


def gui_cau_hoi(cau_hoi):
    """Lưu câu hỏi và câu trả lời vào lịch sử chat."""
    if not cau_hoi or not cau_hoi.strip():
        return

    st.session_state.chat_history.append({
        "role": "user",
        "content": cau_hoi.strip(),
    })

    tra_loi = chatbot_ai(cau_hoi.strip())

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": tra_loi,
    })


# ==================================================
# 7. GIAO DIỆN CHÍNH
# ==================================================
st.title("🧋 QUÁN TRÀ SỮA ÚT THẢO")
st.caption("Ứng dụng gọi món, tính tiền và chatbot AI tư vấn")

tab_dat_mon, tab_chatbot = st.tabs([
    "🛒 Đặt món & thanh toán",
    "🤖 Chatbot AI",
])


# ==================================================
# TAB 1: ĐẶT MÓN VÀ THANH TOÁN
# ==================================================
with tab_dat_mon:
    ten_khach = st.text_input(
        "👤 Tên khách hàng",
        placeholder="Nhập tên khách hàng...",
        key="ten_khach",
    )

    st.subheader("📋 Chọn món")

    loai_mon = st.radio(
        "Bạn muốn gọi món gì?",
        ["Trà sữa / Trà", "Món ăn thêm"],
        horizontal=True,
    )

    if loai_mon == "Trà sữa / Trà":
        with st.form("form_tra_sua"):
            ten_mon = st.selectbox("🧋 Chọn loại trà sữa", list(TRA_SUA.keys()))

            col1, col2 = st.columns(2)

            with col1:
                size = st.selectbox("🥤 Size ly", list(SIZE.keys()))
                duong = st.select_slider(
                    "🍯 Mức độ đường",
                    options=["0%", "30%", "50%", "70%", "100%"],
                    value="100%",
                )

            with col2:
                so_luong = st.number_input(
                    "🔢 Số lượng", min_value=1, max_value=100,
                    value=1, step=1,
                )
                da = st.select_slider(
                    "🧊 Mức độ đá",
                    options=["Không đá", "30% đá", "50% đá", "70% đá", "100% đá"],
                    value="100% đá",
                )

            toppings = st.multiselect(
                "🍮 Chọn topping",
                options=list(TOPPING.keys()),
                format_func=lambda x: f"{x} (+{tien_vnd(TOPPING[x])})",
            )

            gia_co_ban = TRA_SUA[ten_mon]
            gia_size = SIZE[size]
            gia_top = sum(TOPPING[t] for t in toppings)
            gia_don = gia_co_ban + gia_size + gia_top
            gia_du_kien = gia_don * int(so_luong)

            st.info(f"Giá dự kiến: **{tien_vnd(gia_du_kien)}**")

            them_tra_sua = st.form_submit_button(
                "➕ Thêm vào hóa đơn",
                use_container_width=True,
            )

            if them_tra_sua:
                st.session_state.cart.append({
                    "ten_mon": ten_mon,
                    "loai": "Trà sữa",
                    "don_gia": gia_co_ban,
                    "so_luong": int(so_luong),
                    "size": size,
                    "duong": duong,
                    "da": da,
                    "toppings": toppings.copy(),
                    "gia_topping": gia_top,
                    "gia_don": gia_don,
                    "thanh_tien": gia_du_kien,
                })
                st.session_state.invoice = None
                st.success(f"Đã thêm {ten_mon} vào giỏ hàng!")
                st.rerun()

    else:
        with st.form("form_mon_an"):
            ten_mon_an = st.selectbox("🍟 Chọn món ăn thêm", list(MON_AN.keys()))
            so_luong_an = st.number_input(
                "🔢 Số lượng", min_value=1, max_value=100,
                value=1, step=1,
            )

            gia_an = MON_AN[ten_mon_an]
            st.write("Đơn giá:", tien_vnd(gia_an))

            them_mon_an = st.form_submit_button(
                "➕ Thêm vào hóa đơn",
                use_container_width=True,
            )

            if them_mon_an:
                st.session_state.cart.append({
                    "ten_mon": ten_mon_an,
                    "loai": "Món ăn thêm",
                    "don_gia": gia_an,
                    "so_luong": int(so_luong_an),
                    "size": "-",
                    "duong": "-",
                    "da": "-",
                    "toppings": [],
                    "gia_topping": 0,
                    "gia_don": gia_an,
                    "thanh_tien": gia_an * int(so_luong_an),
                })
                st.session_state.invoice = None
                st.success(f"Đã thêm {ten_mon_an} vào giỏ hàng!")
                st.rerun()

    # ------------------------------
    # GIỎ HÀNG
    # ------------------------------
    st.divider()
    st.subheader("🛒 Giỏ hàng hiện tại")

    if st.session_state.cart:
        tong_tien = sum(m["thanh_tien"] for m in st.session_state.cart)

        for i, mon in enumerate(st.session_state.cart):
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"**{i + 1}. {mon['ten_mon']}**")
                    st.caption(
                        f"Số lượng: {mon['so_luong']} | "
                        f"Đơn giá: {tien_vnd(mon['gia_don'])}"
                    )

                    if mon["loai"] == "Trà sữa":
                        st.caption(
                            f"Size: {mon['size']} | Đường: {mon['duong']} | "
                            f"Đá: {mon['da']}"
                        )
                        st.caption(
                            "Topping: " + (
                                ", ".join(mon["toppings"])
                                if mon["toppings"] else "Không có"
                            )
                        )

                    st.write(f"Thành tiền: **{tien_vnd(mon['thanh_tien'])}**")

                with col2:
                    if st.button("🗑️ Xóa", key=f"xoa_{i}"):
                        st.session_state.cart.pop(i)
                        st.session_state.invoice = None
                        st.rerun()

        st.markdown(f"### Tổng cộng: {tien_vnd(tong_tien)}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🧹 Xóa giỏ hàng", use_container_width=True):
                st.session_state.cart = []
                st.session_state.invoice = None
                st.rerun()

        with col2:
            if st.button(
                "💳 Thanh toán",
                type="primary",
                use_container_width=True,
            ):
                if not ten_khach.strip():
                    st.warning("Vui lòng nhập tên khách hàng trước khi thanh toán!")
                else:
                    now = datetime.now()
                    st.session_state.invoice = {
                        "ten_khach": ten_khach.strip(),
                        "thoi_gian": now.strftime("%d/%m/%Y %H:%M:%S"),
                        "ma_hd": now.strftime("%Y%m%d%H%M%S"),
                        "danh_sach": [m.copy() for m in st.session_state.cart],
                        "tong_tien": tong_tien,
                    }
                    st.rerun()

    else:
        st.info("Giỏ hàng đang trống. Hãy chọn món và thêm vào hóa đơn.")

    # ------------------------------
    # HÓA ĐƠN
    # ------------------------------
    if st.session_state.invoice:
        hd = st.session_state.invoice

        st.divider()
        st.subheader("🧾 HÓA ĐƠN THANH TOÁN")

        st.markdown(
            """
            <div style="text-align:center">
                <h2>🧋 QUÁN TRÀ SỮA ÚT THẢO</h2>
                <p>HÓA ĐƠN THANH TOÁN</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(f"**Mã hóa đơn:** {hd['ma_hd']}")
        st.write(f"**Khách hàng:** {hd['ten_khach']}")
        st.write(f"**Thời gian:** {hd['thoi_gian']}")
        st.divider()

        for i, mon in enumerate(hd["danh_sach"], start=1):
            st.markdown(f"**{i}. {mon['ten_mon']}**")
            st.write(
                f"Số lượng: {mon['so_luong']} × "
                f"{tien_vnd(mon['gia_don'])} = "
                f"**{tien_vnd(mon['thanh_tien'])}**"
            )

            if mon["loai"] == "Trà sữa":
                st.caption(
                    f"Size {mon['size']} | Đường {mon['duong']} | Đá {mon['da']}"
                )
                st.caption(
                    "Topping: " + (
                        ", ".join(mon["toppings"])
                        if mon["toppings"] else "Không có"
                    )
                )

        st.divider()
        st.markdown(
            f"<h3 style='text-align:right'>"
            f"TỔNG THANH TOÁN: {tien_vnd(hd['tong_tien'])}</h3>",
            unsafe_allow_html=True,
        )
        st.success("Đã tạo hóa đơn! Cảm ơn quý khách.")

        noi_dung = [
            "       QUAN TRA SUA UT THAO",
            "        HOA DON THANH TOAN",
            "=" * 36,
            f"Ma hoa don: {hd['ma_hd']}",
            f"Khach hang: {hd['ten_khach']}",
            f"Thoi gian: {hd['thoi_gian']}",
            "-" * 36,
        ]

        for i, mon in enumerate(hd["danh_sach"], start=1):
            noi_dung.append(f"{i}. {mon['ten_mon']}")
            noi_dung.append(
                f"   SL: {mon['so_luong']} x {tien_vnd(mon['gia_don'])}"
            )

            if mon["loai"] == "Trà sữa":
                noi_dung.append(
                    f"   Size: {mon['size']} | Duong: {mon['duong']} | Da: {mon['da']}"
                )
                noi_dung.append(
                    "   Topping: " + (
                        ", ".join(mon["toppings"])
                        if mon["toppings"] else "Khong co"
                    )
                )

            noi_dung.append(f"   Thanh tien: {tien_vnd(mon['thanh_tien'])}")

        noi_dung.extend([
            "-" * 36,
            f"TONG TIEN: {tien_vnd(hd['tong_tien'])}",
            "=" * 36,
            "Cam on quy khach!",
        ])

        st.download_button(
            "📥 Tải hóa đơn TXT",
            data="\n".join(noi_dung).encode("utf-8"),
            file_name=f"hoa_don_{hd['ma_hd']}.txt",
            mime="text/plain",
            use_container_width=True,
        )

        if st.button("🆕 Tạo hóa đơn mới", use_container_width=True):
            st.session_state.cart = []
            st.session_state.invoice = None
            st.rerun()


# ==================================================
# TAB 2: CHATBOT AI
# ==================================================
with tab_chatbot:
    st.subheader("🤖 Trợ lý AI Út Thảo")
    st.write(
        "Bạn có thể hỏi tự nhiên về menu, giá, topping, hương vị, "
        "so sánh món hoặc nhờ tư vấn theo ngân sách."
    )

    cau_hoi_mau = [
        "Trà sữa nào đắt nhất?",
        "Món nào rẻ nhất?",
        "Trà sữa matcha nên dùng topping nào?",
        "Mình thích uống béo, nên chọn món gì?",
        "Món nào ít ngọt?",
        "Trà đào giá bao nhiêu?",
        "Có món nào dưới 30k không?",
        "Cho xem bảng giá menu",
    ]

    st.markdown("**💡 Thử hỏi nhanh:**")
    cot1, cot2 = st.columns(2)

    for i, cau in enumerate(cau_hoi_mau):
        cot = cot1 if i % 2 == 0 else cot2
        with cot:
            if st.button(cau, key=f"goi_y_{i}", use_container_width=True):
                gui_cau_hoi(cau)
                st.rerun()

    st.divider()

    # Hiển thị lịch sử trò chuyện
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    cau_hoi = st.chat_input("Nhập câu hỏi của bạn...")

    if cau_hoi:
        with st.spinner("Trợ lý Út Thảo đang suy nghĩ..."):
            gui_cau_hoi(cau_hoi)
        st.rerun()

    if st.button("🧹 Xóa lịch sử trò chuyện", key="xoa_chat"):
        st.session_state.chat_history = []
        st.rerun()


# ==================================================
# 8. CHÂN TRANG
# ==================================================
st.divider()
st.caption("© Quán Trà Sữa Út Thảo | Order & Chatbot AI tư vấn")

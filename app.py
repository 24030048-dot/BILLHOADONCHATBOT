
import streamlit as st
from datetime import datetime
import os
import re
import unicodedata

# ==================================================
# CẤU HÌNH ỨNG DỤNG
# ==================================================
st.set_page_config(
    page_title="Milk Tea Order - Út Thảo",
    page_icon="🧋",
    layout="centered"
)

LOGO = "B1C6BACF-D2A3-4CBE-9079-F30567711538.png"

if os.path.exists(LOGO):
    st.image(LOGO, use_container_width=True)

# ==================================================
# MENU VÀ GIÁ BÁN (VNĐ)
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

SIZE = {
    "M": 0,
    "L": 5000,
    "XL": 10000,
}

# ==================================================
# KHỞI TẠO SESSION STATE
# ==================================================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "invoice" not in st.session_state:
    st.session_state.invoice = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==================================================
# HÀM HỖ TRỢ
# ==================================================
def tien_vnd(so_tien):
    return f"{so_tien:,.0f}đ".replace(",", ".")


def chuan_hoa(text):
    """Bỏ dấu tiếng Việt để chatbot nhận nhiều cách gõ."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )
    return text.replace("đ", "d")


def tim_mon_trong_cau(text, menu):
    """Tìm tên món được nhắc đến trong câu hỏi."""
    cau = chuan_hoa(text)

    for ten_mon in sorted(menu.keys(), key=len, reverse=True):
        ten_chuan = chuan_hoa(ten_mon)

        if ten_chuan in cau:
            return ten_mon

    # Hỗ trợ một số cách gọi ngắn
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


# ==================================================
# CƠ SỞ KIẾN THỨC CHATBOT
# ==================================================
# Đây là gợi ý khẩu vị dựa trên tên món.
# Hãy điều chỉnh theo công thức pha chế thực tế.

GOI_Y_TOPPING = {
    "Trà sữa truyền thống": [
        "Trân châu đen",
        "Pudding trứng",
        "Flan",
    ],
    "Trà sữa trân châu đường đen": [
        "Trân châu đen",
        "Pudding trứng",
    ],
    "Trà sữa matcha": [
        "Trân châu trắng",
        "Pudding trứng",
        "Kem cheese",
    ],
    "Trà sữa ô long": [
        "Trân châu trắng",
        "Sương sáo",
        "Kem cheese",
    ],
    "Trà sữa khoai môn": [
        "Trân châu trắng",
        "Pudding trứng",
        "Flan",
    ],
    "Trà sữa socola": [
        "Trân châu đen",
        "Flan",
        "Kem cheese",
    ],
    "Trà sữa dâu": [
        "Thạch trái cây",
        "Trân châu trắng",
        "Pudding trứng",
    ],
    "Trà sữa thái xanh": [
        "Trân châu trắng",
        "Pudding trứng",
        "Thạch cà phê",
    ],
    "Trà sữa thái đỏ": [
        "Trân châu đen",
        "Pudding trứng",
        "Flan",
    ],
    "Trà đào": [
        "Thạch trái cây",
        "Trân châu trắng",
    ],
    "Trà vải": [
        "Thạch trái cây",
        "Trân châu trắng",
    ],
    "Trà chanh": [
        "Thạch trái cây",
        "Sương sáo",
    ],
}

# Phân loại cảm nhận hương vị dự kiến.
# Không phải số liệu đo lượng đường thực tế.

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


def chatbot_tra_loi(cau_hoi):
    """Chatbot tư vấn theo menu và bộ quy tắc."""

    cau = chuan_hoa(cau_hoi)

    if not cau:
        return "Bạn hãy nhập câu hỏi để mình tư vấn nhé! 🧋"

    # 1. Chào hỏi
    if any(tu in cau for tu in [
        "xin chao", "chao shop", "hello", "hi ban"
    ]):
        return (
            "Xin chào! 🧋 Mình là trợ lý tư vấn của "
            "Quán Trà Sữa Út Thảo.\n\n"
            "Bạn có thể hỏi giá, chọn topping, "
            "độ ngọt hoặc tìm món phù hợp ngân sách nhé!"
        )

    # 2. Hỏi giá cao nhất / thấp nhất
    hoi_cao = any(tu in cau for tu in [
        "cao nhat", "dat nhat", "mac nhat",
        "gia cao", "gia dat", "gia mac"
    ])

    hoi_thap = any(tu in cau for tu in [
        "thap nhat", "re nhat", "gia re",
        "gia thap", "it tien nhat"
    ])

    if "gia" in cau and (hoi_cao or hoi_thap):
        gia_min = min(TRA_SUA.values())
        gia_max = max(TRA_SUA.values())

        if hoi_cao:
            ds = [
                ten for ten, gia in TRA_SUA.items()
                if gia == gia_max
            ]

            return (
                f"💰 Trà sữa có giá cao nhất trong menu "
                f"là {tien_vnd(gia_max)}:\n\n"
                + "\n".join(f"• {ten}" for ten in ds)
                + "\n\nGiá trên chưa bao gồm size lớn "
                "và topping."
            )

        ds = [
            ten for ten, gia in TRA_SUA.items()
            if gia == gia_min
        ]

        return (
            f"🎉 Món có giá thấp nhất trong menu "
            f"là {tien_vnd(gia_min)}:\n\n"
            + "\n".join(f"• {ten}" for ten in ds)
            + "\n\nĐó là giá cơ bản, chưa cộng size "
            "và topping."
        )

    # 3. Hỏi món ngọt nhất / ít ngọt
    if any(tu in cau for tu in [
        "ngot nhat", "ngot dam nhat",
        "mon nao ngot", "tra sua nao ngot",
        "thich ngot", "uong ngot"
    ]):
        return (
            "🍯 Nếu bạn thích vị ngọt đậm, có thể thử "
            "**Trà sữa trân châu đường đen**.\n\n"
            "Nếu thích vị ngọt béo, bạn có thể chọn "
            "**Trà sữa socola** hoặc "
            "**Trà sữa khoai môn**.\n\n"
            "Đây là gợi ý theo hương vị dự kiến, "
            "không phải kết quả đo lượng đường. "
            "Bạn có thể chọn mức đường 30%, 50% "
            "hoặc 70% để điều chỉnh theo khẩu vị."
        )

    if any(tu in cau for tu in [
        "it ngot", "khong ngot", "giam ngot",
        "nguoi khong thich ngot", "thanh mat",
        "mon nao thanh", "mon nao it duong"
    ]):
        return (
            "🧊 Nếu không thích quá ngọt, bạn có thể "
            "tham khảo:\n\n"
            "• Trà chanh: vị chua ngọt.\n"
            "• Trà đào: vị trái cây, ngọt thanh.\n"
            "• Trà ô long: hương trà nổi bật.\n\n"
            "Gợi ý: chọn mức đường 0% hoặc 30%. "
            "Lưu ý, mức đường tùy chọn không nhất thiết "
            "đồng nghĩa với không có đường trong nguyên liệu."
        )

    # 4. Tìm món theo tên
    ten_mon = tim_mon_trong_cau(cau_hoi, TRA_SUA)

    if ten_mon:
        gia = TRA_SUA[ten_mon]

        # Hỏi topping
        if any(tu in cau for tu in [
            "topping", "them gi", "an kem",
            "ket hop", "hop voi gi", "nen chon gi"
        ]):
            ds = GOI_Y_TOPPING.get(ten_mon, [])

            return (
                f"🧋 Với **{ten_mon}**, mình gợi ý:\n\n"
                + "\n".join(
                    f"• {t} (+{tien_vnd(TOPPING[t])})"
                    for t in ds
                )
                + "\n\nBạn có thể chọn nhiều topping "
                "khi đặt món. Đây là gợi ý khẩu vị."
            )

        # Hỏi độ ngọt
        if any(tu in cau for tu in [
            "ngot", "vi gi", "huong vi",
            "khau vi", "thanh mat", "beo"
        ]):
            vi = DO_NGOT.get(
                ten_mon,
                "Hương vị tùy công thức pha chế"
            )

            return (
                f"🍯 **{ten_mon}** có hương vị "
                f"dự kiến: {vi}.\n\n"
                "Bạn có thể chọn mức đường 0%, 30%, "
                "50%, 70% hoặc 100% khi đặt món. "
                "Nếu chưa biết chọn mức nào, hãy thử "
                "50% trước nhé!"
            )

        # Hỏi giá của món
        if any(tu in cau for tu in [
            "gia", "bao nhieu", "tien",
            "gia ban", "gia bao nhieu"
        ]):
            return (
                f"💰 **{ten_mon}** có giá cơ bản "
                f"{tien_vnd(gia)}.\n\n"
                f"Size L cộng {tien_vnd(SIZE['L'])}, "
                f"size XL cộng {tien_vnd(SIZE['XL'])}. "
                "Topping tính thêm theo menu."
            )

        return (
            f"🧋 **{ten_mon}**\n\n"
            f"• Giá cơ bản: {tien_vnd(gia)}\n"
            f"• Hương vị: {DO_NGOT.get(ten_mon, 'Tùy công thức')}\n"
            f"• Topping gợi ý: "
            f"{', '.join(GOI_Y_TOPPING.get(ten_mon, []))}\n\n"
            "Bạn có thể hỏi thêm về giá, topping "
            "hoặc mức đường."
        )

    # 5. So sánh giá
    if any(tu in cau for tu in [
        "so sanh", "cac loai", "bang gia",
        "danh sach gia", "menu gia", "gia tung mon"
    ]):
        return (
            "📋 **Bảng giá trà sữa và trà:**\n\n"
            + "\n".join(
                f"• {ten}: {tien_vnd(gia)}"
                for ten, gia in sorted(
                    TRA_SUA.items(),
                    key=lambda item: item[1]
                )
            )
            + "\n\nĐây là giá cơ bản, chưa bao gồm "
            "size và topping."
        )

    # 6. Hỏi món theo ngân sách
    so_tien = re.search(r"(\d+(?:[.,]\d+)?)\s*(k|nghin|ngan|trieu|tr)?", cau)

    if any(tu in cau for tu in [
        "duoi", "toi da", "ngan sach",
        "tam gia", "khong qua", "khoang"
    ]) and so_tien:
        gia_text = so_tien.group(1).replace(",", ".")
        gia = float(gia_text)

        don_vi = so_tien.group(2) or ""

        if don_vi == "k" or don_vi in ["nghin", "ngan"]:
            gia *= 1000
        elif don_vi == "trieu" or don_vi == "tr":
            gia *= 1000000
        elif gia < 1000:
            gia *= 1000

        ds = [
            (ten, gia_mon)
            for ten, gia_mon in TRA_SUA.items()
            if gia_mon <= gia
        ]

        if not ds:
            return (
                "Mình chưa tìm thấy món phù hợp với "
                "ngân sách này. Bạn thử tăng ngân sách nhé!"
            )

        return (
            f"💵 Các món có giá cơ bản không quá "
            f"{tien_vnd(gia)}:\n\n"
            + "\n".join(
                f"• {ten}: {tien_vnd(gia_mon)}"
                for ten, gia_mon in ds
            )
            + "\n\nLưu ý: size L, XL và topping "
            "có thể làm tổng tiền vượt ngân sách."
        )

    # 7. Hỏi menu món ăn
    if any(tu in cau for tu in [
        "mon an", "do an", "an vat",
        "banh", "khoai tay chien", "xuc xich"
    ]):
        return (
            "🍟 **Menu món ăn thêm:**\n\n"
            + "\n".join(
                f"• {ten}: {tien_vnd(gia)}"
                for ten, gia in MON_AN.items()
            )
        )

    # 8. Câu hỏi ngoài phạm vi
    return (
        "🧋 Mình chưa hiểu rõ câu hỏi này.\n\n"
        "Bạn hãy thử hỏi theo các mẫu:\n"
        "• Trà sữa nào đắt nhất?\n"
        "• Món nào rẻ nhất?\n"
        "• Trà sữa matcha nên dùng topping nào?\n"
        "• Trà sữa nào ngọt nhất?\n"
        "• Món nào ít ngọt?\n"
        "• Trà đào giá bao nhiêu?\n"
        "• Có món nào dưới 30k không?\n"
        "• Cho xem bảng giá menu."
    )


# ==================================================
# GIAO DIỆN CHÍNH
# ==================================================
st.title("🧋 QUÁN TRÀ SỮA ÚT THẢO")
st.caption("Ứng dụng gọi món, tính tiền và chatbot tư vấn")

tab_dat_mon, tab_chatbot = st.tabs([
    "🛒 Đặt món & thanh toán",
    "🤖 Chatbot tư vấn"
])

# ==================================================
# TAB 1: ĐẶT MÓN VÀ THANH TOÁN
# ==================================================
with tab_dat_mon:

    ten_khach = st.text_input(
        "👤 Tên khách hàng",
        placeholder="Nhập tên khách hàng...",
        key="ten_khach"
    )

    st.subheader("📋 Chọn món")

    loai_mon = st.radio(
        "Bạn muốn gọi món gì?",
        ["Trà sữa / Trà", "Món ăn thêm"],
        horizontal=True
    )

    # Chọn trà sữa / trà
    if loai_mon == "Trà sữa / Trà":

        with st.form("form_tra_sua"):

            ten_mon = st.selectbox(
                "🧋 Chọn loại trà sữa",
                list(TRA_SUA.keys())
            )

            col1, col2 = st.columns(2)

            with col1:
                size = st.selectbox(
                    "🥤 Size ly",
                    list(SIZE.keys())
                )

                duong = st.select_slider(
                    "🍯 Mức độ đường",
                    options=["0%", "30%", "50%", "70%", "100%"],
                    value="100%"
                )

            with col2:
                so_luong = st.number_input(
                    "🔢 Số lượng",
                    min_value=1,
                    max_value=100,
                    value=1,
                    step=1
                )

                da = st.select_slider(
                    "🧊 Mức độ đá",
                    options=[
                        "Không đá", "30% đá", "50% đá",
                        "70% đá", "100% đá"
                    ],
                    value="100% đá"
                )

            toppings = st.multiselect(
                "🍮 Chọn topping",
                options=list(TOPPING.keys()),
                format_func=lambda x: (
                    f"{x} (+{tien_vnd(TOPPING[x])})"
                )
            )

            gia_co_ban = TRA_SUA[ten_mon]
            gia_size = SIZE[size]
            gia_top = sum(TOPPING[t] for t in toppings)

            gia_du_kien = (
                gia_co_ban + gia_size + gia_top
            ) * so_luong

            st.info(
                f"Giá dự kiến: **{tien_vnd(gia_du_kien)}**"
            )

            them_tra_sua = st.form_submit_button(
                "➕ Thêm vào hóa đơn",
                use_container_width=True
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
                    "gia_don": gia_co_ban + gia_size + gia_top,
                    "thanh_tien": gia_du_kien,
                })

                st.session_state.invoice = None
                st.success(f"Đã thêm {ten_mon} vào hóa đơn!")
                st.rerun()

    # Chọn món ăn
    else:

        with st.form("form_mon_an"):

            ten_mon_an = st.selectbox(
                "🍟 Chọn món ăn thêm",
                list(MON_AN.keys())
            )

            so_luong_an = st.number_input(
                "🔢 Số lượng",
                min_value=1,
                max_value=100,
                value=1,
                step=1
            )

            st.write(
                "Đơn giá:",
                tien_vnd(MON_AN[ten_mon_an])
            )

            them_mon_an = st.form_submit_button(
                "➕ Thêm vào hóa đơn",
                use_container_width=True
            )

            if them_mon_an:
                gia_an = MON_AN[ten_mon_an]

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
                st.success(f"Đã thêm {ten_mon_an} vào hóa đơn!")
                st.rerun()

    # Giỏ hàng
    st.divider()
    st.subheader("🛒 Giỏ hàng hiện tại")

    if st.session_state.cart:

        tong_tien = sum(
            mon["thanh_tien"]
            for mon in st.session_state.cart
        )

        for i, mon in enumerate(st.session_state.cart):

            with st.container(border=True):

                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(
                        f"**{i + 1}. {mon['ten_mon']}**"
                    )

                    st.caption(
                        f"Số lượng: {mon['so_luong']} | "
                        f"Đơn giá: {tien_vnd(mon['gia_don'])}"
                    )

                    if mon["loai"] == "Trà sữa":

                        st.caption(
                            f"Size: {mon['size']} | "
                            f"Đường: {mon['duong']} | "
                            f"Đá: {mon['da']}"
                        )

                        st.caption(
                            "Topping: "
                            + (
                                ", ".join(mon["toppings"])
                                if mon["toppings"]
                                else "Không có"
                            )
                        )

                    st.write(
                        f"Thành tiền: **{tien_vnd(mon['thanh_tien'])}**"
                    )

                with col2:
                    if st.button("🗑️ Xóa", key=f"xoa_{i}"):
                        st.session_state.cart.pop(i)
                        st.session_state.invoice = None
                        st.rerun()

        st.markdown(f"### Tổng cộng: {tien_vnd(tong_tien)}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "🧹 Xóa giỏ hàng",
                use_container_width=True
            ):
                st.session_state.cart = []
                st.session_state.invoice = None
                st.rerun()

        with col2:
            if st.button(
                "💳 Thanh toán",
                type="primary",
                use_container_width=True
            ):
                if not ten_khach.strip():
                    st.warning(
                        "Vui lòng nhập tên khách hàng trước khi thanh toán!"
                    )
                else:
                    now = datetime.now()

                    st.session_state.invoice = {
                        "ten_khach": ten_khach.strip(),
                        "thoi_gian": now.strftime("%d/%m/%Y %H:%M:%S"),
                        "ma_hd": now.strftime("%Y%m%d%H%M%S"),
                        "danh_sach": [
                            mon.copy()
                            for mon in st.session_state.cart
                        ],
                        "tong_tien": tong_tien,
                    }

                    st.rerun()

    else:
        st.info(
            "Giỏ hàng đang trống. "
            "Hãy chọn món và thêm vào hóa đơn."
        )

    # Hóa đơn thanh toán
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
            unsafe_allow_html=True
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
                    f"Size {mon['size']} | "
                    f"Đường {mon['duong']} | "
                    f"Đá {mon['da']}"
                )

                st.caption(
                    "Topping: "
                    + (
                        ", ".join(mon["toppings"])
                        if mon["toppings"]
                        else "Không có"
                    )
                )

        st.divider()

        st.markdown(
            f"<h3 style='text-align:right'>"
            f"TỔNG THANH TOÁN: {tien_vnd(hd['tong_tien'])}"
            f"</h3>",
            unsafe_allow_html=True
        )

        st.success(
            "Thanh toán thành công! Cảm ơn quý khách."
        )

        # Tạo nội dung TXT
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
                f"   SL: {mon['so_luong']} x "
                f"{tien_vnd(mon['gia_don'])}"
            )

            if mon["loai"] == "Trà sữa":

                noi_dung.append(
                    f"   Size: {mon['size']} | "
                    f"Duong: {mon['duong']} | "
                    f"Da: {mon['da']}"
                )

                noi_dung.append(
                    "   Topping: "
                    + (
                        ", ".join(mon["toppings"])
                        if mon["toppings"]
                        else "Khong co"
                    )
                )

            noi_dung.append(
                f"   Thanh tien: {tien_vnd(mon['thanh_tien'])}"
            )

        noi_dung.extend([
            "-" * 36,
            f"TONG TIEN: {tien_vnd(hd['tong_tien'])}",
            "=" * 36,
            "Cam on quy khach!",
        ])

        file_hoa_don = "\n".join(noi_dung)

        st.download_button(
            label="📥 Tải hóa đơn TXT",
            data=file_hoa_don.encode("utf-8"),
            file_name=f"hoa_don_{hd['ma_hd']}.txt",
            mime="text/plain",
            use_container_width=True
        )

        if st.button(
            "🆕 Tạo hóa đơn mới",
            use_container_width=True
        ):
            st.session_state.cart = []
            st.session_state.invoice = None
            st.rerun()


# ==================================================
# TAB 2: CHATBOT TƯ VẤN
# ==================================================
with tab_chatbot:

    st.subheader("🤖 Trợ lý tư vấn Út Thảo")
    st.write(
        "Hỏi mình về giá bán, topping, hương vị "
        "hoặc cách chọn món phù hợp nhé!"
    )

    # Câu hỏi mẫu
    st.markdown("**💡 Thử hỏi nhanh:**")

    cau_hoi_mau = [
        "Trà sữa nào đắt nhất?",
        "Món nào rẻ nhất?",
        "Trà sữa matcha nên dùng topping nào?",
        "Trà sữa nào ngọt nhất?",
        "Món nào ít ngọt?",
        "Trà đào giá bao nhiêu?",
        "Có món nào dưới 30k không?",
        "Cho xem bảng giá menu",
    ]

    cot1, cot2 = st.columns(2)

    for i, cau in enumerate(cau_hoi_mau):
        cot = cot1 if i % 2 == 0 else cot2

        with cot:
            if st.button(
                cau,
                key=f"goi_y_{i}",
                use_container_width=True
            ):
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": cau
                })

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": chatbot_tra_loi(cau)
                })

                st.rerun()

    st.divider()

    # Hiển thị lịch sử chat
    for tin_nhan in st.session_state.chat_history:

        with st.chat_message(tin_nhan["role"]):
            st.markdown(tin_nhan["content"])

    # Ô nhập câu hỏi
    cau_hoi = st.chat_input(
        "Nhập câu hỏi của bạn..."
    )

    if cau_hoi:

        st.session_state.chat_history.append({
            "role": "user",
            "content": cau_hoi
        })

        tra_loi = chatbot_tra_loi(cau_hoi)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": tra_loi
        })

        st.rerun()

    if st.button(
        "🧹 Xóa lịch sử trò chuyện",
        key="xoa_chat"
    ):
        st.session_state.chat_history = []
        st.rerun()


# ==================================================
# CHÂN TRANG
# ==================================================
st.divider()
st.caption("© Quán Trà Sữa Út Thảo | Order & Chatbot tư vấn")


import streamlit as st
from datetime import datetime
from io import BytesIO
st.image("")
# =========================
# CẤU HÌNH ỨNG DỤNG
# =========================
st.set_page_config(
    page_title="Milk Tea Order",
    page_icon="🧋",
    layout="centered"
)

# =========================
# MENU VÀ GIÁ BÁN (VNĐ)
# Bạn có thể sửa giá tại đây
# =========================
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

# =========================
# KHỞI TẠO GIỎ HÀNG
# =========================
if "cart" not in st.session_state:
    st.session_state.cart = []

if "invoice" not in st.session_state:
    st.session_state.invoice = None

# =========================
# HÀM HỖ TRỢ
# =========================
def tien_vnd(so_tien):
    return f"{so_tien:,.0f}đ".replace(",", ".")


def them_mon(
    ten_mon,
    loai,
    don_gia,
    so_luong,
    size="-",
    duong="-",
    da="-",
    toppings=None
):
    toppings = toppings or []
    gia_topping = sum(TOPPING[t] for t in toppings)

    if loai == "Trà sữa":
        gia_don = don_gia + SIZE[size] + gia_topping
    else:
        gia_don = don_gia

    thanh_tien = gia_don * so_luong

    st.session_state.cart.append({
        "ten_mon": ten_mon,
        "loai": loai,
        "don_gia": don_gia,
        "so_luong": so_luong,
        "size": size,
        "duong": duong,
        "da": da,
        "toppings": toppings.copy(),
        "gia_topping": gia_topping,
        "gia_don": gia_don,
        "thanh_tien": thanh_tien,
    })

    # Hủy hóa đơn cũ nếu thêm món mới
    st.session_state.invoice = None


# =========================
# GIAO DIỆN
# =========================
st.title("🧋 QUÁN TRÀ SỮA ÚT THẢO")
st.caption("Ứng dụng gọi món và tính tiền tự động")

st.divider()

ten_khach = st.text_input(
    "👤 Tên khách hàng",
    placeholder="Nhập tên khách hàng..."
)

st.subheader("📋 Chọn món")

loai_mon = st.radio(
    "Bạn muốn gọi món gì?",
    ["Trà sữa / Trà", "Món ăn thêm"],
    horizontal=True
)

# =========================
# CHỌN TRÀ SỮA / TRÀ
# =========================
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
                options=[
                    "0%", "30%", "50%", "70%", "100%"
                ],
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
                    "Không đá",
                    "30% đá",
                    "50% đá",
                    "70% đá",
                    "100% đá"
                ],
                value="100% đá"
            )

        toppings = st.multiselect(
            "🍮 Chọn topping (có thể chọn nhiều)",
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
            them_mon(
                ten_mon=ten_mon,
                loai="Trà sữa",
                don_gia=gia_co_ban,
                so_luong=int(so_luong),
                size=size,
                duong=duong,
                da=da,
                toppings=toppings
            )
            st.success(f"Đã thêm {ten_mon} vào hóa đơn!")
            st.rerun()

# =========================
# CHỌN MÓN ĂN THÊM
# =========================
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
            them_mon(
                ten_mon=ten_mon_an,
                loai="Món ăn thêm",
                don_gia=MON_AN[ten_mon_an],
                so_luong=int(so_luong_an)
            )
            st.success(f"Đã thêm {ten_mon_an} vào hóa đơn!")
            st.rerun()

# =========================
# GIỎ HÀNG
# =========================
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
                if st.button(
                    "🗑️ Xóa",
                    key=f"xoa_{i}"
                ):
                    st.session_state.cart.pop(i)
                    st.session_state.invoice = None
                    st.rerun()

    st.markdown(
        f"### Tổng cộng: {tien_vnd(tong_tien)}"
    )

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
                st.session_state.invoice = {
                    "ten_khach": ten_khach.strip(),
                    "thoi_gian": datetime.now().strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),
                    "ma_hd": datetime.now().strftime(
                        "%Y%m%d%H%M%S"
                    ),
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

# =========================
# HIỂN THỊ HÓA ĐƠN
# =========================
if st.session_state.invoice:
    hd = st.session_state.invoice

    st.divider()
    st.subheader("🧾 HÓA ĐƠN THANH TOÁN")

    st.markdown(
        """
        <div style="text-align:center">
            <h2>🧋 QUÁN TRÀ SỮA</h2>
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

    st.success("Thanh toán thành công! Cảm ơn quý khách.")

    # Tạo nội dung hóa đơn TXT
    noi_dung = [
        "          QUAN TRA SUA UT THAO",
        "       HOA DON THANH TOAN",
        "=" * 32,
        f"Ma hoa don: {hd['ma_hd']}",
        f"Khach hang: {hd['ten_khach']}",
        f"Thoi gian: {hd['thoi_gian']}",
        "-" * 32,
    ]

    for i, mon in enumerate(hd["danh_sach"], start=1):
        noi_dung.append(
            f"{i}. {mon['ten_mon']}"
        )
        noi_dung.append(
            f"   SL: {mon['so_luong']} x "
            f"{tien_vnd(mon['gia_don'])}"
        )

        if mon["loai"] == "Trà sữa":
            noi_dung.append(
                f"   Size: {mon['size']} | "
                f"Duong: {mon['duong']} | Da: {mon['da']}"
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
        "-" * 32,
        f"TONG TIEN: {tien_vnd(hd['tong_tien'])}",
        "=" * 32,
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

st.divider()
st.caption("© Quán Trà Sữa | Phần mềm tính tiền")

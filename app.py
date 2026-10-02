
import streamlit as st
import pandas as pd
import os
import uuid
import html
from datetime import datetime, date

# ==========================================
# 1. CẤU HÌNH
# ==========================================
st.set_page_config(
    page_title="ÚT THẢO POS",
    page_icon="🧋",
    layout="wide"
)

DATA_DIR = "data"
ORDERS_FILE = os.path.join(DATA_DIR, "orders.csv")
DETAILS_FILE = os.path.join(DATA_DIR, "order_details.csv")

os.makedirs(DATA_DIR, exist_ok=True)

ORDER_COLUMNS = [
    "ma_don", "ngay_gio", "khach_hang",
    "phuong_thuc", "tam_tinh", "giam_gia",
    "tong_tien", "tien_khach_dua", "tien_thua"
]

DETAIL_COLUMNS = [
    "ma_don", "ten_mon", "size", "so_luong",
    "duong", "da", "topping", "don_gia", "thanh_tien"
]

MENU = {
    "Trà sữa truyền thống": 30000,
    "Trà sữa matcha": 35000,
    "Trà sữa socola": 35000,
    "Trà sữa khoai môn": 35000,
    "Trà đào cam sả": 32000,
    "Trà vải": 30000,
    "Trà chanh": 20000,
    "Cà phê sữa": 25000,
    "Bạc xỉu": 28000,
    "Matcha latte": 35000
}

SIZE_EXTRA = {"M": 0, "L": 10000, "XL": 15000}
TOPPING_PRICE = {
    "Trân châu đen": 5000,
    "Trân châu trắng": 7000,
    "Thạch trái cây": 5000,
    "Pudding": 7000,
    "Kem cheese": 10000
}


def read_csv(path, columns):
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            return df[columns]
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            pass
    return pd.DataFrame(columns=columns)


def money(value):
    return f"{int(value):,}".replace(",", ".") + " đ"


def save_order(order, details):
    orders = read_csv(ORDERS_FILE, ORDER_COLUMNS)
    details_df = read_csv(DETAILS_FILE, DETAIL_COLUMNS)

    orders = pd.concat(
        [orders, pd.DataFrame([order])],
        ignore_index=True
    )
    details_df = pd.concat(
        [details_df, pd.DataFrame(details)],
        ignore_index=True
    )

    orders.to_csv(ORDERS_FILE, index=False, encoding="utf-8-sig")
    details_df.to_csv(DETAILS_FILE, index=False, encoding="utf-8-sig")


# ==========================================
# 2. GIAO DIỆN
# ==========================================
st.markdown("""
<style>
.main {background-color: #fffaf5;}
h1, h2, h3 {color: #8b4565;}
div.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}
.receipt {
    background: white;
    color: #222;
    padding: 22px;
    border: 1px dashed #999;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧋 ÚT THẢO POS")
st.caption("Ứng dụng tính tiền và quản lý doanh thu hàng quán")

with st.sidebar:
    st.header("📌 Menu hệ thống")
    page = st.radio(
        "Chọn chức năng",
        ["Bán hàng", "Lịch sử đơn hàng", "Báo cáo doanh thu"]
    )
    st.divider()
    st.caption("Phiên bản demo dành cho sinh viên")


# ==========================================
# 3. BÁN HÀNG
# ==========================================
if page == "Bán hàng":
    st.header("🛒 Tạo hóa đơn mới")

    with st.form("order_form"):
        customer = st.text_input(
            "Tên khách hàng",
            placeholder="Ví dụ: Nguyễn Thị A"
        )

        payment = st.selectbox(
            "Phương thức thanh toán",
            ["Tiền mặt", "Chuyển khoản (demo)"]
        )

        st.subheader("Chọn món")

        menu_items = list(MENU.keys())
        selections = []

        for i in range(3):
            st.markdown(f"**Món {i + 1}**")
            c1, c2, c3 = st.columns([3, 1, 1])

            with c1:
                item = st.selectbox(
                    f"Tên món #{i + 1}",
                    ["-- Không chọn --"] + menu_items,
                    key=f"item_{i}"
                )

            with c2:
                qty = st.number_input(
                    f"Số lượng #{i + 1}",
                    min_value=1,
                    max_value=100,
                    value=1,
                    step=1,
                    key=f"qty_{i}"
                )

            with c3:
                size = st.selectbox(
                    f"Size #{i + 1}",
                    ["M", "L", "XL"],
                    key=f"size_{i}"
                )

            c4, c5, c6 = st.columns(3)

            with c4:
                sugar = st.selectbox(
                    f"Đường #{i + 1}",
                    ["100%", "70%", "50%", "30%", "0%"],
                    key=f"sugar_{i}"
                )

            with c5:
                ice = st.selectbox(
                    f"Đá #{i + 1}",
                    ["100%", "70%", "50%", "30%", "Không đá"],
                    key=f"ice_{i}"
                )

            with c6:
                toppings = st.multiselect(
                    f"Topping #{i + 1}",
                    list(TOPPING_PRICE.keys()),
                    key=f"topping_{i}"
                )

            if item != "-- Không chọn --":
                selections.append({
                    "ten_mon": item,
                    "so_luong": int(qty),
                    "size": size,
                    "duong": sugar,
                    "da": ice,
                    "topping": toppings
                })

            st.divider()

        discount_percent = st.selectbox(
            "Mức giảm giá",
            [0, 5, 10, 15, 20],
            format_func=lambda x: f"{x}%"
        )

        cash_given = st.number_input(
            "Tiền khách đưa (VNĐ)",
            min_value=0,
            value=0,
            step=10000
        )

        submitted = st.form_submit_button(
            "🧾 TÍNH TIỀN VÀ TẠO HÓA ĐƠN",
            use_container_width=True
        )

    if submitted:
        if not selections:
            st.error("Vui lòng chọn ít nhất một món.")
        else:
            detail_rows = []
            subtotal = 0

            order_id = (
                "UT" + datetime.now().strftime("%y%m%d%H%M%S")
                + uuid.uuid4().hex[:4].upper()
            )

            for s in selections:
                base = MENU[s["ten_mon"]]
                size_extra = SIZE_EXTRA[s["size"]]
                topping_total = sum(
                    TOPPING_PRICE[t] for t in s["topping"]
                )

                unit_price = base + size_extra + topping_total
                line_total = unit_price * s["so_luong"]
                subtotal += line_total

                detail_rows.append({
                    "ma_don": order_id,
                    "ten_mon": s["ten_mon"],
                    "size": s["size"],
                    "so_luong": s["so_luong"],
                    "duong": s["duong"],
                    "da": s["da"],
                    "topping": ", ".join(s["topping"]) or "Không",
                    "don_gia": unit_price,
                    "thanh_tien": line_total
                })

            discount = round(subtotal * discount_percent / 100)
            total = subtotal - discount
            change = int(cash_given) - total

            if payment == "Tiền mặt" and cash_given < total:
                st.error(
                    f"Khách còn thiếu {money(total - int(cash_given))}. "
                    "Hãy nhập lại số tiền khách đưa."
                )
            else:
                if payment != "Tiền mặt":
                    cash_value = total
                    change = 0
                else:
                    cash_value = int(cash_given)

                now = datetime.now()

                order = {
                    "ma_don": order_id,
                    "ngay_gio": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "khach_hang": customer.strip() or "Khách lẻ",
                    "phuong_thuc": payment,
                    "tam_tinh": subtotal,
                    "giam_gia": discount,
                    "tong_tien": total,
                    "tien_khach_dua": cash_value,
                    "tien_thua": change
                }

                save_order(order, detail_rows)

                st.session_state["last_order"] = {
                    "order": order,
                    "details": detail_rows
                }

                st.success("Đã tạo và lưu hóa đơn thành công!")


    # Hiển thị hóa đơn gần nhất
    if "last_order" in st.session_state:
        last = st.session_state["last_order"]
        order = last["order"]
        details = last["details"]

        st.subheader("🧾 Hóa đơn của khách hàng")

        rows_html = ""
        for d in details:
            rows_html += (
                "<tr>"
                f"<td>{html.escape(str(d['ten_mon']))}"
                f"<br><small>Size {html.escape(str(d['size']))}; "
                f"Đường {html.escape(str(d['duong']))}; "
                f"Đá {html.escape(str(d['da']))}; "
                f"Topping: {html.escape(str(d['topping']))}</small></td>"
                f"<td>{d['so_luong']}</td>"
                f"<td>{money(d['don_gia'])}</td>"
                f"<td>{money(d['thanh_tien'])}</td>"
                "</tr>"
            )

        receipt_html = f"""
        <div class="receipt">
          <h2 style="text-align:center;">🧋 ÚT THẢO POS</h2>
          <p style="text-align:center;">HÓA ĐƠN THANH TOÁN</p>
          <hr>
          <p>Mã đơn: {html.escape(str(order['ma_don']))}</p>
          <p>Ngày: {html.escape(str(order['ngay_gio']))}</p>
          <p>Khách hàng: {html.escape(str(order['khach_hang']))}</p>
          <table style="width:100%;border-collapse:collapse;">
            <thead><tr>
              <th align="left">Món</th><th>SL</th>
              <th>Đơn giá</th><th>Thành tiền</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
          <hr>
          <p>Tạm tính: <b>{money(order['tam_tinh'])}</b></p>
          <p>Giảm giá: <b>-{money(order['giam_gia'])}</b></p>
          <h3>TỔNG THANH TOÁN: {money(order['tong_tien'])}</h3>
          <p>Phương thức: {html.escape(str(order['phuong_thuc']))}</p>
          <p>Tiền khách đưa: {money(order['tien_khach_dua'])}</p>
          <p>Tiền thừa: {money(order['tien_thua'])}</p>
          <hr>
          <p style="text-align:center;">Cảm ơn quý khách! ❤️</p>
        </div>
        """

        st.markdown(receipt_html, unsafe_allow_html=True)

        st.components.v1.html(
            f"""
            <button onclick="window.print()"
              style="padding:10px 18px;cursor:pointer;">
              🖨️ In hóa đơn
            </button>
            """,
            height=55
        )

        receipt_text = (
            "UT THAO POS - HOA DON\n"
            f"Ma don: {order['ma_don']}\n"
            f"Ngay: {order['ngay_gio']}\n"
            f"Khach: {order['khach_hang']}\n"
            + "\n".join(
                f"{d['ten_mon']} - Size {d['size']} - "
                f"{d['so_luong']} x {money(d['don_gia'])} = "
                f"{money(d['thanh_tien'])}"
                for d in details
            )
            + f"\nTam tinh: {money(order['tam_tinh'])}"
            + f"\nGiam gia: {money(order['giam_gia'])}"
            + f"\nTong tien: {money(order['tong_tien'])}"
            + f"\nThanh toan: {order['phuong_thuc']}"
        )

        st.download_button(
            "📥 Tải hóa đơn dạng TXT",
            data=receipt_text,
            file_name=f"{order['ma_don']}.txt",
            mime="text/plain"
        )


# ==========================================
# 4. LỊCH SỬ ĐƠN HÀNG
# ==========================================
elif page == "Lịch sử đơn hàng":
    st.header("📚 Lịch sử giao dịch")
    orders = read_csv(ORDERS_FILE, ORDER_COLUMNS)

    if orders.empty:
        st.info("Chưa có đơn hàng. Hãy tạo đơn ở mục Bán hàng.")
    else:
        orders["ngay_gio"] = orders["ngay_gio"].astype(str)
        keyword = st.text_input("Tìm theo mã đơn hoặc tên khách")

        filtered = orders.copy()
        if keyword.strip():
            mask = (
                filtered["ma_don"].astype(str).str.contains(
                    keyword, case=False, na=False
                )
                | filtered["khach_hang"].astype(str).str.contains(
                    keyword, case=False, na=False
                )
            )
            filtered = filtered[mask]

        st.dataframe(
            filtered.sort_values("ngay_gio", ascending=False),
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "📥 Tải lịch sử CSV",
            data=filtered.to_csv(index=False).encode("utf-8-sig"),
            file_name="lich_su_don_hang.csv",
            mime="text/csv"
        )


# ==========================================
# 5. BÁO CÁO DOANH THU
# ==========================================
else:
    st.header("📊 Báo cáo doanh thu")

    orders = read_csv(ORDERS_FILE, ORDER_COLUMNS)

    if orders.empty:
        st.info("Chưa có dữ liệu để thống kê.")
    else:
        orders["ngay_gio"] = pd.to_datetime(
            orders["ngay_gio"], errors="coerce"
        )
        orders["tong_tien"] = pd.to_numeric(
            orders["tong_tien"], errors="coerce"
        ).fillna(0)

        min_date = orders["ngay_gio"].min().date()
        max_date = orders["ngay_gio"].max().date()

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Từ ngày", value=min_date
            )
        with col2:
            end_date = st.date_input(
                "Đến ngày", value=max_date
            )

        if start_date > end_date:
            st.error("Ngày bắt đầu không được sau ngày kết thúc.")
        else:
            mask = (
                (orders["ngay_gio"].dt.date >= start_date)
                & (orders["ngay_gio"].dt.date <= end_date)
            )
            report = orders.loc[mask].copy()

            revenue = report["tong_tien"].sum()
            count = len(report)
            average = revenue / count if count else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("Tổng doanh thu", money(revenue))
            c2.metric("Số đơn hàng", f"{count:,}")
            c3.metric("Trung bình/đơn", money(average))

            if not report.empty:
                report["ngay"] = report["ngay_gio"].dt.strftime("%Y-%m-%d")
                daily = report.groupby("ngay")["tong_tien"].sum()

                st.subheader("Doanh thu theo ngày")
                st.bar_chart(daily)

                st.subheader("Chi tiết giao dịch")
                st.dataframe(
                    report.drop(columns=["ngay"]),
                    use_container_width=True,
                    hide_index=True
                )

                st.download_button(
                    "📥 Tải báo cáo CSV",
                    data=report.to_csv(index=False).encode("utf-8-sig"),
                    file_name="bao_cao_doanh_thu.csv",
                    mime="text/csv"
                )
            else:
                st.info("Không có đơn hàng trong khoảng ngày đã chọn.")

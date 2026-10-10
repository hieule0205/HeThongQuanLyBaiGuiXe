import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import mysql.connector
import math
import csv
from tkinter import filedialog

class ParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phần Mềm Quản Lý Bãi Xe & Tính Phí Tự Động")
        self.root.geometry("750x650") # Mở rộng không gian cho thoáng mắt
        self.root.configure(bg="#F4F6F9") # Đổi màu nền toàn ứng dụng sang xám xanh hiện đại

        # Thiết lập Font chữ chuẩn hiện đại
        self.font_title = ("Segoe UI", 11, "bold")
        self.font_normal = ("Segoe UI", 11)

        # Cấu hình kết nối MySQL
        self.db_config = {
            "host": "localhost",
            "user": "root", 
            "password": "020505", # ĐIỀN PASSWORD CỦA BẠN VÀO ĐÂY
            "database": "quan_ly_bai_xe"
        }
        
        self.setup_ui()
        self.refresh_treeview() # Tải dữ liệu lần đầu

    def setup_ui(self):
        # ================= CẤU HÌNH STYLE CHO BẢNG (TREEVIEW) =================
        style = ttk.Style()
        style.theme_use("clam") # Dùng theme clam để thiết kế phẳng
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#2C3E50", foreground="white", padding=5)
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=30, background="#FFFFFF", fieldbackground="#FFFFFF")
        style.map("Treeview", background=[('selected', '#3498DB')]) # Màu xanh dương khi click chọn dòng

        # ================= KHU VỰC CHECK-IN =================
        frame_in = tk.LabelFrame(self.root, text=" 🚗 KHU VỰC NHẬN XE VÀO ", font=self.font_title, fg="#2980B9", bg="#FFFFFF", padx=15, pady=10)
        frame_in.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_in, text="Biển số xe:", font=self.font_normal, bg="#FFFFFF").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_bien_so = tk.Entry(frame_in, font=self.font_normal, width=18, relief="solid", bd=1)
        self.entry_bien_so.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(frame_in, text="Loại xe:", font=self.font_normal, bg="#FFFFFF").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.combo_loai_xe = ttk.Combobox(frame_in, values=["Xe Máy", "Ô Tô"], font=self.font_normal, width=12, state="readonly")
        self.combo_loai_xe.current(0)
        self.combo_loai_xe.grid(row=0, column=3, padx=10, pady=5)

        self.btn_checkin = tk.Button(frame_in, text="Ghi nhận xe vào", font=self.font_title, bg="#27AE60", fg="white", activebackground="#2ECC71", activeforeground="white", relief="flat", cursor="hand2", command=self.check_in)
        self.btn_checkin.grid(row=0, column=4, padx=20, pady=5)

        # ================= KHU VỰC CHECK-OUT =================
        frame_out = tk.LabelFrame(self.root, text=" 📤 KHU VỰC TRẢ XE & TÍNH PHÍ ", font=self.font_title, fg="#C0392B", bg="#FFFFFF", padx=15, pady=10)
        frame_out.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_out, text="Biển số xe cần lấy:", font=self.font_normal, bg="#FFFFFF").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_bien_so_ra = tk.Entry(frame_out, font=self.font_normal, width=18, relief="solid", bd=1)
        self.entry_bien_so_ra.grid(row=0, column=1, padx=10, pady=5)

        self.btn_checkout = tk.Button(frame_out, text="Tính phí & Lấy xe", font=self.font_title, bg="#E74C3C", fg="white", activebackground="#C0392B", activeforeground="white", relief="flat", cursor="hand2", command=self.check_out)
        self.btn_checkout.grid(row=0, column=2, padx=20, pady=5)

        # ================= KHU VỰC HIỂN THỊ DANH SÁCH =================
        frame_list = tk.Frame(self.root, bg="#F4F6F9")
        frame_list.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(frame_list, text="📋 DANH SÁCH XE ĐANG TRONG BÃI", font=("Segoe UI", 12, "bold"), bg="#F4F6F9", fg="#2C3E50").pack(anchor="w", pady=(0, 5))

        # Tạo Treeview (Bảng)
        columns = ("id", "bien_so", "loai_xe", "thoi_gian_vao")
        self.tree = ttk.Treeview(frame_list, columns=columns, show="headings", style="Treeview")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("bien_so", text="Biển Số")
        self.tree.heading("loai_xe", text="Loại Xe")
        self.tree.heading("thoi_gian_vao", text="Thời Gian Vào")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("bien_so", width=150, anchor="center")
        self.tree.column("loai_xe", width=120, anchor="center")
        self.tree.column("thoi_gian_vao", width=250, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        # Thêm Scrollbar cho Treeview
        scrollbar = ttk.Scrollbar(frame_list, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # ================= KHU VỰC CÁC NÚT QUẢN TRỊ KẾT XUẤT =================
        frame_bottom = tk.Frame(self.root, bg="#F4F6F9")
        frame_bottom.pack(fill="x", padx=20, pady=10)

        self.btn_export = tk.Button(frame_bottom, text="📊 Xuất Báo Cáo CSV", font=self.font_title, bg="#F39C12", fg="white", activebackground="#E67E22", activeforeground="white", relief="flat", cursor="hand2", padx=10, command=self.export_csv)
        self.btn_export.pack(side="left")

        self.btn_clear = tk.Button(frame_bottom, text="🗑 Xóa Lịch Sử Gửi Xe", font=self.font_title, bg="#7F8C8D", fg="white", activebackground="#95A5A6", activeforeground="white", relief="flat", cursor="hand2", padx=10, command=self.clear_database)
        self.btn_clear.pack(side="right")

    def connect_db(self):
        try:
            return mysql.connector.connect(**self.db_config)
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể kết nối MySQL:\n{e}")
            return None

    def refresh_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        conn = self.connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, bien_so, loai_xe, thoi_gian_vao FROM lich_su_gui_xe WHERE trang_thai = 'Đang gửi'")
                records = cursor.fetchall()
                for row in records:
                    self.tree.insert("", tk.END, values=row)
            except Exception as e:
                print("Lỗi khi tải dữ liệu:", e)
            finally:
                conn.close()

    def check_in(self):
        bien_so = self.entry_bien_so.get().strip().upper()
        loai_xe = self.combo_loai_xe.get()
        thoi_gian_vao = datetime.now()

        if not bien_so:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Biển số xe!")
            return

        conn = self.connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM lich_su_gui_xe WHERE bien_so = %s AND trang_thai = 'Đang gửi'", (bien_so,))
                if cursor.fetchone():
                    messagebox.showerror("Lỗi", "Xe này đang trong bãi, không thể check-in thêm!")
                    return

                sql = "INSERT INTO lich_su_gui_xe (bien_so, loai_xe, thoi_gian_vao, trang_thai) VALUES (%s, %s, %s, %s)"
                val = (bien_so, loai_xe, thoi_gian_vao, 'Đang gửi')
                cursor.execute(sql, val)
                conn.commit()
                
                messagebox.showinfo("Thành công", f"Đã ghi nhận xe {bien_so} vào bãi!")
                self.entry_bien_so.delete(0, tk.END)
                self.refresh_treeview() 
                
            except Exception as e:
                messagebox.showerror("Lỗi lưu dữ liệu", str(e))
            finally:
                conn.close()

    def check_out(self):
        bien_so = self.entry_bien_so_ra.get().strip().upper()
        if not bien_so:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập biển số xe cần lấy!")
            return

        conn = self.connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, loai_xe, thoi_gian_vao FROM lich_su_gui_xe WHERE bien_so = %s AND trang_thai = 'Đang gửi'", (bien_so,))
                record = cursor.fetchone()

                if not record:
                    messagebox.showerror("Lỗi", "Không tìm thấy xe này trong bãi hoặc xe đã được lấy!")
                    return

                record_id, loai_xe, thoi_gian_vao = record
                thoi_gian_ra = datetime.now()

                delta = thoi_gian_ra - thoi_gian_vao
                hours = delta.total_seconds() / 3600
                hours_rounded = math.ceil(hours) if hours > 0 else 1 

                don_gia = 5000 if loai_xe.lower() == "xe máy" else 20000
                tien_phi = hours_rounded * don_gia

                sql = "UPDATE lich_su_gui_xe SET thoi_gian_ra = %s, tien_phi = %s, trang_thai = 'Đã lấy' WHERE id = %s"
                cursor.execute(sql, (thoi_gian_ra, tien_phi, record_id))
                conn.commit()

                hoa_don = (
                    f"Biển số: {bien_so}\n"
                    f"Loại xe: {loai_xe}\n"
                    f"Thời gian vào: {thoi_gian_vao.strftime('%d/%m/%Y %H:%M:%S')}\n"
                    f"Thời gian ra: {thoi_gian_ra.strftime('%d/%m/%Y %H:%M:%S')}\n"
                    f"Tổng thời gian tính phí: {hours_rounded} giờ\n"
                    f"--------------------\n"
                    f"TỔNG TIỀN: {tien_phi:,} VNĐ"
                )
                messagebox.showinfo("Thanh toán thành công", hoa_don)
                
                self.entry_bien_so_ra.delete(0, tk.END)
                self.refresh_treeview()

            except Exception as e:
                messagebox.showerror("Lỗi xử lý", str(e))
            finally:
                conn.close()

    def export_csv(self):
        conn = self.connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM lich_su_gui_xe")
                records = cursor.fetchall()
                
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv", 
                    filetypes=[("CSV files", "*.csv")],
                    title="Chọn nơi lưu file CSV"
                )
                
                if file_path:
                    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(["ID", "Biển Số", "Loại Xe", "Thời Gian Vào", "Thời Gian Ra", "Tiền Phí", "Trạng Thái"])
                        writer.writerows(records)
                    
                    messagebox.showinfo("Thành công", f"Đã lưu dữ liệu ra file:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi xuất file", str(e))
            finally:
                conn.close()

    def clear_database(self):
        confirm = messagebox.askyesno("Cảnh báo nguy hiểm", "Bạn có chắc chắn muốn XÓA SẠCH toàn bộ dữ liệu xe ra/vào không?\nHành động này không thể hoàn tác!")
        
        if confirm:
            conn = self.connect_db()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("TRUNCATE TABLE lich_su_gui_xe")
                    conn.commit()
                    
                    messagebox.showinfo("Thành công", "Đã xóa toàn bộ dữ liệu trong cơ sở dữ liệu!")
                    self.refresh_treeview()
                except Exception as e:
                    messagebox.showerror("Lỗi khi xóa", str(e))
                finally:
                    conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingApp(root)
    root.mainloop()
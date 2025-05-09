import os
import subprocess
import platform
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from datetime import datetime
import re
import psutil
import logging

# Thiết lập logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Tự động xác định phiên bản handle.exe phù hợp
def get_handle_path():
    logging.debug("Bắt đầu xác định đường dẫn handle.exe")

    handle_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Handle")
    logging.debug(f"Thư mục Handle: {handle_dir}")

    # Kiểm tra kiến trúc hệ thống
    machine = platform.machine()
    logging.debug(f"Kiến trúc hệ thống: {machine}")

    if machine.endswith('64'):
        # Kiểm tra nếu là ARM64
        if 'ARM' in machine.upper():
            handle_exe = "handle64a.exe"
            logging.debug("Đã chọn handle64a.exe (ARM64)")
        else:
            handle_exe = "handle64.exe"
            logging.debug("Đã chọn handle64.exe (x64)")
    else:
        handle_exe = "handle.exe"
        logging.debug("Đã chọn handle.exe (x86)")

    full_path = os.path.join(handle_dir, handle_exe)
    logging.debug(f"Đường dẫn đầy đủ: {full_path}")

    if os.path.exists(full_path):
        logging.debug(f"File {handle_exe} tồn tại")
    else:
        logging.warning(f"File {handle_exe} không tồn tại")

    return full_path

HANDLE_EXE = get_handle_path()  # Đường dẫn tới handle.exe phù hợp với hệ thống

# Hàm đánh giá rủi ro khi kill process
def assess_process_risk(pid, process_name):
    """
    Đánh giá rủi ro khi kill một process

    Args:
        pid: Process ID
        process_name: Tên process

    Returns:
        Tuple (mức độ rủi ro, mô tả rủi ro)
        Mức độ rủi ro: 0 = thấp, 1 = trung bình, 2 = cao
    """
    logging.debug(f"Đánh giá rủi ro cho process: {process_name} (PID: {pid})")

    try:
        # Danh sách các process quan trọng của hệ thống
        critical_processes = [
            "system", "winlogon", "services", "lsass", "svchost", "csrss",
            "smss", "wininit", "explorer", "spoolsv", "taskmgr"
        ]

        # Danh sách các process thường gặp và ít rủi ro
        safe_processes = [
            "chrome", "firefox", "msedge", "iexplore", "notepad", "wordpad",
            "winword", "excel", "powerpnt", "outlook", "code", "devenv"
        ]

        # Chuyển process_name về chữ thường để so sánh
        process_name_lower = process_name.lower()
        logging.debug(f"Process name (lowercase): {process_name_lower}")

        # Kiểm tra nếu là process hệ thống quan trọng
        for proc in critical_processes:
            if proc in process_name_lower:
                logging.warning(f"Process {process_name} được xác định là tiến trình hệ thống quan trọng (rủi ro cao)")
                return (2, f"⚠️ RỦI RO CAO: {process_name} là tiến trình hệ thống quan trọng. "
                           f"Việc kill có thể gây mất ổn định hoặc crash hệ thống.")

        # Kiểm tra nếu là process an toàn
        for proc in safe_processes:
            if proc in process_name_lower:
                logging.debug(f"Process {process_name} được xác định là ứng dụng thông thường (rủi ro thấp)")
                return (0, f"✅ RỦI RO THẤP: {process_name} là ứng dụng thông thường. "
                           f"Có thể kill nhưng bạn có thể mất dữ liệu chưa lưu.")

        # Kiểm tra số lượng child process
        try:
            process = psutil.Process(pid)
            children = process.children(recursive=True)
            logging.debug(f"Process {process_name} có {len(children)} tiến trình con")

            if len(children) > 3:
                logging.info(f"Process {process_name} có nhiều tiến trình con ({len(children)}) - rủi ro trung bình")
                return (1, f"⚠️ RỦI RO TRUNG BÌNH: {process_name} có {len(children)} tiến trình con. "
                           f"Việc kill có thể ảnh hưởng đến các ứng dụng khác.")
        except Exception as child_error:
            logging.error(f"Lỗi khi kiểm tra tiến trình con: {str(child_error)}")

        # Mặc định là rủi ro trung bình
        logging.debug(f"Process {process_name} được đánh giá mặc định là rủi ro trung bình")
        return (1, f"⚠️ RỦI RO TRUNG BÌNH: {process_name} không phải là tiến trình hệ thống quan trọng "
                   f"nhưng cũng không phải ứng dụng thông thường. Hãy cẩn thận khi kill.")

    except Exception as e:
        logging.exception(f"Lỗi khi đánh giá rủi ro cho process {process_name}: {str(e)}")
        return (1, f"⚠️ RỦI RO KHÔNG XÁC ĐỊNH: Không thể đánh giá rủi ro cho {process_name}. {str(e)}")

# Hàm kill process
def kill_process(pid):
    """
    Kill một process theo PID

    Args:
        pid: Process ID

    Returns:
        Tuple (thành công, thông báo)
    """
    logging.info(f"Bắt đầu kill process với PID: {pid}")

    try:
        process = psutil.Process(pid)
        process_name = process.name()
        logging.debug(f"Tìm thấy process: {process_name} (PID: {pid})")

        # Kill process
        process.kill()
        logging.info(f"Đã kill thành công process {process_name} (PID: {pid})")

        return (True, f"✅ Đã kill thành công process {process_name} (PID: {pid})")
    except psutil.NoSuchProcess:
        logging.error(f"Process với PID {pid} không tồn tại")
        return (False, f"❌ Process với PID {pid} không tồn tại")
    except psutil.AccessDenied:
        logging.error(f"Không đủ quyền để kill process (PID: {pid})")
        return (False, f"❌ Không đủ quyền để kill process (PID: {pid}). Hãy chạy với quyền Administrator")
    except Exception as e:
        logging.exception(f"Lỗi khi kill process (PID: {pid}): {str(e)}")
        return (False, f"❌ Lỗi khi kill process (PID: {pid}): {str(e)}")

def check_locked_files(folder_path, callback=None):
    """
    Kiểm tra các file bị khóa trong thư mục

    Args:
        folder_path: Đường dẫn thư mục cần kiểm tra
        callback: Hàm callback để cập nhật kết quả (cho chạy bất đồng bộ)

    Returns:
        Chuỗi kết quả nếu không có callback, hoặc None nếu có callback
        Nếu có callback, trả về dict chứa thông tin process
    """
    logging.debug(f"Bắt đầu kiểm tra file bị khóa trong thư mục: {folder_path}")

    # Kiểm tra handle.exe tồn tại
    handle_exe = HANDLE_EXE
    handle_name = os.path.basename(handle_exe)
    logging.debug(f"Sử dụng handle.exe: {handle_exe}")

    if not os.path.exists(handle_exe):
        logging.error(f"Không tìm thấy {handle_name}")
        result = f"❌ Không tìm thấy {handle_name}. Tải từ: https://learn.microsoft.com/en-us/sysinternals/downloads/handle và đặt vào thư mục Handle"
        if callback:
            callback(result, None)
            return
        return result

    try:
        # Hiển thị thông báo đang chạy nếu có callback
        if callback:
            logging.debug("Gọi callback với thông báo đang kiểm tra")
            callback("⏳ Đang kiểm tra, vui lòng đợi...", None)

        # Chạy handle.exe với đường dẫn thư mục
        # Sử dụng tham số -a để hiển thị tất cả các handle
        logging.debug(f"Chạy lệnh: {handle_exe} -a /accepteula")
        result = subprocess.run([handle_exe, "-a", "/accepteula"],
                               capture_output=True, text=True, timeout=60)

        logging.debug(f"Kết quả trả về: exit code={result.returncode}")
        if result.returncode != 0:
            logging.error(f"Lỗi khi chạy handle.exe: {result.stderr}")

        logging.debug(f"Kích thước output: {len(result.stdout)} ký tự")

        # Phân tích kết quả
        lines = result.stdout.splitlines()
        logging.debug(f"Số dòng output: {len(lines)}")

        locked_files = {}  # Sử dụng dict để nhóm theo process
        process_info_dict = {}  # Lưu thông tin chi tiết về process

        # Pattern để trích xuất PID từ output của handle.exe
        pid_pattern = re.compile(r'(\S+)\s+pid:\s+(\d+)\s+(.*)')
        logging.debug(f"Sử dụng pattern: {pid_pattern.pattern}")

        # Lấy thông tin về các process trước
        current_process = None
        current_pid = None
        current_details = None

        # Thêm debug info vào kết quả
        result_debug = ["=== DEBUG: Handle.exe Output ==="]
        result_debug.extend(lines[:100])  # Chỉ lấy 100 dòng đầu để tránh quá dài
        if len(lines) > 100:
            result_debug.append(f"... và {len(lines) - 100} dòng khác")
        result_debug.append("=== END DEBUG ===\n")

        logging.debug(f"Bắt đầu phân tích {len(lines)} dòng output")
        process_count = 0
        file_count = 0
        matched_file_count = 0

        for i, line in enumerate(lines):
            # Kiểm tra nếu là dòng thông tin process mới
            pid_match = pid_pattern.match(line)
            if pid_match:
                process_count += 1
                current_process = pid_match.group(1)
                current_pid = int(pid_match.group(2))
                current_details = pid_match.group(3)
                logging.debug(f"Tìm thấy process: {current_process} (PID: {current_pid})")
                continue

            # Kiểm tra nếu là dòng thông tin file
            if ":" in line and current_process:
                file_count += 1
                parts = line.split(":", 1)  # Chỉ tách thành 2 phần
                if len(parts) >= 2:
                    file_path = parts[1].strip()

                    # Kiểm tra xem file có thuộc thư mục cần kiểm tra không
                    try:
                        norm_file = os.path.normpath(file_path).lower()
                        norm_folder = os.path.normpath(folder_path).lower()

                        logging.debug(f"So sánh: {norm_file} với {norm_folder}")

                        # Nếu file thuộc thư mục cần kiểm tra hoặc là thư mục con
                        if norm_file.startswith(norm_folder):
                            matched_file_count += 1
                            logging.debug(f"Tìm thấy file bị chiếm dụng: {file_path} bởi {current_process}")

                            # Lưu thông tin process
                            process_key = f"{current_process} (PID: {current_pid})"
                            if process_key not in process_info_dict:
                                process_info_dict[process_key] = {
                                    'name': current_process,
                                    'pid': current_pid,
                                    'details': current_details,
                                    'files': []
                                }

                            process_info_dict[process_key]['files'].append(file_path)

                            # Nhóm theo process
                            if process_key not in locked_files:
                                locked_files[process_key] = []
                            locked_files[process_key].append(file_path)
                    except Exception as e:
                        logging.error(f"Lỗi khi xử lý đường dẫn: {e}")

        logging.debug(f"Kết quả phân tích: {process_count} processes, {file_count} files, {matched_file_count} files bị chiếm dụng")
        logging.debug(f"Số lượng processes chiếm dụng file: {len(locked_files)}")

        # Tạo kết quả
        logging.debug("Bắt đầu tạo kết quả")

        if locked_files:
            logging.info(f"Tìm thấy {len(locked_files)} tiến trình đang chiếm dụng file")
            output = [f"🔒 Các file đang bị chiếm dụng ({len(locked_files)} tiến trình):\n"]

            for process, files in locked_files.items():
                logging.debug(f"Process {process}: {len(files)} files")
                output.append(f"\n📌 Process: {process}")
                for file in files:
                    output.append(f"  - {file}")

            # Thêm thông tin debug
            output.append("\n\n" + "\n".join(result_debug))

            result_text = "\n".join(output)
        else:
            logging.info("Không tìm thấy file nào bị chiếm dụng")
            # Thêm thông tin debug vào kết quả trống
            debug_text = "\n\n" + "\n".join(result_debug)
            result_text = f"✅ Không có file nào bị chiếm dụng trong thư mục này.\n\nThư mục kiểm tra: {folder_path}{debug_text}"
            process_info_dict = None

        # Trả về kết quả
        logging.debug("Hoàn thành kiểm tra, trả về kết quả")
        if callback:
            logging.debug("Gọi callback với kết quả")
            callback(result_text, process_info_dict)
            return
        return result_text

    except subprocess.TimeoutExpired:
        logging.error("Quá thời gian chờ khi chạy handle.exe")
        result = "⚠️ Quá thời gian chờ khi chạy handle.exe. Thư mục có thể quá lớn hoặc có vấn đề truy cập."
        if callback:
            callback(result, None)
            return
        return result
    except Exception as e:
        logging.exception(f"Lỗi không xác định khi kiểm tra file bị khóa: {str(e)}")
        result = f"❌ Lỗi: {str(e)}"
        if callback:
            callback(result, None)
            return
        return result

# ------------------- GUI -------------------
class LockedFileCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Kiểm tra file bị chiếm dụng")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # Biến lưu trữ
        self.folder_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Sẵn sàng")
        self.is_checking = False
        self.check_thread = None
        self.process_info = None  # Lưu thông tin về các process đang chiếm dụng file

        # Tạo giao diện
        self.create_widgets()

        # Tự động điền thư mục hiện tại
        self.folder_var.set(os.getcwd())

        # Thiết lập xử lý khi đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame chọn thư mục
        folder_frame = ttk.LabelFrame(main_frame, text="Thư mục cần kiểm tra", padding="5")
        folder_frame.pack(fill=tk.X, pady=5)

        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_var, width=70)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        browse_btn = ttk.Button(folder_frame, text="Chọn...", command=self.browse_folder)
        browse_btn.pack(side=tk.LEFT, padx=5)

        # Frame nút điều khiển
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        self.check_btn = ttk.Button(
            control_frame,
            text="🔍 Kiểm tra",
            command=self.run_check,
            style="Accent.TButton"
        )
        self.check_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            control_frame,
            text="⛔ Dừng",
            command=self.stop_check,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        save_btn = ttk.Button(
            control_frame,
            text="💾 Lưu kết quả",
            command=self.save_results
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        # Thanh trạng thái
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)

        ttk.Label(status_frame, text="Trạng thái:").pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)

        # Khung kết quả
        result_frame = ttk.LabelFrame(main_frame, text="Kết quả tổng quan", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Tạo container cho kết quả
        result_container = ttk.Frame(result_frame)
        result_container.pack(fill=tk.BOTH, expand=True)

        # Frame chứa bảng tiến trình
        process_frame = ttk.Frame(result_container)
        process_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tạo bảng tiến trình với Treeview
        columns = ("process", "pid", "files", "risk", "action")
        self.process_tree = ttk.Treeview(process_frame, columns=columns, show="headings", selectmode="browse")

        # Định nghĩa các cột
        self.process_tree.heading("process", text="Tiến trình")
        self.process_tree.heading("pid", text="PID")
        self.process_tree.heading("files", text="Số file")
        self.process_tree.heading("risk", text="Mức độ rủi ro")
        self.process_tree.heading("action", text="Hành động")

        # Định nghĩa độ rộng cột
        self.process_tree.column("process", width=200, anchor="w")
        self.process_tree.column("pid", width=70, anchor="center")
        self.process_tree.column("files", width=70, anchor="center")
        self.process_tree.column("risk", width=150, anchor="center")
        self.process_tree.column("action", width=100, anchor="center")

        # Thêm scrollbar cho bảng
        tree_scrollbar = ttk.Scrollbar(process_frame, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=tree_scrollbar.set)

        # Đặt vị trí bảng và scrollbar
        self.process_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")

        # Binding sự kiện chọn process và click vào nút kill
        self.process_tree.bind("<<TreeviewSelect>>", self.on_process_select)
        self.process_tree.bind("<ButtonRelease-1>", self.kill_selected_process)

        # Frame thông tin chi tiết về tiến trình
        info_frame = ttk.LabelFrame(result_container, text="Thông tin chi tiết", padding="5")
        info_frame.pack(fill=tk.X, pady=5, padx=5)

        # Text hiển thị thông tin process
        self.process_info_text = scrolledtext.ScrolledText(
            info_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=6
        )
        self.process_info_text.pack(fill=tk.BOTH, expand=True)
        self.process_info_text.config(state=tk.DISABLED)

        # Tạo style cho các tag
        self.process_tree.tag_configure('low_risk', background='#e6ffe6')  # Xanh nhạt
        self.process_tree.tag_configure('medium_risk', background='#fff2e6')  # Cam nhạt
        self.process_tree.tag_configure('high_risk', background='#ffe6e6')  # Đỏ nhạt

        # Tạo một text box ẩn để lưu kết quả chi tiết (không hiển thị)
        self.output_box = scrolledtext.ScrolledText(self.root)
        self.output_box.pack_forget()

        # Thêm menu
        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Chọn thư mục...", command=self.browse_folder)
        file_menu.add_command(label="Lưu kết quả...", command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Thoát", command=self.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)

        # Menu Công cụ
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="🔍 Kiểm tra", command=self.run_check)
        tools_menu.add_command(label="Xóa kết quả", command=self.clear_results)
        menubar.add_cascade(label="Công cụ", menu=tools_menu)

        # Menu Trợ giúp
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Hướng dẫn", command=self.show_help)
        help_menu.add_command(label="Về ứng dụng", command=self.show_about)
        menubar.add_cascade(label="Trợ giúp", menu=help_menu)

        self.root.config(menu=menubar)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_var.set(folder_selected)

    def update_output(self, text, process_info=None):
        logging.debug("Cập nhật kết quả từ thread kiểm tra")

        # Lưu kết quả chi tiết vào output_box ẩn
        self.output_box.delete(1.0, tk.END)
        self.output_box.insert(tk.END, text)

        # Cập nhật trạng thái
        if process_info and len(process_info) > 0:
            logging.info(f"Tìm thấy {len(process_info)} tiến trình đang chiếm dụng file")
            self.status_var.set(f"Tìm thấy {len(process_info)} tiến trình đang chiếm dụng file")
        else:
            logging.info("Không tìm thấy file bị chiếm dụng")
            self.status_var.set("Hoàn thành - Không tìm thấy file bị chiếm dụng")

        # Kích hoạt lại nút kiểm tra
        logging.debug("Cập nhật trạng thái giao diện")
        self.check_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.is_checking = False

        # Cập nhật thông tin process
        logging.debug("Cập nhật thông tin process")
        self.process_info = process_info
        self.update_process_list()

    def update_process_list(self):
        logging.debug("Cập nhật danh sách process trong bảng")

        # Xóa tất cả các mục trong bảng
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)

        # Xóa thông tin process
        self.process_info_text.config(state=tk.NORMAL)
        self.process_info_text.delete(1.0, tk.END)
        self.process_info_text.config(state=tk.DISABLED)

        # Nếu không có process nào, thoát
        if not self.process_info:
            logging.debug("Không có process nào để hiển thị")
            return

        # Thêm các process vào bảng
        logging.debug(f"Thêm {len(self.process_info)} process vào bảng")
        for process_key, process_data in self.process_info.items():
            pid = process_data['pid']
            process_name = process_data['name']
            file_count = len(process_data['files'])

            logging.debug(f"Xử lý process: {process_name} (PID: {pid}) - {file_count} files")

            # Đánh giá rủi ro
            risk_level, risk_short = self.get_risk_info(pid, process_name)
            logging.debug(f"Đánh giá rủi ro: {risk_short} (level: {risk_level})")

            # Xác định tag dựa trên mức độ rủi ro
            tag = 'low_risk'
            if risk_level == 1:
                tag = 'medium_risk'
            elif risk_level == 2:
                tag = 'high_risk'

            # Thêm vào bảng với nút Kill
            item_id = self.process_tree.insert('', 'end', values=(
                process_name,
                pid,
                file_count,
                risk_short,
                "Kill"
            ), tags=(tag,))

            # Lưu trữ item_id để dễ dàng tìm kiếm sau này
            process_data['item_id'] = item_id

        logging.debug("Hoàn thành cập nhật danh sách process")

    def get_risk_info(self, pid, process_name):
        """Trả về thông tin rủi ro ngắn gọn cho bảng và thông tin chi tiết"""
        risk_level, _ = assess_process_risk(pid, process_name)

        # Tạo thông tin ngắn gọn cho bảng
        if risk_level == 0:
            risk_short = "✅ Thấp"
        elif risk_level == 1:
            risk_short = "⚠️ Trung bình"
        else:
            risk_short = "🛑 Cao"

        return risk_level, risk_short

    def on_process_select(self, _):
        # Lấy item được chọn
        selection = self.process_tree.selection()
        if not selection:
            return

        item_id = selection[0]

        # Tìm process_key tương ứng với item_id
        process_key = None
        for key, data in self.process_info.items():
            if data.get('item_id') == item_id:
                process_key = key
                break

        if not process_key:
            return

        # Hiển thị thông tin process
        process_data = self.process_info[process_key]
        pid = process_data['pid']
        process_name = process_data['name']

        # Đánh giá rủi ro
        risk_level, risk_desc = assess_process_risk(pid, process_name)

        # Hiển thị thông tin
        self.process_info_text.config(state=tk.NORMAL)
        self.process_info_text.delete(1.0, tk.END)

        # Thêm thông tin cơ bản
        self.process_info_text.insert(tk.END, f"Tên: {process_name}\n")
        self.process_info_text.insert(tk.END, f"PID: {pid}\n")
        self.process_info_text.insert(tk.END, f"Chi tiết: {process_data['details']}\n")
        self.process_info_text.insert(tk.END, f"Số file bị chiếm dụng: {len(process_data['files'])}\n\n")

        # Thêm danh sách file bị chiếm dụng
        self.process_info_text.insert(tk.END, "File bị chiếm dụng:\n")
        for i, file in enumerate(process_data['files'], 1):
            if i <= 5:  # Chỉ hiển thị tối đa 5 file
                self.process_info_text.insert(tk.END, f"  {i}. {file}\n")

        if len(process_data['files']) > 5:
            self.process_info_text.insert(tk.END, f"  ... và {len(process_data['files']) - 5} file khác\n")

        self.process_info_text.insert(tk.END, "\n")

        # Thêm thông tin rủi ro với màu sắc tương ứng
        self.process_info_text.insert(tk.END, risk_desc)

        # Đặt màu cho phần đánh giá rủi ro
        if risk_level == 2:  # Cao
            self.process_info_text.tag_add("risk", f"{6 + min(5, len(process_data['files']))}.0", "end")
            self.process_info_text.tag_config("risk", foreground="red")
        elif risk_level == 1:  # Trung bình
            self.process_info_text.tag_add("risk", f"{6 + min(5, len(process_data['files']))}.0", "end")
            self.process_info_text.tag_config("risk", foreground="orange")
        else:  # Thấp
            self.process_info_text.tag_add("risk", f"{6 + min(5, len(process_data['files']))}.0", "end")
            self.process_info_text.tag_config("risk", foreground="green")

        self.process_info_text.config(state=tk.DISABLED)

    def kill_selected_process(self, event=None):
        logging.debug("Bắt đầu xử lý kill process")

        # Nếu được gọi từ sự kiện click, kiểm tra xem có phải click vào cột action không
        if event:
            # Lấy cột được click
            region = self.process_tree.identify_region(event.x, event.y)
            if region != "cell":
                logging.debug(f"Click không phải vào cell (region: {region})")
                return

            column = self.process_tree.identify_column(event.x)
            if column != "#5":  # Cột action là cột thứ 5
                logging.debug(f"Click không phải vào cột action (column: {column})")
                return

            logging.debug("Đã click vào nút Kill trong bảng")

        # Lấy item được chọn
        selection = self.process_tree.selection()
        if not selection:
            logging.debug("Không có item nào được chọn")
            return

        item_id = selection[0]
        logging.debug(f"Item được chọn: {item_id}")

        # Lấy thông tin process từ item được chọn
        values = self.process_tree.item(item_id, 'values')
        process_name = values[0]
        pid = int(values[1])
        logging.info(f"Chuẩn bị kill process: {process_name} (PID: {pid})")

        # Tìm process_key tương ứng
        process_key = None
        for key, data in self.process_info.items():
            if data.get('pid') == pid:
                process_key = key
                break

        if not process_key:
            logging.warning(f"Không tìm thấy process_key cho PID: {pid}")
            return

        # Đánh giá rủi ro
        risk_level, risk_desc = assess_process_risk(pid, process_name)
        logging.debug(f"Đánh giá rủi ro: level={risk_level}, desc={risk_desc}")

        # Hiển thị hộp thoại xác nhận với thông tin rủi ro
        confirm_message = f"Bạn có chắc chắn muốn kill process {process_name} (PID: {pid})?\n\n{risk_desc}"

        if messagebox.askyesno("Xác nhận kill process", confirm_message):
            logging.info(f"Người dùng xác nhận kill process {process_name} (PID: {pid})")

            # Thực hiện kill process
            success, message = kill_process(pid)
            logging.debug(f"Kết quả kill process: success={success}, message={message}")

            if success:
                logging.info(f"Đã kill thành công process {process_name} (PID: {pid})")

                # Cập nhật trạng thái
                self.status_var.set(f"Đã kill process {process_name}")

                # Xóa process khỏi bảng
                self.process_tree.delete(item_id)
                del self.process_info[process_key]

                # Xóa thông tin process
                self.process_info_text.config(state=tk.NORMAL)
                self.process_info_text.delete(1.0, tk.END)
                self.process_info_text.config(state=tk.DISABLED)

                # Cập nhật thông báo trong status bar
                self.status_var.set(message)

                # Nếu không còn process nào, chạy lại kiểm tra
                if not self.process_info:
                    logging.debug("Không còn process nào, chạy lại kiểm tra")
                    self.run_check()
            else:
                logging.error(f"Lỗi khi kill process: {message}")
                # Hiển thị thông báo lỗi
                messagebox.showerror("Lỗi", message)
        else:
            logging.info(f"Người dùng hủy kill process {process_name} (PID: {pid})")

    def run_check(self):
        logging.info("Bắt đầu kiểm tra file bị chiếm dụng từ giao diện")

        folder = self.folder_var.get().strip()
        logging.debug(f"Thư mục cần kiểm tra: {folder}")

        if not folder or not os.path.exists(folder):
            logging.warning(f"Thư mục không hợp lệ: {folder}")
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục hợp lệ.")
            return

        # Vô hiệu hóa nút kiểm tra và kích hoạt nút dừng
        logging.debug("Cập nhật trạng thái giao diện")
        self.check_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_checking = True
        self.status_var.set("Đang kiểm tra...")

        # Xóa kết quả cũ
        logging.debug("Xóa kết quả cũ")
        self.output_box.delete(1.0, tk.END)

        # Xóa danh sách process cũ
        logging.debug("Xóa danh sách process cũ")
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        self.process_info = None

        # Xóa thông tin process
        self.process_info_text.config(state=tk.NORMAL)
        self.process_info_text.delete(1.0, tk.END)
        self.process_info_text.config(state=tk.DISABLED)

        # Chạy kiểm tra trong luồng riêng
        logging.debug("Khởi động thread kiểm tra")
        self.check_thread = threading.Thread(
            target=check_locked_files,
            args=(folder, self.update_output)
        )
        self.check_thread.daemon = True
        self.check_thread.start()
        logging.debug("Đã khởi động thread kiểm tra")

    def stop_check(self):
        if self.is_checking:
            self.status_var.set("Đã hủy")
            self.check_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.is_checking = False
            # Không thể dừng subprocess trực tiếp, nhưng có thể đánh dấu là đã hủy
            self.output_box.insert(tk.END, "\n\n⚠️ Đã hủy thao tác kiểm tra.")

    def save_results(self):
        # Kiểm tra xem có tiến trình nào không
        if not self.process_info:
            # Lấy nội dung từ output_box ẩn
            content = self.output_box.get(1.0, tk.END).strip()
            if not content:
                messagebox.showinfo("Thông báo", "Không có kết quả để lưu.")
                return
        else:
            # Tạo nội dung từ bảng tiến trình
            content = "DANH SÁCH TIẾN TRÌNH ĐANG CHIẾM DỤNG FILE\n"
            content += "=" * 50 + "\n\n"

            for process_key, process_data in self.process_info.items():
                pid = process_data['pid']
                process_name = process_data['name']
                file_count = len(process_data['files'])

                # Đánh giá rủi ro
                _, risk_desc = assess_process_risk(pid, process_name)

                content += f"Tiến trình: {process_name}\n"
                content += f"PID: {pid}\n"
                content += f"Số file bị chiếm dụng: {file_count}\n"
                content += f"Chi tiết: {process_data['details']}\n"
                content += f"Đánh giá rủi ro: {risk_desc}\n\n"

                content += "Danh sách file bị chiếm dụng:\n"
                for i, file in enumerate(process_data['files'], 1):
                    content += f"  {i}. {file}\n"

                content += "\n" + "-" * 50 + "\n\n"

        # Tạo tên file mặc định với timestamp
        default_filename = f"locked_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=default_filename
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Thành công", f"Đã lưu kết quả vào file:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {str(e)}")

    def clear_results(self):
        self.output_box.delete(1.0, tk.END)
        self.status_var.set("Đã xóa kết quả")

    def show_help(self):
        help_text = """
🔍 HƯỚNG DẪN SỬ DỤNG

1. Chọn thư mục cần kiểm tra bằng nút "Chọn..."
2. Nhấn nút "🔍 Kiểm tra" để bắt đầu quá trình kiểm tra
3. Danh sách các tiến trình đang chiếm dụng file sẽ hiển thị trong bảng
4. Chọn một tiến trình trong bảng để xem thông tin chi tiết và đánh giá rủi ro
5. Nhấn vào ô "Kill" trong cột "Hành động" để dừng tiến trình
6. Xác nhận trong hộp thoại hiện ra để kill tiến trình
7. Bạn có thể lưu kết quả bằng nút "💾 Lưu kết quả"

Lưu ý:
- Quá trình kiểm tra có thể mất một chút thời gian tùy thuộc vào kích thước thư mục
- Việc kill process có thể gây mất dữ liệu chưa lưu hoặc ảnh hưởng đến hệ thống
- Màu nền của mỗi dòng trong bảng tiến trình thể hiện mức độ rủi ro:
  + Xanh nhạt: Rủi ro thấp
  + Cam nhạt: Rủi ro trung bình
  + Đỏ nhạt: Rủi ro cao
- Hãy đọc kỹ thông tin đánh giá rủi ro trước khi kill process
        """
        messagebox.showinfo("Hướng dẫn sử dụng", help_text)

    def show_about(self):
        about_text = """
🔍 Kiểm tra File Bị Chiếm Dụng

Phiên bản: 1.4.0
Công cụ giúp kiểm tra các file đang bị khóa (lock) bởi tiến trình nào trong hệ thống.

Tính năng:
- Kiểm tra file bị chiếm dụng trong thư mục
- Hiển thị danh sách tiến trình dạng bảng với màu sắc theo mức độ rủi ro
- Đánh giá rủi ro khi kill tiến trình
- Kill tiến trình trực tiếp từ bảng với xác nhận
- Hiển thị thông tin chi tiết về tiến trình được chọn
- Lưu kết quả kiểm tra

Sử dụng:
- Python và Tkinter cho giao diện
- Handle.exe từ Sysinternals (Microsoft)
- psutil cho quản lý tiến trình

© 2023 - MIT License
        """
        messagebox.showinfo("Về ứng dụng", about_text)

    def on_closing(self):
        if self.is_checking:
            if messagebox.askyesno("Xác nhận", "Đang trong quá trình kiểm tra. Bạn có chắc muốn thoát?"):
                self.root.destroy()
        else:
            self.root.destroy()

# Khởi chạy ứng dụng
if __name__ == "__main__":
    root = tk.Tk()

    # Tạo style cho các widget
    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 10))
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("TLabelframe", font=("Segoe UI", 10))
    style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))

    # Tạo style cho nút Accent
    style.configure("Accent.TButton", background="#007bff")

    app = LockedFileCheckerApp(root)
    root.mainloop()

# 🔍 Kiểm tra File DLL Bị Chiếm Dụng trong Thư Mục (Python GUI)

Đây là một công cụ giao diện đơn giản viết bằng Python giúp bạn **kiểm tra các file trong một thư mục có đang bị tiến trình nào đó khóa (lock)** hay không. Điều này rất hữu ích trong các tình huống như:

* Không thể ghi đè `.dll` khi giải nén vào thư mục IIS.
* Lỗi `Access is denied` khi deploy hoặc cập nhật ứng dụng.
* Muốn kiểm tra tiến trình nào đang giữ file trong hệ thống Windows.

---

## 🗈️ Giao Diện Ứng Dụng

* Giao diện đơn giản với ô nhập đường dẫn thư mục.
* Nút chọn thư mục bằng trình duyệt hệ thống.
* Nút "🔍 Kiểm tra" để hiển thị danh sách các file bị khóa.
* Danh sách các tiến trình đang chiếm dụng file.
* Thông tin chi tiết về tiến trình và đánh giá rủi ro.
* Nút "⚠️ Kill Process" để dừng tiến trình đang chiếm dụng file.
* Kết quả hiển thị chi tiết trong cửa sổ cuộn.

---

## ✅ Yêu Cầu Hệ Thống

### 1. Python

* Python 3.7 trở lên

### 2. Thư viện Python

Cài đặt thư viện cần thiết:

```bash
pip install psutil
```

Thư viện `psutil` được sử dụng để quản lý và kill các tiến trình.

### 3. `handle64.exe` từ Sysinternals

* Tải bộ công cụ Handle từ trang chính thức của Microsoft:
  👉 [https://learn.microsoft.com/en-us/sysinternals/downloads/handle](https://learn.microsoft.com/en-us/sysinternals/downloads/handle)

* Sau khi tải về:

  * Giải nén và đặt các file vào thư mục `Handle` trong cùng thư mục với file `.py`
  * Ứng dụng sẽ sử dụng `handle64.exe` cho hệ thống 64-bit (phiên bản phổ biến nhất)
  * Nếu bạn đang sử dụng hệ thống 32-bit, hãy chỉnh sửa biến `HANDLE_EXE` trong file `locked_file_checker_gui.py` thành `"Handle\\handle.exe"`

---

## 🚀 Cách Sử Dụng

### 1. Chạy ứng dụng

```bash
python locked_file_checker_gui.py
```

### 2. Thao tác trong giao diện

* Nhấn **"Chọn..."** để chọn thư mục cần kiểm tra.
* Nhấn **"🧪 Kiểm tra"**.# 🔍 Kiểm tra File DLL Bị Chiếm Dụng trong Thư Mục (Python GUI)

Đây là một công cụ giao diện đơn giản viết bằng Python giúp bạn **kiểm tra các file trong một thư mục có đang bị tiến trình nào đó khóa (lock)** hay không. Điều này rất hữu ích trong các tình huống như:

* Không thể ghi đè `.dll` khi giải nén vào thư mục IIS.
* Lỗi `Access is denied` khi deploy hoặc cập nhật ứng dụng.
* Muốn kiểm tra tiến trình nào đang giữ file trong hệ thống Windows.

---

## 🗈️ Giao Diện Ứng Dụng

* Giao diện đơn giản với ô nhập đường dẫn thư mục.
* Nút chọn thư mục bằng trình duyệt hệ thống.
* Nút "🔍 Kiểm tra" để hiển thị danh sách các file bị khóa.
* Danh sách các tiến trình đang chiếm dụng file.
* Thông tin chi tiết về tiến trình và đánh giá rủi ro.
* Nút "⚠️ Kill Process" để dừng tiến trình đang chiếm dụng file.
* Kết quả hiển thị chi tiết trong cửa sổ cuộn.

---

## ✅ Yêu Cầu Hệ Thống

### 1. Python

* Python 3.7 trở lên

### 2. Thư viện Python

Cài đặt thư viện cần thiết:

```bash
pip install psutil
```

Thư viện `psutil` được sử dụng để quản lý và kill các tiến trình.

### 3. `handle64.exe` từ Sysinternals

* Tải bộ công cụ Handle từ trang chính thức của Microsoft:
  👉 [https://learn.microsoft.com/en-us/sysinternals/downloads/handle](https://learn.microsoft.com/en-us/sysinternals/downloads/handle)

* Sau khi tải về:

  * Giải nén và đặt các file vào thư mục `Handle` trong cùng thư mục với file `.py`
  * Ứng dụng sẽ sử dụng `handle64.exe` cho hệ thống 64-bit (phiên bản phổ biến nhất)
  * Nếu bạn đang sử dụng hệ thống 32-bit, hãy chỉnh sửa biến `HANDLE_EXE` trong file `locked_file_checker_gui.py` thành `"Handle\\handle.exe"`

---

## 🚀 Cách Sử Dụng

### 1. Chạy ứng dụng

```bash
python locked_file_checker_gui.py
```

### 2. Thao tác trong giao diện

* Nhấn **"Chọn..."** để chọn thư mục cần kiểm tra.
* Nhấn **"🧪 Kiểm tra"**.
* Kết quả sẽ hiển thị trong hộp văn bản bên dưới, liệt kê các file bị chiếm và tiến trình đang giữ.

---

## 📆 Đóng Gói Thành File `.exe` (Tuỳ Chọn)

Nếu bạn muốn chạy ứng dụng mà không cần cài Python, bạn có thể đóng gói thành `.exe` bằng `PyInstaller`:

```bash
pip install pyinstaller
pyinstaller --onefile locked_file_checker_gui.py
```

Sau khi hoàn tất, file `.exe` sẽ nằm trong thư mục `dist/`.

---

## 🛠 Ví Dụ Ứng Dụng

* Kiểm tra lỗi khi giải nén `.rar` vào thư mục `C:\inetpub\wwwroot\...` mà gặp lỗi `Access is denied`.
* Tìm ra process nào đang chiếm dụng file `AOMS.Application.Contracts.dll`, `Autofac.dll`, v.v.
* Dọn tiến trình trước khi deploy hệ thống bằng batch script.

---

## 📄 Giấy Phép

MIT License

---

**Tác giả:** Bạn có thể thêm tên hoặc nhóm phát triển của mình ở đây.
**Công nghệ sử dụng:** Python, Tkinter, Sysinternals Handle (handle64.exe)

* Kết quả sẽ hiển thị trong hộp văn bản bên dưới, liệt kê các file bị chiếm và tiến trình đang giữ.

---

## 📆 Đóng Gói Thành File `.exe` (Tuỳ Chọn)

Nếu bạn muốn chạy ứng dụng mà không cần cài Python, bạn có thể đóng gói thành `.exe` bằng `PyInstaller`:

```bash
pip install pyinstaller
pyinstaller --onefile locked_file_checker_gui.py
```

Sau khi hoàn tất, file `.exe` sẽ nằm trong thư mục `dist/`.

---

## 🛠 Ví Dụ Ứng Dụng

* Kiểm tra lỗi khi giải nén `.rar` vào thư mục `C:\inetpub\wwwroot\...` mà gặp lỗi `Access is denied`.
* Tìm ra process nào đang chiếm dụng file `AOMS.Application.Contracts.dll`, `Autofac.dll`, v.v.
* Dọn tiến trình trước khi deploy hệ thống bằng batch script.

---

## 📄 Giấy Phép

MIT License

---

**Tác giả:** Bạn có thể thêm tên hoặc nhóm phát triển của mình ở đây.
**Công nghệ sử dụng:** Python, Tkinter, Sysinternals Handle (handle64.exe)
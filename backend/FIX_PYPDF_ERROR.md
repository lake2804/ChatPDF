# Fix pypdf Error

## Vấn đề:
Backend báo lỗi: `pypdf package not found` mặc dù đã cài đặt.

## Nguyên nhân:
Backend đang chạy trong môi trường Python khác không có `pypdf`.

## Giải pháp:

### Bước 1: Kiểm tra môi trường hiện tại
```bash
cd backend
python check_running_backend.py
```

### Bước 2: Kiểm tra health endpoint
```bash
curl http://localhost:8000/health
```

Response sẽ hiển thị:
- Python executable đang dùng
- Package status (pypdf có sẵn không)

### Bước 3: Dừng backend hiện tại
Tìm và kill process đang chạy trên port 8000:
```bash
# Windows PowerShell
netstat -ano | findstr :8000
# Lấy PID và kill:
taskkill /PID <PID> /F

# Hoặc tìm trong Task Manager
```

### Bước 4: Kích hoạt virtual environment (nếu có)
```bash
cd backend

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Bước 5: Cài đặt dependencies
```bash
pip install -r requirements.txt
# Hoặc cài riêng:
pip install pypdf pymupdf
```

### Bước 6: Kiểm tra pypdf
```bash
python -c "import pypdf; print('pypdf version:', pypdf.__version__)"
```

### Bước 7: Khởi động lại backend
```bash
# Đảm bảo đang trong virtual environment
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

### Bước 8: Kiểm tra lại
```bash
# Test health endpoint
curl http://localhost:8000/health

# Response phải có:
# "packages": {
#   "pypdf": {"available": true, "version": "..."}
# }
```

## Nếu vẫn lỗi:

1. **Kiểm tra Python executable:**
   - Health endpoint sẽ hiển thị Python path
   - Đảm bảo backend dùng cùng Python với môi trường có pypdf

2. **Cài đặt global (nếu không dùng venv):**
```bash
pip install pypdf pymupdf
```

3. **Kiểm tra multiple Python installations:**
```bash
# Windows
where python
where python3

# Chọn đúng Python và cài pypdf vào đó
```

## Quick Fix:
```bash
# 1. Stop backend (Ctrl+C hoặc kill process)

# 2. Activate venv
cd backend
venv\Scripts\activate  # Windows
# hoặc
source venv/bin/activate  # Linux/Mac

# 3. Install pypdf
pip install pypdf

# 4. Restart backend
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```


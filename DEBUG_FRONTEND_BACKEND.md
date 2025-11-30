# Debug Frontend-Backend Connection

## Vấn đề: Frontend báo lỗi nhưng backend hoạt động bình thường

### Các bước kiểm tra:

1. **Kiểm tra Backend đang chạy:**
```bash
# Kiểm tra port 8000
netstat -ano | findstr :8000

# Hoặc test trực tiếp
curl http://localhost:8000/health
```

2. **Kiểm tra Frontend đang chạy:**
```bash
cd frontend
npm run dev
# Frontend sẽ chạy tại http://localhost:3000
```

3. **Kiểm tra Console trong Browser:**
- Mở Developer Tools (F12)
- Xem tab Console để thấy lỗi chi tiết
- Xem tab Network để kiểm tra requests

4. **Test API trực tiếp:**
- Mở file `frontend/test_api.html` trong browser
- Test các endpoint để xem lỗi cụ thể

### Các lỗi thường gặp:

#### 1. CORS Error
**Triệu chứng:** `Access to fetch at 'http://localhost:8000/...' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Giải pháp:**
- Backend đã config CORS với `allow_origins=["*"]` - nên không có vấn đề
- Nếu vẫn lỗi, kiểm tra backend có đang chạy đúng không

#### 2. Network Error / Failed to fetch
**Triệu chứng:** `Failed to fetch` hoặc `NetworkError`

**Giải pháp:**
- Kiểm tra backend có đang chạy: `curl http://localhost:8000/health`
- Kiểm tra firewall không chặn port 8000
- Thử dùng proxy trong Vite (đã config sẵn)

#### 3. 404 Not Found
**Triệu chứng:** `404 Not Found` khi gọi API

**Giải pháp:**
- Kiểm tra URL đúng: `http://localhost:8000/health`
- Kiểm tra backend routes trong `backend/app/api.py`

#### 4. 500 Internal Server Error
**Triệu chứng:** Backend trả về 500

**Giải pháp:**
- Xem logs của backend để biết lỗi cụ thể
- Kiểm tra dependencies: `python check_dependencies.py`
- Kiểm tra .env file có đúng không

### Cách sửa nhanh:

1. **Sử dụng Proxy (Development):**
   - Frontend đã được config để dùng `/api` proxy trong development
   - Vite sẽ tự động forward requests đến `http://localhost:8000`

2. **Sử dụng Direct Connection:**
   - Set environment variable: `VITE_API_BASE=http://localhost:8000`
   - Hoặc sửa trong code: `const API_BASE = 'http://localhost:8000'`

3. **Kiểm tra Backend Logs:**
```bash
cd backend
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
# Xem logs để biết requests có đến không
```

### Test Scripts:

1. **Test Backend:**
```bash
cd backend
python test_backend.py
```

2. **Test Dependencies:**
```bash
cd backend
python check_dependencies.py
```

3. **Test API từ Browser:**
- Mở `frontend/test_api.html` trong browser
- Test các endpoint

### Environment Variables:

Tạo file `.env` trong `frontend/` nếu cần:
```
VITE_API_BASE=http://localhost:8000
```

Hoặc trong `backend/.env`:
```
GOOGLE_API_KEY=your_key_here
QDRANT_URL=http://localhost:6333
```


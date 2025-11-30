# 🚀 Hướng dẫn Deploy ChatPDF Miễn phí

Hướng dẫn chi tiết deploy project ChatPDF hoàn toàn miễn phí sử dụng:
- **Frontend**: Vercel (miễn phí)
- **Backend**: Railway ($5 credit/tháng - đủ cho development)
- **Database**: Qdrant Cloud (1GB free)

---

## 📋 Chuẩn bị

1. **Tài khoản GitHub** (đã có repo: https://github.com/lake2804/ChatPDF)
2. **Google AI API Key**: https://makersuite.google.com/app/apikey
3. **Tài khoản Vercel**: https://vercel.com (đăng ký miễn phí)
4. **Tài khoản Railway**: https://railway.app (đăng ký miễn phí)
5. **Tài khoản Qdrant Cloud**: https://cloud.qdrant.io (đăng ký miễn phí)

---

## Bước 1: Setup Qdrant Cloud (5 phút)

### 1.1. Tạo tài khoản Qdrant Cloud

1. Truy cập https://cloud.qdrant.io
2. Click **"Sign Up"** → Đăng ký bằng email hoặc GitHub
3. Xác nhận email (nếu cần)

### 1.2. Tạo Cluster

1. Sau khi đăng nhập, click **"Create Cluster"**
2. Chọn **Free Tier** (1GB storage)
3. Chọn region gần bạn nhất (ví dụ: `us-east-1`)
4. Đặt tên cluster: `chatpdf-cluster`
5. Click **"Create"**

### 1.3. Lấy Connection URL

1. Vào cluster vừa tạo
2. Copy **API URL** (ví dụ: `https://xxxxx.us-east-1-0.aws.cloud.qdrant.io`)
3. Copy **API Key** (nếu có) - lưu lại để dùng sau

**Lưu ý**: Lưu URL này, bạn sẽ cần nó cho bước 3.

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.uL-ahgaV6A9h0AKBwqWx7mhdQqMQSH4Dhnq-JvvgfzQ

curl \
    -X GET 'https://83eae4b7-cbfc-4077-9d58-1bb4a74473e3.us-east4-0.gcp.cloud.qdrant.io:6333' \
    --header 'api-key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.uL-ahgaV6A9h0AKBwqWx7mhdQqMQSH4Dhnq-JvvgfzQ'

https://83eae4b7-cbfc-4077-9d58-1bb4a74473e3.us-east4-0.gcp.cloud.qdrant.io



---

## Bước 2: Deploy Backend lên Railway (10 phút)

### 2.1. Tạo tài khoản Railway

1. Truy cập https://railway.app
2. Click **"Start a New Project"**
3. Chọn **"Login with GitHub"**
4. Authorize Railway truy cập GitHub

### 2.2. Deploy Backend

1. Trong Railway dashboard, click **"New Project"**
2. Chọn **"Deploy from GitHub repo"**
3. Chọn repository: `lake2804/ChatPDF`
4. Railway sẽ tự động detect Python

### 2.3. Cấu hình Service

1. Click vào service vừa tạo
2. Vào tab **"Settings"**
3. Tìm **"Root Directory"** → Set: `backend`
4. Tìm **"Build Command"** → Để trống (sử dụng Dockerfile)
5. Tìm **"Start Command"** → Set: `uvicorn app.api:app --host 0.0.0.0 --port $PORT`
6. **Quan trọng**: Đảm bảo Railway sử dụng Dockerfile thay vì Nixpacks
   - Vào **Settings** → **Build** → Chọn **"Dockerfile"** thay vì **"Nixpacks"**

### 2.4. Cấu hình Environment Variables

1. Vào tab **"Variables"**
2. Click **"New Variable"** và thêm từng biến sau:

```env
GOOGLE_API_KEY=your_google_api_key_here
QDRANT_URL=https://your-cluster-url.qdrant.io
QDRANT_COLLECTION=multimodal_rag
EMBEDDING_DIM=768
LLM_MODEL=gemini-2.0-flash
VISION_MODEL=gemini-2.0-flash
EMBEDDING_MODEL=text-embedding-004
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DEFAULT_K=5
UPLOAD_DIR=uploads
MAX_FILE_SIZE=52428800
ALLOWED_ORIGINS=*
PORT=8000
```

**Lưu ý**: 
- Thay `your_google_api_key_here` bằng Google API key thật
- Thay `your-cluster-url.qdrant.io` bằng Qdrant Cloud URL từ bước 1

### 2.5. Lấy Backend URL

1. Railway sẽ tự động deploy
2. Vào tab **"Settings"** → **"Networking"**
3. Click **"Generate Domain"** (nếu chưa có)
4. Copy URL (ví dụ: `https://chatpdf-production.up.railway.app`)
5. **Lưu URL này** - bạn sẽ cần cho bước 3

### 2.6. Kiểm tra Backend hoạt động

1. Mở URL backend + `/health` (ví dụ: `https://chatpdf-production.up.railway.app/health`)
2. Nếu thấy JSON response → Backend đã hoạt động ✅

---

## Bước 3: Deploy Frontend lên Vercel (5 phút)

### 3.1. Cập nhật Frontend Code

Trước khi deploy, cần cập nhật API URL trong frontend:

1. Mở file `frontend/src/App.jsx`
2. Tìm dòng:
```javascript
const API_BASE = import.meta.env.VITE_API_BASE || (
  import.meta.env.DEV 
    ? '/api'
    : import.meta.env.PROD
    ? 'https://your-backend-url.railway.app'  // UPDATE THIS
    : 'http://localhost:8000'
)
```

3. Thay `https://your-backend-url.railway.app` bằng Railway URL từ bước 2.5
4. Commit và push lên GitHub:
```bash
git add frontend/src/App.jsx
git commit -m "Update API URL for production"
git push origin main
```

### 3.2. Deploy lên Vercel

**Cách 1: Qua Vercel Dashboard (Khuyến nghị)**

1. Truy cập https://vercel.com
2. Click **"Sign Up"** → Đăng nhập bằng GitHub
3. Click **"Add New Project"**
4. Import repository: `lake2804/ChatPDF`
5. Cấu hình:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
6. Thêm Environment Variable:
   - **Key**: `VITE_API_BASE`
   - **Value**: Railway URL từ bước 2.5 (ví dụ: `https://chatpdf-production.up.railway.app`)
7. Click **"Deploy"**
8. Đợi 2-3 phút để build và deploy

**Cách 2: Qua Vercel CLI**

```bash
# Cài đặt Vercel CLI
npm i -g vercel

# Đăng nhập
vercel login

# Deploy
cd frontend
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? chatpdf-frontend
# - Directory? ./
# - Override settings? No
```

### 3.3. Lấy Frontend URL

1. Sau khi deploy xong, Vercel sẽ cung cấp URL
2. URL có dạng: `https://chatpdf-frontend.vercel.app`
3. **Lưu URL này**

### 3.4. Cập nhật CORS trong Backend

1. Quay lại Railway dashboard
2. Vào **Variables** của backend service
3. Tìm biến `ALLOWED_ORIGINS`
4. Cập nhật giá trị: `https://your-frontend.vercel.app` (thay bằng Vercel URL thật)
5. Railway sẽ tự động redeploy

---

## Bước 4: Kiểm tra và Test

### 4.1. Test Frontend

1. Mở Vercel URL trong browser
2. Đăng nhập/đăng ký
3. Upload một file test (PDF, DOCX, etc.)
4. Đặt câu hỏi về file
5. Kiểm tra xem có nhận được câu trả lời không

### 4.2. Test Backend API

```bash
# Test health endpoint
curl https://your-backend.railway.app/health

# Test upload (nếu có file)
curl -X POST https://your-backend.railway.app/upload \
  -F "file=@test.pdf"
```

### 4.3. Kiểm tra Logs

**Railway Logs:**
1. Vào Railway dashboard
2. Click vào backend service
3. Tab **"Deployments"** → Click deployment mới nhất
4. Xem logs để debug nếu có lỗi

**Vercel Logs:**
1. Vào Vercel dashboard
2. Click vào project
3. Tab **"Deployments"** → Click deployment
4. Xem logs

---

## 🐛 Troubleshooting

### Frontend không kết nối được Backend

**Nguyên nhân:**
- CORS chưa được cấu hình đúng
- API URL sai

**Giải pháp:**
1. Kiểm tra `ALLOWED_ORIGINS` trong Railway có đúng Vercel URL không
2. Kiểm tra `VITE_API_BASE` trong Vercel environment variables
3. Kiểm tra browser console để xem lỗi cụ thể

### Backend lỗi khi upload file

**Nguyên nhân:**
- Qdrant chưa kết nối được
- Google API key sai

**Giải pháp:**
1. Kiểm tra `QDRANT_URL` trong Railway có đúng không
2. Kiểm tra `GOOGLE_API_KEY` có hợp lệ không
3. Xem logs trong Railway để biết lỗi chi tiết

### Qdrant connection error

**Nguyên nhân:**
- URL sai
- API key sai (nếu cần)

**Giải pháp:**
1. Kiểm tra Qdrant Cloud cluster đang active
2. Copy lại URL từ Qdrant Cloud dashboard
3. Đảm bảo URL có format: `https://xxxxx.qdrant.io`

### Railway hết credit

**Giải pháp:**
- Railway free tier có $5 credit/tháng
- Nếu hết, có thể:
  1. Upgrade lên paid plan ($5/tháng)
  2. Hoặc chuyển sang Render (free tier tốt hơn)

---

## 💰 Chi phí

### Free Tier (Đủ cho development/small project):

- **Vercel**: Miễn phí hoàn toàn
  - Unlimited deployments
  - 100GB bandwidth/tháng
  - CDN toàn cầu

- **Railway**: $5 credit/tháng
  - Đủ cho ~500 hours runtime
  - $5 credit = ~100 hours nếu dùng hết

- **Qdrant Cloud**: 1GB free
  - Đủ cho hàng nghìn documents nhỏ
  - Nếu cần thêm: $25/tháng cho 1GB+

**Tổng chi phí: $0/tháng** (nếu dùng trong free tier limits)

### Nếu cần scale lên:

- **Vercel Pro**: $20/tháng (nếu cần nhiều bandwidth)
- **Railway**: $5-20/tháng (tùy usage)
- **Qdrant Cloud**: $25/tháng (1GB+)

**Tổng: ~$50-65/tháng** cho production scale

---

## ✅ Checklist Deploy

- [ ] Tạo Qdrant Cloud cluster và lấy URL
- [ ] Deploy backend lên Railway
- [ ] Cấu hình environment variables trong Railway
- [ ] Lấy Railway backend URL
- [ ] Cập nhật API URL trong frontend code
- [ ] Deploy frontend lên Vercel
- [ ] Cấu hình CORS trong backend
- [ ] Test upload file
- [ ] Test chat functionality
- [ ] Kiểm tra logs nếu có lỗi

---

## 🎯 Kết quả

Sau khi hoàn thành, bạn sẽ có:

- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.railway.app`
- **Database**: Qdrant Cloud cluster

Project đã được deploy hoàn toàn miễn phí và sẵn sàng sử dụng! 🎉

---

## 📞 Cần hỗ trợ?

Nếu gặp vấn đề, mở issue trên GitHub: https://github.com/lake2804/ChatPDF/issues


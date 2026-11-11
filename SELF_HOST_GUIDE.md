# Hướng Dẫn Phát Triển & Tự Host Treg (Tools Registry)

Tài liệu này hướng dẫn chi tiết cách vận hành, cấu hình và phát triển tiếp hệ thống **Treg** tự host (Self-Hosted) cho cá nhân hoặc doanh nghiệp.

---

## 1. Kiến trúc hệ thống khi Self-Host

Khi tự host, Treg hoạt động như một **Cổng API Gateway & Vault Quản Lý Khóa Tập Trung**:
* **Bảo mật tuyệt đối**: Nhân viên và AI Agent (Claude Code, Cursor, Windsurf, v.v.) chỉ cần 1 token duy nhất (`X-Treg-Token`). API Key thực tế (OpenAI, Stripe, Meta Ads, Zalo OA...) được lưu mã hóa bằng chuẩn Fernet phía máy chủ.
* **Tích hợp sẵn Catalog 990+ công cụ**: Hỗ trợ tìm kiếm, tra cứu tài liệu và tham số API của hàng trăm nhà cung cấp.
* **Song ngữ Việt - Anh**: Giao diện hỗ trợ chuyển đổi linh hoạt giữa Tiếng Việt (`🇻🇳 VI`) và Tiếng Anh (`🇬🇧 EN`).

---

## 2. Các phương thức chạy hệ thống

### Cách 1: Chạy trực tiếp trên máy Mac / Linux (Chế độ Development)

Stack dev hỗ trợ Hot Reload cho cả Backend (FastAPI) và Frontend (Vite):

```bash
# 1. Khởi động hệ thống (chạy ngầm qua tmux)
./scripts/dev-local.sh up

# 2. Kiểm tra trạng thái
./scripts/dev-local.sh status

# 3. Xem log thời gian thực
./scripts/dev-local.sh logs

# 4. Tắt hệ thống khi không dùng
./scripts/dev-local.sh down
```

* **Địa chỉ truy cập**: [http://localhost:18790](http://localhost:18790)
* **API Documentation (OpenAPI / Swagger)**: [http://localhost:18790/docs](http://localhost:18790/docs)

---

### Cách 2: Triển khai bằng Docker Compose (Chế độ Production / Server)

Dự án đã tích hợp sẵn `Dockerfile` multi-stage (Node.js build frontend + Python 3.13 UV runtime) và `docker-compose.yml`:

```bash
# 1. Tạo file cấu hình môi trường
cp .env.example .env  # Hoặc chỉnh sửa file .env đã tạo sẵn

# 2. Khởi chạy container với Docker Compose
docker compose up -d --build

# 3. Kiểm tra container đang chạy
docker compose ps
docker compose logs -f
```

---

## 3. Cấu hình các biến môi trường quan trọng (`.env`)

| Biến môi trường | Ý nghĩa | Giá trị mẫu |
| :--- | :--- | :--- |
| `PORT` | Cổng dịch vụ lắng nghe | `18790` |
| `TREG_PUBLIC_URL` | Domain công khai của hệ thống | `http://localhost:18790` hoặc `https://tools.yourdomain.com` |
| `TREG_SECRET_KEY` | Khóa mã hóa Master Fernet *(Cực kỳ quan trọng, không được làm mất)* | Khóa sinh từ `uv run python -m treg keygen` |
| `TREG_SESSION_SECRET` | Khóa ký Cookie phiên đăng nhập | Chuỗi hex ngẫu nhiên |
| `TREG_DATABASE_URL` | Kết nối cơ sở dữ liệu | SQLite: `sqlite+aiosqlite:///./treg.db`<br>Postgres: `postgresql+asyncpg://user:pass@host:5432/treg` |
| `TREG_EMAIL_DEV_MODE` | Bật chế độ hiển thị OTP ngay trên màn hình | `true` (khi dev/nội bộ), `false` (khi dùng SMTP thật) |
| `TREG_RESEND_API_KEY` | Gửi OTP qua email thật bằng Resend | `re_123456...` (tùy chọn) |

---

## 4. Hướng dẫn sử dụng thực tế

### Bước 1: Đăng nhập và tạo Đội ngũ (Team)
1. Truy cập [http://localhost:18790/login](http://localhost:18790/login).
2. Nhập email của bạn (ví dụ: `admin@company.com`).
3. Mã OTP 6 chữ số sẽ xuất hiện ngay trên giao diện (do đang bật `TREG_EMAIL_DEV_MODE=true`).
4. Nhập mã để vào Bảng điều khiển quản trị.

### Bước 2: Lưu trữ API Key & Đăng ký Tool nội bộ
Bạn có thể thao tác trực tiếp trên giao diện web (mục **Secrets** & **Tools**) hoặc sử dụng CLI:

```bash
# Thêm một Secret mã hóa (ví dụ OpenAI Key hoặc Stripe Key)
./scripts/dev-local.sh cli secret add OPENAI_API_KEY --value "sk-proj-xxxxx"

# Đăng ký Tool chuyển tiếp (Endpoint) sử dụng Secret vừa tạo
./scripts/dev-local.sh cli add openai-chat \
  --base-url https://api.openai.com/v1 \
  --secret OPENAI_API_KEY

# Kiểm tra danh sách tool của team
./scripts/dev-local.sh cli tool ls
```

### Bước 3: Tích hợp làm MCP Hub cho AI Agent (Claude Code / Cursor / Windsurf)

Mở file cấu hình MCP của Cursor (`mcp.json`) hoặc Claude Code (`claude.json`), thêm cấu hình:

```json
{
  "mcpServers": {
    "treg-local": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch", "http://localhost:18790/mcp"],
      "headers": {
        "X-Treg-Token": "<TOKEN_CỦA_BẠN_LẤY_TỪ_DASHBOARD>"
      }
    }
  }
}
```

Từ thời điểm này, AI Agent của bạn có thể tự động khám phá (`treg catalog`) và thực thi toàn bộ API nội bộ mà công ty cấu hình trên Treg.

---

## 5. Quản Lý Tài Khoản & Mật Khẩu Quản Trị (Admin & User Password)

Hệ thống đã được tích hợp đầy đủ tính năng xác thực và đổi mật khẩu cho Quản trị viên và người dùng:

### Cách 1: Đổi mật khẩu trực tiếp trên Giao diện Web
1. Đăng nhập vào trang quản trị `https://treg.xox.vn`.
2. Bấm vào biểu tượng **Avatar tài khoản** ở góc trên cùng bên phải.
3. Chọn **Đổi mật khẩu** (hoặc *Change password*).
4. Nhập mật khẩu hiện tại, mật khẩu mới (tối thiểu 6 ký tự) và bấm **Cập nhật mật khẩu**.

### Cách 2: Đăng nhập bằng Mật khẩu
Trên hộp thoại Đăng nhập, bấm nút **🔑 Đăng nhập bằng Mật khẩu** để chuyển từ chế độ gửi mã OTP sang đăng nhập trực tiếp bằng Email + Mật khẩu.

### Cách 3: Đặt/Reset mật khẩu khẩn cấp qua Terminal VPS (Dành cho Quản trị viên)
Nếu quên mật khẩu, Quản trị viên có thể reset trực tiếp bằng lệnh curl với `TREG_ADMIN_TOKEN`:

```bash
# Đặt lại mật khẩu cho User ID 1 (mr.trinhhao@gmail.com)
curl -s -X POST http://172.17.0.1:3031/admin/users/1/password \
  -H "X-Treg-Token: treg_adm_18597a12e7c274f82d5e97e31dd7e653e43cb380f5645393" \
  -H "Content-Type: application/json" \
  -d '{"password":"MatKhauMoiCuaBan"}'
```



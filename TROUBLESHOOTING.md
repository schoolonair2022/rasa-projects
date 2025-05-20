# Rasa Multilingual Chatbot - Hướng dẫn khắc phục lỗi

## Lỗi phổ biến và cách khắc phục

### 1. Lỗi AttributeError: 'dict' object has no attribute 'prediction_states'

Lỗi này thường xảy ra với các policies như MemoizationPolicy, RulePolicy, hoặc TEDPolicy khi featurizer không được cấu hình đúng.

#### Cách khắc phục:

**Phương pháp 1**: Huấn luyện lại mô hình với cấu hình đã sửa

```bash
# Xóa các mô hình cũ
rm -rf models/*

# Huấn luyện lại với cấu hình mới
rasa train
```

**Phương pháp 2**: Sửa mô hình hiện có

```bash
# Chạy script sửa lỗi
python fix_policy_featurizers.py

# Sử dụng mô hình đã sửa
rasa shell --model models/your_model_fixed.tar.gz
```

### 2. Lỗi 404 Not Found cho action_session_start

Lỗi này xảy ra khi Rasa không thể tìm thấy action_session_start trong action server.

#### Cách khắc phục:

Đảm bảo rằng tất cả các default actions đã được đăng ký trong action server:

```bash
# Khởi động lại action server
rasa run actions
```

### 3. Lỗi YamlSyntaxException: Found duplicate key

Lỗi này xảy ra khi có khóa trùng lặp trong file YAML.

#### Cách khắc phục:

Sử dụng script validate_yaml.py để kiểm tra các file YAML:

```bash
python validate_yaml.py
```

## Cách chạy chatbot

### 1. Cài đặt dependencies

```bash
# Sử dụng script cài đặt thay vì pip install trực tiếp
./install_dependencies.sh
```

### 2. Huấn luyện mô hình

```bash
rasa train
```

### 3. Chạy action server

```bash
# Thiết lập API key cho OpenAI
export OPENAI_API_KEY=your_api_key_here

# Chạy action server
rasa run actions
```

### 4. Chạy Rasa shell

```bash
rasa shell
```

## Kiểm tra multilingual

Thử các lệnh sau để kiểm tra khả năng đa ngôn ngữ:

- Tiếng Anh: "Hello"
- Tiếng Việt: "Xin chào"
- Thêm liên hệ tiếng Anh: "Add a new contact"
- Thêm liên hệ tiếng Việt: "Thêm một liên hệ mới"

# Wallet Address Validation Chatbot

## Tổng quan

Chatbot này sử dụng framework Rasa để xử lý việc nhận và xác thực địa chỉ ví tiền điện tử. Ngoài việc sử dụng các biểu thức chính quy cơ bản, chatbot này còn tận dụng mô hình CryptoBERT được đào tạo đặc biệt cho văn bản liên quan đến tiền điện tử.

## Mô hình CryptoBERT

CryptoBERT là mô hình ngôn ngữ dựa trên BERT được tinh chỉnh trên một tập dữ liệu văn bản tiền điện tử lớn. Mô hình này có thể:
- Nhận dạng địa chỉ ví hợp lệ một cách chính xác hơn
- Phân loại loại ví (Ethereum, Bitcoin, v.v.)
- Hiểu ngữ cảnh của các đoạn văn bản liên quan đến tiền điện tử

Nguồn gốc: [ElKulako/cryptobert](https://huggingface.co/ElKulako/cryptobert)

## Cài đặt

1. Cài đặt các phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```

2. Chạy action server:
   ```bash
   rasa run actions
   ```

3. Trong một terminal khác, chạy Rasa server:
   ```bash
   rasa run --enable-api --cors "*" --debug
   ```

4. Hoặc chạy chatbot trong terminal:
   ```bash
   rasa shell
   ```

## Quy trình xác thực địa chỉ ví

Bot sử dụng chiến lược hai lớp để xác thực địa chỉ ví:
1. Xác thực biểu thức chính quy cho các mẫu địa chỉ phổ biến (Ethereum, Bitcoin)
2. Sử dụng CryptoBERT để phân loại các địa chỉ phức tạp hơn khi xác thực biểu thức chính quy thất bại

Điều này cung cấp khả năng phát hiện địa chỉ ví tiền điện tử chính xác hơn và đáng tin cậy hơn.

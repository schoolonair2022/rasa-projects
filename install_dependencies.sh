#!/usr/bin/env bash
# Script để cài đặt dependencies cho dự án Rasa

echo "=== Bắt đầu cài đặt dependencies ==="

# Kiểm tra Python version
python_version=$(python3 --version 2>&1)
echo "Đang sử dụng: $python_version"

# Đảm bảo pip được cập nhật
echo "Cập nhật pip..."
pip install --upgrade pip

# Cài đặt protobuf trước khi cài Rasa
echo "Cài đặt protobuf (phiên bản yêu cầu bởi Rasa)..."
pip install "protobuf>=4.23.3,<4.23.4"

# Cài đặt numpy
echo "Cài đặt numpy..."
pip install numpy==1.24.3

# Cài đặt tensorflow
echo "Cài đặt tensorflow và các thư viện liên quan..."
pip install tensorflow==2.12.0
pip install tensorflow-hub==0.14.0
pip install tensorflow-text==2.12.1

# Cài đặt underthesea cho Tiếng Việt
echo "Cài đặt underthesea cho tiếng Việt..."
pip install underthesea==6.2.0

# Cài đặt transformers và torch
echo "Cài đặt transformers và torch..."
pip install transformers==4.30.2
pip install torch==2.0.1

# Cài đặt thêm các dependencies khác
echo "Cài đặt các dependencies khác..."
pip install scikit-learn==1.2.2
pip install scipy==1.10.1
pip install sentencepiece==0.1.99
pip install "pydantic<2.0.0"
pip install regex==2022.10.31
pip install openai==0.28.0

# Cuối cùng cài đặt Rasa
echo "Cài đặt Rasa..."
pip install rasa==3.6.10

echo "=== Hoàn thành cài đặt dependencies ==="
echo "Kiểm tra các phiên bản đã cài đặt:"
pip list | grep -E "rasa|protobuf|tensorflow|transformers|torch|openai|underthesea"

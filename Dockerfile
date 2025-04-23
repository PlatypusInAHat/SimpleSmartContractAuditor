# Sử dụng image Python 3.8 làm nền tảng
FROM python:3.8

# Cài đặt các gói hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    libgmp-dev \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Tạo môi trường ảo Python
RUN python -m venv /venv

# Cập nhật pip và cài đặt các thư viện Python từ requirements.txt
RUN /venv/bin/pip install --upgrade pip setuptools wheel
COPY requirements.txt ./
RUN /venv/bin/pip install -r requirements.txt

# Cài đặt Truffle Flattener (nếu cần)
RUN npm install -g truffle-flattener

# Thiết lập thư mục làm việc và sao chép mã nguồn vào container
WORKDIR /app
COPY . /app

# Tạo thư mục hợp đồng và báo cáo nếu chưa có
RUN mkdir -p /app/contracts /app/reports

# Thiết lập biến môi trường PYTHONPATH để bao gồm thư mục src
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Chạy ứng dụng
CMD ["/venv/bin/python", "src/main.py"]

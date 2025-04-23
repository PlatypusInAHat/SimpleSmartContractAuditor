import os
import logging

def read_file(file_path: str) -> str:
    """
    Đọc và trả về nội dung của file.

    :param file_path: Đường dẫn đến file.
    :return: Nội dung file dưới dạng chuỗi.
    :raises FileNotFoundError: Nếu file không tồn tại.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def write_report(file_path: str, content: str):
    """
    Ghi kết quả vào file báo cáo.

    :param file_path: Đường dẫn tới file báo cáo.
    :param content: Nội dung cần ghi vào báo cáo.
    """
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content + "\n")
        logging.info(f"Report written to {file_path}")
    except Exception as e:
        logging.error(f"Error writing report to {file_path}: {e}")

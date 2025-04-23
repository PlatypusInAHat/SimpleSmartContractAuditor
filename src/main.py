import os
import logging
from scanner import scan_contract

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def analyze_contracts(directory="D:/Project cá nhân/GR1/SimpleSmartContractAuditor/contracts", 
                      report_file="D:/Project cá nhân/GR1/SimpleSmartContractAuditor/reports/analysis_report.md"):
    # Kiểm tra và tạo thư mục báo cáo nếu chưa tồn tại
    if not os.path.exists("D:/Project cá nhân/GR1/SimpleSmartContractAuditor/reports"):
        os.makedirs("D:/Project cá nhân/GR1/SimpleSmartContractAuditor/reports")

    # Xóa file báo cáo nếu tồn tại
    if os.path.exists(report_file):
        os.remove(report_file)

    # Tạo file báo cáo mới và ghi tiêu đề
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Smart Contract Security Analysis Report\n\n")

    # Lấy danh sách các file hợp đồng Solidity (.sol)
    contracts = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".sol")]

    # Phân tích từng hợp đồng
    for contract in contracts:
        logging.info(f"Analyzing {contract}...")
        vulnerabilities = scan_contract(contract)
        with open(report_file, "a", encoding="utf-8") as f:
            for vulnerability in vulnerabilities:
                f.write(f"{contract}: {vulnerability}\n")
        logging.info(f"Completed analysis for {contract}")

if __name__ == "__main__":
    analyze_contracts()

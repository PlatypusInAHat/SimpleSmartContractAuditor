import logging
import re
import subprocess
import json
import os

# Cấu hình logging để hiển thị thông tin debug
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def compile_contract(code: str) -> dict:
    """
    Biên dịch hợp đồng Solidity bằng cách sử dụng solc qua subprocess.
    Trả về dict chứa kết quả biên dịch hoặc None nếu biên dịch thất bại.
    """
    input_json = {
        "language": "Solidity",
        "sources": {"contract.sol": {"content": code}},
        "settings": {
            "outputSelection": {"*": {"*": ["metadata", "evm.bytecode", "evm.deployedBytecode", "abi"]}}
        }
    }
    json_input = json.dumps(input_json)
    solc_path = os.getenv("SOLC_PATH", "solc")  # Dùng solc từ PATH hoặc từ biến môi trường
    try:
        process = subprocess.run(
            [solc_path, "--standard-json"],
            input=json_input.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if process.returncode != 0:
            logging.error("Lỗi biên dịch solc: " + process.stderr.decode("utf-8"))
            return None
        else:
            result = json.loads(process.stdout.decode("utf-8"))
            logging.debug("Biên dịch thành công.")
            return result
    except Exception as e:
        logging.error("Lỗi khi gọi solc: " + str(e))
        return None

def scan_underflow(code: str) -> bool:
    """
    Kiểm tra nguy cơ underflow bằng cách tìm:
      - Biểu thức trừ liên quan đến totalSupply (ví dụ: totalSupply -= _amount)
      - Và không có câu lệnh require(totalSupply >= _amount)
    """
    subtraction_pattern = re.compile(r'totalSupply\s*[-+]=\s*_amount', re.IGNORECASE)
    subtraction_match = re.search(subtraction_pattern, code)
    
    require_pattern = re.compile(r'require\s*\(\s*totalSupply\s*>=\s*_amount\s*,', re.IGNORECASE)
    require_match = re.search(require_pattern, code)
    
    logging.debug("Kiểm tra underflow: subtraction_match = {}, require_match = {}".format(subtraction_match, require_match))
    return bool(subtraction_match and not require_match)

def extract_functions(code: str) -> list:
    """
    Trích xuất các hàm trong hợp đồng Solidity.
    Trả về danh sách tuple (chữ ký hàm, nội dung hàm).
    Sử dụng regex đơn giản để trích xuất phần nội dung giữa dấu { ... } của hàm.
    """
    pattern = re.compile(
        r'function\s+[\w\d_]+\s*\([^)]*\)\s*(public|external|internal|private)?\s*(?:nonReentrant)?\s*{(.*?)}',
        re.DOTALL
    )
    functions = pattern.findall(code)
    logging.debug("Tìm thấy {} hàm trong hợp đồng.".format(len(functions)))
    return functions

def scan_contract(contract_path: str) -> list:
    """
    Quét mã nguồn hợp đồng để phát hiện các lỗ hổng bảo mật:
      - Reentrancy: phân tích thứ tự giữa gọi external và cập nhật trạng thái.
      - Integer Overflow/Underflow: kiểm tra các phép toán số học nếu không dùng SafeMath hoặc unchecked.
      
    :param contract_path: Đường dẫn đến file Solidity (.sol)
    :return: Danh sách các cảnh báo được phát hiện.
    """
    vulnerabilities = []
    try:
        with open(contract_path, "r", encoding="utf-8") as f:
            code = f.read()
        logging.debug("Đã đọc hợp đồng từ: {}".format(contract_path))
        
        # Biên dịch hợp đồng để kiểm tra tính hợp lệ
        compile_result = compile_contract(code)
        if compile_result is None:
            vulnerabilities.append("Lỗi: Không biên dịch được hợp đồng.")

        # --- Phân tích Reentrancy ---
        functions = extract_functions(code)
        for idx, func in enumerate(functions):
            func_body = func[1]
            # Tìm external call: .call{value:...} hoặc transfer(...)
            external_call_match = re.search(r'\.(call\s*\{\s*value\s*:|transfer\s*\()', func_body, re.IGNORECASE)
            # Tìm câu lệnh cập nhật trạng thái: balances[msg.sender] += hoặc -=
            state_update_match = re.search(r'balances\s*\[\s*msg\.sender\s*\]\s*[-+]=', func_body, re.IGNORECASE)
            
            logging.debug("Hàm {}: external_call = {}, state_update = {}".format(
                idx + 1, external_call_match, state_update_match))
            
            if external_call_match:
                external_call_index = external_call_match.start()
                if not state_update_match:
                    vulnerabilities.append(
                        f"Cảnh báo Reentrancy ở hàm {idx + 1}: Gọi external nhưng không cập nhật trạng thái."
                    )
                else:
                    state_update_index = state_update_match.start()
                    if state_update_index > external_call_index:
                        vulnerabilities.append(
                            f"Cảnh báo Reentrancy ở hàm {idx + 1}: Gọi external xảy ra trước khi cập nhật trạng thái."
                        )

        # --- Kiểm tra Integer Underflow / Overflow ---
        if scan_underflow(code):
            vulnerabilities.append(
                "Cảnh báo Underflow: Thực hiện phép trừ trên totalSupply mà không có kiểm tra require."
            )
        elif "SafeMath" not in code and "unchecked" not in code:
            arithmetic_patterns = [
                r'\+\+|--', r'\d+\s*\+\s*\d+', r'\d+\s*-\s*\d+', r'\d+\s*\*\s*\d+'
            ]
            for pattern in arithmetic_patterns:
                if re.search(pattern, code):
                    vulnerabilities.append(
                        "Cảnh báo Overflow/Underflow: Có phép toán số học trực tiếp nhưng không dùng SafeMath hoặc unchecked."
                    )
                    break

    except Exception as e:
        logging.error("Lỗi khi quét hợp đồng {}: {}".format(contract_path, e))
        vulnerabilities.append("Lỗi trong quá trình phân tích hợp đồng: " + str(e))
    
    return vulnerabilities

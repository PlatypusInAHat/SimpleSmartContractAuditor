// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Reentrancy {
    mapping(address => uint) public balances;
    
    // Nạp tiền vào hợp đồng
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    // Rút tiền từ hợp đồng (vulnerable to reentrancy)
    function withdraw(uint _amount) public {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        payable(msg.sender).transfer(_amount);
        balances[msg.sender] -= _amount;
    }
}
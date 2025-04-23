// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OverflowUnderflow {
    uint public totalSupply;

    // Tăng số lượng phát hành token
    function increaseSupply(uint _amount) public {
        totalSupply += _amount;
    }
    
    // Giảm số lượng phát hành token (vulnerable to underflow)
    function decreaseSupply(uint _amount) public {
        totalSupply -= _amount; // Có thể dẫn đến underflow nếu _amount > totalSupply
    }
}

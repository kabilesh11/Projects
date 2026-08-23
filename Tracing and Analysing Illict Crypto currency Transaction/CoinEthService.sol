// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CoinEthService {
    address public owner;
    // 0 = Safe, 1 = Warning, 2 = Frozen
    mapping(address => uint8) public riskLevel; 

    event RiskLevelUpdated(address indexed account, uint8 level);
    event TransactionVerified(address indexed from, address indexed to, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Unauthorized");
        _;
    }

    constructor() { owner = msg.sender; }

    receive() external payable {}
    fallback() external payable {}

    function setRiskLevel(address _account, uint8 _level) public onlyOwner {
        require(_level <= 2, "Invalid Risk Level");
        riskLevel[_account] = _level;
        emit RiskLevelUpdated(_account, _level);
    }

    function secureTransfer(address payable _to) public payable {
        require(riskLevel[msg.sender] < 2, "FROZEN: Sender account is blocked.");
        require(riskLevel[_to] < 2, "FROZEN: Destination account is blocked.");
        
        (bool success, ) = _to.call{value: msg.value}("");
        require(success, "Transfer failed.");
        
        emit TransactionVerified(msg.sender, _to, msg.value);
    }
}
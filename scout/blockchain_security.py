"""
Advanced blockchain and Web3 security analysis module.
Provides comprehensive smart contract auditing, DeFi protocol analysis,
and Web3 threat detection.
"""

import asyncio
import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from scout.logging import log_error, log_info, log_warning

try:
    import requests
    from eth_account import Account
    from web3 import Web3
except ImportError:
    Web3 = Account = requests = None

# Constants
ETHEREUM_MAINNET_RPC = "https://mainnet.infura.io/v3/"
POLYGON_RPC = "https://polygon-rpc.com"
BSC_RPC = "https://bsc-dataseed.binance.org"
ARBITRUM_RPC = "https://arb1.arbitrum.io/rpc"


class BlockchainNetwork(Enum):
    """Supported blockchain networks."""
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BINANCE_SMART_CHAIN = "bsc"
    ARBITRUM = "arbitrum"
    AVALANCHE = "avalanche"
    FANTOM = "fantom"
    OPTIMISM = "optimism"


class VulnerabilityType(Enum):
    """Smart contract vulnerability types."""
    REENTRANCY = "reentrancy"
    INTEGER_OVERFLOW = "integer_overflow"
    ACCESS_CONTROL = "access_control"
    UNCHECKED_EXTERNAL_CALLS = "unchecked_external_calls"
    DENIAL_OF_SERVICE = "denial_of_service"
    FRONT_RUNNING = "front_running"
    TIMESTAMP_DEPENDENCE = "timestamp_dependence"
    SHORT_ADDRESS_ATTACK = "short_address_attack"


class SecurityLevel(Enum):
    """Security assessment levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SmartContractVulnerability:
    """Smart contract vulnerability finding."""
    id: str
    contract_address: str
    network: BlockchainNetwork
    vulnerability_type: VulnerabilityType
    severity: SecurityLevel
    title: str
    description: str
    code_location: str
    impact: str
    recommendation: str
    confidence: float
    gas_impact: Optional[int] = None
    exploitability: float = 0.0
    references: Optional[List[str]] = None


@dataclass
class DeFiProtocolAnalysis:
    """DeFi protocol security analysis result."""
    protocol_name: str
    contract_addresses: List[str]
    total_value_locked: float
    risk_score: float
    vulnerabilities: List[SmartContractVulnerability]
    liquidity_risks: List[str]
    governance_risks: List[str]
    smart_contract_risks: List[str]
    recommendations: List[str]


@dataclass
class Web3Transaction:
    """Web3 transaction analysis."""
    tx_hash: str
    from_address: str
    to_address: str
    value: float
    gas_used: int
    gas_price: int
    block_number: int
    timestamp: datetime
    status: str
    risk_indicators: List[str]


class SmartContractAnalyzer:
    """Advanced smart contract security analyzer."""

    def __init__(self, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM):
        self.network = network
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.severity_matrix = self._load_severity_matrix()
        
    def _load_vulnerability_patterns(self) -> Dict[str, List[str]]:
        """Load vulnerability detection patterns."""
        return {
            'reentrancy': [
                r'call\.value\(',
                r'\.call\(',
                r'transfer\(',
                r'send\('
            ],
            'integer_overflow': [
                r'\+\s*=',
                r'-\s*=',
                r'\*\s*=',
                r'unchecked'
            ],
            'access_control': [
                r'onlyOwner',
                r'require\(msg\.sender',
                r'modifier\s+\w+\s*\('
            ]
        }

    async def analyze_contract(self, contract_address: str,
                              source_code: str = None) -> List[SmartContractVulnerability]:
        """Analyze smart contract for vulnerabilities."""
        try:
            log_info(f"Starting analysis of contract {contract_address}")
            
            vulnerabilities = []
            
            if source_code:
                vulnerabilities.extend(await self._analyze_source_code(
                    contract_address, source_code))
            
            vulnerabilities.extend(await self._analyze_bytecode(contract_address))
            vulnerabilities.extend(await self._analyze_transactions(contract_address))
            
            log_info(f"Found {len(vulnerabilities)} vulnerabilities in {contract_address}")
            return vulnerabilities
            
        except Exception as e:
            log_error(f"Error analyzing contract {contract_address}: {e}")
            return []

    async def _analyze_source_code(self, contract_address: str,
                                  source_code: str) -> List[SmartContractVulnerability]:
        """Analyze smart contract source code."""
        vulnerabilities = []
        
        for vuln_type, patterns in self.vulnerability_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, source_code, re.IGNORECASE)
                for match in matches:
                    line_number = source_code[:match.start()].count('\n') + 1
                    
                    vulnerability = SmartContractVulnerability(
                        id=f"{contract_address}_{vuln_type}_{line_number}",
                        contract_address=contract_address,
                        network=self.network,
                        vulnerability_type=VulnerabilityType(vuln_type),
                        severity=self._calculate_severity(vuln_type),
                        title=f"{vuln_type.replace('_', ' ').title()} Vulnerability",
                        description=f"Potential {vuln_type} vulnerability detected",
                        code_location=f"Line {line_number}",
                        impact=self._get_impact_description(vuln_type),
                        recommendation=self._get_recommendation(vuln_type),
                        confidence=0.8
                    )
                    vulnerabilities.append(vulnerability)
        
        return vulnerabilities

    def _calculate_severity(self, vuln_type: str) -> SecurityLevel:
        """Calculate vulnerability severity."""
        severity_map = {
            'reentrancy': SecurityLevel.CRITICAL,
            'integer_overflow': SecurityLevel.HIGH,
            'access_control': SecurityLevel.HIGH,
            'unchecked_external_calls': SecurityLevel.MEDIUM,
            'denial_of_service': SecurityLevel.MEDIUM,
            'front_running': SecurityLevel.LOW,
            'timestamp_dependence': SecurityLevel.LOW
        }
        return severity_map.get(vuln_type, SecurityLevel.MEDIUM)

    def _get_impact_description(self, vuln_type: str) -> str:
        """Get impact description for vulnerability type."""
        impacts = {
            'reentrancy': "Funds can be drained through recursive calls",
            'integer_overflow': "Arithmetic operations may overflow/underflow",
            'access_control': "Unauthorized access to critical functions",
            'unchecked_external_calls': "External calls may fail silently"
        }
        return impacts.get(vuln_type, "Potential security risk")

    def _get_recommendation(self, vuln_type: str) -> str:
        """Get recommendation for vulnerability type."""
        recommendations = {
            'reentrancy': "Use checks-effects-interactions pattern",
            'integer_overflow': "Use SafeMath library or Solidity 0.8+",
            'access_control': "Implement proper access control mechanisms",
            'unchecked_external_calls': "Check return values of external calls"
        }
        return recommendations.get(vuln_type, "Review and fix the code")

    async def _analyze_bytecode(self, contract_address: str) -> List[SmartContractVulnerability]:
        """Analyze contract bytecode for vulnerabilities."""
        # Placeholder for bytecode analysis
        return []

    async def _analyze_transactions(self, contract_address: str) -> List[SmartContractVulnerability]:
        """Analyze contract transactions for suspicious patterns."""
        # Placeholder for transaction analysis
        return []


class DeFiProtocolAnalyzer:
    """DeFi protocol security analyzer."""

    def __init__(self):
        self.contract_analyzer = SmartContractAnalyzer()
        self.risk_thresholds = {
            'tvl_risk': 1000000,  # $1M
            'age_risk': 30,  # 30 days
            'audit_risk': True
        }

    async def analyze_protocol(self, protocol_name: str,
                              contract_addresses: List[str]) -> DeFiProtocolAnalysis:
        """Analyze DeFi protocol for security risks."""
        try:
            log_info(f"Starting DeFi protocol analysis for {protocol_name}")
            
            all_vulnerabilities = []
            
            # Analyze each contract
            for address in contract_addresses:
                vulnerabilities = await self.contract_analyzer.analyze_contract(address)
                all_vulnerabilities.extend(vulnerabilities)
            
            # Calculate risk metrics
            tvl = await self._get_total_value_locked(contract_addresses)
            risk_score = self._calculate_protocol_risk_score(
                all_vulnerabilities, tvl)
            
            # Generate risk assessments
            liquidity_risks = self._assess_liquidity_risks(tvl)
            governance_risks = self._assess_governance_risks()
            smart_contract_risks = self._assess_smart_contract_risks(all_vulnerabilities)
            recommendations = self._generate_recommendations(all_vulnerabilities)
            
            analysis = DeFiProtocolAnalysis(
                protocol_name=protocol_name,
                contract_addresses=contract_addresses,
                total_value_locked=tvl,
                risk_score=risk_score,
                vulnerabilities=all_vulnerabilities,
                liquidity_risks=liquidity_risks,
                governance_risks=governance_risks,
                smart_contract_risks=smart_contract_risks,
                recommendations=recommendations
            )
            
            log_info(f"Completed DeFi analysis for {protocol_name}: "
                    f"Risk Score {risk_score:.2f}")
            return analysis
            
        except Exception as e:
            log_error(f"Error analyzing DeFi protocol {protocol_name}: {e}")
            raise

    async def _get_total_value_locked(self, addresses: List[str]) -> float:
        """Get total value locked in protocol."""
        # Placeholder - would integrate with DeFiPulse, Llama, etc.
        return 1000000.0

    def _calculate_protocol_risk_score(self,
                                      vulnerabilities: List[SmartContractVulnerability],
                                      tvl: float) -> float:
        """Calculate overall protocol risk score."""
        if not vulnerabilities:
            return 0.1  # Low risk

        # Calculate vulnerability score
        vuln_score = 0
        for vuln in vulnerabilities:
            severity_weights = {
                SecurityLevel.CRITICAL: 1.0,
                SecurityLevel.HIGH: 0.7,
                SecurityLevel.MEDIUM: 0.4,
                SecurityLevel.LOW: 0.2,
                SecurityLevel.INFO: 0.1
            }
            vuln_score += severity_weights.get(vuln.severity, 0.1)

        # Normalize by number of contracts
        vuln_score = vuln_score / len(set(v.contract_address for v in vulnerabilities))

        # TVL risk factor
        tvl_risk = min(tvl / 10000000, 1.0)  # Max risk at $10M

        return min(vuln_score * tvl_risk, 1.0)

    def _assess_liquidity_risks(self, tvl: float) -> List[str]:
        """Assess liquidity-related risks."""
        risks = []
        if tvl < 100000:
            risks.append("Low liquidity may impact trading")
        if tvl > 10000000:
            risks.append("High TVL makes attractive target for attackers")
        return risks

    def _assess_governance_risks(self) -> List[str]:
        """Assess governance-related risks."""
        return [
            "Centralized governance keys",
            "Lack of timelock on critical functions",
            "No community voting mechanism"
        ]

    def _assess_smart_contract_risks(self,
                                    vulnerabilities: List[SmartContractVulnerability]) -> List[str]:
        """Assess smart contract risks."""
        risks = []
        
        critical_vulns = [v for v in vulnerabilities if v.severity == SecurityLevel.CRITICAL]
        if critical_vulns:
            risks.append(f"{len(critical_vulns)} critical vulnerabilities found")
            
        high_vulns = [v for v in vulnerabilities if v.severity == SecurityLevel.HIGH]
        if high_vulns:
            risks.append(f"{len(high_vulns)} high-severity vulnerabilities found")
            
        return risks

    def _generate_recommendations(self,
                                 vulnerabilities: List[SmartContractVulnerability]) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        
        if vulnerabilities:
            recommendations.append("Conduct comprehensive security audit")
            recommendations.append("Implement bug bounty program")
            recommendations.append("Use formal verification tools")
            
        recommendations.extend([
            "Implement circuit breakers for large withdrawals",
            "Use multi-signature wallets for admin functions",
            "Regular security monitoring and alerting"
        ])
        
        return recommendations


class Web3ThreatDetector:
    """Web3 threat detection and monitoring."""

    def __init__(self):
        self.threat_patterns = self._load_threat_patterns()
        self.suspicious_addresses = set()

    def _load_threat_patterns(self) -> Dict[str, Any]:
        """Load threat detection patterns."""
        return {
            'flashloan_attacks': [
                'flashloan',
                'borrow',
                'repay'
            ],
            'front_running': [
                'high_gas_price',
                'mev_bot'
            ],
            'rug_pulls': [
                'liquidity_removal',
                'ownership_transfer'
            ]
        }

    async def monitor_transactions(self, tx_hashes: List[str]) -> List[Web3Transaction]:
        """Monitor transactions for threats."""
        transactions = []
        
        for tx_hash in tx_hashes:
            try:
                tx_analysis = await self._analyze_transaction(tx_hash)
                if tx_analysis:
                    transactions.append(tx_analysis)
            except Exception as e:
                log_error(f"Error analyzing transaction {tx_hash}: {e}")
                
        return transactions

    async def _analyze_transaction(self, tx_hash: str) -> Optional[Web3Transaction]:
        """Analyze individual transaction."""
        # Placeholder for transaction analysis
        return Web3Transaction(
            tx_hash=tx_hash,
            from_address="0x...",
            to_address="0x...",
            value=0.0,
            gas_used=21000,
            gas_price=20,
            block_number=0,
            timestamp=datetime.now(),
            status="success",
            risk_indicators=[]
        )


# Global instances
contract_analyzer = SmartContractAnalyzer()
defi_analyzer = DeFiProtocolAnalyzer()
threat_detector = Web3ThreatDetector()

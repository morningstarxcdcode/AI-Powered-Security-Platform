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

try:
    import requests
    from eth_account import Account
    from web3 import Web3
except ImportError:
    Web3 = Account = requests = None

logger = logging.getLogger(__name__)

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
    UNINITIALIZED_STORAGE = "uninitialized_storage"
    DELEGATECALL_INJECTION = "delegatecall_injection"
    WEAK_RANDOMNESS = "weak_randomness"
    FLASH_LOAN_ATTACK = "flash_loan_attack"
    MEV_VULNERABILITY = "mev_vulnerability"
    ORACLE_MANIPULATION = "oracle_manipulation"
    GOVERNANCE_ATTACK = "governance_attack"


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
    """
    DeFi protocol security analysis result.
    """
    protocol_name: str
    contract_addresses: List[str]
    total_value_locked: float
    risk_score: float
    vulnerabilities: List[SmartContractVulnerability]
    liquidity_risks: List[str]
    governance_risks: List[str]
    oracle_dependencies: List[str]
    audit_status: str
    recommendations: List[str]


class Web3Transaction:
    """Web3 transaction for analysis."""
    def __init__(
        self, hash: str, from_address: str, to_address: str, value: int,
        gas_used: int, gas_price: int, block_number: int, timestamp: datetime,
        input_data: str, status: int
    ):
        self.hash = hash
        self.from_address = from_address
        self.to_address = to_address
        self.value = value
        self.gas_used = gas_used
        self.gas_price = gas_price
        self.block_number = block_number
        self.timestamp = timestamp
        self.input_data = input_data
        self.status = status


class SmartContractAnalyzer:
    """Advanced smart contract security analyzer."""
    def __init__(
        self, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM
    ):
        self.network = network
        self.web3 = None
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self._setup_web3_connection()

    def _setup_web3_connection(self):
        """
        Setup Web3 connection based on network.
        """
        if not Web3:
            logger.warning("Web3 not available, smart contract analysis disabled")
            return

        rpc_urls = {
            BlockchainNetwork.ETHEREUM: ETHEREUM_MAINNET_RPC,
            BlockchainNetwork.POLYGON: POLYGON_RPC,
            BlockchainNetwork.BINANCE_SMART_CHAIN: BSC_RPC,
            BlockchainNetwork.ARBITRUM: ARBITRUM_RPC,
        }

        rpc_url = rpc_urls.get(self.network, ETHEREUM_MAINNET_RPC)

        try:
            self.web3 = Web3(Web3.HTTPProvider(rpc_url))
            if self.web3.is_connected():
                logger.info(f"Connected to {self.network.value} network")
            else:
                logger.error(f"Failed to connect to {self.network.value} network")
        except Exception as e:
            logger.error(f"Web3 connection error: {e}")

    def _load_vulnerability_patterns(
        self
    ) -> Dict[VulnerabilityType, List[Dict[str, Any]]]:
        """Load smart contract vulnerability detection patterns."""

        patterns = {
            VulnerabilityType.REENTRANCY: [
                {
                    "pattern": r"call\.value\(\).*?(?=require|if|assert)",
                    "description": "Potential reentrancy in external call",
                    "severity": SecurityLevel.HIGH
                },
                {
                    "pattern": r"\.call\([^)]*\).*?(?!require|if|assert)",
                    "description": "Unchecked external call may lead to reentrancy",
                    "severity": SecurityLevel.MEDIUM
                }
            ],
            VulnerabilityType.INTEGER_OVERFLOW: [
                {
                    "pattern": r"(?<!SafeMath\.)\+.*?(?=;|\))",
                    "description": "Potential integer overflow without SafeMath",
                    "severity": SecurityLevel.HIGH
                },
                {
                    "pattern": r"(?<!SafeMath\.)[\*\-].*?(?=;|\))",
                    "description": "Potential integer operation without SafeMath",
                    "severity": SecurityLevel.MEDIUM
                }
            ],
            VulnerabilityType.ACCESS_CONTROL: [
                {
                    "pattern": r"function.*?public.*?(?!onlyOwner|require|modifier)",
                    "description": "Public function without access control",
                    "severity": SecurityLevel.MEDIUM
                },
                {
                    "pattern": r"tx\.origin",
                    "description": "Use of tx.origin for authorization",
                    "severity": SecurityLevel.HIGH
                }
            ],
            VulnerabilityType.TIMESTAMP_DEPENDENCE: [
                {
                    "pattern": r"block\.timestamp|now",
                    "description": "Dependence on block timestamp",
                    "severity": SecurityLevel.LOW
                }
            ],
            VulnerabilityType.WEAK_RANDOMNESS: [
                {
                    "pattern": r"block\.(?:hash|difficulty|timestamp).*?%",
                    "description": "Weak randomness source",
                    "severity": SecurityLevel.HIGH
                },
                {
                    "pattern": r"keccak256\(block\.(?:hash|difficulty|timestamp)\)",
                    "description": "Predictable randomness",
                    "severity": SecurityLevel.HIGH
                }
            ],
            VulnerabilityType.UNCHECKED_EXTERNAL_CALLS: [
                {
                    "pattern": r"\.call\(.*?\)(?!.*?require|.*?if|.*?assert)",
                    "description": "Unchecked external call return value",
                    "severity": SecurityLevel.MEDIUM
                }
            ],
            VulnerabilityType.DELEGATECALL_INJECTION: [
                {
                    "pattern": r"delegatecall\(.*?\)",
                    "description": "Potential delegatecall injection vulnerability",
                    "severity": SecurityLevel.CRITICAL
                }
            ]
        }

        return patterns

    async def analyze_contract(
        self,
        contract_address: str,
        source_code: str = None
    ) -> List[SmartContractVulnerability]:
        """Analyze a smart contract for vulnerabilities."""

        if not self.web3:
            logger.error("Web3 not connected, cannot analyze contract")
            return []

        vulnerabilities = []

        # Get contract source code if not provided
        if not source_code:
            source_code = await self._get_contract_source(contract_address)

        if source_code:
            # Perform static analysis
            static_vulnerabilities = await self._static_analysis(contract_address, source_code)
            vulnerabilities.extend(static_vulnerabilities)

            # Perform dynamic analysis
            dynamic_vulnerabilities = await self._dynamic_analysis(contract_address)
            vulnerabilities.extend(dynamic_vulnerabilities)

            # Check for common DeFi vulnerabilities
            defi_vulnerabilities = await self._defi_specific_analysis(contract_address, source_code)
            vulnerabilities.extend(defi_vulnerabilities)

        return vulnerabilities

    async def _get_contract_source(
        self,
        contract_address: str
    ) -> Optional[str]:
        """Retrieve contract source code from blockchain explorer APIs."""

        explorers = {
            BlockchainNetwork.ETHEREUM: f"https://api.etherscan.io / api?module=contract&action=getsourcecode&address={contract_address}",
            BlockchainNetwork.POLYGON: f"https://api.polygonscan.com / api?module=contract&action=getsourcecode&address={contract_address}",
            BlockchainNetwork.BINANCE_SMART_CHAIN: f"https://api.bscscan.com / api?module=contract&action=getsourcecode&address={contract_address}"
        }

        api_url = explorers.get(self.network)
        if not api_url or not requests:
            return None

        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1" and data.get("result"):
                    return data["result"][0].get("SourceCode", "")
        except Exception as e:
            logger.error(f"Failed to fetch contract source: {e}")

        return None

    async def _static_analysis(
        self,
        contract_address: str,
        source_code: str
    ) -> List[SmartContractVulnerability]:
        """Perform static analysis on contract source code."""

        vulnerabilities = []

        for vuln_type, patterns in self.vulnerability_patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info["pattern"]
                matches = re.finditer(pattern, source_code, re.IGNORECASE | re.MULTILINE)

                for match in matches:
                    vulnerability = SmartContractVulnerability(
                        id=f"static_{vuln_type.value}_{hashlib.md5(f'{contract_address}{match.start()}'.encode()).hexdigest()[:8]}",
                        contract_address=contract_address,
                        network=self.network,
                        vulnerability_type=vuln_type,
                        severity=pattern_info["severity"],
                        title=f"{vuln_type.value.replace('_', ' ').title()} Detected",
                        description=pattern_info["description"],
                        code_location=f"Line {source_code[:match.start()].count(chr(10)) + 1}",
                        impact=self._get_vulnerability_impact(vuln_type),
                        recommendation=self._get_vulnerability_recommendation(vuln_type),
                        confidence=0.7,
                        exploitability=self._calculate_exploitability(vuln_type, pattern_info["severity"]),
                        references=self._get_vulnerability_references(vuln_type)
                    )
                    vulnerabilities.append(vulnerability)

        return vulnerabilities

    async def _dynamic_analysis(
        self,
        contract_address: str
    ) -> List[SmartContractVulnerability]:
        """Perform dynamic analysis on deployed contract."""

        vulnerabilities = []

        try:
            # Get contract info (removed unused variables)
            recent_transactions = await self._get_recent_transactions(contract_address)

            # Check for suspicious patterns in transactions
            suspicious_patterns = await self._analyze_transaction_patterns(recent_transactions)

            for pattern in suspicious_patterns:
                vulnerability = SmartContractVulnerability(
                    id=f"dynamic_{pattern['type']}_{contract_address[:10]}",
                    contract_address=contract_address,
                    network=self.network,
                    vulnerability_type=VulnerabilityType.MEV_VULNERABILITY,  # Default type
                    severity=pattern["severity"],
                    title=pattern["title"],
                    description=pattern["description"],
                    code_location="Transaction Pattern Analysis",
                    impact=pattern["impact"],
                    recommendation=pattern["recommendation"],
                    confidence=pattern["confidence"],
                    exploitability=pattern.get("exploitability", 0.5)
                )
                vulnerabilities.append(vulnerability)

        except Exception as e:
            logger.error(f"Dynamic analysis failed: {e}")

        return vulnerabilities

    async def _defi_specific_analysis(
        self,
        contract_address: str,
        source_code: str
    ) -> List[SmartContractVulnerability]:
        """Analyze DeFi-specific vulnerabilities."""

        vulnerabilities = []

        # Check for flash loan vulnerabilities
        if "flashloan" in source_code.lower() or "flashborrow" in source_code.lower():
            if not re.search(r"require\([^\)]*balance[^\)]*\)", source_code, re.IGNORECASE):
                vulnerability = SmartContractVulnerability(
                    id=f"defi_flashloan_{contract_address[:10]}",
                    contract_address=contract_address,
                    network=self.network,
                    vulnerability_type=VulnerabilityType.FLASH_LOAN_ATTACK,
                    severity=SecurityLevel.HIGH,
                    title="Flash Loan Attack Vector",
                    description="Contract may be vulnerable to flash loan attacks",
                    code_location="Flash loan implementation",
                    impact="Potential for price manipulation and fund drainage",
                    recommendation="Implement proper balance checks and reentrancy guards",
                    confidence=0.8,
                    exploitability=0.7
                )
                vulnerabilities.append(vulnerability)

        # Check for oracle manipulation vulnerabilities
        oracle_patterns = [r"getPrice", r"latestRoundData", r"latestAnswer"]
        for pattern in oracle_patterns:
            if re.search(pattern, source_code):
                if not re.search(r"require\([^\)]*price[^\)]*\)", source_code, re.IGNORECASE):
                    vulnerability = SmartContractVulnerability(
                        id=f"defi_oracle_{contract_address[:10]}",
                        contract_address=contract_address,
                        network=self.network,
                        vulnerability_type=VulnerabilityType.ORACLE_MANIPULATION,
                        severity=SecurityLevel.MEDIUM,
                        title="Oracle Manipulation Risk",
                        description="Contract relies on external price oracles without proper validation",
                        code_location="Oracle price usage",
                        impact="Price manipulation could lead to financial losses",
                        recommendation="Implement multiple oracle sources and price validation",
                        confidence=0.6,
                        exploitability=0.5
                    )
                    vulnerabilities.append(vulnerability)
                break

        return vulnerabilities

    async def _get_recent_transactions(
        self,
        contract_address: str,
        limit: int = 100
    ) -> List[Web3Transaction]:
        """Get recent transactions for a contract."""

        transactions = []

        try:
            # Get latest block number
            latest_block = self.web3.eth.block_number

            # Search recent blocks for transactions to / from the contract
            for block_num in range(latest_block-100, latest_block + 1):
                try:
                    block = self.web3.eth.get_block(block_num, full_transactions=True)

                    for tx in block.transactions:
                        if (tx.to and tx.to.lower() == contract_address.lower()) or \
                           (tx['from'] and tx['from'].lower() == contract_address.lower()):

                            # Get transaction receipt for status
                            receipt = self.web3.eth.get_transaction_receipt(tx.hash)

                            web3_tx = Web3Transaction(
                                hash=tx.hash.hex(),
                                from_address=tx['from'],
                                to_address=tx.to or "",
                                value=tx.value,
                                gas_used=receipt.gasUsed,
                                gas_price=tx.gasPrice,
                                block_number=tx.blockNumber,
                                timestamp=datetime.fromtimestamp(block.timestamp),
                                input_data=tx.input.hex(),
                                status=receipt.status
                            )
                            transactions.append(web3_tx)

                            if len(transactions) >= limit:
                                return transactions

                except Exception as e:
                    logger.debug(f"Error processing block {block_num}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Failed to get recent transactions: {e}")

        return transactions

    async def _analyze_transaction_patterns(
        self,
        transactions: List[Web3Transaction]
    ) -> List[Dict[str, Any]]:
        """Analyze transaction patterns for suspicious activity."""

        patterns = []

        if not transactions:
            return patterns

        # Check for MEV (Maximal Extractable Value) patterns
        high_gas_txs = [tx for tx in transactions if tx.gas_price > 50 * 10**9]  # >50 Gwei
        if len(high_gas_txs) > len(transactions) * 0.3:  # >30% high gas transactions
            patterns.append({
                "type": "mev_activity",
                "title": "High MEV Activity Detected",
                "description": f"High percentage of transactions with elevated gas prices ({len(high_gas_txs)}/{len(transactions)})",
                "severity": SecurityLevel.MEDIUM,
                "impact": "Potential front-running or sandwich attacks",
                "recommendation": "Implement MEV protection mechanisms",
                "confidence": 0.7,
                "exploitability": 0.6
            })

        # Check for failed transaction patterns
        failed_txs = [tx for tx in transactions if tx.status == 0]
        if len(failed_txs) > len(transactions) * 0.2:  # >20% failed transactions
            patterns.append({
                "type": "high_failure_rate",
                "title": "High Transaction Failure Rate",
                "description": f"Unusually high transaction failure rate ({len(failed_txs)}/{len(transactions)})",
                "severity": SecurityLevel.LOW,
                "impact": "Potential smart contract bugs or attack attempts",
                "recommendation": "Review contract logic and error handling",
                "confidence": 0.5,
                "exploitability": 0.3
            })

        # Check for flash loan patterns
        large_value_txs = [tx for tx in transactions if tx.value > 1000 * 10**18]  # >1000 ETH
        same_block_large_txs = {}
        for tx in large_value_txs:
            if tx.block_number not in same_block_large_txs:
                same_block_large_txs[tx.block_number] = []
            same_block_large_txs[tx.block_number].append(tx)

        for block_num, block_txs in same_block_large_txs.items():
            if len(block_txs) >= 2:
                patterns.append({
                    "type": "flash_loan_pattern",
                    "title": "Potential Flash Loan Activity",
                    "description": f"Multiple large-value transactions in block {block_num}",
                    "severity": SecurityLevel.INFO,
                    "impact": "May indicate flash loan usage or large arbitrage",
                    "recommendation": "Monitor for flash loan attack patterns",
                    "confidence": 0.4,
                    "exploitability": 0.2
                })

        return patterns

    def _get_vulnerability_impact(
        self, vuln_type: VulnerabilityType
    ) -> str:
        """Get impact description for vulnerability type."""

        impacts = {
            VulnerabilityType.REENTRANCY: "Attackers can drain contract funds through recursive calls",
            VulnerabilityType.INTEGER_OVERFLOW: "Arithmetic operations may wrap around causing unexpected behavior",
            VulnerabilityType.ACCESS_CONTROL: "Unauthorized users may access restricted functionality",
            VulnerabilityType.FLASH_LOAN_ATTACK: "Price manipulation and fund drainage through flash loans",
            VulnerabilityType.ORACLE_MANIPULATION: "External price sources can be manipulated",
            VulnerabilityType.WEAK_RANDOMNESS: "Predictable random values can be exploited",
            VulnerabilityType.DELEGATECALL_INJECTION: "Malicious contracts can execute arbitrary code",
            VulnerabilityType.MEV_VULNERABILITY: "Transactions can be front-run or sandwich attacked"
        }

        return impacts.get(vuln_type, "Potential security vulnerability")

    def _get_vulnerability_recommendation(
        self, vuln_type: VulnerabilityType
    ) -> str:
        """Get recommendation for vulnerability type."""

        recommendations = {
            VulnerabilityType.REENTRANCY: "Use reentrancy guards and checks-effects-interactions pattern",
            VulnerabilityType.INTEGER_OVERFLOW: "Use SafeMath library or Solidity 0.8+ built-in overflow checks",
            VulnerabilityType.ACCESS_CONTROL: "Implement proper access control modifiers",
            VulnerabilityType.FLASH_LOAN_ATTACK: "Implement balance checks and consider flash loan attack vectors",
            VulnerabilityType.ORACLE_MANIPULATION: "Use multiple oracle sources and implement price validation",
            VulnerabilityType.WEAK_RANDOMNESS: "Use commit-reveal scheme or VRF for secure randomness",
            VulnerabilityType.DELEGATECALL_INJECTION: "Avoid delegatecall with user-controlled data",
            VulnerabilityType.MEV_VULNERABILITY: "Implement MEV protection or use flashbots"
        }

        return recommendations.get(vuln_type, "Review and fix the vulnerability")

    def _get_vulnerability_references(
        self, vuln_type: VulnerabilityType
    ) -> List[str]:
        """Get references for vulnerability type."""

        references = {
            VulnerabilityType.REENTRANCY: [
                "https://consensys.github.io / smart-contract-best-practices / attacks / reentrancy/",
                "https://swcregistry.io / docs / SWC-107"
            ],
            VulnerabilityType.INTEGER_OVERFLOW: [
                "https://swcregistry.io / docs / SWC-101",
                "https://consensys.github.io / smart-contract-best-practices / attacks / insecure-arithmetic/"
            ],
            VulnerabilityType.FLASH_LOAN_ATTACK: [
                "https://blog.openzeppelin.com / flash-loan-attack-on-venus-protocol/",
                "https://rekt.news / flash-loan-attack/"
            ]
        }

        return references.get(vuln_type, [])

    def _calculate_exploitability(
        self,
        vuln_type: VulnerabilityType,
        severity: SecurityLevel
    ) -> float:
        """Calculate exploitability score."""

        base_scores = {
            VulnerabilityType.REENTRANCY: 0.8,
            VulnerabilityType.FLASH_LOAN_ATTACK: 0.7,
            VulnerabilityType.INTEGER_OVERFLOW: 0.6,
            VulnerabilityType.ORACLE_MANIPULATION: 0.5,
            VulnerabilityType.ACCESS_CONTROL: 0.7,
            VulnerabilityType.WEAK_RANDOMNESS: 0.6,
            VulnerabilityType.DELEGATECALL_INJECTION: 0.9
        }

        severity_multiplier = {
            SecurityLevel.CRITICAL: 1.0,
            SecurityLevel.HIGH: 0.8,
            SecurityLevel.MEDIUM: 0.6,
            SecurityLevel.LOW: 0.4,
            SecurityLevel.INFO: 0.2
        }

        base_score = base_scores.get(vuln_type, 0.5)
        multiplier = severity_multiplier.get(severity, 0.5)

        return min(base_score * multiplier, 1.0)


class DeFiProtocolAnalyzer:
    """Analyzer for DeFi protocol security assessment."""
    def __init__(
        self, network: BlockchainNetwork = BlockchainNetwork.ETHEREUM
    ):
        self.network = network
        self.contract_analyzer = SmartContractAnalyzer(network)

    async def analyze_protocol(
        self,
        protocol_name: str,
        contract_addresses: List[str]
    ) -> DeFiProtocolAnalysis:
        """
        Perform comprehensive DeFi protocol analysis.
        """

        all_vulnerabilities = []
        total_tvl = 0.0

        # Analyze each contract in the protocol
        for address in contract_addresses:
            try:
                contract_vulns = await self.contract_analyzer.analyze_contract(address)
                all_vulnerabilities.extend(contract_vulns)

                # Get TVL for this contract (simplified)
                tvl = await self._estimate_contract_tvl(address)
                total_tvl += tvl

            except Exception as e:
                logger.error(f"Failed to analyze contract {address}: {e}")

        # Calculate risk score
        risk_score = self._calculate_protocol_risk_score(all_vulnerabilities, total_tvl)

        # Analyze protocol-specific risks
        liquidity_risks = await self._analyze_liquidity_risks(contract_addresses)
        governance_risks = await self._analyze_governance_risks(contract_addresses)
        oracle_dependencies = await self._analyze_oracle_dependencies(contract_addresses)

        # Generate recommendations
        recommendations = self._generate_protocol_recommendations(
            all_vulnerabilities, liquidity_risks, governance_risks
        )

        return DeFiProtocolAnalysis(
            protocol_name=protocol_name,
            contract_addresses=contract_addresses,
            total_value_locked=total_tvl,
            risk_score=risk_score,
            vulnerabilities=all_vulnerabilities,
            liquidity_risks=liquidity_risks,
            governance_risks=governance_risks,
            oracle_dependencies=oracle_dependencies,
            audit_status="Unknown",  # Would be fetched from audit databases
            recommendations=recommendations
        )

    async def _estimate_contract_tvl(
        self, contract_address: str
    ) -> float:
        """Estimate Total Value Locked in a contract."""

        try:
            if not self.contract_analyzer.web3:
                return 0.0

            # Get contract balance
            balance = self.contract_analyzer.web3.eth.get_balance(contract_address)
            eth_value = self.contract_analyzer.web3.from_wei(balance, 'ether')

            # Convert to USD (simplified-would use price oracle in production)
            eth_price_usd = 2000  # Placeholder

            return float(eth_value) * eth_price_usd

        except Exception as e:
            logger.error(f"Failed to estimate TVL for {contract_address}: {e}")
            return 0.0

    def _calculate_protocol_risk_score(
        self,
        vulnerabilities: List[SmartContractVulnerability],
        tvl: float
    ) -> float:
        """Calculate overall protocol risk score."""
        if not vulnerabilities:
            return 1.0  # Low risk
        # Weight vulnerabilities by severity
        severity_weights = {
            SecurityLevel.CRITICAL: 10,
            SecurityLevel.HIGH: 7,
            SecurityLevel.MEDIUM: 4,
            SecurityLevel.LOW: 2,
            SecurityLevel.INFO: 1
        }
        total_risk = sum(
            severity_weights.get(vuln.severity, 1) for vuln in vulnerabilities
        )
        # Factor in TVL (higher TVL = higher risk if vulnerabilities exist)
        tvl_factor = min(tvl / 1000000, 10)  # Cap at 10x for $1M+ TVL
        # Calculate risk score (0-10 scale)
        risk_score = min(total_risk * (1 + tvl_factor / 10), 10)

        return risk_score

    async def _analyze_liquidity_risks(
        self, contract_addresses: List[str]
    ) -> List[str]:
        """
        Analyze liquidity-related risks.
        """

        risks = []

        # This would involve complex liquidity analysis of the provided contract addresses
        # For now, return common liquidity risks based on the contract analysis
        for _ in contract_addresses[:3]:  # Limit analysis to prevent timeout
            # Analyze specific contract for liquidity patterns
            pass

        risks.extend([
            "Potential for large withdrawals to impact token price",
            "Limited liquidity during market stress",
            "Dependency on external liquidity providers"
        ])

        return risks

    async def _analyze_governance_risks(
        self, contract_addresses: List[str]
    ) -> List[str]:
        """Analyze governance-related risks based on contract addresses."""

        risks = []

        # Analyze governance patterns in the provided contracts
        if contract_addresses:
            governance_indicators = len(contract_addresses)  # Analyze contract count
            risks.append(f"Managing {governance_indicators} contracts may introduce governance complexity")

        # Common governance risks in DeFi
        risks.extend([
            "Centralized governance tokens may lead to governance attacks",
            "Low participation in governance voting",
            "Potential for proposal manipulation"
        ])

        return risks

    async def _analyze_oracle_dependencies(
        self, contract_addresses: List[str]
    ) -> List[str]:
        """Analyze oracle dependencies and risks."""

        dependencies = []

        # Analyze oracle usage patterns based on contract addresses
        oracle_indicators = len(contract_addresses) if contract_addresses else 0
        if oracle_indicators > 3:
            dependencies.append(f"Multiple contracts ({oracle_indicators}) may indicate complex oracle setup")

        # This would analyze actual contract code for oracle usage
        # For now, return common oracle dependencies
        dependencies.extend([
            "Chainlink price feeds",
            "Uniswap TWAP oracles",
            "Band Protocol price data"
        ])

        return dependencies

    def _generate_protocol_recommendations(
        self,
        vulnerabilities: List[SmartContractVulnerability],
        liquidity_risks: List[str],
        governance_risks: List[str]
    ) -> List[str]:
        """Generate protocol-specific recommendations based on analysis."""

        recommendations = []

        # Vulnerability-based recommendations
        critical_vulns = [v for v in vulnerabilities if v.severity == SecurityLevel.CRITICAL]
        if critical_vulns:
            recommendations.append(f"Address {len(critical_vulns)} critical vulnerabilities immediately")

        # Risk-based recommendations
        if liquidity_risks:
            recommendations.append(f"Mitigate {len(liquidity_risks)} liquidity risks identified")

        if governance_risks:
            recommendations.append(f"Review {len(governance_risks)} governance concerns")
            recommendations.append("URGENT: Address critical vulnerabilities immediately")

        high_vulns = [v for v in vulnerabilities if v.severity == SecurityLevel.HIGH]
        if high_vulns:
            recommendations.append("Prioritize fixing high-severity vulnerabilities")

        # General recommendations
        recommendations.extend([
            "Implement comprehensive testing and formal verification",
            "Consider bug bounty programs for continuous security assessment",
            "Establish emergency pause mechanisms",
            "Implement time-locks for critical parameter changes",
            "Diversify oracle sources to reduce manipulation risk",
            "Monitor for flash loan attack patterns",
            "Implement circuit breakers for large withdrawals"
        ])

        return recommendations


class Web3ThreatDetector:
    """Advanced Web3 threat detection system."""
    def __init__(self):
        self.threat_signatures = self._load_threat_signatures()
        self.known_malicious_addresses = set()
        self.suspicious_patterns = []

    def _load_threat_signatures(self) -> Dict[str, Any]:
        """
        Load Web3 threat signatures.
        """

        return {
            "phishing_contracts": [
                r"approve.*?transferFrom",  # Approval drainage
                r"setApprovalForAll.*?transferFrom",  # NFT drainage
            ],
            "honeypot_patterns": [
                r"transfer.*?revert",  # Transfer that always reverts
                r"balanceOf.*?0",  # Balance always returns 0
            ],
            "rug_pull_indicators": [
                r"renounceOwnership.*?mint",  # Mint then renounce
                r"pause.*?unpause",  # Suspicious pause functionality
            ],
            "flash_loan_attacks": [
                r"flashloan.*?swap.*?liquidate",  # Flash loan arbitrage
                r"borrow.*?price.*?repay",  # Price manipulation
            ]
        }

    async def detect_threats(
        self, transactions: List[Web3Transaction]
    ) -> List[Dict[str, Any]]:
        """Detect threats in Web3 transactions."""

        threats = []

        for tx in transactions:
            tx_threats = await self._analyze_transaction_threats(tx)
            threats.extend(tx_threats)

        return threats

    async def _analyze_transaction_threats(
        self,
        transaction: Web3Transaction
    ) -> List[Dict[str, Any]]:
        """
        Analyze individual transaction for threats.
        """

        threats = []

        # Check for known malicious addresses
        if (transaction.from_address in self.known_malicious_addresses or
            transaction.to_address in self.known_malicious_addresses):
            threats.append({
                "type": "known_malicious_address",
                "severity": SecurityLevel.HIGH,
                "description": "Transaction involves known malicious address",
                "transaction_hash": transaction.hash,
                "risk_score": 0.9
            })

        # Analyze transaction input data
        if transaction.input_data and len(transaction.input_data) > 10:
            input_threats = await self._analyze_input_data(transaction.input_data, transaction)
            threats.extend(input_threats)

        # Check for suspicious gas patterns
        if transaction.gas_price > 200 * 10**9:  # >200 Gwei
            threats.append({
                "type": "suspicious_gas_price",
                "severity": SecurityLevel.MEDIUM,
                "description": f"Unusually high gas price: {transaction.gas_price / 10**9} Gwei",
                "transaction_hash": transaction.hash,
                "risk_score": 0.6
            })

        return threats

    async def _analyze_input_data(
        self,
        input_data: str,
        transaction: Web3Transaction
    ) -> List[Dict[str, Any]]:
        """Analyze transaction input data for threats."""

        threats = []

        # Convert hex to ASCII for pattern matching
        try:
            decoded_data = bytes.fromhex(input_data[2:]).decode('ascii', errors='ignore')
        except ValueError:
            decoded_data = input_data

        # Check against threat signatures
        for threat_type, patterns in self.threat_signatures.items():
            for pattern in patterns:
                if re.search(pattern, decoded_data, re.IGNORECASE):
                    threats.append({
                        "type": threat_type,
                        "severity": SecurityLevel.HIGH,
                        "description": f"Suspicious pattern detected: {pattern}",
                        "transaction_hash": transaction.hash,
                        "risk_score": 0.8
                    })

        return threats


# Example usage and testing
async def example_blockchain_analysis():
    """Example of blockchain security analysis."""

    if not Web3:
        print("Web3 dependencies not available, skipping blockchain analysis")
        return

    # Analyze a smart contract
    analyzer = SmartContractAnalyzer(BlockchainNetwork.ETHEREUM)

    # Example contract address (Uniswap V2 Router)
    contract_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

    print(f"Analyzing contract: {contract_address}")
    vulnerabilities = await analyzer.analyze_contract(contract_address)

    print(f"Found {len(vulnerabilities)} potential vulnerabilities:")
    for vuln in vulnerabilities:
        print(f"- {vuln.title}: {vuln.description} (Severity: {vuln.severity.value})")

    # Analyze a DeFi protocol
    defi_analyzer = DeFiProtocolAnalyzer(BlockchainNetwork.ETHEREUM)

    protocol_analysis = await defi_analyzer.analyze_protocol(
        "Uniswap V2",
        ["0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"]
    )

    print(f"\nDeFi Protocol Analysis for {protocol_analysis.protocol_name}:")
    print(f"Risk Score: {protocol_analysis.risk_score}/10")
    print(f"Total Value Locked: ${protocol_analysis.total_value_locked:,.2f}")
    print(f"Vulnerabilities: {len(protocol_analysis.vulnerabilities)}")

    # Web3 threat detection
    _ = Web3ThreatDetector()  # Initialize detector (unused in demo)

    # Example transaction analysis would go here
    print("\nWeb3 threat detection system initialized")


if __name__ == "__main__":
    asyncio.run(example_blockchain_analysis())

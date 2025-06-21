"""
Advanced AI-powered security analysis engine with LLM integration.
Provides intelligent vulnerability analysis, threat prediction,
and automated remediation.
"""

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from scout.logging import log_error, log_info, log_warning

try:
    import numpy as np
except ImportError:
    np = None

try:
    import torch
    from transformers import AutoModel, AutoTokenizer, pipeline
except ImportError:
    pipeline = AutoTokenizer = AutoModel = torch = None

try:
    import ollama
except ImportError:
    ollama = None

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

# Constants
MICROSOFT_CODEBERT_MODEL = "microsoft/codebert-base"

class AIProvider(Enum):
    """Supported AI providers for security analysis."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"

@dataclass
class VulnerabilityAnalysis:
    """AI-generated vulnerability analysis."""
    vulnerability_id: str
    severity_score: float
    confidence: float
    description: str
    impact_assessment: str
    exploitation_likelihood: float
    remediation_suggestions: List[str]
    false_positive_probability: float
    threat_actor_relevance: Dict[str, float]
    business_impact: str
    technical_details: Dict[str, Any]

@dataclass
class ThreatIntelligence:
    """AI-enhanced threat intelligence data."""
    threat_id: str
    threat_type: str
    indicators: List[str]
    attribution: Dict[str, float]
    campaign_correlation: List[str]
    prediction_confidence: float
    timeline_analysis: Dict[str, str]
    mitigation_strategies: List[str]

class SecurityLLM:
    """Advanced Language Model for security analysis."""

    def __init__(self, provider: AIProvider = AIProvider.OLLAMA):
        self.provider = provider
        self.model_cache = {}
        self.conversation_history = []
        self._setup_provider()

    def _setup_provider(self):
        """
    Initialize the selected AI provider."""
        if self.provider == AIProvider.OPENAI:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = AsyncOpenAI(api_key=api_key)
                self.model_name = "gpt-4"
            else:
                log_warning(
                    "OpenAI API key not found, falling back to Ollama"
                )
                self.provider = AIProvider.OLLAMA
                self._setup_ollama()

        elif self.provider == AIProvider.ANTHROPIC:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.client = anthropic.AsyncAnthropic(api_key=api_key)
                self.model_name = "claude-3-sonnet-20240229"
            else:
                log_warning(
                    "Anthropic API key not found, falling back to Ollama"
                )
                self.provider = AIProvider.OLLAMA
                self._setup_ollama()

        elif self.provider == AIProvider.OLLAMA:
            self._setup_ollama()

        elif self.provider == AIProvider.HUGGINGFACE:
            self._setup_huggingface()

    def _setup_ollama(self):
        """Setup local Ollama model."""
        try:
            # Try to use a security-focused model if available
            models = ollama.list()
            security_models = ['codellama:13b', 'llama2:13b', 'mistral:7b']

            for model in security_models:
                if any(m['name'].startswith(model.split(':')[0]) for m in models['models']):
                    self.model_name = model
                    break
            else:
                # Default to first available model
                if models['models']:
                    self.model_name = models['models'][0]['name']
                else:
                    log_error("No Ollama models available")
                    self.model_name = "llama2:7b"  # Fallback
        except Exception as e:
            log_error(f"Failed to setup Ollama: {e}")
            self.model_name = "llama2:7b"

    def _setup_huggingface(self):
        """Setup HuggingFace models for local inference."""
        try:
            # Security-focused models
            self.vulnerability_classifier = pipeline(
                "text-classification",
                model=MICROSOFT_CODEBERT_MODEL,
                return_all_scores=True
            )

            self.code_analyzer = pipeline(
                "text-generation",
                model="microsoft / DialoGPT-medium"
            )

            self.tokenizer = AutoTokenizer.from_pretrained(MICROSOFT_CODEBERT_MODEL)
            self.model = AutoModel.from_pretrained(MICROSOFT_CODEBERT_MODEL)

        except Exception as e:
            log_error(f"Failed to setup HuggingFace models: {e}")
            self.provider = AIProvider.OLLAMA
            self._setup_ollama()

    async def analyze_vulnerability(self,
        vulnerability_data: Dict[str,
        Any]) -> VulnerabilityAnalysis:
        """Perform AI-powered vulnerability analysis."""

        prompt = self._build_vulnerability_prompt(vulnerability_data)

        try:
            if self.provider == AIProvider.OPENAI:
                response = await self._query_openai(prompt)
            elif self.provider == AIProvider.ANTHROPIC:
                response = await self._query_anthropic(prompt)
            elif self.provider == AIProvider.OLLAMA:
                response = await self._query_ollama(prompt)
            else:
                response = await self._query_huggingface(prompt)

            return self._parse_vulnerability_analysis(response, vulnerability_data)

        except Exception as e:
            log_error(f"AI vulnerability analysis failed: {e}")
            return self._fallback_analysis(vulnerability_data)

    def _build_vulnerability_prompt(self, vuln_data: Dict[str, Any]) -> str:
        """Build a comprehensive prompt for vulnerability analysis."""

        return f"""
    You are an expert cybersecurity analyst with deep knowledge of vulnerability assessment and threat modeling.

    Analyze the following vulnerability data and provide a comprehensive security assessment:

    Vulnerability Details:
   -Type: {vuln_data.get('type', 'Unknown')}
   -Target: {vuln_data.get('target', 'Unknown')}
   -Description: {vuln_data.get('description', 'No description')}
   -Severity: {vuln_data.get('severity', 'Unknown')}
   -Evidence: {vuln_data.get('evidence', 'No evidence')}
   -Context: {vuln_data.get('context', {})}

    Please provide a detailed analysis including:

    1. **Severity Assessment**: Rate the vulnerability from 1-10 with justification
    2. **Exploitation Analysis**: Likelihood and complexity of exploitation
    3. **Business Impact**: Potential damage to the organization
    4. **False Positive Assessment**: Probability this is a false positive (0-1)
    5. **Remediation Strategy**: Step-by-step mitigation recommendations
    6. **Threat Actor Relevance**: Which threat actors might exploit this
    7. **Technical Deep Dive**: Detailed technical analysis

    Respond in JSON format with structured analysis data.
        """.strip()

    async def _query_openai(self, prompt: str) -> str:
        """Query OpenAI GPT models."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity expert specializing in vulnerability analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            log_error(f"OpenAI query failed: {e}")
            raise

    async def _query_anthropic(self, prompt: str) -> str:
        """Query Anthropic Claude models."""
        try:
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            log_error(f"Anthropic query failed: {e}")
            raise

    async def _query_ollama(self, prompt: str) -> str:
        """Query local Ollama models."""
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'temperature': 0.1,
                    'top_p': 0.9,
                    'num_predict': 1000
                }
            )
            return response['response']
        except Exception as e:
            log_error(f"Ollama query failed: {e}")
            raise

    async def _query_huggingface(self, prompt: str) -> str:
        """Query HuggingFace models locally."""
        try:
            # Simplified local processing
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

            with torch.no_grad():
                outputs = self.model(**inputs)
                # Simple analysis based on embeddings
                embeddings = outputs.last_hidden_state.mean(dim=1)

                # Generate a basic analysis (in production, use more sophisticated models)
                analysis = {
                    "severity_score": float(torch.sigmoid(embeddings[0][0])) * 10,
                    "confidence": float(torch.sigmoid(embeddings[0][1])),
                    "false_positive_probability": float(torch.sigmoid(embeddings[0][2]))
                }

                return json.dumps(analysis)
        except Exception as e:
            log_error(f"HuggingFace query failed: {e}")
            raise

    def _parse_vulnerability_analysis(self,
                                      ai_response: str,
                                      vuln_data: Dict[str, Any]
                                      ) -> VulnerabilityAnalysis:
        """Parse AI response into structured vulnerability analysis."""

        try:
            # Try to parse JSON response
            if ai_response.strip().startswith('{'):
                analysis_data = json.loads(ai_response)
            else:
                # Parse natural language response
                analysis_data = self._extract_analysis_from_text(ai_response)

            return VulnerabilityAnalysis(
                vulnerability_id=vuln_data.get('id', f"vuln_{datetime.now().strftime('%Y % m%d_ % H%M % S')}"),
                severity_score=analysis_data.get('severity_score', 5.0),
                confidence=analysis_data.get('confidence', 0.7),
                description=analysis_data.get('description', vuln_data.get('description', '')),
                impact_assessment=analysis_data.get('impact_assessment', 'Medium impact'),
                exploitation_likelihood=analysis_data.get('exploitation_likelihood', 0.5),
                remediation_suggestions=analysis_data.get('remediation_suggestions', ['Review and patch']),
                false_positive_probability=analysis_data.get('false_positive_probability', 0.3),
                threat_actor_relevance=analysis_data.get('threat_actor_relevance', {}),
                business_impact=analysis_data.get('business_impact', 'Potential business disruption'),
                technical_details=analysis_data.get('technical_details', {})
            )

        except Exception as e:
            log_error(f"Failed to parse AI analysis: {e}")
            return self._fallback_analysis(vuln_data)

    def _extract_analysis_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured data from natural language AI response."""

        # Simple regex-based extraction (in production, use more sophisticated NLP)
        import re

        analysis = {}

        # Extract severity score
        severity_match = re.search(r'severity.*?(\d + (?:\.\d+)?)', text, re.IGNORECASE)
        if severity_match:
            analysis['severity_score'] = float(severity_match.group(1))

        # Extract confidence
        confidence_match = re.search(r'confidence.*?(\d + (?:\.\d+)?)', text, re.IGNORECASE)
        if confidence_match:
            analysis['confidence'] = float(confidence_match.group(1)) / 100 if float(confidence_match.group(1)) > 1 else float(confidence_match.group(1))

        # Extract false positive probability
        fp_match = re.search(r'false positive.*?(\d + (?:\.\d+)?)', text, re.IGNORECASE)
        if fp_match:
            analysis['false_positive_probability'] = float(fp_match.group(1)) / 100 if float(fp_match.group(1)) > 1 else float(fp_match.group(1))

        # Extract remediation suggestions
        remediation_section = re.search(r'remediation.*?:(.*?)(?:\n\n|\n\d+\.|\nThreat|\nBusiness|$)',
            text,
            re.IGNORECASE | re.DOTALL)
        if remediation_section:
            remediation_text = remediation_section.group(1)
            suggestions = [s.strip('- ').strip() for s in remediation_text.split('\n') if s.strip() and not s.strip().startswith('*')]
            analysis['remediation_suggestions'] = suggestions[:5]  # Limit to 5 suggestions

        return analysis

    def _fallback_analysis(self, vuln_data: Dict[str, Any]) -> VulnerabilityAnalysis:
        """
    Provide fallback analysis when AI fails."""

        severity_map = {'critical': 9.0, 'high': 7.0, 'medium': 5.0, 'low': 3.0, 'info': 1.0}
        severity = vuln_data.get('severity', 'medium').lower()
        severity_score = severity_map.get(severity, 5.0)

        return VulnerabilityAnalysis(
            vulnerability_id=vuln_data.get('id', f"vuln_{datetime.now().strftime('%Y % m%d_ % H%M % S')}"),
            severity_score=severity_score,
            confidence=0.6,
            description=vuln_data.get('description', 'Vulnerability detected'),
            impact_assessment=f"{severity.title()} impact vulnerability",
            exploitation_likelihood=severity_score / 10.0,
            remediation_suggestions=['Review the vulnerability', 'Apply security patches', 'Implement monitoring'],
            false_positive_probability=0.4,
            threat_actor_relevance={'generic': 0.5},
            business_impact='Potential security risk',
            technical_details=vuln_data.get('context', {})
        )

class ThreatPredictionEngine:
    """AI-powered threat prediction and intelligence engine."""

    def __init__(self, llm):
        self.llm = llm
        self.threat_patterns = {}
        self.historical_data = []

    async def predict_threats(self, current_vulnerabilities: List[VulnerabilityAnalysis]) -> List[ThreatIntelligence]:
        """
    Predict potential threats based on current vulnerabilities."""

        threat_predictions = []

        for vuln in current_vulnerabilities:
            prediction = await self._analyze_threat_landscape(vuln)
            threat_predictions.append(prediction)

        return threat_predictions

    async def _analyze_threat_landscape(self, vulnerability: VulnerabilityAnalysis) -> ThreatIntelligence:
        """
    Analyze threat landscape for a specific vulnerability."""

        prompt = f"""
    Analyze the threat landscape for this vulnerability:

    Vulnerability: {vulnerability.vulnerability_id}
    Severity: {vulnerability.severity_score}/10
    Description: {vulnerability.description}
    Exploitation Likelihood: {vulnerability.exploitation_likelihood}

    Provide threat intelligence including:
    1. Potential threat actors who might exploit this
    2. Attack campaigns that might use this vulnerability
    3. Timeline for potential exploitation
    4. Mitigation strategies
    5. Related IOCs and TTPs

    Respond in JSON format.
        """

        try:
            response = await self.llm._query_ollama(prompt)  # Use Ollama for local analysis
            threat_data = self._parse_threat_response(response)

            return ThreatIntelligence(
                threat_id=f"threat_{vulnerability.vulnerability_id}",
                threat_type=threat_data.get('threat_type', 'Unknown'),
                indicators=threat_data.get('indicators', []),
                attribution=threat_data.get('attribution', {}),
                campaign_correlation=threat_data.get('campaigns', []),
                prediction_confidence=threat_data.get('confidence', 0.5),
                timeline_analysis=threat_data.get('timeline', {}),
                mitigation_strategies=threat_data.get('mitigation', [])
            )

        except Exception as e:
            log_error(f"Threat prediction failed: {e}")
            return self._fallback_threat_intelligence(vulnerability)

    def _parse_threat_response(self, response: str) -> Dict[str, Any]:
        """Parse threat intelligence from AI response."""
        try:
            if response.strip().startswith('{'):
                return json.loads(response)
            else:
                # Simple fallback parsing
                return {
                    'threat_type': 'Generic',
                    'confidence': 0.5,
                    'indicators': [],
                    'attribution': {},
                    'campaigns': [],
                    'timeline': {},
                    'mitigation': ['Monitor for exploitation', 'Apply patches']
                }
        except json.JSONDecodeError:
            return {}

    def _fallback_threat_intelligence(self, vulnerability: VulnerabilityAnalysis) -> ThreatIntelligence:
        """
    Fallback threat intelligence when AI analysis fails."""

        return ThreatIntelligence(
            threat_id=f"threat_{vulnerability.vulnerability_id}",
            threat_type="Generic Threat",
            indicators=[],
            attribution={'unknown': 1.0},
            campaign_correlation=[],
            prediction_confidence=0.3,
            timeline_analysis={'immediate': 'Low risk', 'short_term': 'Medium risk', 'long_term': 'High risk'},
            mitigation_strategies=['Apply security updates', 'Monitor for indicators', 'Implement detection rules']
        )

class AISecurityEngine:
    """Main AI security engine coordinating all AI-powered analysis."""

    def __init__(self, provider: AIProvider = AIProvider.OLLAMA):
        self.llm = SecurityLLM(provider)
        self.threat_engine = ThreatPredictionEngine(self.llm)
        self.analysis_cache = {}

    async def comprehensive_analysis(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """
    Perform comprehensive AI-powered security analysis."""

        log_info("Starting AI-powered security analysis...")

        # Extract vulnerabilities from scan results
        vulnerabilities = scan_results.get('vulnerabilities', [])

        # Perform AI analysis on each vulnerability
        ai_analyses = []
        for vuln in vulnerabilities:
            analysis = await self.llm.analyze_vulnerability(vuln)
            ai_analyses.append(analysis)

        # Predict threats based on vulnerabilities
        threat_predictions = await self.threat_engine.predict_threats(ai_analyses)

        # Generate executive summary
        executive_summary = await self._generate_executive_summary(ai_analyses, threat_predictions)

        # Compile comprehensive report
        comprehensive_report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'ai_provider': self.llm.provider.value,
            'vulnerability_analyses': [self._analysis_to_dict(a) for a in ai_analyses],
            'threat_intelligence': [self._threat_to_dict(t) for t in threat_predictions],
            'executive_summary': executive_summary,
            'risk_metrics': self._calculate_risk_metrics(ai_analyses),
            'recommendations': self._generate_recommendations(ai_analyses, threat_predictions)
        }

        log_info(f"AI analysis complete. Analyzed {len(ai_analyses)} vulnerabilities.")

        return comprehensive_report

    async def _generate_executive_summary(self,
        analyses: List[VulnerabilityAnalysis],
        threats: List[ThreatIntelligence]) -> str:
        """Generate executive summary using AI."""

        total_vulns = len(analyses)
        high_severity = len([a for a in analyses if a.severity_score >= 7.0])
        avg_confidence = sum(a.confidence for a in analyses) / total_vulns if total_vulns > 0 else 0

        prompt = f"""
    Generate an executive summary for a security assessment:

    Statistics:
   -Total vulnerabilities: {total_vulns}
   -High severity vulnerabilities: {high_severity}
   -Average AI confidence: {avg_confidence:.2f}
   -Threat predictions: {len(threats)}

    Key findings:
    {chr(10).join([f"- {a.description[:100]}..." for a in analyses[:5]])}

    Create a concise executive summary suitable for C-level executives.
        """

        try:
            summary = await self.llm._query_ollama(prompt)
            return summary
        except Exception:
            return f"Security assessment identified {total_vulns} vulnerabilities, including {high_severity} high-severity issues requiring immediate attention."

    def _calculate_risk_metrics(self, analyses: List[VulnerabilityAnalysis]) -> Dict[str, float]:
        """Calculate comprehensive risk metrics."""

        if not analyses:
            return {}

        severity_scores = [a.severity_score for a in analyses]
        exploitation_scores = [a.exploitation_likelihood for a in analyses]
        confidence_scores = [a.confidence for a in analyses]

        return {
            'overall_risk_score': np.mean(severity_scores) * np.mean(exploitation_scores),
            'average_severity': np.mean(severity_scores),
            'max_severity': np.max(severity_scores),
            'exploitation_probability': np.mean(exploitation_scores),
            'analysis_confidence': np.mean(confidence_scores),
            'vulnerability_count': len(analyses),
            'critical_vulnerability_count': len([a for a in analyses if a.severity_score >= 9.0]),
            'false_positive_rate': np.mean([a.false_positive_probability for a in analyses])
        }

    def _generate_recommendations(self,
                                  analyses: List[VulnerabilityAnalysis],
                                  threats) -> List[str]:
        """
    Generate prioritized recommendations."""

        recommendations = set()

        # High-severity vulnerability recommendations
        high_severity_vulns = [a for a in analyses if a.severity_score >= 7.0]
        if high_severity_vulns:
            recommendations.add("Immediately address high-severity vulnerabilities")
            for vuln in high_severity_vulns[:3]:  # Top 3
                recommendations.update(vuln.remediation_suggestions[:2])  # Top 2 suggestions

        # Threat-based recommendations
        high_confidence_threats = [t for t in threats if t.prediction_confidence >= 0.7]
        if high_confidence_threats:
            recommendations.add("Implement threat-specific monitoring and detection")
            for threat in high_confidence_threats[:2]:  # Top 2
                recommendations.update(threat.mitigation_strategies[:2])

        # General recommendations
        recommendations.add("Implement continuous security monitoring")
        recommendations.add("Establish regular vulnerability assessment schedule")
        recommendations.add("Enhance security awareness training")

        return list(recommendations)[:10]  # Limit to top 10

    def _analysis_to_dict(self, analysis: VulnerabilityAnalysis) -> Dict[str, Any]:
        """Convert vulnerability analysis to dictionary."""
        return {
            'vulnerability_id': analysis.vulnerability_id,
            'severity_score': analysis.severity_score,
            'confidence': analysis.confidence,
            'description': analysis.description,
            'impact_assessment': analysis.impact_assessment,
            'exploitation_likelihood': analysis.exploitation_likelihood,
            'remediation_suggestions': analysis.remediation_suggestions,
            'false_positive_probability': analysis.false_positive_probability,
            'threat_actor_relevance': analysis.threat_actor_relevance,
            'business_impact': analysis.business_impact,
            'technical_details': analysis.technical_details
        }

    def _threat_to_dict(self, threat: ThreatIntelligence) -> Dict[str, Any]:
        """
    Convert threat intelligence to dictionary."""
        return {
            'threat_id': threat.threat_id,
            'threat_type': threat.threat_type,
            'indicators': threat.indicators,
            'attribution': threat.attribution,
            'campaign_correlation': threat.campaign_correlation,
            'prediction_confidence': threat.prediction_confidence,
            'timeline_analysis': threat.timeline_analysis,
            'mitigation_strategies': threat.mitigation_strategies
        }

async def main():
    """
    Example usage of AI security engine."""

    # Initialize AI engine
    ai_engine = AISecurityEngine(AIProvider.OLLAMA)

    # Example scan results
    scan_results = {
        'vulnerabilities': [
            {
                'id': 'sql_injection_001',
                'type': 'SQL Injection',
                'target': 'login.php',
                'description': 'SQL injection vulnerability in login form',
                'severity': 'high',
                'evidence': 'Error-based SQL injection detected',
                'context': {'method': 'POST', 'parameter': 'username'}
            },
            {
                'id': 'xss_001',
                'type': 'Cross-Site Scripting',
                'target': 'search.php',
                'description': 'Reflected XSS in search parameter',
                'severity': 'medium',
                'evidence': 'Script injection successful',
                'context': {'method': 'GET', 'parameter': 'q'}
            }
        ]
    }

    # Perform AI analysis
    analysis_result = await ai_engine.comprehensive_analysis(scan_results)

    print(json.dumps(analysis_result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())

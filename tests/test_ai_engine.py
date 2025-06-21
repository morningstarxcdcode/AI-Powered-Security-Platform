"""
Test Scout AI Engine functionality
"""
from unittest.mock import Mock, patch

import pytest

from scout.ai_engine import AIEngine, AIProvider


class TestAIEngine:
    """Test AI Engine functionality."""

    def test_ai_engine_initialization(self):
        """Test AI engine initialization."""
        engine = AIEngine()
        assert engine.default_provider == AIProvider.OPENAI
        assert engine.providers == {}

    @patch('scout.ai_engine.openai')
    def test_openai_provider_setup(self, mock_openai):
        """Test OpenAI provider setup."""
        engine = AIEngine()
        engine.setup_provider(AIProvider.OPENAI, api_key="test-key")
        assert AIProvider.OPENAI in engine.providers

    def test_analyze_vulnerabilities_mock(self):
        """Test vulnerability analysis with mocked response."""
        engine = AIEngine()
        
        # Mock findings
        findings = [
            {
                'finding': 'SQL injection vulnerability in login form',
                'target': 'https://example.com/login'
            }
        ]
        
        # Mock AI response
        mock_response = {
            'analysis': 'Critical SQL injection vulnerability detected',
            'severity': 'critical',
            'recommendations': ['Use parameterized queries', 'Input validation']
        }
        
        with patch.object(engine, '_call_ai_provider', return_value=mock_response):
            result = engine.analyze_vulnerabilities(findings)
            assert 'analysis' in result
            assert result['severity'] == 'critical'

    def test_generate_executive_summary_mock(self):
        """Test executive summary generation with mocked response."""
        engine = AIEngine()
        
        findings = [
            {'finding': 'XSS vulnerability', 'severity': 'high'},
            {'finding': 'Missing security headers', 'severity': 'medium'}
        ]
        
        mock_summary = {
            'executive_summary': 'Security assessment revealed 2 vulnerabilities',
            'risk_level': 'HIGH',
            'priority_actions': ['Fix XSS vulnerability immediately']
        }
        
        with patch.object(engine, '_call_ai_provider', return_value=mock_summary):
            result = engine.generate_executive_summary(findings)
            assert 'executive_summary' in result
            assert result['risk_level'] == 'HIGH'

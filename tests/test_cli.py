"""
Test Scout CLI functionality
"""
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from scout.cli import cli


class TestCLI:
    """Test CLI functionality."""

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Scout Security Platform' in result.output

    def test_scan_help(self):
        """Test scan command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['scan', '--help'])
        assert result.exit_code == 0
        assert 'security scan' in result.output.lower()

    def test_report_help(self):
        """Test report command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['report', '--help'])
        assert result.exit_code == 0
        assert 'generate' in result.output.lower()

    def test_config_help(self):
        """Test config command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['config', '--help'])
        assert result.exit_code == 0

    @patch('scout.cli.perform_security_scan')
    def test_scan_command_basic(self, mock_scan):
        """Test basic scan command execution."""
        mock_scan.return_value = {
            'findings': [],
            'scan_info': {
                'target': 'https://example.com',
                'scan_time': '2025-06-21 12:00:00'
            }
        }
        
        runner = CliRunner()
        result = runner.invoke(cli, ['scan', 'https://example.com'])
        
        # Should not fail
        assert result.exit_code == 0
        mock_scan.assert_called_once()

    @patch('scout.cli.generate_reports')
    def test_report_command_basic(self, mock_report):
        """Test basic report command execution."""
        mock_report.return_value = None
        
        runner = CliRunner()
        result = runner.invoke(cli, ['report', '--input', 'test.json'])
        
        # Should handle missing file gracefully or call report function
        mock_report.assert_called_once()

    def test_version_command(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        # Should not fail, even if version is not set
        assert result.exit_code == 0

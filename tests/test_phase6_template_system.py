"""
Test suite for Phase 6.3: Template System
Tests the template_processor.py module functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import json

from src.data_acquisition.template_processor import TemplateProcessor


class TestTemplateProcessor:
    """Test cases for TemplateProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a test template processor instance."""
        return TemplateProcessor(
            template_dir=Path("/tmp/templates"),
            output_dir=Path("/tmp/output")
        )
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        template_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        yield Path(template_dir), Path(output_dir)
        shutil.rmtree(template_dir)
        shutil.rmtree(output_dir)
    
    def test_initialization(self, temp_dirs):
        """Test template processor initialization."""
        template_dir, output_dir = temp_dirs
        
        processor = TemplateProcessor(
            template_dir=template_dir,
            output_dir=output_dir
        )
        
        assert processor.template_dir == template_dir
        assert processor.output_dir == output_dir
        assert processor.templates == {}
    
    def test_load_templates(self, processor, temp_dirs):
        """Test loading template files."""
        template_dir, output_dir = temp_dirs
        processor.template_dir = template_dir
        
        # Create test template files
        registration_template = template_dir / "registration_template.csv"
        registration_template.write_text("Name,Club,Division\n{name},{club},{division}")
        
        match_template = template_dir / "match_template.xlsx"
        match_template.write_text("Match ID,Winner,Loser,Method\n{match_id},{winner},{loser},{method}")
        
        result = processor.load_templates()
        
        assert result is True
        assert len(processor.templates) == 2
        assert "registration_template.csv" in processor.templates
        assert "match_template.xlsx" in processor.templates
    
    def test_create_registration_template(self, processor, temp_dirs):
        """Test creating registration data template."""
        template_dir, output_dir = temp_dirs
        processor.template_dir = template_dir
        processor.output_dir = output_dir
        
        result = processor.create_registration_template()
        
        assert result["success"] is True
        assert "template_file" in result
        
        template_file = Path(result["template_file"])
        assert template_file.exists()
        assert template_file.suffix == ".csv"
    
    def test_create_match_template(self, processor, temp_dirs):
        """Test creating match data template."""
        template_dir, output_dir = temp_dirs
        processor.template_dir = template_dir
        processor.output_dir = output_dir
        
        result = processor.create_match_template()
        
        assert result["success"] is True
        assert "template_file" in result
        
        template_file = Path(result["template_file"])
        assert template_file.exists()
        assert template_file.suffix == ".xlsx"
    
    def test_validate_registration_data(self, processor):
        """Test registration data validation."""
        # Valid registration data
        valid_data = {
            "name": "John Doe",
            "club": "Test Club",
            "division": "Adult / Advanced / 70kg",
            "age": 25
        }
        
        result = processor.validate_registration_data(valid_data)
        assert result["valid"] is True
        
        # Invalid registration data (missing required fields)
        invalid_data = {
            "name": "John Doe",
            "club": "Test Club"
            # Missing division
        }
        
        result = processor.validate_registration_data(invalid_data)
        assert result["valid"] is False
        assert "errors" in result
    
    def test_validate_match_data(self, processor):
        """Test match data validation."""
        # Valid match data
        valid_data = {
            "match_id": "M001",
            "winner": "John Doe",
            "loser": "Jane Smith",
            "method": "SUBMISSION",
            "time": "2:30"
        }
        
        result = processor.validate_match_data(valid_data)
        assert result["valid"] is True
        
        # Invalid match data
        invalid_data = {
            "match_id": "M001",
            "winner": "John Doe"
            # Missing loser and method
        }
        
        result = processor.validate_match_data(invalid_data)
        assert result["valid"] is False
        assert "errors" in result
    
    def test_process_registration_data(self, processor, temp_dirs):
        """Test processing registration data."""
        template_dir, output_dir = temp_dirs
        processor.template_dir = template_dir
        processor.output_dir = output_dir
        
        # Create template
        template_result = processor.create_registration_template()
        template_file = Path(template_result["template_file"])
        
        # Test data
        test_data = [
            {"name": "John Doe", "club": "Club A", "division": "Adult / Advanced / 70kg"},
            {"name": "Jane Smith", "club": "Club B", "division": "Adult / Advanced / 65kg"}
        ]
        
        result = processor.process_registration_data(test_data, template_file)
        
        assert result["success"] is True
        assert "output_file" in result
        
        output_file = Path(result["output_file"])
        assert output_file.exists()
    
    def test_process_match_data(self, processor, temp_dirs):
        """Test processing match data."""
        template_dir, output_dir = temp_dirs
        processor.template_dir = template_dir
        processor.output_dir = output_dir
        
        # Create template
        template_result = processor.create_match_template()
        template_file = Path(template_result["template_file"])
        
        # Test data
        test_data = [
            {"match_id": "M001", "winner": "John Doe", "loser": "Jane Smith", "method": "SUBMISSION"},
            {"match_id": "M002", "winner": "Bob Johnson", "loser": "Alice Brown", "method": "POINTS"}
        ]
        
        result = processor.process_match_data(test_data, template_file)
        
        assert result["success"] is True
        assert "output_file" in result
        
        output_file = Path(result["output_file"])
        assert output_file.exists()
    
    def test_get_auto_suggestions(self, processor):
        """Test auto-suggestion functionality."""
        # Test athlete name suggestions
        suggestions = processor.get_auto_suggestions("athlete_name", "Jo")
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        
        # Test club name suggestions
        suggestions = processor.get_auto_suggestions("club_name", "Test")
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
    
    def test_export_template(self, processor, temp_dirs):
        """Test template export functionality."""
        template_dir, output_dir = temp_dirs
        processor.template_dir = template_dir
        processor.output_dir = output_dir
        
        # Create a template
        template_result = processor.create_registration_template()
        template_file = Path(template_result["template_file"])
        
        # Export template
        result = processor.export_template(template_file, "registration_export.csv")
        
        assert result["success"] is True
        assert "export_file" in result
        
        export_file = Path(result["export_file"])
        assert export_file.exists()
    
    def test_import_template(self, processor, temp_dirs):
        """Test template import functionality."""
        template_dir, output_dir = temp_dirs
        processor.template_dir = template_dir
        processor.output_dir = output_dir
        
        # Create a test template file
        test_template = output_dir / "test_template.csv"
        test_template.write_text("Name,Club,Division\n{name},{club},{division}")
        
        # Import template
        result = processor.import_template(test_template, "imported_template")
        
        assert result["success"] is True
        assert "template_name" in result
        
        # Check if template was loaded
        assert "imported_template.csv" in processor.templates


class TestTemplateProcessorIntegration:
    """Integration tests for TemplateProcessor."""
    
    @pytest.fixture
    def processor(self, temp_dirs):
        """Create a test template processor instance."""
        template_dir, output_dir = temp_dirs
        return TemplateProcessor(
            template_dir=template_dir,
            output_dir=output_dir
        )
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        template_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        yield Path(template_dir), Path(output_dir)
        shutil.rmtree(template_dir)
        shutil.rmtree(output_dir)
    
    def test_complete_template_workflow(self, processor):
        """Test complete template workflow."""
        # Load templates
        load_result = processor.load_templates()
        assert load_result is True
        
        # Create registration template
        reg_template_result = processor.create_registration_template()
        assert reg_template_result["success"] is True
        
        # Create match template
        match_template_result = processor.create_match_template()
        assert match_template_result["success"] is True
        
        # Process sample data
        registration_data = [
            {"name": "John Doe", "club": "Club A", "division": "Adult / Advanced / 70kg"}
        ]
        
        reg_process_result = processor.process_registration_data(
            registration_data, 
            Path(reg_template_result["template_file"])
        )
        assert reg_process_result["success"] is True
        
        # Validate the output
        output_file = Path(reg_process_result["output_file"])
        assert output_file.exists()
        assert output_file.stat().st_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
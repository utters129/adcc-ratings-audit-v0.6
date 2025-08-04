"""
Template Processor for ADCC Analysis Engine v0.6
Handles template-based data entry and validation for manual data input.
"""

import structlog
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import json
import shutil
from datetime import datetime
import re

logger = structlog.get_logger(__name__)


class TemplateProcessor:
    """
    Template-based data processing system.
    
    Handles template creation, data validation, auto-suggestions,
    and manual data entry for registration and match data.
    """
    
    def __init__(self, template_dir: Path, output_dir: Path):
        """
        Initialize template processor.
        
        Args:
            template_dir: Directory for template files
            output_dir: Directory for output files
        """
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.templates = {}
        
        # Ensure directories exist
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing templates
        self.load_templates()
        
        logger.info("TemplateProcessor initialized", 
                   template_dir=str(template_dir), 
                   output_dir=str(output_dir))
    
    def load_templates(self) -> bool:
        """
        Load existing template files.
        
        Returns:
            bool: True if templates loaded successfully
        """
        try:
            if not self.template_dir.exists():
                logger.warning("Template directory does not exist", 
                              template_dir=str(self.template_dir))
                return False
            
            # Find template files
            template_files = list(self.template_dir.glob("*.csv")) + \
                           list(self.template_dir.glob("*.xlsx"))
            
            for template_file in template_files:
                try:
                    template_content = template_file.read_text(encoding='utf-8')
                    self.templates[template_file.name] = {
                        "path": template_file,
                        "content": template_content,
                        "type": template_file.suffix
                    }
                    logger.debug("Loaded template", filename=template_file.name)
                except Exception as e:
                    logger.error("Error loading template", 
                                filename=template_file.name, error=str(e))
            
            logger.info("Templates loaded", count=len(self.templates))
            return True
            
        except Exception as e:
            logger.error("Error loading templates", error=str(e))
            return False
    
    def create_registration_template(self) -> Dict[str, Any]:
        """
        Create a registration data template.
        
        Returns:
            Dict containing template creation result
        """
        try:
            template_content = """Name,Club,Division,Age,Weight,Experience Level,Notes
{name},{club},{division},{age},{weight},{experience},{notes}"""
            
            template_filename = f"registration_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            template_path = self.template_dir / template_filename
            
            template_path.write_text(template_content, encoding='utf-8')
            
            # Add to templates dictionary
            self.templates[template_filename] = {
                "path": template_path,
                "content": template_content,
                "type": ".csv"
            }
            
            logger.info("Registration template created", filename=template_filename)
            
            return {
                "success": True,
                "template_file": str(template_path),
                "filename": template_filename
            }
            
        except Exception as e:
            logger.error("Error creating registration template", error=str(e))
            return {
                "success": False,
                "error": f"Template creation failed: {str(e)}"
            }
    
    def create_match_template(self) -> Dict[str, Any]:
        """
        Create a match data template.
        
        Returns:
            Dict containing template creation result
        """
        try:
            template_content = """Match ID,Winner,Loser,Method,Time,Division,Round,Notes
{match_id},{winner},{loser},{method},{time},{division},{round},{notes}"""
            
            template_filename = f"match_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            template_path = self.template_dir / template_filename
            
            template_path.write_text(template_content, encoding='utf-8')
            
            # Add to templates dictionary
            self.templates[template_filename] = {
                "path": template_path,
                "content": template_content,
                "type": ".csv"
            }
            
            logger.info("Match template created", filename=template_filename)
            
            return {
                "success": True,
                "template_file": str(template_path),
                "filename": template_filename
            }
            
        except Exception as e:
            logger.error("Error creating match template", error=str(e))
            return {
                "success": False,
                "error": f"Template creation failed: {str(e)}"
            }
    
    def validate_registration_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate registration data.
        
        Args:
            data: Registration data to validate
            
        Returns:
            Dict containing validation result
        """
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ["name", "club", "division"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate name format
        if "name" in data and data["name"]:
            if not re.match(r"^[A-Za-z\s\-']+$", data["name"]):
                warnings.append("Name contains unusual characters")
        
        # Validate age if present
        if "age" in data and data["age"]:
            try:
                age = int(data["age"])
                if age < 5 or age > 100:
                    warnings.append("Age seems unusual")
            except ValueError:
                errors.append("Age must be a number")
        
        # Validate weight if present
        if "weight" in data and data["weight"]:
            try:
                weight = float(data["weight"])
                if weight < 20 or weight > 200:
                    warnings.append("Weight seems unusual")
            except ValueError:
                errors.append("Weight must be a number")
        
        # Validate division format
        if "division" in data and data["division"]:
            division = data["division"]
            if not any(keyword in division.lower() for keyword in ["adult", "youth", "masters"]):
                warnings.append("Division format may be incorrect")
        
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
        
        if errors:
            logger.warning("Registration data validation failed", 
                          errors=errors, data=data)
        elif warnings:
            logger.info("Registration data validation completed with warnings", 
                       warnings=warnings)
        else:
            logger.info("Registration data validation passed")
        
        return result
    
    def validate_match_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate match data.
        
        Args:
            data: Match data to validate
            
        Returns:
            Dict containing validation result
        """
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ["match_id", "winner", "loser", "method"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate match ID format
        if "match_id" in data and data["match_id"]:
            if not re.match(r"^[A-Za-z0-9\-_]+$", data["match_id"]):
                warnings.append("Match ID contains unusual characters")
        
        # Validate method
        if "method" in data and data["method"]:
            valid_methods = ["SUBMISSION", "POINTS", "DECISION", "DISQUALIFICATION", "INJURY"]
            if data["method"].upper() not in valid_methods:
                warnings.append(f"Method '{data['method']}' not in standard list")
        
        # Validate time format if present
        if "time" in data and data["time"]:
            time_pattern = r"^\d{1,2}:\d{2}$"
            if not re.match(time_pattern, data["time"]):
                warnings.append("Time format should be MM:SS")
        
        # Check for same winner and loser
        if "winner" in data and "loser" in data and data["winner"] and data["loser"]:
            if data["winner"].lower() == data["loser"].lower():
                errors.append("Winner and loser cannot be the same")
        
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
        
        if errors:
            logger.warning("Match data validation failed", 
                          errors=errors, data=data)
        elif warnings:
            logger.info("Match data validation completed with warnings", 
                       warnings=warnings)
        else:
            logger.info("Match data validation passed")
        
        return result
    
    def process_registration_data(self, data: List[Dict[str, Any]], 
                                template_file: Path) -> Dict[str, Any]:
        """
        Process registration data using a template.
        
        Args:
            data: List of registration data dictionaries
            template_file: Path to template file
            
        Returns:
            Dict containing processing result
        """
        try:
            # Validate template file
            if not template_file.exists():
                return {
                    "success": False,
                    "error": f"Template file not found: {template_file}"
                }
            
            # Read template
            template_content = template_file.read_text(encoding='utf-8')
            
            # Process each data record
            processed_rows = []
            for i, record in enumerate(data):
                # Validate data
                validation = self.validate_registration_data(record)
                if not validation["valid"]:
                    logger.warning(f"Invalid data at index {i}", errors=validation["errors"])
                    continue
                
                # Apply template
                try:
                    processed_row = template_content.format(**record)
                    processed_rows.append(processed_row)
                except KeyError as e:
                    logger.error(f"Missing template variable at index {i}", 
                                missing_field=str(e))
                    continue
            
            if not processed_rows:
                return {
                    "success": False,
                    "error": "No valid data to process"
                }
            
            # Create output file
            output_filename = f"processed_registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            output_path = self.output_dir / output_filename
            
            # Write processed data
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(processed_rows))
            
            logger.info("Registration data processed", 
                       input_count=len(data), 
                       output_count=len(processed_rows),
                       output_file=str(output_path))
            
            return {
                "success": True,
                "output_file": str(output_path),
                "processed_count": len(processed_rows),
                "total_count": len(data)
            }
            
        except Exception as e:
            logger.error("Error processing registration data", error=str(e))
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}"
            }
    
    def process_match_data(self, data: List[Dict[str, Any]], 
                          template_file: Path) -> Dict[str, Any]:
        """
        Process match data using a template.
        
        Args:
            data: List of match data dictionaries
            template_file: Path to template file
            
        Returns:
            Dict containing processing result
        """
        try:
            # Validate template file
            if not template_file.exists():
                return {
                    "success": False,
                    "error": f"Template file not found: {template_file}"
                }
            
            # Read template
            template_content = template_file.read_text(encoding='utf-8')
            
            # Process each data record
            processed_rows = []
            for i, record in enumerate(data):
                # Validate data
                validation = self.validate_match_data(record)
                if not validation["valid"]:
                    logger.warning(f"Invalid data at index {i}", errors=validation["errors"])
                    continue
                
                # Apply template
                try:
                    processed_row = template_content.format(**record)
                    processed_rows.append(processed_row)
                except KeyError as e:
                    logger.error(f"Missing template variable at index {i}", 
                                missing_field=str(e))
                    continue
            
            if not processed_rows:
                return {
                    "success": False,
                    "error": "No valid data to process"
                }
            
            # Create output file
            output_filename = f"processed_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            output_path = self.output_dir / output_filename
            
            # Write processed data
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(processed_rows))
            
            logger.info("Match data processed", 
                       input_count=len(data), 
                       output_count=len(processed_rows),
                       output_file=str(output_path))
            
            return {
                "success": True,
                "output_file": str(output_path),
                "processed_count": len(processed_rows),
                "total_count": len(data)
            }
            
        except Exception as e:
            logger.error("Error processing match data", error=str(e))
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}"
            }
    
    def get_auto_suggestions(self, field_type: str, partial_input: str) -> List[str]:
        """
        Get auto-suggestions for data entry.
        
        Args:
            field_type: Type of field (athlete_name, club_name, etc.)
            partial_input: Partial user input
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # This is a simplified implementation
        # In a real system, this would query a database of existing data
        
        if field_type == "athlete_name":
            # Sample athlete names
            sample_names = [
                "John Doe", "Jane Smith", "Bob Johnson", "Alice Brown",
                "Charlie Wilson", "Diana Davis", "Edward Miller", "Fiona Garcia"
            ]
            suggestions = [name for name in sample_names 
                          if partial_input.lower() in name.lower()]
        
        elif field_type == "club_name":
            # Sample club names
            sample_clubs = [
                "Test Club", "Training Academy", "Fight Team", "BJJ School",
                "Martial Arts Center", "Combat Club", "Grappling Academy"
            ]
            suggestions = [club for club in sample_clubs 
                          if partial_input.lower() in club.lower()]
        
        elif field_type == "division":
            # Sample divisions
            sample_divisions = [
                "Adult / Advanced / 70kg", "Adult / Advanced / 65kg",
                "Adult / Intermediate / 80kg", "Youth / Advanced / 60kg",
                "Masters / Advanced / 75kg"
            ]
            suggestions = [div for div in sample_divisions 
                          if partial_input.lower() in div.lower()]
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def export_template(self, template_file: Path, export_name: str) -> Dict[str, Any]:
        """
        Export a template to a new location.
        
        Args:
            template_file: Path to template file
            export_name: Name for exported file
            
        Returns:
            Dict containing export result
        """
        try:
            if not template_file.exists():
                return {
                    "success": False,
                    "error": f"Template file not found: {template_file}"
                }
            
            export_path = self.output_dir / export_name
            
            # Copy template file
            shutil.copy2(template_file, export_path)
            
            logger.info("Template exported", 
                       source=str(template_file), 
                       destination=str(export_path))
            
            return {
                "success": True,
                "export_file": str(export_path)
            }
            
        except Exception as e:
            logger.error("Error exporting template", error=str(e))
            return {
                "success": False,
                "error": f"Export failed: {str(e)}"
            }
    
    def import_template(self, template_file: Path, template_name: str) -> Dict[str, Any]:
        """
        Import a template file.
        
        Args:
            template_file: Path to template file to import
            template_name: Name for the imported template
            
        Returns:
            Dict containing import result
        """
        try:
            if not template_file.exists():
                return {
                    "success": False,
                    "error": f"Template file not found: {template_file}"
                }
            
            # Generate import filename
            import_filename = f"{template_name}{template_file.suffix}"
            import_path = self.template_dir / import_filename
            
            # Copy template file
            shutil.copy2(template_file, import_path)
            
            # Load template content
            template_content = import_path.read_text(encoding='utf-8')
            
            # Add to templates dictionary
            self.templates[import_filename] = {
                "path": import_path,
                "content": template_content,
                "type": template_file.suffix
            }
            
            logger.info("Template imported", 
                       source=str(template_file), 
                       destination=str(import_path))
            
            return {
                "success": True,
                "template_name": import_filename
            }
            
        except Exception as e:
            logger.error("Error importing template", error=str(e))
            return {
                "success": False,
                "error": f"Import failed: {str(e)}"
            }
    
    def get_template_list(self) -> List[Dict[str, Any]]:
        """
        Get list of available templates.
        
        Returns:
            List of template information dictionaries
        """
        template_list = []
        
        for filename, template_info in self.templates.items():
            template_list.append({
                "name": filename,
                "path": str(template_info["path"]),
                "type": template_info["type"],
                "size": template_info["path"].stat().st_size if template_info["path"].exists() else 0
            })
        
        return template_list 
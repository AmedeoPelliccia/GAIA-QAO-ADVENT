"""
Markdown Parser for ATA Technical Documentation
Parsea documentos Markdown con procedimientos técnicos aeroespaciales
"""

import re
import markdown
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from markdown.extensions import toc, tables, fenced_code

@dataclass
class ProcedureStep:
    """Represents a single step in a procedure"""
    id: str
    title: str
    description: str
    duration: float = 5.0
    camera_angle: str = "default"
    overlay_text: str = ""
    narration: str = ""
    safety_notes: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.safety_notes is None:
            self.safety_notes = []

@dataclass
class ProcedureData:
    """Complete procedure data structure"""
    id: str
    title: str
    overview: str
    aircraft_model: str = ""
    ata_code: str = ""
    steps: Optional[List[ProcedureStep]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.metadata is None:
            self.metadata = {}

class MarkdownParser:
    """Parser for ATA-compliant Markdown documentation"""
    
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'toc',
                'tables', 
                'fenced_code',
                'attr_list',
                'def_list'
            ]
        )
        
        # Regex patterns for ATA codes and technical elements
        self.ata_pattern = re.compile(r'(\d{2}-\d{2}-\d{2}-\d{2})')
        self.step_pattern = re.compile(r'^###?\s*Step\s*(\d+)[:.]?\s*(.*)', re.IGNORECASE)
        self.torque_pattern = re.compile(r'(\d+)\s*(nm|n\.m|newton.*meter)', re.IGNORECASE)
        self.clearance_pattern = re.compile(r'(\d+)\s*(cm|mm|m|inch|in)', re.IGNORECASE)
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a Markdown file and return procedure data"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content, file_path.stem)
    
    def parse_content(self, content: str, filename: str = "") -> Dict[str, Any]:
        """Parse Markdown content and extract procedure information"""
        
        # Convert to HTML to extract structure (for future use)
        _ = self.md.convert(content)
        
        # Extract metadata from filename if it follows ATA convention
        procedure_id = self._extract_ata_code(filename) or self._extract_ata_code(content)
        
        # Parse main sections
        title = self._extract_title(content)
        overview = self._extract_overview(content)
        aircraft_model = self._extract_aircraft_model(content)
        steps = self._extract_steps(content)
        
        # Build procedure data
        procedure_data = {
            'id': procedure_id or filename,
            'title': title,
            'overview': overview,
            'aircraft_model': aircraft_model,
            'ata_code': procedure_id,
            'steps': steps,
            'metadata': {
                'source_file': filename,
                'total_steps': len(steps),
                'estimated_duration': sum(step['duration'] for step in steps)
            }
        }
        
        return procedure_data
    
    def _extract_title(self, content: str) -> str:
        """Extract main title from content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "Procedimiento sin título"
    
    def _extract_overview(self, content: str) -> str:
        """Extract overview section"""
        lines = content.split('\n')
        in_overview = False
        overview_lines = []
        
        for line in lines:
            if re.match(r'^##\s*overview', line, re.IGNORECASE):
                in_overview = True
                continue
            elif line.startswith('##') and in_overview:
                break
            elif in_overview and line.strip():
                overview_lines.append(line.strip())
        
        return ' '.join(overview_lines) if overview_lines else ""
    
    def _extract_aircraft_model(self, content: str) -> str:
        """Extract aircraft model from content"""
        # Look for common aircraft model patterns
        patterns = [
            r'BWB-Q\d+',
            r'Boeing \d{3}',
            r'Airbus A\d{3}',
            r'Aircraft:\s*([A-Z0-9-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1) if pattern.endswith(')') else match.group(0)
        
        return ""
    
    def _extract_ata_code(self, text: str) -> Optional[str]:
        """Extract ATA code from text"""
        match = self.ata_pattern.search(text)
        return match.group(1) if match else None
    
    def _extract_steps(self, content: str) -> List[Dict[str, Any]]:
        """Extract procedure steps from content"""
        steps = []
        lines = content.split('\n')
        current_step = None
        step_content = []
        
        for line in lines:
            step_match = self.step_pattern.match(line)
            
            if step_match:
                # Save previous step if exists
                if current_step:
                    current_step.update(self._parse_step_content(step_content))
                    steps.append(current_step)
                
                # Start new step
                step_num = step_match.group(1)
                step_title = step_match.group(2)
                current_step = {
                    'id': f"step_{step_num.zfill(2)}",
                    'title': step_title,
                    'description': step_title,
                    'duration': 5.0,
                    'camera_angle': 'default',
                    'overlay_text': '',
                    'narration': step_title,
                    'safety_notes': []
                }
                step_content = []
                
            elif current_step and line.strip():
                step_content.append(line)
        
        # Don't forget the last step
        if current_step:
            current_step.update(self._parse_step_content(step_content))
            steps.append(current_step)
        
        return steps
    
    def _parse_step_content(self, content_lines: List[str]) -> Dict[str, Any]:
        """Parse content of a step to extract details"""
        content = '\n'.join(content_lines)
        parsed = {}
        
        # Extract torque values
        torque_match = self.torque_pattern.search(content)
        if torque_match:
            parsed['overlay_text'] = f"Torque: {torque_match.group(1)} {torque_match.group(2).upper()}"
        
        # Extract clearance values
        clearance_match = self.clearance_pattern.search(content)
        if clearance_match:
            if parsed.get('overlay_text'):
                parsed['overlay_text'] += f" | Clearance: {clearance_match.group(0)}"
            else:
                parsed['overlay_text'] = f"Clearance: {clearance_match.group(0)}"
        
        # Extract safety notes (lines starting with ⚠️ or WARNING)
        safety_notes = []
        for line in content_lines:
            if '⚠️' in line or 'WARNING' in line.upper() or 'CAUTION' in line.upper():
                safety_notes.append(line.strip())
        
        if safety_notes:
            parsed['safety_notes'] = safety_notes
        
        # Build narration from all content
        clean_content = re.sub(r'[*_`#-]', '', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        if clean_content:
            parsed['narration'] = clean_content
        
        # Estimate duration based on content length
        word_count = len(clean_content.split())
        parsed['duration'] = max(3.0, min(15.0, word_count * 0.5))
        
        return parsed

# Example usage and testing
if __name__ == "__main__":
    # Test with sample content
    sample_md = """
# 00-30-10-01 Towbar Attachment Procedure

## Overview
This procedure describes the safe attachment of towbar to BWB-Q100 nose gear.

## Steps

### Step 1: Position Towbar
- Align towbar with nose gear connection point
- Verify clearance of 10cm minimum
- ⚠️ Ensure aircraft is properly chocked

### Step 2: Attach Connection
- Insert pin through connection holes
- Apply torque of 100Nm
- Verify secure connection

### Step 3: Final Check
- Perform visual inspection
- Test towbar movement
- Record completion in logbook
"""
    
    parser = MarkdownParser()
    result = parser.parse_content(sample_md, "00-30-10-01-TowbarAttachment")
    
    print("📋 Resultado del parser:")
    print(f"ID: {result['id']}")
    print(f"Título: {result['title']}")
    print(f"Pasos: {len(result['steps'])}")
    for step in result['steps']:
        print(f"  - {step['id']}: {step['title']} ({step['duration']}s)")
        if step['overlay_text']:
            print(f"    Overlay: {step['overlay_text']}")

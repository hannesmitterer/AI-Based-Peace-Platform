# NRE-002 Implementation Guide

## Overview

This guide demonstrates how to implement and use the NRE-002 Content Protection and Anti-Censorship Protocol in your application.

## Quick Start

### Installation

```bash
# Ensure the NRE-002 system module is available
cd /path/to/AI-Based-Peace-Platform
python -c "import nre_002_system"
```

### Basic Usage

```python
from nre_002_system import (
    NRE002System,
    StratificationLevel,
    ContentWarningType
)

# Initialize the system
nre_system = NRE002System()

# Archive historical content with protection
result = nre_system.archive_content(
    content_id="historical_event_1945",
    content="Complete historical documentation of events...",
    metadata={
        "title": "Historical Event Documentation",
        "year": 1945,
        "source": "National Archives"
    },
    level=StratificationLevel.COMPLETE,
    curator="Independent Historical Curatorium",
    rationale="Primary source documentation for research and education",
    warning_types=[ContentWarningType.HISTORICAL_ATROCITY]
)

print(f"Content archived with hash: {result['hash']}")
```

## Content Stratification

### Level 1: Foundation (General Audience)

```python
# Archive foundational educational content
nre_system.archive_content(
    content_id="wwii_overview",
    content="World War II was a global conflict from 1939-1945...",
    metadata={"title": "WWII Overview", "audience": "general"},
    level=StratificationLevel.FOUNDATION,
    curator="Educational Team",
    rationale="Age-appropriate overview for general education"
)
```

### Level 2: Detailed (Academic)

```python
# Archive detailed academic content
nre_system.archive_content(
    content_id="wwii_analysis",
    content="Comprehensive analysis with primary source excerpts...",
    metadata={"title": "WWII Analysis", "audience": "academic"},
    level=StratificationLevel.DETAILED,
    curator="Historical Research Team",
    rationale="Detailed analysis for academic study",
    warning_types=[ContentWarningType.EMOTIONALLY_INTENSE]
)
```

### Level 3: Complete (Research)

```python
# Archive complete unredacted documentation
nre_system.archive_content(
    content_id="nuremberg_transcripts",
    content="[Complete unredacted trial transcripts...]",
    metadata={
        "title": "Nuremberg Trials Transcripts",
        "audience": "research",
        "classification": "primary_source"
    },
    level=StratificationLevel.COMPLETE,
    curator="Independent Historical Curatorium",
    rationale="Complete primary source for research",
    warning_types=[
        ContentWarningType.GRAPHIC_CONTENT,
        ContentWarningType.HISTORICAL_ATROCITY
    ]
)
```

## User Access Patterns

### Standard Access (Respects User Preferences)

```python
# User accesses content at their default level
success, content, message = nre_system.access_content(
    user_id="student_001",
    content_id="wwii_overview",
    requested_level=StratificationLevel.FOUNDATION,
    override=False
)

if success:
    print(content['content']['content'])
    if content['warning']:
        print(f"\nWarning: {content['warning']['description']}")
```

### Override Access (User Requests Complete Access)

```python
# Researcher requests complete unrestricted access
success, content, message = nre_system.access_content(
    user_id="researcher_001",
    content_id="nuremberg_transcripts",
    requested_level=StratificationLevel.COMPLETE,
    override=True  # NRE-002 guarantees this is always granted
)

if success:
    print(f"Access granted: {message}")
    print(f"Level: {content['level']}")
    # User can now access complete unredacted content
```

## Content Warnings

### Adding Warnings

```python
from nre_002_system import ContentWarningSystem, ContentWarningType

warnings = ContentWarningSystem()

# Add warning to sensitive content
warning = warnings.add_warning(
    content_id="sensitive_testimony",
    warning_types=[
        ContentWarningType.TRAUMA_SENSITIVE,
        ContentWarningType.EMOTIONALLY_INTENSE
    ],
    description="survivor testimony containing descriptions of violence",
    alternatives=[
        "scholarly_summary",
        "contextual_analysis",
        "skip_to_next_section"
    ]
)

# Display formatted warning
print(warnings.format_warning("sensitive_testimony"))
```

### Example Warning Output

```
⚠️ Content Warning
This material contains survivor testimony containing descriptions of violence.
This material is presented for educational and memorial purposes.

Options:
[View Content] [Alternative Summary] [Skip Section]
```

## Archive Integrity

### Verifying Content Integrity

```python
# Verify that archived content hasn't been tampered with
is_valid = nre_system.archive.verify_integrity("historical_event_1945")

if is_valid:
    print("✓ Content integrity verified")
else:
    print("✗ INTEGRITY VIOLATION DETECTED")
    # This triggers NRE-002 violation protocols
```

### Version History

```python
# Access complete version history
history = nre_system.archive.get_version_history("historical_event_1945")

for version in history:
    print(f"Version: {version['timestamp']}")
    print(f"Hash: {version['hash']}")
```

## Transparency Reporting

### Generate Complete Transparency Report

```python
# Generate quarterly transparency report
report = nre_system.generate_transparency_report()

print(f"Protocol: {report['protocol']}")
print(f"Version: {report['version']}")
print(f"\nCuration Decisions: {len(report['curation_decisions'])}")
print(f"Total Archive Items: {report['archive_integrity']['total_items']}")
print(f"\nAccess Metrics:")
print(f"  Total Accesses: {report['access_metrics']['total_accesses']}")
print(f"  Override Requests: {report['access_metrics']['override_requests']}")
print(f"  Override %: {report['access_metrics']['override_percentage']:.2f}%")
```

### Example Report Output

```json
{
  "protocol": "NRE-002",
  "version": "1.0.0",
  "report_date": "2025-12-12T00:00:00Z",
  "curation_decisions": [
    {
      "content_id": "historical_event_1945",
      "stratification_level": 3,
      "curation_rationale": "Primary source documentation for research",
      "curator": "Independent Historical Curatorium",
      "date": "2025-12-12T00:00:00Z",
      "review_status": "approved",
      "appeal_available": true,
      "complete_version_link": "/archive/historical_event_1945/level/3"
    }
  ],
  "access_metrics": {
    "total_accesses": 150,
    "override_requests": 12,
    "override_percentage": 8.0
  },
  "anti_censorship_status": {
    "censorship_prohibited": true,
    "override_available": true
  }
}
```

## User Preference Management

### Setting User Preferences

```python
from nre_002_system import UserAccessControl, StratificationLevel

# Set user's default preferences
nre_system.access_control.set_user_preference(
    user_id="educator_001",
    default_level=StratificationLevel.DETAILED,
    show_warnings=True
)
```

### Respecting Zero-Obligation Principle

```python
# Users are NEVER forced to view content
# They can always:
# 1. Skip content
# 2. View alternative summaries
# 3. Choose lower stratification levels
# 4. Exit at content warnings

# Example: Providing alternatives
alternatives = {
    "scholarly_summary": "Academic analysis without graphic details",
    "statistical_overview": "Quantitative data and historical context",
    "memorial_perspective": "Focus on remembrance and lessons learned"
}
```

## Democratic Oversight Integration

### Curatorium Review Process

```python
# Get all stratification decisions for review
decisions = nre_system.stratification.get_transparency_report()

# Curatorium can review and approve/modify
for decision in decisions:
    print(f"Content: {decision['content_id']}")
    print(f"Level: {decision['stratification_level']}")
    print(f"Rationale: {decision['curation_rationale']}")
    print(f"Curator: {decision['curator']}")
    print(f"Appeal Available: {decision['appeal_available']}")
    print("---")
```

### Appeal Process

```python
# Users can appeal stratification decisions
appeal = {
    "content_id": "historical_event_1945",
    "appellant": "researcher_002",
    "reason": "Request for level 2 stratification instead of level 3",
    "justification": "Content suitable for undergraduate education"
}

# Appeals are reviewed by Independent Historical Curatorium
# All appeals are logged in transparency reports
```

## Anti-Censorship Enforcement

### What NRE-002 Prohibits

```python
# PROHIBITED: Permanent blocking based on user characteristics
def prohibited_age_gate(user_age, content_id):
    # ❌ VIOLATION: Cannot permanently block based on age
    if user_age < 18:
        return False, "Too young to access"  # THIS IS PROHIBITED
    
# ALLOWED: Providing age-appropriate default with override
def allowed_stratification(user_id, content_id):
    # ✓ COMPLIANT: Suggest appropriate level, allow override
    default_level = StratificationLevel.FOUNDATION  # Suggestion
    success, content, msg = nre_system.access_content(
        user_id,
        content_id,
        default_level,
        override=True  # ALWAYS AVAILABLE
    )
    return success, content, msg
```

### Monitoring for Violations

```python
# System automatically monitors for censorship attempts
# If any of these occur, alerts are triggered:

violations = [
    "permanent_content_blocking",
    "algorithmic_suppression",
    "invisible_filtering",
    "user_profile_based_blocking",
    "override_denial"
]

# Each violation triggers:
# 1. Immediate alert to oversight
# 2. Transparency report publication
# 3. Automatic remediation
# 4. Audit trail entry
```

## Best Practices

### 1. Always Preserve Complete Content

```python
# Store complete unredacted version first
complete_content = load_primary_source()
nre_system.archive_content(
    content_id="source_001",
    content=complete_content,
    metadata={"version": "complete"},
    level=StratificationLevel.COMPLETE,
    curator="archival_team",
    rationale="Primary source preservation"
)

# Then create educational adaptations as separate entries
# linking back to complete version
```

### 2. Transparent Curation Rationale

```python
# Good: Specific, educational rationale
rationale = "Stratified to Level 2 due to graphic testimony content; suitable for academic study with proper context"

# Bad: Vague or censorship-based rationale
# rationale = "Too disturbing for general audience"  # ❌ NOT ALLOWED
```

### 3. Regular Integrity Checks

```python
import schedule

def verify_all_content():
    for content_id in nre_system.archive.archive.keys():
        if not nre_system.archive.verify_integrity(content_id):
            logger.critical(f"INTEGRITY VIOLATION: {content_id}")
            # Trigger incident response

# Schedule regular integrity verification
schedule.every().day.at("03:00").do(verify_all_content)
```

### 4. Quarterly Transparency Reports

```python
def generate_and_publish_quarterly_report():
    report = nre_system.generate_transparency_report()
    
    # Publish publicly
    with open(f"transparency_reports/Q{quarter}_2025.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    # Notify stakeholders
    notify_curatorium(report)
    publish_public_summary(report)

# Run quarterly
schedule.every(3).months.do(generate_and_publish_quarterly_report)
```

## Integration with Existing Systems

### Web Application Integration

```python
from flask import Flask, request, jsonify
from nre_002_system import NRE002System, StratificationLevel

app = Flask(__name__)
nre = NRE002System()

@app.route('/api/content/<content_id>')
def get_content(content_id):
    user_id = request.args.get('user_id')
    level = int(request.args.get('level', 1))
    override = request.args.get('override', 'false') == 'true'
    
    success, content, message = nre.access_content(
        user_id,
        content_id,
        StratificationLevel(level),
        override
    )
    
    if success:
        return jsonify({
            'content': content,
            'message': message,
            'nre_002_compliant': True
        })
    else:
        return jsonify({'error': message}), 403
```

### API Documentation Integration

```python
@app.route('/api/content/<content_id>/transparency')
def get_transparency_info(content_id):
    """Get NRE-002 transparency information for content."""
    
    stratification = nre.stratification.get_stratification(content_id)
    warning = nre.warnings.get_warning(content_id)
    
    return jsonify({
        'content_id': content_id,
        'stratification': stratification,
        'warning': warning,
        'override_available': True,  # NRE-002 guarantee
        'complete_access_link': f'/api/content/{content_id}?level=3&override=true'
    })
```

## Conclusion

NRE-002 ensures that:
- ✓ Historical truth is preserved completely
- ✓ Users have sovereign control over their access
- ✓ Content is curated for education, not censored
- ✓ All decisions are transparent and appealable
- ✓ Democratic oversight prevents abuse

For questions or support, contact the Independent Historical Curatorium.

---

**Version:** 1.0.0  
**Last Updated:** 2025-12-12  
**Protocol:** NRE-002 Content Protection and Anti-Censorship

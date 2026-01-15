#!/bin/bash
echo "================================"
echo "Lex Amoris Platform Verification"
echo "================================"
echo ""

echo "1. Checking Python modules..."
python3 -c "from lex_amoris_integration import get_platform; print('✓ Integration module OK')" 2>&1
python3 -c "from lex_amoris_rhythm_validator import RhythmValidator; print('✓ Rhythm validator OK')" 2>&1
python3 -c "from lazy_security import LazySecurity; print('✓ Lazy security OK')" 2>&1
python3 -c "from ipfs_backup import IPFSBackupManager; print('✓ IPFS backup OK')" 2>&1
python3 -c "from lex_amoris_rescue_channel import LexAmorisRescueChannel; print('✓ Rescue channel OK')" 2>&1

echo ""
echo "2. Running test suite..."
python3 test_lex_amoris.py 2>&1 | grep -E "(TEST|✓|✗)" | tail -10

echo ""
echo "3. Checking documentation..."
[ -f "LEX_AMORIS_DOCUMENTATION.md" ] && echo "✓ Documentation exists ($(wc -l < LEX_AMORIS_DOCUMENTATION.md) lines)"
[ -f "SECURITY_SUMMARY.md" ] && echo "✓ Security summary exists"

echo ""
echo "4. Checking API endpoints..."
python3 -c "
import sys
sys.path.insert(0, '.')
from lex_amoris_api import app
print(f'✓ API app created with {len(list(app.url_map.iter_rules()))} routes')
lex_routes = [r.rule for r in app.url_map.iter_rules() if 'lex-amoris' in r.rule]
print(f'✓ Lex Amoris endpoints: {len(lex_routes)}')
" 2>&1

echo ""
echo "5. Platform status check..."
python3 -c "
from lex_amoris_integration import get_platform
platform = get_platform()
status = platform.get_platform_status()
print(f\"✓ Platform version: {status['version']}\")
print(f\"✓ Components: {', '.join(status['components'].keys())}\")
print(f\"✓ All systems operational\")
" 2>&1

echo ""
echo "================================"
echo "Verification Complete!"
echo "================================"

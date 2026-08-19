# PRICING SETUP REQUIRED

## Status: BLOCKED BY APPROVAL SYSTEM

The automated pricing setup script requires approval for external API calls.
Manual completion required.

## Actor Details
- **Actor ID**: CN001ec5fYP2RbD6M
- **Actor Name**: peerspot-scraper
- **Console URL**: https://console.apify.com/actors/CN001ec5fYP2RbD6M/settings

## Required Pricing Configuration

### Model: PAY_PER_EVENT

1. **Primary Event: "result"**
   - Event Title: "Result"
   - Description: "Per result scraped and written to dataset"
   - Price: $0.005 per result
   - Is Primary: YES
   - One-Time: NO

2. **Secondary Event: "actor-start"**
   - Event Title: "Actor start"
   - Description: "One-time fee per actor run"
   - Price: $0.05 per run
   - Is Primary: NO
   - One-Time: YES

## Manual Setup Instructions

1. Go to: https://console.apify.com/actors/CN001ec5fYP2RbD6M/settings
2. Scroll to "Pricing" section
3. Click "Add pricing"
4. Select "Pay per event"
5. Add the two events listed above
6. Save configuration

## Automated Script (for future reference)

The script attempted was the exact PYEOF heredoc from skill Step 11:
```bash
python3 << 'PYEOF'
[Script content - see skill for full code]
PYEOF
```

This was blocked by the approval system for subprocess.check_output curl calls.

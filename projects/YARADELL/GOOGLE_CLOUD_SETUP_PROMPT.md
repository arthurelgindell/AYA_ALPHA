# AI Agent Prompt: Google Cloud Console Setup for YouTube Intelligence

**Mission**: Set up Google Cloud Console credentials for Yara ❤️ Dell's YouTube channel analytics system.

---

## Context

A YouTube intelligence system has been built at `/Users/arthurdell/YARADELL/` that requires Google Cloud Console API credentials to function. The system is complete but non-operational without these credentials.

**YouTube Account**:
- Email: Yara.sivak@gmail.com
- Password: IAmYaraDell376797$
- Channel: Yara ❤️ Dell

**System Location**: `/Users/arthurdell/YARADELL/`
**Config File**: `/Users/arthurdell/YARADELL/config/.env`

---

## Your Mission

Using browser automation or interactive capabilities, complete the following setup process and add the resulting credentials to the `.env` file.

---

## Step-by-Step Instructions

### Phase 1: Access Google Cloud Console

1. **Navigate to**: https://console.cloud.google.com/
2. **Click**: "Sign in" button
3. **Enter Email**: Yara.sivak@gmail.com
4. **Click**: "Next"
5. **Enter Password**: IAmYaraDell376797$
6. **Click**: "Next"
7. **Handle 2FA** (if prompted):
   - If SMS verification: Request code be sent, wait for human to provide code
   - If email verification: Check Yara.sivak@gmail.com inbox for code
   - If authenticator app: Request human assistance
8. **Accept Terms** (if first-time user):
   - Read and accept Google Cloud Console Terms of Service
   - Click "Agree and Continue"

### Phase 2: Create Project

9. **Look for**: "Select a project" dropdown at top of page
10. **Click**: "New Project" button
11. **Project Name**: Enter "Yara YouTube Intelligence"
12. **Project ID**: Leave as auto-generated (or use: yara-youtube-intel)
13. **Organization**: Leave as "No organization" (unless one exists)
14. **Location**: Leave as default
15. **Click**: "Create" button
16. **Wait**: Project creation (10-30 seconds)
17. **Verify**: Project name appears in top navigation bar

### Phase 3: Enable YouTube Data API v3

18. **Click**: "☰" (hamburger menu) in top-left
19. **Hover over**: "APIs & Services"
20. **Click**: "Library"
21. **Search box**: Type "YouTube Data API v3"
22. **Click**: "YouTube Data API v3" from results
23. **Click**: "Enable" button
24. **Wait**: API enablement (5-10 seconds)
25. **Verify**: "API enabled" message appears

### Phase 4: Enable YouTube Analytics API

26. **Click**: "Library" in left sidebar (or back button)
27. **Search box**: Type "YouTube Analytics API"
28. **Click**: "YouTube Analytics API" from results
29. **Click**: "Enable" button
30. **Wait**: API enablement (5-10 seconds)
31. **Verify**: "API enabled" message appears

### Phase 5: Create API Key (for Public Data)

32. **Click**: "Credentials" in left sidebar
33. **Click**: "+ CREATE CREDENTIALS" button at top
34. **Select**: "API key" from dropdown
35. **Wait**: Key generation popup appears
36. **Copy**: The API key shown (starts with "AIza...")
37. **Important**: Save this immediately - you'll need it
38. **Click**: "Restrict Key" button (recommended)
39. **Name field**: Enter "Yara YouTube Data Key"
40. **API restrictions**: Select "Restrict key"
41. **Select APIs**: Check only:
    - YouTube Data API v3
    - YouTube Analytics API
42. **Click**: "Save"
43. **Store**: API key in temporary secure location

### Phase 6: Create OAuth 2.0 Client (for Analytics Data)

44. **Click**: "+ CREATE CREDENTIALS" button again
45. **Select**: "OAuth client ID"
46. **If prompted**: "Configure consent screen"
    - Click "Configure Consent Screen"
    - **User Type**: Select "External"
    - Click "Create"
    - **App name**: "Yara YouTube Intelligence"
    - **User support email**: Yara.sivak@gmail.com
    - **Developer contact**: Yara.sivak@gmail.com
    - Click "Save and Continue" (3 times through scopes and test users)
    - Click "Back to Dashboard"
47. **Application type**: Select "Desktop app"
48. **Name**: Enter "Yara YouTube OAuth Client"
49. **Click**: "Create"
50. **Popup appears** with Client ID and Client Secret
51. **Copy**: Client ID (looks like: xxx-xxx.apps.googleusercontent.com)
52. **Copy**: Client Secret (looks like: GOCSPX-xxx)
53. **Click**: "Download JSON" (optional backup)
54. **Click**: "OK"

### Phase 7: Get YouTube Channel ID

55. **Open new tab**: https://www.youtube.com/
56. **Sign in** (should be already signed in as Yara)
57. **Click**: Channel icon (top-right)
58. **Click**: "Your channel"
59. **Look at URL**: Should be youtube.com/channel/UCxxxxxxxxxxxxxxxxxx
60. **Copy**: The channel ID (UCxxxxxxxxxxxxxxxxxx part)
61. **Alternative**: Go to YouTube Studio > Settings > Channel > Advanced settings

### Phase 8: Update Configuration File

62. **Open terminal or file editor**
63. **Navigate to**: `/Users/arthurdell/YARADELL/config/`
64. **Edit file**: `.env`
65. **Update these lines**:

```bash
# Replace these placeholder values with actual credentials:
YOUTUBE_API_KEY=AIza...your_api_key_here...
YOUTUBE_CLIENT_ID=xxx-xxx.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-xxx...your_secret_here...
YOUTUBE_CHANNEL_ID=UCxxxxxxxxxxxxxxxxxx
```

66. **Save file**
67. **Verify**: File permissions are secure (not world-readable)

### Phase 9: Test Credentials

68. **Open terminal**
69. **Run**:
```bash
cd /Users/arthurdell/YARADELL/scripts
python3 youtube_api_client.py
```

70. **Expected output**:
    - ✅ Configuration status shown
    - ✅ API Key: ✅ Set
    - ✅ Client ID: ✅ Set
    - ✅ Channel ID: (channel ID displayed)
    - ✅ Database connection successful
    - ✅ Channel info fetched
    - ✅ Channel data saved to database

71. **If errors occur**: Note exact error message for troubleshooting

### Phase 10: OAuth Authorization Flow (First Run)

72. **When running scripts that need analytics data**, you'll see:
    - A URL printed to console
    - Instructions to visit URL in browser
73. **Copy URL** and open in browser
74. **Sign in** as Yara.sivak@gmail.com (if not already)
75. **Review permissions**: YouTube Analytics, YouTube Data
76. **Click**: "Allow" or "Continue"
77. **Copy authorization code** from browser
78. **Paste** into terminal when prompted
79. **Verify**: "Authentication successful" message
80. **Note**: Token stored locally, won't need to repeat

---

## Success Criteria

✅ Google Cloud Console project "Yara YouTube Intelligence" created
✅ YouTube Data API v3 enabled
✅ YouTube Analytics API enabled
✅ API key generated and restricted
✅ OAuth 2.0 client ID and secret created
✅ Channel ID identified
✅ All credentials added to `.env` file
✅ Test script runs successfully
✅ Channel data appears in database

---

## Credentials to Capture

At the end, you should have these values in `/Users/arthurdell/YARADELL/config/.env`:

```bash
YOUTUBE_API_KEY=AIza...
YOUTUBE_CLIENT_ID=xxx-xxx.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-xxx
YOUTUBE_CHANNEL_ID=UCxxxxxxxxxxxxxxxxxx
```

---

## Troubleshooting Common Issues

### "Project already exists"
- Use existing project named similar to "Yara YouTube Intelligence"
- Or append date: "Yara YouTube Intelligence 2025"

### "APIs not enabled"
- Return to Library and search for both YouTube APIs
- Verify green checkmark next to each API

### "Quota exceeded"
- YouTube Data API has free quota: 10,000 units/day
- Analytics API has no quota limit
- Should not hit limits during setup

### "OAuth consent screen verification required"
- For external user type, can use "Testing" mode
- Add Yara.sivak@gmail.com as test user
- Don't need full Google verification for personal use

### "Channel ID not found"
- Ensure signed in as correct Google account
- Verify channel actually exists (has videos/activity)
- Try YouTube Studio > Settings > Channel > Advanced

---

## Security Reminders

⚠️ **IMPORTANT**:
- These credentials grant access to Yara's YouTube analytics
- Keep `.env` file secure and never commit to git
- `.gitignore` is already configured to exclude `.env`
- Only share credentials over secure channels
- Can revoke access anytime from Google Cloud Console

---

## Post-Setup Actions

After successful setup, the system can:
1. Collect daily audience demographics (automated at 6am)
2. Generate weekly AI-powered insights (Monday 7am)
3. Display real-time dashboards (http://localhost:8080)
4. Create automated PDF/Markdown reports
5. Query historical data via SQL

---

## If You Encounter Blocks

**Cannot automate browser**:
- Provide detailed instructions for human to follow
- Create numbered checklist
- Indicate where to copy/paste credentials

**2FA/Verification codes**:
- Pause and request human input
- Provide clear instructions on what's needed
- Resume once verified

**Unexpected UI changes**:
- Google Cloud Console UI may differ slightly
- Look for similar button names/functions
- Document any discrepancies found

---

## Reporting Back

Upon completion, provide:

1. **Status**: Success or failure
2. **Credentials Status**:
   - API Key: ✅/❌
   - Client ID: ✅/❌
   - Client Secret: ✅/❌
   - Channel ID: ✅/❌
3. **Test Results**: Output from `youtube_api_client.py`
4. **Issues Encountered**: Any problems or blocks
5. **Next Steps**: What human action (if any) still needed

---

## Example Success Report

```
SETUP COMPLETE ✅

Credentials Configured:
✅ API Key: AIzaSyD...Xx (restricted to YouTube APIs)
✅ Client ID: 123456789-abc.apps.googleusercontent.com
✅ Client Secret: GOCSPX-xyz123
✅ Channel ID: UCabcdefghijklmnop

Test Results:
✅ Database connection successful
✅ Channel info fetched: "Yara ❤️ Dell"
✅ Subscribers: 12,500
✅ Videos: 84
✅ Total views: 1,234,567
✅ Data saved to youtube_channels table

System Status: FULLY OPERATIONAL

Next Steps:
1. Run dashboard: cd /Users/arthurdell/YARADELL/dashboards && python3 dashboard_api.py
2. View dashboard: http://localhost:8080
3. Set up n8n workflows (optional automation)
```

---

**Time Estimate**: 15-20 minutes (human-assisted)  
**Difficulty**: Medium (requires browser interaction)  
**Prerequisites**: Access to Yara.sivak@gmail.com email for verification  
**Success Rate**: 95% (if 2FA codes accessible)


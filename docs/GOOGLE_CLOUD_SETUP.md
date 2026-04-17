# Google Cloud OAuth Setup — Visual Walkthrough

**Time: ~10 minutes.** One-time setup. Never share `credentials.json`.

---

## Why This Step Exists

FlowBridge needs permission to:
- Read your Gmail (to find job emails)
- Read/write your Google Sheet (message queue)

Google requires an OAuth Client ID for this. It's free.

---

## Step 1: Go to Google Cloud Console

Open: **https://console.cloud.google.com**

Sign in with the **same Google account** you want FlowBridge to read Gmail from.

---

## Step 2: Create a Project

```
┌────────────────────────────────────────────────────┐
│  Google Cloud Console                              │
├────────────────────────────────────────────────────┤
│  [Select a project ▼]    <-- Click this at top   │
│                                                    │
│  ┌─────────────────────────┐                      │
│  │  SELECT A PROJECT       │                      │
│  │                         │                      │
│  │  Recent    Starred      │                      │
│  │                         │                      │
│  │  [NEW PROJECT]  <-- Click                      │
│  └─────────────────────────┘                      │
└────────────────────────────────────────────────────┘
```

1. Click project dropdown (top bar)
2. Click **NEW PROJECT**
3. Name: `flowbridge`
4. Click **CREATE**
5. Wait 30 seconds for project to be ready

---

## Step 3: Enable 3 APIs

Navigate: **☰ Menu → APIs & Services → Library**

Search and enable each one:

### 3a. Google Sheets API
1. Search: `Google Sheets API`
2. Click first result
3. Click **ENABLE**
4. Wait for green checkmark

### 3b. Google Drive API
1. Back to Library
2. Search: `Google Drive API`
3. Click first result
4. Click **ENABLE**

### 3c. Gmail API
1. Back to Library
2. Search: `Gmail API`
3. Click first result
4. Click **ENABLE**

---

## Step 4: Configure OAuth Consent Screen

Navigate: **☰ Menu → APIs & Services → OAuth consent screen**

```
┌────────────────────────────────────────────────────┐
│  User Type                                         │
│                                                    │
│  ( ) Internal   — only Google Workspace users     │
│  (•) External   <-- Pick this                     │
│                                                    │
│  [CREATE]                                          │
└────────────────────────────────────────────────────┘
```

1. Pick **External**
2. Click **CREATE**

### App information page
- App name: `FlowBridge`
- User support email: your email
- Developer contact email: your email
- Leave rest blank
- Click **SAVE AND CONTINUE**

### Scopes page
- Click **SAVE AND CONTINUE** (no scopes needed here)

### Test users page
```
┌────────────────────────────────────────────────────┐
│  Test users                                        │
│                                                    │
│  [+ ADD USERS]  <-- Click                         │
│                                                    │
│  Enter: your-email@gmail.com                      │
│  [ADD]                                             │
└────────────────────────────────────────────────────┘
```

1. Click **+ ADD USERS**
2. Type **your own email address**
3. Click **ADD**
4. Click **SAVE AND CONTINUE**

### Summary
- Click **BACK TO DASHBOARD**

---

## Step 5: Create OAuth Client ID

Navigate: **☰ Menu → APIs & Services → Credentials**

```
┌────────────────────────────────────────────────────┐
│  Credentials                                       │
│                                                    │
│  [+ CREATE CREDENTIALS ▼]  <-- Click              │
│     - API key                                      │
│     - OAuth client ID    <-- Pick this            │
│     - Service account                              │
└────────────────────────────────────────────────────┘
```

1. Click **+ CREATE CREDENTIALS**
2. Pick **OAuth client ID**
3. Application type: **Desktop app** (important!)
4. Name: `flowbridge-desktop`
5. Click **CREATE**

---

## Step 6: Download credentials.json

```
┌────────────────────────────────────────────────────┐
│  OAuth client created                              │
│                                                    │
│  Client ID: 123456789.apps.googleusercontent.com  │
│  Client secret: GOCSPX-...                         │
│                                                    │
│  [DOWNLOAD JSON]   <-- Click this                 │
└────────────────────────────────────────────────────┘
```

1. Click **DOWNLOAD JSON** in the popup
2. Save the file
3. **Rename it to exactly** `credentials.json`
4. Move to: `flowbridge-job-forwarder/setup/credentials.json`

**⚠️ Important:** Never share this file. Never commit to git. It is your key.

---

## Step 7: First Run Authorization

When FlowBridge starts for the first time, it opens your browser to authorize.

```
┌────────────────────────────────────────────────────┐
│  Google hasn't verified this app                   │
│                                                    │
│  The app is requesting access to sensitive info    │
│  from your Google Account. Until the developer    │
│  verifies this app with Google, you shouldn't use │
│  it.                                               │
│                                                    │
│  [BACK TO SAFETY]   [Advanced ▼]  <-- Click here  │
└────────────────────────────────────────────────────┘
```

This warning is **normal for test apps**. You are the developer.

1. Click **Advanced**
2. Click **Go to FlowBridge (unsafe)** — your app, your data
3. Review the permissions:
   - See and download all Google Sheets ✓
   - See messages in your Gmail ✓
4. Click **Allow**
5. Browser shows "authentication flow completed"
6. Token cached to `setup/token.json` (never share this either)

---

## Step 8: Verify

Check both files exist:
```
flowbridge-job-forwarder/
  setup/
    credentials.json   ← from Step 6
    token.json         ← auto-created on first run
```

Both are in `.gitignore` — they never leave your computer.

---

## Revoking Access Later

If you want to remove FlowBridge's access to your Google account:

1. Go to https://myaccount.google.com/permissions
2. Find **FlowBridge**
3. Click **Remove Access**
4. Also delete `setup/token.json` locally

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `access_denied` | Not added as test user | Add your email in OAuth consent screen |
| `Gmail API has not been used` | API not enabled | Enable Gmail API (Step 3c) |
| `invalid_client` | Wrong file downloaded | Re-download OAuth Desktop client JSON |
| Browser loop | Token expired | Delete `setup/token.json`, rerun |

**Next:** [QUICKSTART.md Step 3](QUICKSTART.md)

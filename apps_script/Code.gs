/**
 * Job Forwarder — Gmail Monitor (Google Apps Script)
 *
 * Watches Gmail for job-related emails, extracts metadata,
 * and queues them in a Google Sheet for the Python agent to pick up.
 *
 * SETUP:
 *   1. Open Google Sheets → Extensions → Apps Script
 *   2. Paste this code into Code.gs
 *   3. Set SHEET_ID and GMAIL_LABEL below
 *   4. Run setupTrigger() once to create the 5-minute poll
 *   5. Authorize when prompted
 *
 * Sheet columns:
 *   A: ID  |  B: Status  |  C: Subject  |  D: Body  |  E: Company
 *   F: Source  |  G: DateReceived  |  H: DateSent  |  I: RetryCount
 */

// ── Configuration ──────────────────────────────────────────────────────────
var CONFIG = {
  SHEET_ID: "",                   // Your Google Sheet ID
  SHEET_NAME: "Queue",
  GMAIL_QUERY: "is:unread label:jobs",  // Gmail search query
  MAX_BODY_LENGTH: 5000,          // Truncate long email bodies
};

// ── Trigger setup ──────────────────────────────────────────────────────────

/**
 * Run this ONCE to create a time-driven trigger that calls
 * checkForJobEmails() every 5 minutes.
 */
function setupTrigger() {
  // Remove existing triggers to avoid duplicates
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === "checkForJobEmails") {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }

  ScriptApp.newTrigger("checkForJobEmails")
    .timeBased()
    .everyMinutes(5)
    .create();

  Logger.log("Trigger created: checkForJobEmails every 5 minutes");
}

// ── Main function ──────────────────────────────────────────────────────────

/**
 * Search Gmail for unread job emails, queue them in the Sheet,
 * and mark them as read.
 */
function checkForJobEmails() {
  var sheet = SpreadsheetApp.openById(CONFIG.SHEET_ID)
    .getSheetByName(CONFIG.SHEET_NAME);

  if (!sheet) {
    Logger.log("ERROR: Sheet '" + CONFIG.SHEET_NAME + "' not found");
    return;
  }

  // Ensure header row exists
  if (sheet.getLastRow() === 0) {
    sheet.appendRow([
      "ID", "Status", "Subject", "Body", "Company",
      "Source", "DateReceived", "DateSent", "RetryCount"
    ]);
  }

  var threads = GmailApp.search(CONFIG.GMAIL_QUERY, 0, 50);
  var queued = 0;

  for (var t = 0; t < threads.length; t++) {
    var messages = threads[t].getMessages();

    for (var m = 0; m < messages.length; m++) {
      var msg = messages[m];

      if (!msg.isUnread()) continue;

      var subject = msg.getSubject() || "(No Subject)";
      var body = msg.getPlainBody() || "";
      var from = msg.getFrom() || "";
      var date = msg.getDate();

      // Truncate body if too long
      if (body.length > CONFIG.MAX_BODY_LENGTH) {
        body = body.substring(0, CONFIG.MAX_BODY_LENGTH) + "...";
      }

      // Extract company name from sender (best-effort: "Name <email>" → "Name")
      var company = extractCompany(from);

      // Generate unique ID: YYYYMMDD_HHmmss_NNN
      var id = generateId(date, queued);

      // Append row
      sheet.appendRow([
        id,                                       // A: ID
        "PENDING",                                // B: Status
        subject,                                  // C: Subject
        body,                                     // D: Body
        company,                                  // E: Company
        from,                                     // F: Source
        Utilities.formatDate(date, Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss"),  // G: DateReceived
        "",                                       // H: DateSent
        "0",                                      // I: RetryCount
      ]);

      // Mark as read so we don't process it again
      msg.markRead();
      queued++;
    }
  }

  if (queued > 0) {
    Logger.log("Queued " + queued + " new job email(s)");
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────

/**
 * Extract a company/sender name from a "From" header.
 * "Acme Jobs <jobs@acme.com>" → "Acme Jobs"
 * "jobs@acme.com"             → "acme.com"
 */
function extractCompany(from) {
  var match = from.match(/^(.+?)\s*<.+>$/);
  if (match) {
    return match[1].replace(/"/g, "").trim();
  }
  // Fallback: use domain
  var domainMatch = from.match(/@([^>]+)/);
  return domainMatch ? domainMatch[1] : from;
}

/**
 * Generate a timestamp-based ID: YYYYMMDD_HHmmss_NNN
 */
function generateId(date, counter) {
  var pad = function(n, len) {
    var s = String(n);
    while (s.length < (len || 2)) s = "0" + s;
    return s;
  };

  return (
    pad(date.getFullYear(), 4) +
    pad(date.getMonth() + 1) +
    pad(date.getDate()) +
    "_" +
    pad(date.getHours()) +
    pad(date.getMinutes()) +
    pad(date.getSeconds()) +
    "_" +
    pad(counter, 3)
  );
}

// ── Menu (manual trigger) ──────────────────────────────────────────────────

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Job Forwarder")
    .addItem("Check for new jobs now", "checkForJobEmails")
    .addItem("Setup 5-min trigger", "setupTrigger")
    .addToUi();
}

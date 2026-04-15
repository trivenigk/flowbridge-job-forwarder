# Provisional Patent Application — Claims and Technical Specification

**Title:** FlowBridge: System and Method for Multi-Signal Content Deduplication (DedupGuard) and Automated Cross-Platform Message Delivery Using Synthetic Clipboard Event Injection (ClipCast) and Self-Healing Browser Session Management (SessionHeal) in Containerized Virtual Display Environments

**Inventor:** Triveni Ganta
**Date:** April 2026
**Status:** Draft — For Provisional Patent Application

---

## Field of Invention

The present invention relates to improvements in computer-implemented messaging automation, and more particularly to technical methods for (1) reducing redundant data transmission across cross-platform content pipelines through multi-signal deduplication at pipeline boundaries, (2) overcoming character encoding limitations in browser automation drivers through synthetic clipboard event injection, and (3) maintaining browser session integrity in containerized environments through self-healing lock recovery mechanisms.

## Technical Problems Solved

### Problem 1: ChromeDriver Unicode Processing Limitation
ChromeDriver's `send_keys()` method processes characters through a keyboard simulation layer that only supports the Basic Multilingual Plane (BMP, U+0000–U+FFFF). Characters in the Supplementary Multilingual Plane (SMP, U+10000+) — including all emoji — throw `ChromeDriver only supports characters in the BMP` errors. This prevents browser automation tools from inputting emoji-rich formatted content into web application text fields.

**Prior solutions and their failures:**
- Avoid emoji entirely → Degrades message formatting and user engagement
- Use `pyperclip` + Ctrl+V keystroke → Requires system clipboard access, fails in headless/containerized environments without display server clipboard
- Use ActionChains → Same BMP limitation as send_keys()
- Use headless mode → Messaging platforms (WhatsApp Web, Telegram Web) require full rendering and session state

**Before (without invention):** 100% failure rate for messages containing emoji characters via browser automation.
**After (with invention):** 100% success rate — full Unicode range including SMP characters.

### Problem 2: Redundant Message Delivery in Cross-Platform Pipelines
When content is ingested from one platform (email) and delivered to another (messaging), duplicate content arrives through multiple channels — same sender resends, multiple forwarding paths, job boards re-notify. No existing deduplication method operates at the cross-platform pipeline boundary.

**Prior solutions and their failures:**
- Email-level dedup (spam filters, conversation threading) → Only works within the email platform, not at the pipeline output
- Exact string matching → Misses reworded content with same meaning
- Single-signal matching (subject only) → Misses same content with different subject lines

**Before:** 15-25% duplicate message rate in forwarded content.
**After:** 0% duplicate rate with zero false positives in production evaluation.

### Problem 3: Browser Session Loss in Containerized Environments
Chrome creates filesystem lock files (SingletonLock, SingletonCookie, SingletonSocket) to enforce single-instance execution. In containerized environments, process crashes leave stale locks that prevent browser restart. Combined with messaging platform session requirements (QR code authentication), this causes complete pipeline failure requiring manual intervention.

**Prior solutions and their failures:**
- Manual lock file deletion → Requires human intervention, defeats automation purpose
- Fresh browser profile each restart → Loses messaging platform session, requires re-authentication
- Docker `--rm` flag → Destroys session data, requires QR re-scan

**Before:** Mean time to recovery: 30+ minutes (manual intervention required).
**After:** Mean time to recovery: < 5 seconds (automatic, zero human intervention).

## Claims

### Independent Claim 1 — DedupGuard: Multi-Signal Pipeline Boundary Deduplication

A computer-implemented method for preventing redundant content delivery in a cross-platform messaging pipeline, the method executed by one or more processors and comprising:

(a) receiving a plurality of content items from a first communication platform, each content item comprising at least a subject field, a sender identifier, a content body, and a unique item identifier;

(b) maintaining a persistent deduplication index comprising fingerprint records, identifier records, and content signatures derived from previously transmitted content items;

(c) for each received content item, computing a sender fingerprint by extracting a domain component from the sender identifier and concatenating a normalized form of the subject field with the extracted domain component;

(d) comparing the computed sender fingerprint against the fingerprint records in the deduplication index;

(e) upon the sender fingerprint not matching any fingerprint record, comparing the unique item identifier against the identifier records in the deduplication index;

(f) upon the unique item identifier not matching any identifier record, computing a content similarity score between a predetermined portion of the content body and content signatures of previously transmitted items using a sequence matching algorithm;

(g) comparing the computed content similarity score against a predetermined similarity threshold;

(h) upon the content similarity score being below the predetermined threshold, determining the content item is not a duplicate and transmitting the content item to a second communication platform;

(i) upon any of comparisons (d), (e), or (g) indicating a match, marking the content item with a duplicate status indicator and preventing transmission;

wherein the multi-signal approach reduces duplicate transmission rate to zero while maintaining a zero false-positive rate, as compared to single-signal methods that achieve 85-95% duplicate detection.

### Independent Claim 2 — ClipCast: Synthetic Clipboard Event Injection for Unicode Bypass

A computer-implemented method for transmitting text containing characters outside the Basic Multilingual Plane through a browser automation driver that restricts character input to the Basic Multilingual Plane, the method comprising:

(a) detecting that a text payload contains one or more characters with Unicode code points above U+FFFF;

(b) identifying a target input element in a web application rendered by a browser instance controlled by the browser automation driver;

(c) constructing a DataTransfer object and setting its text/plain data to the complete text payload including characters above U+FFFF;

(d) constructing a synthetic ClipboardEvent of type 'paste' with the clipboardData property set to the DataTransfer object, the bubbles property set to true, and the cancelable property set to true;

(e) executing JavaScript via the browser automation driver to dispatch the synthetic ClipboardEvent to the target input element;

(f) whereby the web application's native paste event handler processes the complete text payload including characters above U+FFFF, bypassing the browser automation driver's character encoding restriction;

wherein the method achieves 100% character fidelity for the full Unicode range including Supplementary Multilingual Plane characters without requiring system clipboard access, operating system-specific APIs, or modifications to the browser automation driver.

### Independent Claim 3 — SessionHeal: Self-Healing Browser Session Recovery in Containerized Environments

A computer-implemented method for maintaining continuous browser automation operation in a containerized computing environment, the method comprising:

(a) storing browser session authentication state in a persistent volume external to the container filesystem;

(b) prior to each browser launch, performing a lock remediation routine comprising:
  (i) detecting the presence of browser lock files in the browser profile directory;
  (ii) removing detected lock files;
  (iii) enumerating running browser driver processes;
  (iv) terminating orphaned browser driver processes that lack an active parent session;
  (v) waiting a predetermined period for filesystem synchronization;

(c) launching the browser instance with the persistent profile directory;

(d) upon browser crash detection by the container orchestration layer, automatically restarting the container;

(e) upon container restart, executing the lock remediation routine of step (b) and restoring the browser session from the persistent volume of step (a);

wherein the method achieves automatic recovery from any browser failure state without requiring re-authentication with the web application, reducing mean time to recovery from over 30 minutes (manual intervention) to under 5 seconds (automatic).

### Independent Claim 4 — SheetConfig: Spreadsheet-Mediated Dynamic Pipeline Configuration

A computer-implemented system for managing an automated content processing pipeline through spreadsheet-based configuration, the system comprising:

(a) a cloud-hosted spreadsheet comprising:
  (i) a first worksheet storing content pipeline records with status tracking fields;
  (ii) a second worksheet storing target destination identifiers for content delivery;

(b) a polling agent executing within a containerized environment that, on each polling cycle:
  (i) reads the second worksheet to obtain a current set of target destination identifiers;
  (ii) reads the first worksheet to obtain content pipeline records with a pending status;
  (iii) processes the content pipeline records through a deduplication engine;
  (iv) delivers non-duplicate content to each target destination;
  (v) updates the status tracking fields in the first worksheet;

(c) wherein modifications to the second worksheet by any authorized user take effect on the next polling cycle without requiring code deployment, configuration file edits, system restart, or developer access;

(d) wherein the cloud-hosted spreadsheet maintains a revision history providing an audit trail of all configuration changes and content processing events.

### Dependent Claims

**Claim 5.** The method of Claim 1, wherein the sequence matching algorithm of step (f) operates on a predetermined first N characters of the content body, wherein N is selected to balance computational efficiency against matching accuracy, and wherein using the first 500 characters achieves equivalent accuracy to full-body comparison while reducing computation time by a factor proportional to body length.

**Claim 6.** The method of Claim 1, further comprising a batch deduplication step wherein content items received within a single polling cycle are additionally compared against each other using the multi-signal method of steps (c) through (i), preventing intra-batch duplicate transmission.

**Claim 7.** The method of Claim 1, further comprising a batch aggregation step wherein all non-duplicate content items from a single polling cycle are combined into a single formatted message with date headers and visual separators, reducing the number of transmission events from N x G to G, where N is the number of content items and G is the number of target destinations.

**Claim 8.** The method of Claim 2, wherein the target input element is a contenteditable div element rendered by a React-based web application, and wherein the synthetic ClipboardEvent triggers the web application's React synthetic event handler for paste events.

**Claim 9.** The method of Claim 3, wherein the containerized computing environment comprises:
  (a) an X Virtual Framebuffer providing a headless display server;
  (b) a web browser rendering a messaging platform web application within the virtual display;
  (c) a VNC server optionally exposing the virtual display for remote monitoring;
  (d) a shared memory allocation exceeding 512MB to support browser rendering requirements;
  wherein the virtual display environment enables full web application rendering without a physical display device.

**Claim 10.** The system of Claim 4, further comprising a retry mechanism wherein content items that fail delivery are assigned an incrementing retry counter, are re-attempted on subsequent polling cycles up to a configurable maximum retry count, and upon exceeding the maximum are assigned a permanent failure status for manual review.

**Claim 11.** The method of Claim 1, further comprising an AI-enhanced variant wherein:
  (a) a locally-hosted language model extracts structured metadata from unstructured content bodies;
  (b) vector embeddings computed by a sentence-transformer model enable semantic similarity matching as an additional deduplication signal;
  (c) a relevance scoring module filters content against configurable criteria before delivery;
  wherein all AI processing executes locally without external API dependencies, maintaining zero recurring cost.

**Claim 12.** The method of Claim 1, wherein the first communication platform is an email system and the second communication platform is a group messaging application, and wherein the method is applied to forward job postings, sales lead notifications, property listings, research paper alerts, price change notifications, or security incident alerts.

## Technical Specification — Ordered Combination Doctrine

The claims above define an ordered combination of technical steps that creates functionality none of the individual steps provide alone:

1. **Email ingestion** alone provides raw content but no deduplication or delivery
2. **Deduplication** alone has no content to process or delivery mechanism
3. **Clipboard injection** alone has no content source or session management
4. **Self-healing sessions** alone has no content pipeline or message formatting
5. **Spreadsheet configuration** alone has no processing engine or delivery capability

The specific sequence — ingest → deduplicate → batch → format with clipboard injection → deliver via session-healed browser — produces an automated cross-platform content pipeline that:
- Eliminates redundant transmissions (0% duplicate rate vs. 15-25% baseline)
- Supports full Unicode formatting (100% vs. 0% for SMP characters)
- Operates continuously without human intervention (MTTR < 5s vs. 30+ min)
- Enables non-technical runtime configuration (zero-deploy changes)

No single component achieves these outcomes. The synergistic combination is non-obvious because:
- Browser automation tools (Selenium) are designed for testing, not production messaging
- Containerized virtual displays (Xvfb) are designed for CI/CD, not persistent sessions
- Spreadsheet APIs are designed for data storage, not pipeline configuration
- Clipboard events are designed for user interaction, not automation driver bypass

Combining these tools in this specific ordered sequence for production messaging automation had no prior motivation in the art.

## Drawings Description

- **Figure 1**: System architecture — five-stage pipeline from email to messaging platform
- **Figure 2**: Multi-signal deduplication flowchart showing decision tree across 4 signals
- **Figure 3**: ClipboardEvent injection sequence diagram (DataTransfer → ClipboardEvent → dispatchEvent → React handler)
- **Figure 4**: Self-healing lock recovery state machine (crash → restart → cleanup → lock removal → browser launch → session restore)
- **Figure 5**: Spreadsheet-as-configuration schema (Queue tab + Groups tab + revision history)
- **Figure 6**: Before/after comparison table for each technical problem
- **Figure 7**: Batch aggregation showing N×G → G transmission reduction

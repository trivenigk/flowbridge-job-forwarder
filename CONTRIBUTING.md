# Contributing to FlowBridge

Thanks for considering contributing. Read this first.

---

## Ways to Contribute

| Type | How |
|------|-----|
| Bug reports | Open issue with logs + repro steps |
| Feature requests | Open issue with use case + why existing features don't solve it |
| Documentation | PRs welcome, especially typo fixes |
| Code | Fork → branch → PR |
| Use case guides | Extend `docs/USE_CASES.md` |

---

## Before You Submit Code

1. Read `docs/ARCHITECTURE.md` — understand the pipeline
2. Check existing issues/PRs — may already be in progress
3. Keep changes small and focused
4. Match existing code style (PEP 8 Python)

---

## Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/flowbridge-job-forwarder.git
cd flowbridge-job-forwarder

# Install dependencies (for local dev, outside Docker)
cd agent
pip install -r requirements.txt

# Run tests
python -c "from sheets import _make_fingerprint, _body_similarity; print('OK')"
```

---

## Code Style

- Python 3.11+
- Type hints encouraged, not required
- Docstrings for public functions
- Comments only where logic is non-obvious
- No line-by-line comments

---

## Pull Request Checklist

Before opening PR:

- [ ] Changes build: `docker compose build`
- [ ] Manual test: `docker compose up -d` + logs check
- [ ] README/docs updated if behavior changed
- [ ] No hardcoded credentials or personal data
- [ ] `.env`, `credentials.json`, `token.json` NOT committed
- [ ] Commit message explains "why" not just "what"

---

## Areas Wanting Help

- [ ] Telegram Bot API adapter (replaces WhatsApp Web for users who want official API)
- [ ] Slack webhook adapter
- [ ] Discord webhook adapter
- [ ] Semantic dedup using sentence-transformers
- [ ] Test suite (pytest)
- [ ] GitHub Actions CI
- [ ] Web UI for config (no need to edit YAML/Python)

---

## Security Issues

Do NOT open public issues for security bugs. Email directly:
- Email: `[author email]`
- Or use GitHub Security Advisories

---

## Code of Conduct

Be kind. Disagree respectfully. No harassment, spam, or discrimination. Maintainers reserve right to remove contributions that violate this.

---

## License

By contributing, you agree your contributions are MIT licensed.

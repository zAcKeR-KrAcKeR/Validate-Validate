# Validate Validate ⚔️

**AI builds. AI challenges. Evidence decides.**

Validate Validate is an adversarial, gamified code-review MVP. A Developer Agent proposes a small task and can prepare a patch; a Validator Agent hunts for concrete defects and cites source evidence; a referee verifies the cited file, line, and snippet before the finding is adjudicated.

## Features

- Load a public GitHub repository or upload a repository ZIP.
- Bounded source inspection with common generated/vendor directories excluded.
- Optional live Developer and Validator agents through an OpenAI-compatible chat-completions API.
- Offline demo mode with deterministic heuristic candidates.
- Evidence checks for safe relative paths, valid line numbers, and matching source snippets.
- Unified-diff patch proposals, shown before explicit user-approved application.
- Scoreboard, round history, JSON report download, unit tests, and GitHub Actions CI.

## Quick start

Requires Python 3.10+ and Git for cloning and patch application.

\`\`\`bash
git clone https://github.com/zAcKeR-KrAcKeR/Validate-Validate.git
cd Validate-Validate
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
\`\`\`

Open the Streamlit URL printed in the terminal (normally http://localhost:8501).

## Live AI mode

Add an API key in the app sidebar, or set environment variables:

\`\`\`dotenv
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_DEVELOPER_MODEL=gpt-4.1-mini
OPENAI_VALIDATOR_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=https://api.openai.com/v1
\`\`\`

The configured provider must support chat completions and JSON response format. Keep API keys private.

## Demo mode

No API key is required. Local heuristics look for patterns such as \`eval()\`, \`shell=True\`, credential-like assignments, debug prints, and TODO markers. These are review candidates, not automatically confirmed bugs.

## How to play

1. Load a public GitHub repository or upload a ZIP.
2. Generate a development task.
3. Run adversarial validation.
4. Inspect each finding's cited evidence and impact.
5. Submit a finding to the Developer Agent for acceptance or dispute.
6. Review a proposed patch and explicitly apply it if appropriate.
7. Run your own tests and inspect the diff before merging.

## Scoring

| Event | Points |
|---|---:|
| Accepted low / medium / high / critical finding | +5 / +10 / +15 / +25 Validator |
| Rejected false positive | -10 Validator |
| Applied patch | +15 provisional Developer |
| Regression suite pass | Not awarded automatically |

## Safety and limitations

- Repository code is inspected as text; the app does not execute untrusted repository scripts, install dependencies, or run tests.
- Evidence-location verification is not semantic proof. A human must still decide whether a finding is a real defect.
- Patch application requires explicit user action. \`git apply --check\` checks applicability, not correctness or safety.
- Only public GitHub HTTPS repositories are supported by the clone workflow.
- Source context is bounded to 80 files and 24,000 characters.
- The app does not autonomously commit or push changes to repositories it reviews.
- Live-agent prompts send inspected source context to the configured model provider. Do not submit private or sensitive code unless that data flow is approved.

## Project structure

\`\`\`text
Validate-Validate/
├── app.py
├── vv/
│   ├── agents.py
│   ├── analyzers.py
│   ├── patching.py
│   ├── repository.py
│   └── scoring.py
├── tests/test_core.py
├── .github/workflows/tests.yml
├── requirements.txt
├── .env.example
└── Dockerfile
\`\`\`

## Tests

\`\`\`bash
pytest -q
\`\`\`

## Docker

\`\`\`bash
docker build -t validate-validate .
docker run --rm -p 8501:8501 validate-validate
\`\`\`

## Roadmap

- Isolated ephemeral containers for safely executing tests with resource and network limits.
- Independent referee model and disagreement resolution.
- Branch-per-round workflow and pull-request creation after explicit approval.
- Test generation, regression detection, mutation testing, and coverage deltas.
- Multi-model tournaments, Elo ratings, and public leaderboards.
- Retrieval/indexing for large monorepositories.

## License

MIT. See [LICENSE](LICENSE).

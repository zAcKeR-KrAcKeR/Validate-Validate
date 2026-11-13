# Validate Validate ⚔️

**AI builds. AI challenges. Evidence decides.**

This repository contains the Validate Validate MVP source archive. Download `validate-validate.zip` from the repository root and extract it to get the complete project, including the Streamlit app, agent modules, tests, Dockerfile, and GitHub Actions workflow.

## Quick start

```bash
unzip validate-validate.zip
cd validate-validate
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

See the extracted project's README.md for configuration, safety notes, scoring rules, and limitations.

## Important MVP limitations

- Repository source is inspected as text; untrusted repository code is not executed.
- Demo mode uses heuristic review candidates, not proof of defects.
- Live AI mode requires an OpenAI-compatible API key.
- Patch proposals require explicit review and application.
- The MVP does not autonomously commit or push changes to target repositories.

License: MIT.

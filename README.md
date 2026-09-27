# AI Test Case Generator

Turns software requirements into structured, executable test cases with AI. Built step by step in the YouTube series **[Prompt to Prod with Sonali](https://www.youtube.com/@PromptToProdWithSonali)**.

## Run locally
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://localhost:8000/docs to try the API.

## Run the tests
```powershell
pytest -q
```

## Tips

**Shorter terminal prompt (PowerShell).** Run once to show only the folder name in your prompt:
```powershell
Set-Content -Path $PROFILE -Value 'function prompt { "PS $(Split-Path -Leaf (Get-Location))> " }'
```
Open a new terminal to see it. To undo, run `notepad $PROFILE` and delete the line.

import subprocess

MODEL = "gemma:4b"


def ask_llm(user_input: str) -> str:
    prompt = f"""
You are a STRICT command-to-JSON compiler.

YOU MUST ALWAYS OUTPUT VALID JSON.
You are NOT allowed to output nothing.
You are NOT allowed to output text.

If the command cannot be executed, you MUST output:
{{ "steps": [] }}

Allowed actions:
open_app
create_file
write_file
read_file
move_file

Rules:
- Output JSON ONLY
- No explanations
- No markdown
- No extra text

Understand natural language:
- "create a file flower.txt in ab2"
- "create a text file named soul in ab3"
- "text file" means .txt
- Folder aliases: ab1, ab2, ab3

Examples:

User: create a file flower.txt in ab2
Output:
{{
  "steps": [
    {{ "action": "create_file", "target": "AB2/flower.txt", "content": null }}
  ]
}}

User: create a text file named soul in ab3
Output:
{{
  "steps": [
    {{ "action": "create_file", "target": "AB3/soul.txt", "content": null }}
  ]
}}

User: hello
Output:
{{ "steps": [] }}

REMEMBER:
YOU MUST ALWAYS OUTPUT JSON.

User: {user_input}
"""

    result = subprocess.run(
        ["ollama", "run", MODEL, "--prompt", prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    output = result.stdout.strip()

    # 🔒 HARD SAFETY NET (CRITICAL)
    if not output.startswith("{"):
        return '{ "steps": [] }'

    return output

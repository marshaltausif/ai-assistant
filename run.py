import json
from controller.llm import ask_llm
from executors.file_exec import create_file, write_file, read_file, move_file
from memory.memory import update_memory, resolve_reference
from voice.stt import listen_and_transcribe
from voice.tts import speak

SPEAK_ALWAYS = True


def say(text):
    if not text:
        return
    print(text)
    if SPEAK_ALWAYS:
        speak(text)


def extract_folder_from_text(text):
    text = text.lower()
    for folder in ["ab1", "ab2", "ab3"]:
        if folder in text:
            return folder
    return None


say("AI Assistant initialized. Memory and voice are enabled.")
say("Type exit to quit. Type V and press Enter to speak.")


def clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return text


while True:
    user = input("You: ")

    if user.lower() in ["exit", "quit"]:
        say("Shutting down. Goodbye.")
        break

    if user.lower() == "v":
        say("Listening")
        user = listen_and_transcribe()
        say(f"You said {user}")

    say("Thinking")
    raw = ask_llm(user)
    say("I have understood your request")

    try:
        data = json.loads(clean_json(raw))
        
    except Exception:
        say("I could not understand the instruction.")
        continue

    for step in data.get("steps", []):

        action = step.get("action")
        target = step.get("target")
        content = step.get("content")

        # ---------- GENERAL QUESTION / CHAT ----------
        if action in ["none", "search_web"]:
            say("Answering your question")
            answer = ask_llm(user)
            say(answer)
            continue

        # ---------- CREATE FILE ----------
        if action == "create_file":
            say("Creating file")

            # Case: full path already provided (ab2/hello.py)
            if target and "/" in target:
                create_file(target)
                folder = target.split("/")[0]
                filename = target.split("/")[-1]
                update_memory(
                    last_created_file=filename,
                    last_touched_file=filename,
                    last_folder=folder,
                )
                say(f"Created file {filename} in {folder.upper()}")
                continue

            folder = resolve_reference(content) if content else None
            if not folder:
                folder = extract_folder_from_text(user)

            filename = target
            if not filename.endswith((".py", ".txt", ".doc", ".docx")):
                filename += ".txt"

            if folder in ["ab1", "ab2", "ab3"]:
                create_file(f"{folder}/{filename}")
                update_memory(
                    last_created_file=filename,
                    last_touched_file=filename,
                    last_folder=folder,
                )
                say(f"Created file {filename} in {folder.upper()}")
            else:
                create_file(filename)
                update_memory(
                    last_created_file=filename,
                    last_touched_file=filename,
                )
                say(f"Created file {filename}")

        # ---------- WRITE FILE ----------
        elif action == "write_file":
            target = resolve_reference(target)
            say(f"Writing content to {target}")
            write_file(target, content)
            update_memory(last_written_file=target, last_touched_file=target)
            say("Writing complete")

        # ---------- READ FILE ----------
        elif action == "read_file":
            target = resolve_reference(target)
            say(f"Reading file {target}")
            text = read_file(target)
            update_memory(last_touched_file=target)
            say(text)

        # ---------- MOVE FILE ----------
        elif action == "move_file":
            say("Preparing to move file")

            if target and target.lower() in ["ab1", "ab2", "ab3"]:
                source = resolve_reference("that file")
                destination = target
            else:
                source = resolve_reference(target)
                destination = resolve_reference(content)

            if not source or not destination:
                say("I could not determine the file or destination.")
                continue

            move_file(source, destination)
            update_memory(last_touched_file=source, last_folder=destination)
            say(f"Moved {source} to {destination.upper()}")

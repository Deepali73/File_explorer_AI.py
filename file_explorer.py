import streamlit as st
import os
import shutil
import speech_recognition as sr
import pyttsx3
import threading

# ====================== Voice Engine Setup =====================
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    def run():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run).start()

def listen_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening for your command.")
        st.info("🎙️ Listening... Please speak now.")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio)
        st.success(f"🗣️ You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I could not understand your command.")
        st.error("Could not understand. Please try again.")
        return ""
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        st.error("Recognition service error.")
        return ""

# =================== File Management Functions ==================
def list_files_sorted(folder):
    try:
        files = os.listdir(folder)
        file_info = []
        for f in files:
            full_path = os.path.join(folder, f)
            if os.path.isfile(full_path):
                file_type = os.path.splitext(f)[1][1:] or "unknown"
                size = os.path.getsize(full_path)
                file_info.append((f, file_type, size))
        file_info.sort(key=lambda x: (x[1], x[2]))  # sort by type then size
        return file_info
    except Exception as e:
        return f"❌ Error: {e}"

def rename_file(old_name, new_name, directory):
    os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))

def delete_path(name, directory):
    path = os.path.join(directory, name)
    if os.path.isfile(path):
        os.remove(path)
        return "✅ File deleted."
    elif os.path.isdir(path):
        shutil.rmtree(path)
        return "✅ Directory deleted."
    else:
        return "❌ Invalid path."

def create_dir(folder_name, directory):
    os.makedirs(os.path.join(directory, folder_name), exist_ok=True)
    return "✅ Directory created."

# ======================= Streamlit UI Setup ========================
st.set_page_config("📁 Fiorer", layout="centered")
st.markdown("<h1 style='color:#7B68EE;'>📁 Fiorer</h1>", unsafe_allow_html=True)
st.markdown("#### A smarter voice-enabled file management explorer")

default_directory = os.getcwd()
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar for command history
st.sidebar.markdown("## 📜 Commands Run")
if st.session_state.history:
    for cmd in st.session_state.history[::-1]:
        st.sidebar.markdown(f"- {cmd}")
else:
    st.sidebar.info("No commands yet.")

# ====================== Mode Selection =======================
mode = st.sidebar.selectbox("Choose Input Mode", ["Voice Command", "API Command"])

# ====================== VOICE COMMAND MODE ======================
if mode == "Voice Command":
    if st.button("🎤 Speak Command"):
        command = listen_command()
        if not command:
            st.stop()

        st.session_state.history.append(f"Voice: {command}")

        # Normalize voice command
        command = command.lower().strip()

        if any(kw in command for kw in ["list", "show", "display", "see files", "all files", "contents"]):
            files = list_files_sorted(default_directory)
            if isinstance(files, str):
                st.error(files)
            else:
                st.markdown("### 🗂️ Files in Current Folder (Sorted)")
                st.markdown("**Name** | **Type** | **Size (bytes)**")
                st.markdown("---")
                for f, ext, size in files:
                    st.markdown(f"`{f}` | `{ext}` | `{size}`")
                st.toast("📄 File listing complete!")

        elif any(kw in command for kw in ["rename", "change name", "modify name", "update name"]):
            speak("Sorry, rename via voice is not yet supported. Use API tab.")
            st.warning("⚠️ Rename not supported in voice mode.")

        elif any(kw in command for kw in ["delete", "remove", "erase", "trash", "clear file", "clear folder"]):
            speak("Sorry, delete via voice is not yet supported. Use API tab.")
            st.warning("⚠️ Delete not supported in voice mode.")

        elif any(kw in command for kw in ["create", "make folder", "new folder", "add folder", "mkdir"]):
            speak("Sorry, folder creation via voice is not yet supported. Use API tab.")
            st.warning("⚠️ Folder creation not supported in voice mode.")

        else:
            speak("That command is not available right now.")
            st.warning("❌ Unrecognized command. Try: show files, delete file, rename file, or make folder.")

# ======================= API COMMAND MODE =========================
elif mode == "API Command":
    st.subheader("🔧 Select Operation")
    command = st.selectbox("Choose Command", ["list", "rename", "delete", "create"])
    directory = st.text_input("📂 Enter folder path", value=default_directory)

    if command == "list":
        if st.button("🔍 List Files"):
            st.session_state.history.append(f"API: list - {directory}")
            files = list_files_sorted(directory)
            if isinstance(files, str):
                st.error(files)
            else:
                st.markdown("### 🗂️ Files in Selected Folder (Sorted)")
                st.markdown("**Name** | **Type** | **Size (bytes)**")
                st.markdown("---")
                for f, ext, size in files:
                    st.markdown(f"`{f}` | `{ext}` | `{size}`")
                st.toast("📁 Listing complete")

    elif command == "rename":
        old_name = st.text_input("Enter OLD file name")
        new_name = st.text_input("Enter NEW file name")
        if st.button("✏️ Rename"):
            try:
                rename_file(old_name, new_name, directory)
                st.success("✅ File renamed successfully.")
                st.toast("✏️ Renamed")
                st.session_state.history.append(f"API: rename {old_name} → {new_name}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    elif command == "delete":
        name = st.text_input("Enter file/folder name to DELETE")
        if st.button("🗑️ Delete"):
            if name:
                result = delete_path(name, directory)
                st.success(result)
                st.toast("🗑️ Deleted")
                st.session_state.history.append(f"API: delete {name}")
            else:
                st.warning("Please enter a valid file/folder name.")

    elif command == "create":
        folder_name = st.text_input("Enter NEW folder name")
        if st.button("📁 Create Folder"):
            if folder_name:
                try:
                    result = create_dir(folder_name, directory)
                    st.success(result)
                    st.toast("📂 Folder created")
                    st.session_state.history.append(f"API: create folder {folder_name}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("Enter a folder name.")

# ========================== Footer =============================
st.markdown("---")
st.info("⚙️ Fiorer: A smart file explorer using voice & API. Say commands like 'show files' or use the API tab.")

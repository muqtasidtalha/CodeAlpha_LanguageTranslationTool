import os
import threading
import customtkinter as ctk
from translatepy import Translator
from gtts import gTTS
import pygame

# Initialize Pygame Mixer for Text-to-Speech Audio
pygame.mixer.init()

# Initialize Translator
translator = Translator()

# Configure App Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Available Languages (Display Name: Language Code)
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Chinese (Simplified)": "zh-CN",
    "Korean": "ko",
    "Arabic": "ar",
    "Hindi": "hi",
    "Urdu": "ur",
    "Turkish": "tr"
}

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CodeAlpha - Language Translation Tool")
        self.geometry("650x550")
        self.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        # Header Title
        title_label = ctk.CTkLabel(
            self, 
            text="AI Language Translator", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(20, 10))

        # Language Selection Frame
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(fill="x", padx=30, pady=10)

        # Source Language Dropdown
        ctk.CTkLabel(lang_frame, text="From:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=5, sticky="w")
        self.src_lang_cb = ctk.CTkComboBox(lang_frame, values=list(LANGUAGES.keys()), width=200)
        self.src_lang_cb.set("English")
        self.src_lang_cb.grid(row=0, column=1, padx=10)

        # Target Language Dropdown
        ctk.CTkLabel(lang_frame, text="To:", font=ctk.CTkFont(size=14)).grid(row=0, column=2, padx=(20, 5), sticky="w")
        self.dest_lang_cb = ctk.CTkComboBox(lang_frame, values=list(LANGUAGES.keys()), width=200)
        self.dest_lang_cb.set("French")
        self.dest_lang_cb.grid(row=0, column=3, padx=10)

        # Input Text Area
        ctk.CTkLabel(self, text="Enter Text:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=30, pady=(10, 2))
        self.input_textbox = ctk.CTkTextbox(self, width=590, height=120, font=("Consolas", 13))
        self.input_textbox.pack(padx=30, pady=(0, 10))

        # Action Buttons (Translate & Clear)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=5)

        self.translate_btn = ctk.CTkButton(
            btn_frame, 
            text="Translate", 
            command=self.start_translation_thread,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=35
        )
        self.translate_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.clear_btn = ctk.CTkButton(
            btn_frame, 
            text="Clear", 
            fg_color="#D32F2F", 
            hover_color="#9A0007",
            command=self.clear_all,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=35
        )
        self.clear_btn.pack(side="right", expand=True, fill="x", padx=(5, 0))

        # Output Text Area
        ctk.CTkLabel(self, text="Translated Output:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=30, pady=(15, 2))
        self.output_textbox = ctk.CTkTextbox(self, width=590, height=120, font=("Consolas", 13))
        self.output_textbox.pack(padx=30, pady=(0, 10))

        # Extra Actions Frame (Copy & Speak)
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", padx=30, pady=5)

        self.copy_btn = ctk.CTkButton(
            actions_frame, 
            text="Copy to Clipboard", 
            command=self.copy_to_clipboard, 
            width=160
        )
        self.copy_btn.pack(side="left", padx=5)

        self.speak_btn = ctk.CTkButton(
            actions_frame, 
            text="Listen (TTS)", 
            command=self.start_tts_thread, 
            width=160
        )
        self.speak_btn.pack(side="left", padx=5)

        # Status Bar
        self.status_label = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=12), text_color="gray")
        self.status_label.pack(side="bottom", pady=5)

    def start_translation_thread(self):
        """Runs translation in a background thread to keep UI smooth."""
        threading.Thread(target=self.translate_text, daemon=True).start()

    def translate_text(self):
        text = self.input_textbox.get("1.0", "end-1c").strip()
        if not text:
            self.status_label.configure(text="Please enter text to translate.", text_color="#FF9800")
            return

        self.status_label.configure(text="Translating...", text_color="#2196F3")
        self.translate_btn.configure(state="disabled")

        try:
            dest_code = LANGUAGES[self.dest_lang_cb.get()]

            # Translate using translatepy
            result = translator.translate(text, destination_language=dest_code)
            translated_text = str(result)

            self.output_textbox.delete("1.0", "end")
            self.output_textbox.insert("1.0", translated_text)
            self.status_label.configure(text="Translation Complete!", text_color="#4CAF50")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="#F44336")
        finally:
            self.translate_btn.configure(state="normal")

    def copy_to_clipboard(self):
        translated_text = self.output_textbox.get("1.0", "end-1c").strip()
        if translated_text:
            self.clipboard_clear()
            self.clipboard_append(translated_text)
            self.status_label.configure(text="Copied to clipboard!", text_color="#4CAF50")

    def start_tts_thread(self):
        """Runs Text-to-Speech audio in a background thread."""
        threading.Thread(target=self.play_tts, daemon=True).start()

    def play_tts(self):
        translated_text = self.output_textbox.get("1.0", "end-1c").strip()
        if not translated_text:
            return

        self.status_label.configure(text="Playing audio...", text_color="#2196F3")
        try:
            dest_code = LANGUAGES[self.dest_lang_cb.get()]
            tts = gTTS(text=translated_text, lang=dest_code, slow=False)
            filename = "temp_audio.mp3"
            tts.save(filename)

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()
            if os.path.exists(filename):
                os.remove(filename)

            self.status_label.configure(text="Audio finished.", text_color="#4CAF50")
        except Exception as e:
            self.status_label.configure(text=f"TTS Error: {str(e)}", text_color="#F44336")

    def clear_all(self):
        self.input_textbox.delete("1.0", "end")
        self.output_textbox.delete("1.0", "end")
        self.status_label.configure(text="Cleared.", text_color="gray")


if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
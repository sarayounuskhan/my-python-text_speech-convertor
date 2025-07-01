import os
from gtts import gTTS
import tempfile # To create and manage temporary files securely
from pydub import AudioSegment
from pydub.playback import play

# --- Function to convert text to speech ---
def convert_text_to_speech(text, lang='en', slow=False):
    """
    Converts the given text to speech using gTTS and plays it.

    Args:
        text (str): The text to be converted to speech.
        lang (str): The language/accent code (e.g., 'en' for English,
                    'en-uk' for British English, 'es' for Spanish).
                    Defaults to 'en'.
        slow (bool): If True, the speech will be slower. Defaults to False.
    """
    if not text:
        print("Please enter some text to convert.")
        return

    # Create a temporary file to save the speech
    # Using NamedTemporaryFile ensures a unique filename and proper cleanup
    filename = None # Initialize filename to None
    try:
        # Create a gTTS object
        print(f"Converting text to speech (Language: {lang}, Slow: {slow})...")
        tts = gTTS(text=text, lang=lang, slow=slow)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as fp:
            filename = fp.name
            tts.save(filename)
            print(f"Speech saved to temporary file: {filename}")

        # Play the generated speech using pydub
        print("Playing speech...")
        audio = AudioSegment.from_file(filename, format="mp3")
        play(audio)
        print("Speech playback finished.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure you have an active internet connection and "
              "the 'gTTS', 'pydub', and 'simpleaudio' libraries are correctly installed. "
              "Also, ensure 'ffmpeg' is installed and in your system's PATH if you encounter issues with pydub.")
    finally:
        # Clean up: remove the temporary audio file
        if filename and os.path.exists(filename):
            os.remove(filename)
            print(f"Temporary file '{filename}' removed.")

# --- Main part of the application ---
if __name__ == "__main__":
    print("Welcome to the Text-to-Speech Converter!")
    print("---------------------------------------")
    print("Before you start, make sure you have the following installed:")
    print("1. gTTS: pip install gtts")
    print("2. pydub: pip install pydub")
    print("3. simpleaudio (for Windows/macOS): pip install simpleaudio")
    print("   (Note: For pydub to work, you might also need to install 'ffmpeg' and add it to your system's PATH. You can download it from https://ffmpeg.org/download.html)")
    print("\n")

    while True:
        # Get text input from the user
        user_text = input("Enter the text you want to convert to speech (type 'exit' to quit): ").strip()

        if user_text.lower() == 'exit':
            print("Exiting Text-to-Speech Converter. Goodbye!")
            break

        # Get language/accent preference
        print("\nAvailable Languages/Accents (common examples):")
        print("  - en (English, default)")
        print("  - en-us (English - United States)")
        print("  - en-uk (English - United Kingdom)")
        print("  - es (Spanish)")
        print("  - fr (French)")
        print("  - de (German)")
        print("  - hi (Hindi)")
        # You can find more language codes in the gTTS documentation
        lang_choice = input("Enter language code (e.g., 'en', 'es', 'en-uk', leave empty for 'en'): ").strip().lower()
        if not lang_choice:
            lang_choice = 'en'

        # Get speech rate preference
        rate_choice = input("Do you want the speech to be slow? (yes/no, default: no): ").strip().lower()
        is_slow = (rate_choice == 'yes')

        # Convert and play the speech
        convert_text_to_speech(user_text, lang=lang_choice, slow=is_slow)
        print("\n" + "="*40 + "\n") # Separator for next inputs
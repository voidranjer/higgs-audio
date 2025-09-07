import subprocess
import time
from google import genai
from PIL import Image
from io import BytesIO

from config import REMOTE_USER, REMOTE_HOST, REMOTE_PORT, REMOTE_DIR, POLLING_INTERVAL
from utils import reset_tmp_folder, get_sys_prompt

# Initialize the genai client once
try:
    client = genai.Client()
    print("DEBUG: Google GenAI client initialized successfully.")
except Exception as e:
    print(f"ERROR: Failed to initialize Google GenAI client: {e}")
    print("Please ensure your API key is correctly configured for the `google-generativeai` library.")
    exit(1)  # Exit if the client cannot be initialized


# --- Image Generation Function ---
def generate_image_with_gemini(transcript_text, output_filename="generated_image.png"):
    """
    Generates an image using the Google Gemini API based on the transcript text
    and saves it to the specified output filename.
    """
    print(f"\n--- Gemini Image Generation ---")
    # print(f"Prompting Gemini with: '{transcript_text.strip()}'")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=contents,
        )

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(f"DEBUG: Gemini response contained text: {part.text}")
                # You might want to handle this case, e.g., if Gemini returns a description instead of an image
            elif part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(output_filename)
                print(f"SUCCESS: Image saved to {output_filename}")
                return output_filename  # Return the filename if successful
        print("WARNING: Gemini response did not contain an image.")
        return None

    except Exception as e:
        print(f"ERROR: Failed to generate image with Gemini: {e}")
        return None


# --- Utility Functions (poll_and_generate_images) ---
def poll_and_generate_images():
    print(f"DEBUG: Starting transcript polling at interval of {POLLING_INTERVAL} seconds.")
    print("-" * 30)

    try:
        current_file_index = 0
        reset_tmp_folder()

        while True:
            filename = f"{current_file_index}.txt"  # Polling for .txt transcript files

            scp_command = [
                "scp",
                "-P",
                REMOTE_PORT,
                f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/{filename}",
                "./tmp",
            ]

            result = subprocess.run(scp_command, capture_output=True)

            if result.returncode == 0:
                print(f"TRACE: Found and downloaded {filename}.")

                # Read the content of the transcript file
                filepath = f"tmp/{filename}"
                with open(filepath, "r") as f:
                    transcript_content = f.read()

                print(f"DEBUG: Transcript content: {transcript_content.strip()}")

                # Generate an image using the Gemini API with the transcript content
                output_image_path = f"generated_image.png"  # Unique filename for each image
                generated_image_file = generate_image_with_gemini(transcript_content, output_image_path)

                if generated_image_file:
                    print(f"Successfully generated image: {generated_image_file}")
                    # You can now use the 'generated_image_file' path, for example, to display it
                else:
                    print(f"Could not generate an image for transcript in {filepath}.")

                current_file_index += 1
            else:
                # File was not found. Wait and try again.
                time.sleep(POLLING_INTERVAL)
                continue

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        time.sleep(5)


if __name__ == "__main__":
    poll_and_generate_images()

import subprocess
import time
import platform

from utils import reset_tmp_folder

# --- Configuration ---
# You can change these values to match your specific setup.
REMOTE_USER = "james"
REMOTE_HOST = "184.148.227.159"
REMOTE_PORT = "40806"
REMOTE_DIR = "/home/james/higgs-audio/team09/tmp"
POLLING_INTERVAL = 0.5  # Time to wait between polling cycles in seconds


# --- Utility Functions ---
def play_audio(filepath):
    """
    Plays a local .wav file using the appropriate system command.
    Uses 'afplay' for macOS and 'aplay' for Linux.
    """
    system_os = platform.system()
    audio_command = None

    if system_os == "Darwin":
        audio_command = "afplay"
    elif system_os == "Linux":
        audio_command = "aplay"
    else:
        print(f"ERROR: Unsupported operating system: {system_os}. Cannot play audio.")
        return

    print(f"DEBUG: Playing audio file: {filepath} with command '{audio_command}'.")
    try:
        # We redirect stdout and stderr to a null device to avoid cluttering the terminal.
        subprocess.run([audio_command, filepath], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"DEBUG: Finished playing {filepath}.")
    except FileNotFoundError:
        print(f"ERROR: '{audio_command}' command not found. Please ensure it is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to play audio file. Command returned an error: {e}")


# def delete_remote_file(filename):
#     """
#     Deletes a file on the remote server using SSH.
#     """
#     print(f"DEBUG: Deleting remote file '{filename}' via SSH.")
#     ssh_command = ["ssh", "-p", REMOTE_PORT, f"{REMOTE_USER}@{REMOTE_HOST}", f"rm -f {REMOTE_DIR}/{filename}"]
#     # Execute the SSH command to delete the file.
#     result = subprocess.run(ssh_command, capture_output=True, text=True)
#     if result.returncode == 0:
#         print(f"TRACE: Remote file '{filename}' deleted successfully.")
#     else:
#         print(f"ERROR: Failed to delete remote files. SSH command failed with return code {result.returncode}")
#         print(f"Stderr: {result.stderr}")


def poll_and_play():
    """
    Main function to poll the remote directory for new audio files.

    Algorithm logic:
    1. Start by polling for 0.wav.
    2. When 0.wav appears, play it. After playing, delete it from the remote server using SSH.
    3. Check for the next file in sequence (1.wav, 2.wav, etc.) and repeat step 2.
       Also check for 0.wav again. If 0.wav appears before the next in sequence is found, reset back to step 1.
    """
    print(f"DEBUG: Starting audio polling at interval of {POLLING_INTERVAL} seconds.")
    print("-" * 30)

    try:
        current_file_index = 0
        reset_tmp_folder()

        # Inner loop to check for files sequentially (0.wav, 1.wav, etc.)
        while True:
            filename = f"{current_file_index}.wav"

            # print(f"TRACE: Checking for file: {filename}")

            # Construct the scp command to download the file.
            scp_command = [
                "scp",
                "-P",
                REMOTE_PORT,
                f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}/{filename}",
                "./tmp",
            ]

            # Execute the scp command. We redirect stderr to a null device
            # to suppress 'No such file or directory' errors.
            result = subprocess.run(scp_command, capture_output=True)

            if result.returncode == 0:
                # File was successfully downloaded.
                print(f"TRACE: Found and downloaded {filename}.")
                play_audio(filename)
                current_file_index += 1
            else:
                # File was not found. This marks the end of the sequence.
                # print(f"TRACE: File {filename} not found. End of sequence.")
                time.sleep(POLLING_INTERVAL)
                continue  # Break the inner loop to start the cleanup process.

        # print(f"DEBUG: No files found in this cycle. Waiting for {POLLING_INTERVAL} seconds...")
        # print("-" * 30)

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Wait before retrying to prevent a rapid error loop.
        time.sleep(5)


if __name__ == "__main__":
    poll_and_play()

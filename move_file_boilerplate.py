import shutil
import os

def move_file_to_destination(target_file):
    """
    Moves a specified file to a predefined destination directory.
    """
    # Define your destination directory here
    destination_dir = r'I:\\groups\\fac2\\fabs\\stores\\FSSAP\\test_ignore\\destination'
    
    # Ensure the destination directory exists
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
        print(f"Created missing directory: {destination_dir}")

    try:
        # Construct the full destination path
        file_name = os.path.basename(target_file)
        destination_path = os.path.join(destination_dir, file_name)
        
        # Perform the move
        shutil.move(target_file, destination_path)
        print(f"Successfully moved: {file_name}")
        print(f"To: {destination_path}")
        
    except FileNotFoundError:
        print(f"Error: The file '{target_file}' was not found.")
    except PermissionError:
        print("Error: Permission denied. Check if the file is open elsewhere.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Placeholder Trigger ---
# This simulates the 'other function' passing the file path
placeholder_file = r'I:\\groups\\fac2\\fabs\\stores\\FSSAP\\test_ignore\\1\\testcopy.pdf'

# Trigger the function
move_file_to_destination(placeholder_file)
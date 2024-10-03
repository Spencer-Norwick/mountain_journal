"""
File: mountain_journal.py
Author: Spencer Norwick
Date: October 2, 2024
Description: This script contains the command-line interface for a mountaineering journal application.
             Users can log text, audio, and image entries, and each entry is timestamped and synced with 
             a simulated GPS location. Start and end times/locations are recorded for each climb.

Usage:
    - Run this script to interact with the journal through the command-line interface.
    - Available options: Start a climb, log a journal entry, end a climb, list climbs, clear all climbs.

Future Work:
    - Integrate real GPS data and file handling for audio and images.
    - Add data visualization for climb entries.

"""

import json
from datetime import datetime
import random
import os
import shutil  # For clearing all climbs

# Simulate GPS location
def get_location():
    return round(random.uniform(-90, 90), 6), round(random.uniform(-180, 180), 6)

# Function to check if any climb is active (i.e., no 'end_time' in the file)
def is_active_climb():
    app_data_path = "app_data"
    for root, dirs, files in os.walk(app_data_path):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file), "r") as f:
                    climb = json.load(f)
                    if "end_time" not in climb:
                        return os.path.join(root, file)  # Return the full path of the active climb file
    return None

# Ensure the app_data folder exists
def ensure_app_data_folder():
    if not os.path.exists("app_data"):
        os.makedirs("app_data")

# Function to create journal entry subfolders
def create_journal_entry_folders(climb_dir):
    journal_entries_dir = os.path.join(climb_dir, "journal_entries")
    os.makedirs(journal_entries_dir, exist_ok=True)
    
    # Create subfolders for text, audio, and images
    os.makedirs(os.path.join(journal_entries_dir, "text"), exist_ok=True)
    os.makedirs(os.path.join(journal_entries_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(journal_entries_dir, "images"), exist_ok=True)

# Function to list all climbs in app_data
def list_climbs():
    ensure_app_data_folder()  # Ensure app_data exists
    climbs = os.listdir("app_data")
    
    if not climbs:
        print("No climbs found.")
        return
    
    active_climb = is_active_climb()
    
    for climb in climbs:
        if os.path.isdir(os.path.join("app_data", climb)):
            if active_climb and climb in active_climb:
                print(f"{climb} (active)")
            else:
                print(climb)

# Function to clear all climbs in app_data
def clear_climbs():
    active_climb = is_active_climb()

    # Prevent clearing if there is an active climb
    if active_climb:
        print(f"Cannot clear climbs while an active climb is ongoing: '{active_climb}'.")
        return

    confirm = input("Are you sure you want to delete all climbs? This action cannot be undone. (yes/no): ").strip().lower()
    
    if confirm == "yes":
        shutil.rmtree("app_data")
        ensure_app_data_folder()  # Recreate the app_data folder after deletion
        print("All climbs have been cleared.")
    else:
        print("Operation cancelled. Climbs were not deleted.")

# Function to get a valid climb name (no spaces, handle duplicates)
def get_climb_filename():
    ensure_app_data_folder()  # Ensure app_data folder exists

    while True:
        climb_name = input("Enter a name for your climb (no spaces): ").strip()
        if " " in climb_name:
            print("Climb name cannot contain spaces. Please try again.")
            continue

        # Check if a folder with the climb name exists, and handle numbering
        original_name = climb_name
        counter = 0
        climb_dir = os.path.join("app_data", climb_name)

        while os.path.exists(climb_dir):
            counter += 1
            climb_dir = os.path.join("app_data", f"{original_name}{counter}")

        os.makedirs(climb_dir)  # Create the climb directory
        create_journal_entry_folders(climb_dir)  # Create subfolders for journal entries
        return climb_dir  # Return the directory path

# Function to start a new climb
def start_climb():
    active_climb = is_active_climb()
    
    # Check if there is already an active climb
    if active_climb:
        print(f"A climb is already active: '{active_climb}'. Please end the current climb before starting a new one.")
        return

    # Get the climb directory
    climb_dir = get_climb_filename()

    start_time = datetime.now().isoformat()
    start_location = get_location()

    climb = {
        "start_time": start_time,
        "start_location": start_location,
        "entries": []
    }

    # Save the climb data in a JSON file within the climb folder
    climb_file = os.path.join(climb_dir, "climb_data.json")
    with open(climb_file, "w") as f:
        json.dump(climb, f)

    print(f"Climb '{climb_dir}' started at {start_time}, location: {start_location}")

# Generalized function to log a new journal entry (text, audio, image)
def log_entry():
    active_climb = is_active_climb()

    # If no active climb is found, automatically start a new one
    if not active_climb:
        print("No active climb found. Starting a new climb...")
        start_climb()
        active_climb = is_active_climb()  # After starting a climb, re-fetch the active climb

    climb_dir = os.path.dirname(active_climb)
    journal_entries_dir = os.path.join(climb_dir, "journal_entries")

    with open(active_climb, "r+") as f:
        climb = json.load(f)

    entry_type = input("Entry type (text, audio, image): ").strip().lower()
    entry_time = datetime.now().isoformat()
    entry_location = get_location()

    if entry_type == "text":
        entry_data = input("Journal entry (text): ")
        entry_file = os.path.join(journal_entries_dir, "text", f"{entry_time}.txt")
        with open(entry_file, "w") as file:
            file.write(entry_data)

        entry = {
            "type": "text",
            "time": entry_time,
            "location": entry_location,
            "file_path": entry_file
        }

    elif entry_type == "audio":
        entry_data = input("Path to audio file (or placeholder): ")
        entry_file = os.path.join(journal_entries_dir, "audio", f"{entry_time}.mp3")
        with open(entry_file, "w") as file:
            file.write(entry_data)  # Placeholder for now

        entry = {
            "type": "audio",
            "time": entry_time,
            "location": entry_location,
            "file_path": entry_file
        }

    elif entry_type == "image":
        entry_data = input("Path to image file (or placeholder): ")
        entry_file = os.path.join(journal_entries_dir, "images", f"{entry_time}.jpg")
        with open(entry_file, "w") as file:
            file.write(entry_data)  # Placeholder for now

        entry = {
            "type": "image",
            "time": entry_time,
            "location": entry_location,
            "file_path": entry_file
        }

    else:
        print("Invalid entry type. Please choose 'text', 'audio', or 'image'.")
        return

    climb["entries"].append(entry)

    with open(active_climb, "w") as f:
        json.dump(climb, f)

    print(f"{entry_type.capitalize()} entry logged at {entry_time}, location: {entry_location}")

# End the climb
def end_climb():
    active_climb = is_active_climb()

    if not active_climb:
        print("No active climb found to end.")
        return

    with open(active_climb, "r+") as f:
        climb = json.load(f)

    end_time = datetime.now().isoformat()
    end_location = get_location()

    climb["end_time"] = end_time
    climb["end_location"] = end_location

    with open(active_climb, "w") as f:
        json.dump(climb, f)

    print(f"Climb '{active_climb}' ended at {end_time}, location: {end_location}")

# Function to handle exiting the program
def exit_program():
    active_climb = is_active_climb()

    if active_climb:
        confirm = input(f"An active climb is ongoing: '{active_climb}'. Exiting will end the current climb. Do you want to proceed? (yes/no): ").strip().lower()
        if confirm == "yes":
            end_climb()  # End the active climb before exiting
            print("Exiting the program.")
            exit()
        else:
            print("Continuing the current climb.")
            return
    else:
        print("No active climb. Exiting the program.")
        exit()

# Main CLI function
def main():
    while True:
        print("\nMountaineering Journal")
        print("1. Start a new climb")
        print("2. Log a journal entry")
        print("3. End the climb")
        print("4. List all climbs")
        print("5. Clear all climbs")
        print("6. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            start_climb()
        elif choice == "2":
            log_entry()
        elif choice == "3":
            end_climb()
        elif choice == "4":
            list_climbs()
        elif choice == "5":
            clear_climbs()
        elif choice == "6":
            exit_program()
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()

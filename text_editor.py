import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os # For path manipulation, like getting the base name of a file

class SimpleTextEditor:
    def __init__(self, master_window): # Renamed 'master' to 'master_window' for clarity
        """
        It Sets up the main window and components of our text editor.
        This is where it begins!
        """
        self.master = master_window
        self.master.title("My Wonderful Python Text Editor - Untitled") 
        self.master.geometry("850x650") 

        self.current_file_path = None # It Keep track of the file we're currently working on

        # Let's create the main text input area.
        #We can use ScrollText as, its super handy because it includes scrollbars automatically.
        self.text_area = scrolledtext.ScrolledText(
            self.master,
            wrap='word', 
            font=("Cascadia Code", 13), 
            bg="#ffffff",
            fg="#222222", 
            insertbackground="#000000", 
            selectbackground="#a0c8f9", 
            borderwidth=1, 
            relief="solid", 
            padx=12, 
            pady=12 
        )
        # Make the text area fill up all available space as the window resizes
        self.text_area.pack(expand=True, fill='both', padx=15, pady=15) # Slightly increased outer padding

        # We need a status bar at the bottom to show info like word count
        self.status_bar = tk.Label(
            self.master,
            text="Ready to type!", # A more welcoming initial message
            bd=1,
            relief=tk.SUNKEN, # Gives it a nice recessed look
            anchor=tk.W, # Aligns text to the left
            font=("Arial", 9, "italic"), # Slightly different font style
            bg="#f0f0f0", # A soft light gray
            fg="#666666" # Subtler text color
        )
        self.status_bar.pack(fill='x', side='bottom', ipady=2) # Added some internal padding

        # Whenever a key is released, we'll update the status bar (e.g., word count)
        self.text_area.bind('<KeyRelease>', self.update_status_info) # Renamed method for clarity
        # And let's update it right away when the editor opens
        self.update_status_info()

        # Time to build the menu bar for New, Open, Save, etc.
        self.setup_main_menu() # Renamed method

    def setup_main_menu(self):
        """
        Configures the top menu bar with standard file operations.
        """
        main_menubar = tk.Menu(self.master)
        self.master.config(menu=main_menubar)

        # The "File" dropdown menu
        file_options_menu = tk.Menu(main_menubar, tearoff=0) # tearoff=0 is important to keep it attached
        main_menubar.add_cascade(label="File", menu=file_options_menu)

        # Adding commands to the File menu
        file_options_menu.add_command(label="New File", command=self.start_new_document) # Renamed
        file_options_menu.add_command(label="Open Existing...", command=self.load_file) # Renamed
        file_options_menu.add_command(label="Save Current", command=self.save_current_file) # Renamed
        file_options_menu.add_command(label="Save As New...", command=self.save_file_as_new) # Renamed
        file_options_menu.add_separator()
        file_options_menu.add_command(label="Exit Editor", command=self.quit_editor) # Renamed

    def start_new_document(self):
        """
        Prepares the editor for a brand new, empty file.
        Prompts to save current work if there's unsaved text.
        """
        if self.text_area.get(1.0, tk.END).strip(): # Check if there's any text in the editor
            # If there's text, ask the user if they want to save it first
            if messagebox.askyesno("Unsaved Changes!", "Looks like you have unsaved changes. Want to save them first?"):
                if not self.save_current_file(): # Try to save; if user cancels, don't proceed
                    return # Stop here if save was cancelled

        self.text_area.delete(1.0, tk.END) # Clear everything from the text area
        self.current_file_path = None # No file is linked yet
        self.master.title("My Wonderful Python Text Editor - Untitled")
        self.update_status_info("Ready for a fresh start!")

    def load_file(self):
        """
        Opens a text file chosen by the user and loads its content into the editor.
        Also prompts to save current work if needed.
        """
        if self.text_area.get(1.0, tk.END).strip():
            if messagebox.askyesno("Unsaved Changes!", "Save current work before opening a new file?"):
                if not self.save_current_file():
                    return

        # Open a file dialog for the user to pick a file
        chosen_file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")] # Friendly file type filters
        )
        if chosen_file_path: # If the user actually selected a file (didn't cancel)
            try:
                # Open the file for reading with UTF-8 encoding (good for various characters)
                with open(chosen_file_path, 'r', encoding='utf-8') as file_handle:
                    file_content = file_handle.read() # Read all the text
                self.text_area.delete(1.0, tk.END) # Clear out anything that was there
                self.text_area.insert(1.0, file_content) # Put the new content in
                self.current_file_path = chosen_file_path # Remember this file's path
                # Update the window title to show the opened file's name
                self.master.title(f"My Wonderful Python Text Editor - {os.path.basename(chosen_file_path)}")
                self.update_status_info(f"Opened: {os.path.basename(chosen_file_path)}")
            except Exception as err: # Catch any errors during file operations
                messagebox.showerror("Error Opening File", f"Oops! Couldn't open that file: {err}")
                self.update_status_info("Failed to open file.")

    def save_current_file(self):
        """
        Saves the text to the currently associated file.
        If it's a new file, it will call 'save_file_as_new'.
        Returns True on successful save, False if cancelled or error.
        """
        if self.current_file_path: # Check if we already have a path for this file
            try:
                # Open the file in write mode ('w') - this will overwrite existing content
                with open(self.current_file_path, 'w', encoding='utf-8') as file_to_save:
                    # Get all text from the text area, stripping any extra newline at the end
                    file_to_save.write(self.text_area.get(1.0, tk.END).strip())
                self.update_status_info(f"Changes saved to: {os.path.basename(self.current_file_path)}")
                return True
            except Exception as err:
                messagebox.showerror("Save Error", f"Couldn't save the file! Problem: {err}")
                self.update_status_info("Error during save.")
                return False
        else:
            # If no file path, it means it's a new file, so we call "Save As"
            return self.save_file_as_new()

    def save_file_as_new(self):
        """
        Prompts the user to pick a new location and filename to save the current text.
        Returns True on successful save, False if cancelled.
        """
        new_file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")]
        )
        if new_file_path: # If the user picked a path
            try:
                with open(new_file_path, 'w', encoding='utf-8') as file_to_write:
                    file_to_write.write(self.text_area.get(1.0, tk.END).strip())
                self.current_file_path = new_file_path # Update the current file path
                self.master.title(f"My Wonderful Python Text Editor - {os.path.basename(new_file_path)}")
                self.update_status_info(f"Saved new file: {os.path.basename(new_file_path)}")
                return True
            except Exception as err:
                messagebox.showerror("Save As Error", f"Couldn't save as new file: {err}")
                self.update_status_info("Error saving as new file.")
                return False
        return False # User cancelled the "Save As" dialog

    def quit_editor(self):
        """
        Handles exiting the editor. Asks to save any unsaved changes.
        """
        # Check if there's any text in the editor that might need saving
        if self.text_area.get(1.0, tk.END).strip():
            if messagebox.askyesno("Exit Confirmation", "You have unsaved work. Would you like to save before quitting?"):
                if not self.save_current_file(): # Try to save; if user cancels, don't exit
                    return

        self.master.destroy() # This closes the main window and ends the program

    def update_status_info(self, custom_message=None):
        """
        Updates the status bar with real-time information like word count and character count.
        Can also display a temporary custom message.
        """
        # Get all the text from the editor, removing leading/trailing whitespace
        all_text_in_editor = self.text_area.get(1.0, tk.END).strip()

        # Calculate word count: split by spaces, but handle empty text gracefully
        words_count = len(all_text_in_editor.split()) if all_text_in_editor else 0
        # Calculate character count (excluding extra whitespace from strip)
        characters_count = len(all_text_in_editor)

        # Prepare the text for the status bar
        display_text = f"Words: {words_count} | Characters: {characters_count}"
        if custom_message:
            display_text = f"{custom_message} | {display_text}"

        self.status_bar.config(text=display_text)


# --- This is the part that runs when you start the script ---
if __name__ == "__main__":
    main_root_window = tk.Tk() # Create the very first window for our application
    my_editor_app = SimpleTextEditor(main_root_window) # Create an instance of our editor class
    main_root_window.mainloop() # Start the Tkinter event loop - this keeps the window open and responsive


import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import zipfile
from datetime import datetime
import ctypes

class ZipApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Zipper")

        # Disable minimize and maximize buttons
        self.root.resizable(False, False)

        # Set the source directory to \Net Attendance Manager\
        self.source_dir = "Net Attendance Manager"

        # Set the save directory to \Net Attendance Manager\Past Rosters\
        self.save_dir = os.path.join(self.source_dir, "Past Rosters")

        # Frame the entire app
        self.frame = tk.Frame(root, bg="lightgray")  # Added background color for visibility
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # List to store selected files
        self.files = []

        # Create Menu Bar
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        # Create File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Add Files", command=self.add_files)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # Create Help Menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.help_menu.add_command(label="User Manual", command=self.show_user_manual)

        # Create GUI elements
        self.label = tk.Label(self.frame, text="Select files to zip:", bg="lightgray")
        self.label.pack(pady=10)

        self.file_listbox = tk.Listbox(self.frame, selectmode=tk.MULTIPLE, width=80, height=20)  # Increased width and height
        self.file_listbox.pack(pady=10)

        self.remove_button = tk.Button(self.frame, text="Remove Selected", command=self.remove_files)
        self.remove_button.pack(pady=5)

        self.zip_button = tk.Button(self.frame, text="Zip Files", command=self.zip_files)
        self.zip_button.pack(pady=20)

    def add_files(self):
        # Open file dialog to select multiple files from the source directory
        file_paths = filedialog.askopenfilenames(title="Select Files to Zip", initialdir=self.source_dir)
        if file_paths:
            for file_path in file_paths:
                self.files.append(file_path)
                self.file_listbox.insert(tk.END, file_path)

    def remove_files(self):
        # Remove selected files from the list
        selected_indices = self.file_listbox.curselection()
        for index in reversed(selected_indices):
            self.files.pop(index)
            self.file_listbox.delete(index)

    def zip_files(self):
        if not self.files:
            messagebox.showwarning("No Files", "Please select files to zip.")
            return

        # Get current month and year
        now = datetime.now()
        month_year = now.strftime("%B_%Y")
        default_filename = f"Roll_Call_Net_archive_{month_year}.zip"

        # Ask for the zip file name and location
        zip_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip files", "*.zip")], title="Save Zip File As", initialdir=self.save_dir, initialfile=default_filename)
        if not zip_path:
            return

        # Create a new zip file and add selected files to it
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in self.files:
                zipf.write(file, os.path.basename(file))

        messagebox.showinfo("Success", f"Files zipped successfully to {zip_path}")

        # Prompt user to delete source files
        delete_files = messagebox.askyesno("Delete Source Files", "Do you want to delete the source files?")
        if delete_files:
            for file in self.files:
                try:
                    os.remove(file)
                    self.file_listbox.delete(tk.ANCHOR)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete file {file}: {e}")

    def show_about(self):
        about_text = (
            "File Zipper Application\n"
            "Version 1.0\n"
            "This application allows you to select multiple files and zip them into a single archive.\n"
            "User Guide:\n"
            "1. Use 'File' -> 'Add Files' to select files.\n"
            "2. Use 'Remove Selected' to remove files from the list.\n"
            "3. Use 'Zip Files' to create a zip archive.\n"
            "4. Use 'File' -> 'Exit' to close the application.\n"
            "5. Use 'Help' -> 'About' to view this guide.\n"
            "6. Use 'Help' -> 'User Manual' to view the user manual."
        )
        messagebox.showinfo("About", about_text)

    def show_user_manual(self):
        user_manual_text = (
            "User Manual\n"
            "------------\n"
            "1. Adding Files:\n"
            "   - Click 'File' -> 'Add Files' to open a file dialog.\n"
            "   - Select multiple files to add to the list.\n"
            "2. Removing Files:\n"
            "   - Select files in the list and click 'Remove Selected' to remove them.\n"
            "3. Zipping Files:\n"
            "   - Click 'Zip Files' to create a zip archive.\n"
            "   - The default file name will be 'Roll_Call_Net_archive_Month_Year.zip'.\n"
            "   - The zip file will be saved in the 'Past Rosters' subdirectory.\n"
            "4. Deleting Source Files:\n"
            "   - After zipping, you will be prompted to delete the source files.\n"
            "   - Click 'Yes' to delete or 'No' to keep the files.\n"
            "5. Exiting the Application:\n"
            "   - Click 'File' -> 'Exit' to close the application.\n"
            "6. Viewing Help:\n"
            "   - Click 'Help' -> 'About' to view the about information.\n"
            "   - Click 'Help' -> 'User Manual' to view this user manual."
        )
        user_manual_window = tk.Toplevel(self.root)
        user_manual_window.title("User Manual")
        user_manual_text_area = scrolledtext.ScrolledText(user_manual_window, wrap=tk.WORD, width=80, height=20)
        user_manual_text_area.insert(tk.INSERT, user_manual_text)
        user_manual_text_area.pack(pady=10)

if __name__ == "__main__":
    # Minimize console window on Windows
    if os.name == 'nt':
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)

    root = tk.Tk()
    app = ZipApp(root)
    root.mainloop()
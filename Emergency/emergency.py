import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from datetime import datetime
import subprocess

# Set the working directory
current_drive = os.path.splitdrive(os.getcwd())[0]
os.chdir(os.path.join(current_drive, r'\Net Attendance Manager\Emergency'))

# Function to create CSV files if they don't exist and are empty
def create_csv_files():
    net_control_contacts_file = "Net Control Contacts.csv"
    emergency_contacts_file = "Emergency Contacts.csv"
    emergency_information_file = "Emergency Information.csv"

    # Create Net Control Contacts.csv if it doesn't exist and is empty
    if not os.path.exists(net_control_contacts_file) or os.path.getsize(net_control_contacts_file) == 0:
        with open(net_control_contacts_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Call Sign", "QTH", "Name", "Phone Number", "Capabilities", "Contacted"])
            writer.writerow(["KL2MF", "WASILLA", "ED", "123-456-7890", "12345", "Yes"])
            writer.writerow(["N7FXX", "PALMER", "CLAUDE", "123-456-7890", "12345", "Yes"])
            writer.writerow(["KL7EDK", "FAIRBANKS", "JERRY", "123-456-7890", "12345", "Yes"])
            writer.writerow(["WL7PM", "HOMER", "DEAN", "123-456-7890", "12345", "Yes"])

    # Create Emergency Contacts.csv if it doesn't exist and is empty
    if not os.path.exists(emergency_contacts_file) or os.path.getsize(emergency_contacts_file) == 0:
        with open(emergency_contacts_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Contact Number", "Current Location", "Type of Emergency", "Contacted"])
            writer.writerow(["Dr. Emily Clark", "222-333-4444", "Hospital A", "Medical", "No"])
            writer.writerow(["Officer James Wilson", "333-444-5555", "Police Station B", "Security", "No"])
            writer.writerow(["Firefighter Michael Lee", "444-555-6666", "Fire Station C", "Fire", "No"])
            writer.writerow(["Paramedic Sarah Davis", "555-666-7777", "Ambulance D", "Medical", "No"])

    # Create Emergency Information.csv if it doesn't exist and is empty
    if not os.path.exists(emergency_information_file) or os.path.getsize(emergency_information_file) == 0:
        with open(emergency_information_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Type of Emergency", "Location", "Contact Number", "Description", "Start Time", "End Time", "Date"])

# Call the function to create the CSV files if needed
create_csv_files()

class EmergencyInformationCollector:
    def __init__(self, root):
        self.root = root
        self.root.title("Emergency Information Collector")
        self.changed = False  # Flag to track unsaved changes

        self.frame = tk.Frame(self.root, borderwidth=2, relief="groove", bg="#A3071B")
        self.frame.pack(fill="both", expand=True)

        self.create_toolbar()
        self.create_widgets()
        self.center_view()
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)

        self.start_time = None
        self.end_time = None

        # Initialize data structures
        self.net_control_contacts_data = []
        self.emergency_contacts_data = []
        self.emergency_information_data = []

        # Load initial data from CSV files
        self.load_net_control_contacts()
        self.load_emergency_contacts()
        self.load_emergency_information()

    def create_toolbar(self):
        toolbar = tk.Frame(self.frame, bg="lightgrey")
        toolbar.pack(side="top", fill="x")
        add_emergency_info_button = tk.Button(toolbar, text="Add New Emergency Information", fg='red',
                                              command=self.add_new_emergency_information)
        add_emergency_info_button.pack(side="left", padx=5, pady=5)
        self.clock_label = tk.Label(toolbar, text="", font=("Arial", 12))
        self.clock_label.pack(side="right", padx=5, pady=5)
        self.update_clock()
        self.date_label = tk.Label(toolbar, text="", font=("Arial", 12))
        self.date_label.pack(side="right", padx=5, pady=5)
        self.update_date()

    def create_widgets(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Emergency Information", command=self.open_emergency_information)
        file_menu.add_command(label="Save Emergency Information", command=self.save_emergency_information)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.confirm_exit)
        options_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Options", menu=options_menu)
        options_menu.add_command(label="Add New Net Control Contact", command=self.add_new_net_control_contact)
        options_menu.add_command(label="Add New Emergency Contact", command=self.add_new_emergency_contact)

        net_control_frame = tk.Frame(self.frame)
        net_control_frame.pack(side="top", fill="both", expand=True)
        net_control_label = tk.Label(net_control_frame, text="Net Control Contacts", font=("Arial", 12))
        net_control_label.pack(side="top", pady=5)
        self.net_control_contacts_tree = ttk.Treeview(net_control_frame, columns=["Call Sign", "QTH", "Name", "Phone Number", "Capabilities", "Contacted"], show="headings")
        self.net_control_contacts_tree.pack(side="top", fill="both", expand=True)
        self.set_treeview_headings(self.net_control_contacts_tree, ["Call Sign", "QTH", "Name", "Phone Number", "Capabilities", "Contacted"])
        self.load_net_control_contacts()
        self.net_control_contacts_tree.bind('<ButtonRelease-1>', self.on_net_control_click)

        emergency_contacts_frame = tk.Frame(self.frame)
        emergency_contacts_frame.pack(side="top", fill="both", expand=True)
        emergency_contacts_label = tk.Label(emergency_contacts_frame, text="Emergency Contacts", font=("Arial", 12))
        emergency_contacts_label.pack(side="top", pady=5)
        self.emergency_contacts_tree = ttk.Treeview(emergency_contacts_frame, columns=["Name", "Contact Number", "Current Location", "Type of Emergency", "Contacted"], show="headings")
        self.emergency_contacts_tree.pack(side="top", fill="both", expand=True)
        self.set_treeview_headings(self.emergency_contacts_tree, ["Name", "Contact Number", "Current Location", "Type of Emergency", "Contacted"])
        self.load_emergency_contacts()
        self.emergency_contacts_tree.bind('<ButtonRelease-1>', self.on_emergency_contact_click)

        emergency_info_frame = tk.Frame(self.frame)
        emergency_info_frame.pack(side="top", fill="both", expand=True)
        emergency_info_label = tk.Label(emergency_info_frame, text="Emergency Information", font=("Arial", 12))
        emergency_info_label.pack(side="top", pady=5)
        self.emergency_info_tree = ttk.Treeview(emergency_info_frame, columns=["Name", "Type of Emergency", "Location", "Contact Number", "Description", "Start Time", "End Time", "Date"], show="headings")
        self.emergency_info_tree.pack(side="top", fill="both", expand=True)
        self.set_treeview_headings(self.emergency_info_tree, ["Name", "Type of Emergency", "Location", "Contact Number", "Description", "Start Time", "End Time", "Date"])
        self.load_emergency_information()

    def set_treeview_headings(self, treeview, headings):
        for col in headings:
            treeview.heading(col, text=col)
            treeview.column(col, width=100, anchor='center')

    def load_net_control_contacts(self):
        self.net_control_contacts_tree.delete(*self.net_control_contacts_tree.get_children())
        try:
            with open("Net Control Contacts.csv", "r") as file:
                reader = csv.reader(file)
                next(reader)
                self.net_control_contacts_data = list(reader)
                for row in self.net_control_contacts_data:
                    self.net_control_contacts_tree.insert("", "end", values=row)
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "Net Control Contacts.csv not found.")

    def load_emergency_contacts(self):
        self.emergency_contacts_tree.delete(*self.emergency_contacts_tree.get_children())
        try:
            with open("Emergency Contacts.csv", "r") as file:
                reader = csv.reader(file)
                next(reader)
                self.emergency_contacts_data = list(reader)
                for row in self.emergency_contacts_data:
                    self.emergency_contacts_tree.insert("", "end", values=row)
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "Emergency Contacts.csv not found.")

    def load_emergency_information(self):
        self.emergency_info_tree.delete(*self.emergency_info_tree.get_children())
        try:
            with open("Emergency Information.csv", "r") as file:
                reader = csv.reader(file)
                next(reader)
                self.emergency_information_data = list(reader)
                for row in self.emergency_information_data:
                    while len(row) < 8:
                        row.append("")
                    self.emergency_info_tree.insert("", "end", values=row)
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "Emergency Information.csv not found.")

    def open_emergency_information(self):
        file_path = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.emergency_info_tree.delete(*self.emergency_info_tree.get_children())
            with open(file_path, "r") as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    while len(row) < 8:
                        row.append("")
                    self.emergency_info_tree.insert("", "end", values=row)

    def save_emergency_information(self):
        if self.changed:
            response = messagebox.askyesno("Confirm Save", "Do you want to save the changes?")
            if response:
                items = self.emergency_info_tree.get_children()
                if items:
                    first_item = items[0]
                    name = self.emergency_info_tree.item(first_item, "values")[0]
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    file_name = f"{name}_{current_date}.csv"
                    file_path = filedialog.asksaveasfilename(initialfile=file_name, defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
                    if file_path:
                        self.end_time = datetime.now().strftime("%H:%M:%S")
                        with open(file_path, "w", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow(["Name", "Type of Emergency", "Location", "Contact Number", "Description", "Start Time", "End Time", "Date"])
                            for item in self.emergency_info_tree.get_children():
                                values = list(self.emergency_info_tree.item(item, "values"))
                                values[6] = self.end_time  # Update the end time
                                writer.writerow(values)
                        self.changed = False  # Reset changed flag
                else:
                    messagebox.showwarning("No Data", "No emergency information to save.")
        else:
            messagebox.showinfo("No Changes", "No changes to save.")

    def add_new_net_control_contact(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Net Control Contact")
        tk.Label(dialog, text="Call Sign:").grid(row=0, column=0)
        call_sign_entry = tk.Entry(dialog)
        call_sign_entry.grid(row=0, column=1)
        tk.Label(dialog, text="QTH:").grid(row=1, column=0)
        qth_entry = tk.Entry(dialog)
        qth_entry.grid(row=1, column=1)
        tk.Label(dialog, text="Name:").grid(row=2, column=0)
        name_entry = tk.Entry(dialog)
        name_entry.grid(row=2, column=1)
        tk.Label(dialog, text="Phone Number:").grid(row=3, column=0)
        phone_entry = tk.Entry(dialog)
        phone_entry.grid(row=3, column=1)
        tk.Label(dialog, text="Capabilities:").grid(row=4, column=0)
        capabilities_entry = tk.Entry(dialog)
        capabilities_entry.grid(row=4, column=1)
        tk.Label(dialog, text="Contacted:").grid(row=5, column=0)
        contacted_entry = tk.Entry(dialog)
        contacted_entry.insert(0, "No")
        contacted_entry.grid(row=5, column=1)
        def submit():
            call_sign = call_sign_entry.get()
            qth = qth_entry.get()
            name = name_entry.get()
            phone = phone_entry.get()
            capabilities = capabilities_entry.get()
            contacted = contacted_entry.get()
            self.net_control_contacts_tree.insert("", "end", values=[call_sign, qth, name, phone, capabilities, contacted])
            self.net_control_contacts_data.append([call_sign, qth, name, phone, capabilities, contacted])
            dialog.destroy()
            self.changed = True  # Set changed flag
        tk.Button(dialog, text="Submit", command=submit).grid(row=6, column=0, columnspan=2)

    def add_new_emergency_contact(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Emergency Contact")
        tk.Label(dialog, text="Name:").grid(row=0, column=0)
        name_entry = tk.Entry(dialog)
        name_entry.grid(row=0, column=1)
        tk.Label(dialog, text="Contact Number:").grid(row=1, column=0)
        contact_entry = tk.Entry(dialog)
        contact_entry.grid(row=1, column=1)
        tk.Label(dialog, text="Current Location:").grid(row=2, column=0)
        location_entry = tk.Entry(dialog)
        location_entry.grid(row=2, column=1)
        tk.Label(dialog, text="Type of Emergency:").grid(row=3, column=0)
        emergency_entry = tk.Entry(dialog)
        emergency_entry.grid(row=3, column=1)
        tk.Label(dialog, text="Contacted:").grid(row=4, column=0)
        contacted_entry = tk.Entry(dialog)
        contacted_entry.insert(0, "No")
        contacted_entry.grid(row=4, column=1)
        def submit():
            name = name_entry.get()
            contact = contact_entry.get()
            location = location_entry.get()
            emergency = emergency_entry.get()
            contacted = contacted_entry.get()
            self.emergency_contacts_tree.insert("", "end", values=[name, contact, location, emergency, contacted])
            self.emergency_contacts_data.append([name, contact, location, emergency, contacted])
            dialog.destroy()
            self.changed = True  # Set changed flag
        tk.Button(dialog, text="Submit", command=submit).grid(row=5, column=0, columnspan=2)

    def add_new_emergency_information(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Emergency Information")
        tk.Label(dialog, text="Name:").grid(row=0, column=0)
        name_entry = tk.Entry(dialog)
        name_entry.grid(row=0, column=1)
        tk.Label(dialog, text="Type of Emergency:").grid(row=1, column=0)
        type_entry = tk.Entry(dialog)
        type_entry.grid(row=1, column=1)
        tk.Label(dialog, text="Location:").grid(row=2, column=0)
        location_entry = tk.Entry(dialog)
        location_entry.grid(row=2, column=1)
        tk.Label(dialog, text="Contact Number:").grid(row=3, column=0)
        contact_entry = tk.Entry(dialog)
        contact_entry.grid(row=3, column=1)
        tk.Label(dialog, text="Description:").grid(row=4, column=0)
        description_entry = tk.Entry(dialog)
        description_entry.grid(row=4, column=1)
        
        self.start_time = datetime.now().strftime("%H:%M:%S")
        
        def submit():
            name = name_entry.get()
            type_of_emergency = type_entry.get()
            location = location_entry.get()
            contact_number = contact_entry.get()
            description = description_entry.get()
            current_date = datetime.now().strftime("%Y-%m-%d")
            self.emergency_info_tree.insert("", "end", values=[name, type_of_emergency, location, contact_number, description, self.start_time, "", current_date])
            self.emergency_information_data.append([name, type_of_emergency, location, contact_number, description, self.start_time, "", current_date])
            dialog.destroy()
            self.changed = True  # Set changed flag
        tk.Button(dialog, text="Submit", command=submit).grid(row=5, column=0, columnspan=2)

    def confirm_exit(self):
        if self.changed:
            response = messagebox.askyesnocancel("Save Changes", "There are unsaved changes. Do you want to save them before exiting?")
            if response is None:
                return  # Cancel
            elif response:
                self.save_emergency_information()
                self.root.destroy()
            else:
                self.root.destroy()
        else:
            self.root.destroy()

    def center_view(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def update_clock(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)

    def update_date(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.date_label.config(text=current_date)
        self.root.after(60000, self.update_date)

    def on_net_control_click(self, event):
        item = self.net_control_contacts_tree.selection()
        if item:
            item = item[0]
            values = self.net_control_contacts_tree.item(item, "values")
            try:
                contacted = values[5]
                new_contacted = "No" if contacted == "Yes" else "Yes"
                response = messagebox.askyesno("Toggle Contacted Status", f"Change 'Contacted' from '{contacted}' to '{new_contacted}'?")
                if response:
                    self.net_control_contacts_tree.set(item, column="Contacted", value=new_contacted)
                    self.net_control_contacts_data[self.net_control_contacts_tree.index(item)][5] = new_contacted
                    self.changed = True  # Set changed flag
            except IndexError:
                print("IndexError: Row does not have enough columns.")
            except Exception as e:
                print(f"An error occurred: {e}")

    def on_emergency_contact_click(self, event):
        item = self.emergency_contacts_tree.selection()
        if item:
            item = item[0]
            values = self.emergency_contacts_tree.item(item, "values")
            try:
                contacted = values[4]
                new_contacted = "No" if contacted == "Yes" else "Yes"
                response = messagebox.askyesno("Toggle Contacted Status", f"Change 'Contacted' from '{contacted}' to '{new_contacted}'?")
                if response:
                    self.emergency_contacts_tree.set(item, column="Contacted", value=new_contacted)
                    self.emergency_contacts_data[self.emergency_contacts_tree.index(item)][4] = new_contacted
                    self.changed = True  # Set changed flag
            except IndexError:
                print("IndexError: Row does not have enough columns.")
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EmergencyInformationCollector(root)
    root.mainloop()

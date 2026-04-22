import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from datetime import datetime
import csv
import re
import ctypes
import subprocess


class DataBaseUtility:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Base Utility")

        # Create a frame to wrap the entire app with a border
        self.frame = tk.Frame(self.root, borderwidth=2, relief="groove")
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.columns = ["Call Sign", "QTH", "Name", "Status", "Relayed", "Traffic", "Sweep?", "This Month"]
        self.data = []
        self.unsaved_changes = False
        self.status_counts = {"Absent": 0, "Present": 0, "Excused": 0}
        self.total_call_sign_count = 0
        self.time_start = None
        self.time_end = None
        self.net_control = ""
        self.attendance = {name: {} for name in ["Person 1", "Person 2", "Person 3", "Person 4"]}
        self.alaska_towns = self.load_regions_from_csv('regions.csv')
        self.preamble_text = self.load_preamble_from_csv('preamble.csv')
        self.visitor_count = 0  # Initialize the visitor count
        self.current_net_name = ""  # Initialize the current net name
        self.loaded_header = None  # Initialize the loaded header
        self.loaded_file_name = ""  # Initialize the loaded file name

        self.create_widgets()
        self.center_view()
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)

        self.present_today = set()

        # Turn on Caps Lock when the app starts
        self.turn_caps_lock_on()

        # Minimize the command window when the app starts
        self.minimize_command_window()

        # Initialize dark mode state
        self.dark_mode = False
        self.style = ttk.Style()
        self.update_style()

    def load_regions_from_csv(self, file_path):
        regions = {}
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                regions[row['City']] = row['Region']
        return regions

    def load_preamble_from_csv(self, file_path):
        preamble_text = ""
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            if rows:
                first_line = rows[0][0]
                if first_line != "BLANK":
                    self.current_net_name = first_line
                else:
                    # Skip setting current_net_name if first line is "BLANK"
                    self.current_net_name = ""
                for row in rows[1:]:
                    preamble_text += " ".join(row) + "\n"
        return preamble_text.strip()

    def generate_row(self, i):
        return ["", "", "", "Absent", "", "", "", "0"]

    def create_widgets(self):
        self.create_menu_bar()
        self.create_top_frame()
        self.create_tree_view()
        self.create_stats_view()
        self.create_sweepers_view()

    def create_menu_bar(self):
        menu_frame = tk.Frame(self.frame)
        menu_frame.grid(row=0, column=0, sticky="ew")

        menu_bar = tk.Menu(menu_frame)
        self.root.config(menu=menu_bar)

        self.create_file_menu(menu_bar)
        self.create_options_menu(menu_bar)

    def create_file_menu(self, menu_bar):
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        
        # Add Data Management Menu
        data_management_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Data Management", menu=data_management_menu)
        data_management_menu.add_command(label="Create Monthly Roster", command=self.create_monthly_roster)
        data_management_menu.add_command(label="Archive Monthly Roster", command=self.archive_monthly_roster)
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.confirm_exit)

    def create_options_menu(self, menu_bar):
        options_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Options", menu=options_menu)
        
        self.font_size_var = tk.StringVar(value="Small")
        font_size_menu = tk.Menu(options_menu, tearoff=0)
        options_menu.add_cascade(label="Font Size", menu=font_size_menu)
        font_size_menu.add_checkbutton(label="Small", variable=self.font_size_var, onvalue="Small", offvalue="Medium", command=lambda: self.change_font_size(self.font_size_var.get()))
        font_size_menu.add_checkbutton(label="Medium", variable=self.font_size_var, onvalue="Medium", offvalue="Small", command=lambda: self.change_font_size(self.font_size_var.get()))
        font_size_menu.add_checkbutton(label="Large", variable=self.font_size_var, onvalue="Large", offvalue="Medium", command=lambda: self.change_font_size(self.font_size_var.get()))

        # Add "Preamble" submenu
        preamble_menu = tk.Menu(options_menu, tearoff=0)
        options_menu.add_cascade(label="Preamble", menu=preamble_menu)
        preamble_menu.add_command(label="Roll Call Net", command=lambda: self.load_preamble_and_set("PreambleRollCallNet.csv"))  # New command
        preamble_menu.add_command(label="Open Net", command=lambda: self.load_preamble_and_set("PreambleOpenNet.csv"))

        # Add "Net Type" submenu
        net_type_menu = tk.Menu(options_menu, tearoff=0)
        options_menu.add_cascade(label="Net Type", menu=net_type_menu)
        net_type_menu.add_command(label="Roll Call Net", command=self.start_roll_call_net)
        net_type_menu.add_command(label="Open Net", command=self.start_open_net)

        # Add dark mode toggle
        options_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)

    def start_roll_call_net(self):
        net_name = simpledialog.askstring("Input", "Enter Roll Call Net Name:")
        if net_name:
            self.current_net_name = net_name
            messagebox.showinfo("Net Type", f"Roll Call Net selected: {self.current_net_name}")
        else:
            messagebox.showwarning("Net Type", "Roll Call Net name not set.")

    def start_open_net(self):
        net_name = simpledialog.askstring("Input", "Enter Open Net Name:")
        if net_name:
            self.current_net_name = net_name
            messagebox.showinfo("Net Type", f"Open Net selected: {self.current_net_name}")
        else:
            messagebox.showwarning("Net Type", "Open Net name not set.")

    def create_top_frame(self):
        top_frame = tk.Frame(self.frame)
        top_frame.grid(row=0, column=0, sticky="ew")

        self.search_button = tk.Button(top_frame, text="Search", command=self.search_table)
        self.search_button.pack(side="left", padx=(5, 10))

        self.refresh_button = tk.Button(top_frame, text="Refresh", command=self.refresh_table)
        self.refresh_button.pack(side="left", padx=(5, 10))

        self.reset_button = tk.Button(top_frame, text="Reset", command=self.reset_table)
        self.reset_button.pack(side="left", padx=(5, 10))

        self.results_label = tk.Label(top_frame, text="", font=("Arial", 10))
        self.results_label.pack(side="left", padx=(5, 10))

    def create_tree_view(self):
        self.tree = ttk.Treeview(self.frame, columns=self.columns, show="headings", height=14)
        self.tree.grid(row=1, column=0, sticky="nsew")

        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            if col == "QTH":  # Column 2 (index 1)
                self.tree.column(col, width=150, anchor='center')  # Increased width
            elif col == "Traffic":  # Column 6 (index 5)
                self.tree.column(col, width=150, anchor='center')  # Increased width
            else:
                self.tree.column(col, width=100, anchor='center')

        self.tree.bind("<Button-1>", self.handle_click)
        self.tree.bind("<Double-1>", self.handle_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Up>", self.scroll_up)
        self.tree.bind("<Down>", self.scroll_down)
        self.tree.bind("<Tab>", self.handle_tab)

        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=1, sticky="ns")

        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Insert row above", command=lambda: self.modify_row('insert_above'))
        self.context_menu.add_command(label="Insert row below", command=lambda: self.modify_row('insert_below'))
        self.context_menu.add_command(label="Delete row", command=self.delete_row)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy row", command=self.copy_row)
        self.context_menu.add_command(label="Paste row", command=self.paste_row)

        self.sort_menu = tk.Menu(self.frame, tearoff=0)
        self.sort_menu.add_command(label="Sort Ascending", command=lambda: self.sort_column(self.columns[0], ascending=True))
        self.sort_menu.add_command(label="Sort Descending", command=lambda: self.sort_column(self.columns[0], ascending=False))

    def create_stats_view(self):
        self.stats_label = tk.Label(self.frame, text="Stats", font=("Arial", 12))
        self.stats_label.grid(row=3, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.stats_text_view = tk.Text(self.frame, height=12, width=50, font=("Arial", 10))  # Increased height to 12
        self.stats_text_view.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        self.stats_text_view.config(state=tk.DISABLED)

    def create_sweepers_view(self):
        self.sweepers_label = tk.Label(self.frame, text="Sweepers", font=("Arial", 12))
        self.sweepers_label.grid(row=5, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.sweepers_tree = ttk.Treeview(self.frame, columns=["Call Sign", "QTH", "Name", "Region"], show="headings", height=5)
        self.sweepers_tree.grid(row=6, column=0, sticky="nsew", padx=10, pady=10)
        self.sweepers_tree.heading("Call Sign", text="Call Sign")
        self.sweepers_tree.heading("QTH", text="QTH")
        self.sweepers_tree.heading("Name", text="Name")
        self.sweepers_tree.heading("Region", text="Region")
        self.sweepers_tree.column("Call Sign", width=100, anchor='center')
        self.sweepers_tree.column("QTH", width=100, anchor='center')
        self.sweepers_tree.column("Name", width=100, anchor='center')
        self.sweepers_tree.column("Region", width=100, anchor='center')

        self.sweepers_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.sweepers_tree.yview)
        self.sweepers_tree.configure(yscrollcommand=self.sweepers_scrollbar.set)
        self.sweepers_scrollbar.grid(row=6, column=1, sticky="ns")

        self.sweepers_context_menu = tk.Menu(self.frame, tearoff=0)
        self.sweepers_context_menu.add_command(label="Clear Sweepers List", command=self.clear_sweepers_list)
        self.sweepers_context_menu.add_command(label="Delete Sweeper", command=self.delete_sweeper)

        self.sweepers_tree.bind("<Button-3>", self.show_sweepers_context_menu)

    def show_context_menu(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            col = self.tree.identify_column(event.x)
            if col == "#1":
                self.sort_menu.post(event.x_root, event.y_root)
        else:
            self.context_menu.post(event.x_root, event.y_root)

    def show_sweepers_context_menu(self, event):
        self.sweepers_context_menu.post(event.x_root, event.y_root)

    def handle_click(self, event):
        if not self.tree.get_children():
            messagebox.showwarning("No Data", "Please load data first.")
            return

        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            col = self.tree.identify_column(event.x)
            if col in ["#1", "#2", "#3"]:
                self.sort_column(self.columns[int(col[1:]) - 1])
            return
        col = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)

        if col == "#4":
            self.update_status_cell(item, "Present")
        elif col == "#5":
            self.handle_relayed_click(item)
        elif col == "#6":
            self.handle_traffic_click(item)
        elif col == "#7":
            self.handle_sweep_click(item)
        elif col == "#8":
            self.handle_this_month_click(item)

    def handle_double_click(self, event):
        if not self.tree.get_children():
            messagebox.showwarning("No Data", "Please load data first.")
            return

        col = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)

        if col in ["#1", "#2", "#3"]:
            self.edit_cell(item, col)
        elif col == "#4":
            self.update_status_cell(item, "Excused")
        elif col == "#8":
            self.edit_this_month_cell(item)

    def update_status_cell(self, item, new_value):
        values = list(self.tree.item(item, "values"))
        old_status = values[3]
        values[3] = new_value
        self.tree.item(item, values=values)
        self.unsaved_changes = True

        self.update_status_counts(old_status, new_value)

        if new_value == "Present":
            call_sign = values[0]
            if call_sign not in self.present_today:
                self.present_today.add(call_sign)
                this_month = int(values[7]) if values[7].isdigit() else 0
                this_month += 1
                values[7] = str(this_month)
                self.tree.item(item, values=values)

            # Check if the "Name" contains a "/"
            name = values[2]
            if "/" in name:
                names = name.split("/")
                # Increment the "Present" count by the number of names split by "/"
                self.status_counts["Present"] += len(names) - 1
                for name in names:
                    self.record_attendance(name.strip(), datetime.now().day, new_value)
            else:
                self.record_attendance(name, datetime.now().day, new_value)

            # Increment visitor count if QTH and NAME are both "VISITOR"
            if values[1] == "VISITOR" and values[2] == "VISITOR":
                self.visitor_count += 1

        next_item = self.tree.next(item)
        if next_item:
            self.tree.focus(next_item)
            self.tree.selection_set(next_item)

        self.update_results_label("Status updated")
        self.record_attendance(values[2], datetime.now().day, new_value)

    def handle_sweep_click(self, item):
        values = list(self.tree.item(item, "values"))
        if values[6] == "Yes":
            # Clear the cell and remove the corresponding entry from the Sweepers tree
            values[6] = ""
            self.tree.item(item, values=values)
            self.unsaved_changes = True
            self.remove_from_sweepers_tree(values[0])
        else:
            # Update the cell to "Yes" and add the corresponding entry to the Sweepers tree
            self.update_sweep_cell(item, "Yes")

    def remove_from_sweepers_tree(self, call_sign):
        for item in self.sweepers_tree.get_children():
            if self.sweepers_tree.item(item, "values")[0] == call_sign:
                self.sweepers_tree.delete(item)
                self.update_results_label("Sweeper removed.")
                break

    def update_sweep_cell(self, item, sweep_input):
        values = list(self.tree.item(item, "values"))
        values[6] = sweep_input
        self.tree.item(item, values=values)
        self.unsaved_changes = True

        if values[3] == "":
            self.update_status_cell(item, "Present")

        next_item = self.tree.next(item)
        if next_item:
            self.tree.focus(next_item)
            self.tree.selection_set(next_item)

        self.update_sweepers_tree(values[0])

    def update_sweepers_tree(self, call_sign):
        qth = self.get_qth_for_call_sign(call_sign)
        name = self.get_name_for_call_sign(call_sign)
        region = self.alaska_towns.get(qth, "Unknown")

        for item in self.sweepers_tree.get_children():
            if self.sweepers_tree.item(item, "values")[0] == call_sign:
                self.sweepers_tree.item(item, values=(call_sign, qth, name, region))
                return

        self.sweepers_tree.insert("", "end", values=(call_sign, qth, name, region))

    def get_qth_for_call_sign(self, call_sign):
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[0] == call_sign:
                return values[1].upper()
        return "Unknown"

    def get_name_for_call_sign(self, call_sign):
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[0] == call_sign:
                return values[2]
        return "Unknown"

    def handle_relayed_click(self, item):
        relayed_input = simpledialog.askstring("Input", "Enter Name or US Amateur Call Sign:")
        if relayed_input:
            self.update_relayed_cell(item, relayed_input)

    def update_relayed_cell(self, item, relayed_input):
        values = list(self.tree.item(item, "values"))
        if relayed_input != "0":
            values[4] = relayed_input
            self.tree.item(item, values=values)
            self.unsaved_changes = True

        if self.call_sign_exists(relayed_input):
            next_item = self.tree.next(item)
            if next_item:
                self.tree.focus(next_item)
                self.tree.selection_set(next_item)

    def call_sign_exists(self, call_sign):
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[0] == call_sign:
                return True
        return False

    def modify_row(self, action):
        selected_item = self.tree.selection()
        if selected_item:
            index = self.tree.index(selected_item)
            if action == 'insert_above':
                self.tree.insert("", index, values=self.generate_row(index))
            elif action == 'insert_below':
                self.tree.insert("", index + 1, values=self.generate_row(index + 1))
            self.total_call_sign_count += 1
            self.unsaved_changes = True
            self.apply_separator_style()

    def delete_row(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)
            self.total_call_sign_count -= 1
            self.unsaved_changes = True
            self.apply_separator_style()

    def copy_row(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.copied_row = self.tree.item(selected_item, "values")

    def paste_row(self):
        if hasattr(self, 'copied_row'):
            selected_item = self.tree.selection()
            if selected_item:
                index = self.tree.index(selected_item) + 1
                self.tree.insert("", index, values=self.copied_row)
                self.unsaved_changes = True
                self.apply_separator_style()

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            try:
                self.data = []
                self.tree.delete(*self.tree.get_children())
                self.sweepers_tree.delete(*self.sweepers_tree.get_children())
                self.visitor_count = 0  # Reset the visitor count
                with open(file_path, "r") as file:
                    reader = csv.reader(file)
                    self.loaded_header = next(reader)  # Store the header
                    # Check if the header matches the special header
                    if self.loaded_header == ["Time Start", "Time End", "Total Present", "Current Net Name", "Total Excused", "Net Control"]:
                        additional_data = next(reader)
                        self.time_start = additional_data[0]
                        self.time_end = additional_data[1]
                        self.current_net_name = additional_data[3]
                        self.status_counts["Present"] = int(additional_data[2])
                        self.status_counts["Excused"] = int(additional_data[4])
                        self.net_control = additional_data[5]
                        # Read the rest of the data as tree rows
                        for row in reader:
                            self.tree.insert("", "end", values=row)
                            # Check if "Sweep?" is "Yes" and add to Sweepers tree
                            if len(row) > 6 and row[6] == "Yes":
                                call_sign = row[0]
                                qth = row[1].upper()
                                name = row[2]
                                region = self.alaska_towns.get(qth, "Unknown")
                                self.sweepers_tree.insert("", "end", values=(call_sign, qth, name, region))
                            # Check if "Name" contains a "/" and adjust the present count
                            if len(row) > 2 and "/" in row[2] and row[3] == "Present":
                                names = row[2].split("/")
                                self.status_counts["Present"] += len(names) - 1
                            # Increment visitor count if QTH and NAME are both "VISITOR"
                            if len(row) > 1 and row[1] == "VISITOR" and len(row) > 2 and row[2] == "VISITOR":
                                self.visitor_count += 1
                    else:
                        self.status_counts = {"Absent": 0, "Present": 0, "Excused": 0}
                        for row in reader:
                            if len(row) < len(self.columns):
                                row.extend([''] * (len(self.columns) - len(row)))
                            if len(row) > 4 and row[4] == "0":
                                row[4] = ""
                            if len(row) > 3 and row[3] == "Unknown":
                                row[3] = "Absent"
                            self.tree.insert("", "end", values=row[:8])
                            if len(row) > 3 and row[3]:
                                self.update_status_counts(None, row[3])
                            if len(row) > 6 and row[6] == "Yes":
                                call_sign = row[0]
                                qth = row[1].upper()
                                name = row[2]
                                region = self.alaska_towns.get(qth, "Unknown")
                                self.sweepers_tree.insert("", "end", values=(call_sign, qth, name, region))
                            # Check if "Name" contains a "/" and adjust the present count
                            if len(row) > 2 and "/" in row[2] and row[3] == "Present":
                                names = row[2].split("/")
                                self.status_counts["Present"] += len(names) - 1
                            # Increment visitor count if QTH and NAME are both "VISITOR"
                            if len(row) > 1 and row[1] == "VISITOR" and len(row) > 2 and row[2] == "VISITOR":
                                self.visitor_count += 1
                self.unsaved_changes = False
                self.total_call_sign_count = len(self.tree.get_children())  # Set total count
                self.loaded_file_name = file_path  # Set loaded file name
                self.display_totals_and_times()
                self.apply_separator_style()
                first_item = self.tree.get_children()[0] if self.tree.get_children() else None
                if first_item:
                    values = self.tree.item(first_item, "values")
                    if len(values) > 3 and not values[3]:
                        self.tree.focus(first_item)
                        self.tree.selection_set(first_item)
            except Exception as e:
                messagebox.showerror("Open Error", f"Failed to open file: {e}")

    def save_file(self):
        now = datetime.now()
        month_str = now.strftime("%B")
        day_str = now.strftime("%d")
        year_str = now.strftime("%Y")
        default_filename = f"Roll Call Net Working {month_str} {day_str} {year_str}.csv"
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], initialfile=default_filename)
        if file_path:
            try:
                if file_path.endswith("Roll Call Net.csv"):
                    header = ["Time Start", "Time End", "Total Present", "Current Net Name", "Total Excused", "Net Control"]
                    data_to_write = [
                        [self.time_start, self.time_end, self.status_counts["Present"], self.current_net_name, self.status_counts["Excused"], self.net_control]
                    ]
                    for row in self.tree.get_children():
                        data_to_write.append(self.tree.item(row, "values"))
                    with open(file_path, "w", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow(header)
                        writer.writerows(data_to_write)
                else:
                    with open(file_path, "w", newline="") as file:
                        writer = csv.writer(file)
                        if self.loaded_header:
                            writer.writerow(self.loaded_header)
                        writer.writerow([self.time_start, self.time_end, self.status_counts["Present"], self.current_net_name, self.status_counts["Excused"], self.net_control])
                        for row in self.tree.get_children():
                            writer.writerow(self.tree.item(row, "values"))
                self.unsaved_changes = False
                self.loaded_file_name = file_path  # Set loaded file name after save
                messagebox.showinfo("Save", "Data saved successfully.")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file: {e}")

    def scroll_up(self, event):
        self.tree.yview_scroll(-1, "units")

    def scroll_down(self, event):
        self.tree.yview_scroll(1, "units")

    def center_view(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def confirm_exit(self):
        if self.unsaved_changes:
            confirm = messagebox.askyesno("Unsaved Changes", "There are unsaved changes. Do you want to save before exiting?")
            if confirm:
                self.save_file()
            else:
                self.root.quit()
        else:
            self.root.quit()

    def sort_column(self, col, ascending=True):
        # Convert column name to index
        col_idx = self.columns.index(col)
        
        data = [(self.tree.set(child, col_idx), child) for child in self.tree.get_children('')]
        
        # Sort based on the column type
        if col in ["Call Sign", "QTH", "Name"]:
            data.sort(key=lambda x: str(x[0]).lower(), reverse=not ascending)
        elif col in ["This Month"]:
            data.sort(key=lambda x: int(x[0]) if x[0].isdigit() else float('inf'), reverse=not ascending)
        else:
            data.sort(reverse=not ascending)
        
        # Rearrange the items in the treeview
        for index, (_, child) in enumerate(data):
            self.tree.move(child, '', index)
        
        # Update the heading command to toggle the sort order
        self.tree.heading(col, text=col, command=lambda: self.sort_column(col, ascending=not ascending))
        self.apply_separator_style()

    def search_table(self):
        if not self.tree.get_children():
            messagebox.showwarning("No Data", "The table is empty. Please load data first.")
            return

        search_term = simpledialog.askstring("Search", "Enter search term:")
        if not search_term:
            self.turn_caps_lock_off()
            return

        self.tree.selection_remove(*self.tree.selection())
        found = False
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if any(search_term.lower() in str(value).lower() for value in values):
                self.tree.selection_add(item)
                self.tree.focus(item)
                self.tree.see(item)
                found = True

        if not found:
            add_new = messagebox.askyesno("No Results", "No results found. Add a new row with the search query?")
            if add_new:
                new_row = self.generate_row(0)
                new_row[0] = search_term  # Set "Call Sign" column to search term
                new_row[1] = "VISITOR"    # Set "QTH" column to "VISITOR"
                new_row[2] = "VISITOR"    # Set "Name" column to "VISITOR"
                new_row[3] = "Present"    # Set "Status" to "Present"
                new_item = self.tree.insert("", 0, values=new_row)
                self.tree.focus(new_item)
                self.tree.selection_set(new_item)
                self.tree.see(new_item)
                self.tree.update_idletasks()  # Ensure the treeview is updated immediately
                self.unsaved_changes = True
                self.update_results_label(f"New row added with search query: {search_term}")
                self.apply_separator_style()

                # Increment visitor count when a new visitor is added
                self.visitor_count += 1

        self.turn_caps_lock_off()

    def update_status_counts(self, old_status, new_status):
        if old_status and old_status in self.status_counts:
            self.status_counts[old_status] -= 1
        if new_status in self.status_counts:
            self.status_counts[new_status] += 1

        self.total_call_sign_count = len(self.tree.get_children())
        self.display_totals_and_times()

    def update_results_label(self, message):
        self.results_label.config(text=message)

    def update_status_text_view(self, text):
        self.stats_text_view.config(state=tk.NORMAL)
        self.stats_text_view.delete(1.0, tk.END)
        self.stats_text_view.insert(tk.END, text)
        self.stats_text_view.config(state=tk.DISABLED)

    def display_totals_and_times(self):
        present_count = sum(1 for item in self.tree.get_children() if self.tree.item(item, "values")[3] == "Present")
        status_summary = (
            f"Roster: {self.total_call_sign_count}, "
            f"Present: {present_count}, "
            f"Excused: {self.status_counts['Excused']}, "
            f"Visitors: {self.visitor_count}"  # Add Visitors count
        )

        # Calculate totals for "Traffic", "Relayed", and "Sweep?"
        traffic_count = sum(1 for item in self.tree.get_children() if self.tree.item(item, "values")[5])
        relayed_count = sum(1 for item in self.tree.get_children() if self.tree.item(item, "values")[4])
        sweep_count = sum(1 for item in self.tree.get_children() if self.tree.item(item, "values")[6] == "Yes")

        # Calculate total time elapsed
        if self.time_start and self.time_end:
            start_time = datetime.strptime(self.time_start, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(self.time_end, "%Y-%m-%d %H:%M:%S")
            total_time = end_time - start_time
            total_time_str = str(total_time).split(".")[0]  # Remove microseconds
        else:
            total_time_str = "N/A"

        # Include the loaded file name
        loaded_file_name_str = f"Loaded File: {self.loaded_file_name}" if hasattr(self, 'loaded_file_name') else "Loaded File: N/A"

        # Check if Net Control Call Sign exists in the table data and retrieve the corresponding "Name"
        net_control_name = "N/A"
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[0] == self.net_control:
                net_control_name = values[2]
                break

        # Count unique regions
        total_regions = self.count_unique_regions()

        # Calculate the roster total, considering "/" in "Call Sign"
        roster_total = 0
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if "/" in values[0]:  # If "Call Sign" contains a "/", count as 2
                roster_total += 2
            else:
                roster_total += 1

        self.update_status_text_view(
            f"Net Control: {self.net_control} ({net_control_name})\n"
            f"Current Net: {self.current_net_name}\n"
            f"Roster: {roster_total}, Present: {present_count}, Excused: {self.status_counts['Excused']}, Visitors: {self.visitor_count}\n"
            f"Traffic: {traffic_count}\n"
            f"Relayed: {relayed_count}\n"
            f"Sweep?: {sweep_count}\n"
            f"Total Time: {total_time_str}\n"
            f"Total Regions: {total_regions}\n"
            f"Start Time: {self.time_start}\n"
            f"End Time: {self.time_end}\n"
            f"{loaded_file_name_str}"
        )

    def validate_call_sign(self, call_sign):
        if re.match(r"^[A-Z0-9]+$", call_sign):
            return call_sign
        else:
            messagebox.showerror("Invalid Call Sign", "Please enter a valid US Amateur Call Sign.")
            return None

    def handle_traffic_click(self, item):
        traffic_input = simpledialog.askstring("Input", "Enter Traffic:")
        if traffic_input:
            self.update_traffic_cell(item, traffic_input)

    def update_traffic_cell(self, item, traffic_input):
        values = list(self.tree.item(item, "values"))
        values[5] = traffic_input
        self.tree.item(item, values=values)
        self.unsaved_changes = True

        if values[3] == "":
            self.update_status_cell(item, "Present")

        next_item = self.tree.next(item)
        if next_item:
            self.tree.focus(next_item)
            self.tree.selection_set(next_item)

    def reset_status_counts(self):
        self.status_counts = {"Absent": 0, "Present": 0, "Excused": 0}

    def reset_table_statuses(self):
        for item in self.tree.get_children():
            values = list(self.tree.item(item, "values"))
            values[3] = "Absent"
            self.tree.item(item, values=values)

    def reset_status_and_columns(self):
        for item in self.tree.get_children():
            values = list(self.tree.item(item, "values"))
            if values[3] != "Excused":
                values[3] = "Absent"
            values[4] = ""
            values[5] = ""
            values[6] = ""
            self.tree.item(item, values=values)
            self.unsaved_changes = True

    def record_attendance(self, name, day, status):
        if name in self.attendance:
            self.attendance[name][day] = status

    def display_attendance(self):
        attendance_text = ""
        for name, days in self.attendance.items():
            attendance_text += f"{name}:\n"
            for day, status in days.items():
                attendance_text += f"  Day {day}: {status}\n"
        messagebox.showinfo("Attendance Record", attendance_text)

    def change_font_size(self, font_size):
        if font_size == "Small":
            self.set_font_size(10)
        elif font_size == "Medium":
            self.set_font_size(14)
        elif font_size == "Large":
            self.set_font_size(18)

    def set_font_size(self, size):
        font = ("Arial", size)
        self.search_button.config(font=font)
        self.refresh_button.config(font=font)  # Update the font size for the new button
        self.reset_button.config(font=font)  # Update the font size for the new button
        self.results_label.config(font=font)
        self.stats_label.config(font=font)
        self.stats_text_view.config(font=font)
        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=font)
        style.configure("Treeview", font=font)

    def apply_separator_style(self):
        for i, item in enumerate(self.tree.get_children()):
            if i % 2 == 0:
                self.tree.item(item, tags=('separator',))
            else:
                self.tree.item(item, tags=())

    def clear_sweepers_list(self):
        self.sweepers_tree.delete(*self.sweepers_tree.get_children())
        self.update_results_label("Sweepers list cleared.")

    def delete_sweeper(self):
        selected_item = self.sweepers_tree.selection()
        if selected_item:
            self.sweepers_tree.delete(selected_item)
            self.update_results_label("Sweeper deleted.")

    def handle_this_month_click(self, item):
        values = list(self.tree.item(item, "values"))
        current_value = values[7]
        new_value = simpledialog.askstring("Edit This Month", "Enter new value for This Month:", initialvalue=current_value)
        if new_value is not None:
            values[7] = new_value
            self.tree.item(item, values=values)
            self.unsaved_changes = True
            self.update_row_color(item, values[7])

    def update_row_color(self, item, this_month_value):
        if this_month_value.isdigit() and int(this_month_value) >= 7:
            self.tree.item(item, tags=('light_green',))
        else:
            self.tree.item(item, tags=())

    def turn_caps_lock_on(self):
        ctypes.windll.user32.keybd_event(0x14, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0x14, 0, 2, 0)

    def turn_caps_lock_off(self):
        ctypes.windll.user32.keybd_event(0x14, 0, 2, 0)

    def edit_cell(self, item, col):
        values = list(self.tree.item(item, "values"))
        col_idx = int(col[1:]) - 1
        if col_idx < len(values):  # Ensure the index is within the bounds of the list
            current_value = values[col_idx]
            entry = tk.Entry(self.tree, font=("Arial", 10))
            entry.insert(0, current_value)
            entry.select_range(0, tk.END)
            entry.focus_set()

            def save_changes(event):
                new_value = entry.get()
                values[col_idx] = new_value
                self.tree.item(item, values=values)
                self.unsaved_changes = True
                entry.destroy()

            entry.bind("<Return>", save_changes)
            entry.bind("<FocusOut>", save_changes)

            x, y, width, height = self.tree.bbox(item, col)
            entry.place(x=x, y=y, width=width, height=height, anchor='nw')
        else:
            messagebox.showerror("Error", "Invalid column index.")

    def handle_tab(self, event):
        focused_item = self.tree.focus()
        if focused_item:
            col = self.tree.identify_column(event.x)
            col_idx = int(col[1:]) - 1
            next_col_idx = (col_idx + 1) % len(self.columns)
            next_col = f"#{next_col_idx + 1}"
            next_item = self.tree.next(focused_item) if next_col_idx == 0 else focused_item
            
            # Get the bounding box of the next cell
            x, y, width, height = self.tree.bbox(next_item, next_col)
            
            # Focus on the next cell
            self.tree.focus(next_item)
            self.tree.selection_set(next_item)
            self.tree.see(next_item)
            self.tree.focus_set()
            self.tree.focus(next_item)
            self.tree.focus_force()
            
            # Move the cursor to the next cell
            self.tree.update()
            self.tree.event_generate("<Button-1>", x=x+width//2, y=y+height//2)

    def count_unique_regions(self):
        regions = set()
        for item in self.sweepers_tree.get_children():
            values = self.sweepers_tree.item(item, "values")
            if len(values) > 3:
                regions.add(values[3])
        return len(regions)

    def create_monthly_roster(self):
        if self.unsaved_changes:
            confirm = messagebox.askyesno("Unsaved Changes", "There are unsaved changes. Do you want to save before creating a new monthly roster?")
            if confirm:
                self.save_file()

        if not self.tree.get_children():
            response = messagebox.askyesno("No Data", "The table is empty. Do you want to load a source file first?")
            if response:
                self.open_file()
            else:
                return

        # Set all "Status" to "Absent"
        for item in self.tree.get_children():
            values = list(self.tree.item(item, "values"))
            values[3] = "Absent"  # Column 4 (Status)
            self.tree.item(item, values=values)

        # Clear columns 5, 6, 7, and 8
        for item in self.tree.get_children():
            values = list(self.tree.item(item, "values"))
            values[4] = ""  # Column 5 (Relayed)
            values[5] = ""  # Column 6 (Traffic)
            values[6] = ""  # Column 7 (Sweep?)
            values[7] = "0"  # Column 8 (This Month)
            self.tree.item(item, values=values)

        # Clear Stats
        self.stats_text_view.config(state=tk.NORMAL)
        self.stats_text_view.delete(1.0, tk.END)
        self.stats_text_view.config(state=tk.DISABLED)

        # Clear Sweepers
        self.sweepers_tree.delete(*self.sweepers_tree.get_children())

        # Delete rows where "QTH" is "VISITOR"
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[1] == "VISITOR":
                self.tree.delete(item)

        # Reset Net Control
        self.net_control = ""

        # Reset Total Time, Start Time, and End Time
        self.time_start = None
        self.time_end = None

        # Prompt user to save the file
        now = datetime.now()
        month_str = now.strftime("%B")
        year_str = now.strftime("%Y")
        default_filename = f"Roll Call Net Master {month_str} {year_str}.csv"
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], initialfile=default_filename)
        if file_path:
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                # Write the summary header
                summary_header = ["Time Start", "Time End", "Total Present", "Current Net Name", "Total Excused", "Net Control"]
                writer.writerow(summary_header)
                # Write the summary data
                summary_data = [self.time_start, self.time_end, self.status_counts["Present"], self.current_net_name, self.status_counts["Excused"], self.net_control]
                writer.writerow(summary_data)
                # Write the detailed roster data without the header
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item, "values"))
            messagebox.showinfo("Create Monthly Roster", "Monthly roster created successfully.")

    def archive_monthly_roster(self):
        # Implement the logic to archive a monthly roster
        now = datetime.now()
        month_str = now.strftime("%B")
        year_str = now.strftime("%Y")
        default_filename = f"Archived Roster {month_str} {year_str}.csv"
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], initialfile=default_filename)
        if file_path:
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(self.columns)
                for item in self.tree.get_children():
                    writer.writerow(self.tree.item(item, "values"))
            messagebox.showinfo("Archive Monthly Roster", "Monthly roster archived successfully.")

        # Launch Zipper.py in the current directory
        try:
            subprocess.run(["python", "Zipper.py"], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to launch Zipper.py: {e}")

    def load_preamble_and_set(self, file_path):
        preamble_text = self.load_preamble_from_csv(file_path)
        self.show_preamble_popup(preamble_text, file_path)

    def show_preamble_popup(self, preamble_text, file_path):
        popup = tk.Toplevel(self.root)
        popup.title("Open Net Preamble")  # Name the widget "Open Net"
        
        preamble_text_view = tk.Text(popup, height=15, width=50, font=("Arial", 10))
        preamble_text_view.pack(padx=10, pady=10)
        preamble_text_view.insert(tk.END, preamble_text)
        
        save_button = tk.Button(popup, text="Save", command=lambda: self.save_preamble(preamble_text_view, file_path))
        save_button.pack(pady=5, side=tk.LEFT)
        
        clear_button = tk.Button(popup, text="Clear", command=lambda: preamble_text_view.delete(1.0, tk.END))
        clear_button.pack(pady=5, side=tk.LEFT)

    def save_preamble(self, text_widget, file_path):
        preamble_text = text_widget.get(1.0, tk.END).strip()
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            # Write the preamble text line by line
            for line in preamble_text.split("\n"):
                writer.writerow([line])
        messagebox.showinfo("Save", "Preamble saved successfully.")

    def refresh_table(self):
        if not self.tree.get_children():
            messagebox.showwarning("No Data", "The table is empty. Please load data first.")
            return

        # Refresh table stats
        self.display_totals_and_times()

        # Refresh sweepers
        self.sweepers_tree.delete(*self.sweepers_tree.get_children())
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[6] == "Yes":
                call_sign = values[0]
                qth = values[1].upper()
                name = values[2]
                region = self.alaska_towns.get(qth, "Unknown")
                self.sweepers_tree.insert("", "end", values=(call_sign, qth, name, region))

        # Alphabetize the table in ascending order based on "Call Sign"
        self.sort_column("Call Sign", ascending=True)

        self.update_results_label("Table refreshed.")

    def reset_table(self):
        if not self.tree.get_children():
            messagebox.showwarning("No Data", "The table is empty. Please load data first.")
            return

        # Reset "Status" to all "Absent"
        for item in self.tree.get_children():
            values = list(self.tree.item(item, "values"))
            values[3] = "Absent"  # Column 4 (Status)
            values[7] = "0"  # Column 8 (This Month)
            values[4] = ""  # Column 5 (Relayed)
            values[5] = ""  # Column 6 (Traffic)
            values[6] = ""  # Column 7 (Sweep?)
            self.tree.item(item, values=values)

        # Clear Sweepers
        self.sweepers_tree.delete(*self.sweepers_tree.get_children())

        # Reset Stats
        self.reset_status_counts()
        self.visitor_count = 0  # Reset visitor count
        self.total_call_sign_count = len(self.tree.get_children())  # Reset total call sign count
        self.time_start = None  # Reset start time
        self.time_end = None  # Reset end time
        self.net_control = ""  # Reset net control
        self.display_totals_and_times()

        # Sort the table in alphabetical ascending order based on "Call Sign"
        self.sort_column("Call Sign", ascending=True)

        # Delete rows where "QTH" or "NAME" is "VISITOR"
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[1] == "VISITOR" or values[2] == "VISITOR":
                self.tree.delete(item)

        # Change focus to row one column one
        first_item = self.tree.get_children()[0] if self.tree.get_children() else None
        if first_item:
            self.tree.focus(first_item)
            self.tree.selection_set(first_item)

        self.update_results_label("Table reset.")

    def minimize_command_window(self):
        # This function minimizes the command window on Windows
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.update_style()
        self.apply_dark_mode_styles()

    def apply_dark_mode_styles(self):
        bg_color = "black" if self.dark_mode else "white"
        fg_color = "white" if self.dark_mode else "black"


    def update_style(self):
        bg_color = "#2e2e2e" if self.dark_mode else "white"  # Dark gray background
        fg_color = "white" if self.dark_mode else "black"  # Light text for dark mode
        heading_bg_color = "#444444" if self.dark_mode else "lightgray"  # Darker gray for headings
        button_bg_color = "#555555" if self.dark_mode else "lightgray"  # Button background
        button_fg_color = "white" if self.dark_mode else "black"  # Button text
        hover_color = "#777777" if self.dark_mode else "gray"  # Hover effect for buttons

        # Update root and frame colors
        self.root.config(bg=bg_color)
        self.frame.config(bg=bg_color)

        # Update labels and buttons
        self.search_button.config(bg=bg_color, fg=fg_color)
        self.stats_label.config(bg=bg_color, fg=fg_color)
        self.stats_text_view.config(bg=bg_color, fg=fg_color)
        self.sweepers_label.config(bg=bg_color, fg=fg_color)

        # Update ttk styles
        self.style.configure("Treeview", background=bg_color, foreground=fg_color, fieldbackground=bg_color)
        self.style.configure("Treeview.Heading", background=heading_bg_color, foreground=fg_color)
        self.style.configure("TButton", background=button_bg_color, foreground=button_fg_color)
        self.style.map("TButton", background=[("active", hover_color)])  # Hover effect
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TFrame", background=bg_color)

        # Update non-ttk widgets (e.g., Text, Label, Button)
        self.stats_text_view.config(bg=bg_color, fg=fg_color)
        self.search_button.config(bg=button_bg_color, fg=button_fg_color, activebackground=hover_color)
        self.refresh_button.config(bg=button_bg_color, fg=button_fg_color, activebackground=hover_color)
        self.reset_button.config(bg=button_bg_color, fg=button_fg_color, activebackground=hover_color)
        self.results_label.config(bg=bg_color, fg=fg_color)
        self.stats_label.config(bg=bg_color, fg=fg_color)
        self.sweepers_label.config(bg=bg_color, fg=fg_color)

        # Style scrollbars
        self.style.configure("Vertical.TScrollbar", background=bg_color, troughcolor=heading_bg_color, arrowcolor=fg_color)

        # Apply dark mode to message boxes
        # Comment out or remove the following lines to disable popups
        # if self.dark_mode:
        #     messagebox.showinfo("Dark Mode", "Dark mode is now enabled.")
        # else:
        #     messagebox.showinfo("Light Mode", "Light mode is now enabled.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataBaseUtility(root)
    root.mainloop()

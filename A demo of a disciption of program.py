import tkinter as tk

# Global variable to track the teletype effect
teletype_id = None

def teletype_print(text_widget, text, delay=30):
    """
    Simulates a teletype-style text display in a Tkinter text widget.
    :param text_widget: The Tkinter Text widget to display the text.
    :param text: The text to display.
    :param delay: The delay (in milliseconds) between each character.
    """
    def add_char(index=0):
        global teletype_id
        try:
            if index < len(text):
                text_widget.insert(tk.END, text[index])
                text_widget.see(tk.END)  # Scroll to the end of the text
                text_widget.update_idletasks()  # Update the widget to show the new character
                teletype_id = text_widget.after(delay, add_char, index + 1)  # Schedule the next character
        except Exception as e:
            print(f"Error during teletype effect: {e}")

    add_char()  # Start the teletype effect

def restart_app(text_area, message):
    """
    Clears the text widget, cancels any ongoing teletype effect, and restarts the teletype effect.
    :param text_area: The Tkinter Text widget to clear and restart.
    :param message: The text to display.
    """
    global teletype_id

    try:
        # Cancel any ongoing teletype effect
        if teletype_id is not None:
            text_area.after_cancel(teletype_id)
            teletype_id = None

        # Clear the text widget
        text_area.delete(1.0, tk.END)

        # Add a small delay before restarting to ensure no leftover tasks interfere
        text_area.after(100, lambda: teletype_print(text_area, message))
    except Exception as e:
        print(f"Error during restart: {e}")

def toggle_dark_mode(text_area):
    """
    Toggles the dark mode on and off for the text widget.
    :param text_area: The Tkinter Text widget to toggle.
    """
    if text_area["bg"] == "black":
        text_area.config(bg="white", fg="black")
    else:
        text_area.config(bg="black", fg="white")

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Teletype Text Display")
    root.geometry("800x600")  # Set the window size

    # Create a border frame for the riveted look
    border_frame = tk.Frame(root, bg="gray12", highlightthickness=0)
    border_frame.pack(fill=tk.BOTH, expand=True)

    # Create a text widget (no scrollbar)
    text_area = tk.Text(border_frame, wrap=tk.WORD, font=("Courier", 12), bg="black", fg="white")
    text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # Add padding for the rivets

    # The text to display
    message = (
        "Greetings, fellow hams! Welcome! Discover how this app brings exciting new possibilities to your ham radio setup. "
        "Today, we’re diving into a program created specifically for net control operators and anyone managing roll calls during net sessions. "
        "It’s called the Net Attendance Manager, and it’s crafted with the ham radio community in mind. "
        "Let me tell you what it’s all about and how it can make your net operations smoother and more efficient.\n\n"

        "If you’ve ever been a net control operator, you know how important it is to keep track of who’s present, who’s excused, and who’s relaying traffic. "
        "It’s a lot to manage, especially during a busy net. That’s where the Net Attendance Manager comes in. "
        "This program is your all-in-one tool for managing roll calls, tracking attendance, and even handling emergency traffic.\n\n"

        "At its core, the Net Attendance Manager is a user-friendly application that helps you manage your net roll call with ease. "
        "It keeps track of participants, their statuses, and even allows you to mark who’s relaying traffic or acting as a sweeper. "
        "The interface is clean and intuitive, making it easy to focus on the task at hand—running a smooth net.\n\n"

        "When you’re ready to start the net, simply click the ‘Start Roll Call’ button. "
        "The program will prompt you to enter the net control’s call sign and then begin tracking the time. "
        "The stopwatch feature keeps you updated on how long the net has been running, and it even alerts you if the net goes on longer than expected. "
        "This is especially helpful for keeping things on schedule.\n\n"

        "The heart of the program is the roll call table. "
        "It’s where you’ll see all your participants listed with their call signs, QTHs, and statuses. "
        "You can quickly mark someone as ‘Present,’ ‘Excused,’ or ‘Absent.’ "
        "If someone is relaying traffic, you can log that too. "
        "And if you’re managing sweepers, the program makes it easy to track who’s covering which areas.\n\n"

        "One of the most critical features of this program is its ability to handle emergency traffic. "
        "During a net, if an emergency arises, you can quickly launch the emergency traffic module. "
        "This ensures that the current log isn’t saved, allowing you to focus entirely on the emergency situation. "
        "It’s a lifesaver—literally—for those moments when every second counts.\n\n"

        "Once the net is over, you can save all the data to a CSV file. "
        "This includes the start and end times, attendance totals, and any notes you’ve made during the session. "
        "The saved file can be easily shared or archived for future reference. "
        "It’s a great way to keep detailed records of your nets.\n\n"

        "For those late-night nets, the program includes a dark mode option. "
        "It switches the interface to a sleek black background with white text, making it easier on the eyes during those long sessions. "
        "It’s a small but thoughtful feature that shows how much thought has gone into this tool.\n\n"

        "The Net Attendance Manager isn’t just a tool—it’s a partner in your net operations. "
        "It takes the stress out of tracking attendance, managing traffic, and handling emergencies. "
        "Whether you’re a seasoned net control operator or just starting out, this program can help you run smoother, more organized nets.\n\n"

        "If you’re looking to streamline your net operations and make your role as net control easier, the Net Attendance Manager is definitely worth checking out. "
        "It’s a tool built by hams, for hams, and it’s designed to make your net sessions more efficient and enjoyable.\n\n"

        "If you found this video helpful, don’t forget to like, subscribe, and hit the notification bell for more ham radio tips and tools. "
        "Thanks for watching, and I’ll see you in the next video!\n\n"

        "[73s NL7PA]"
    )

    # Display the text in the text widget
    teletype_print(text_area, message)

    # Rivet symbol
    rivet_symbol = "锔"

    # Function to place rivet labels around the border frame
    def place_rivets(event):
        frame = event.widget
        frame.update_idletasks()  # Ensure the frame has its current size

        # Remove any existing rivet labels
        for label in getattr(frame, '_rivet_labels', []):
            label.destroy()
        frame._rivet_labels = []

        # Define the interval between rivets
        interval = 20  # Adjust as needed

        # Top and bottom rivets
        width = frame.winfo_width()
        for x in range(0, width, interval):
            # Top rivet
            label = tk.Label(frame, text=rivet_symbol, bg="gray12", fg="gray50", font=("Courier", 8))
            label.place(x=x, y=0)
            frame._rivet_labels.append(label)
            # Bottom rivet
            label = tk.Label(frame, text=rivet_symbol, bg="gray12", fg="gray50", font=("Courier", 8))
            label.place(x=x, y=frame.winfo_height()-label.winfo_reqheight())
            frame._rivet_labels.append(label)

        # Left and right rivets
        height = frame.winfo_height()
        for y in range(0, height, interval):
            # Left rivet
            label = tk.Label(frame, text=rivet_symbol, bg="gray12", fg="gray50", font=("Courier", 8))
            label.place(x=0, y=y)
            frame._rivet_labels.append(label)
            # Right rivet
            label = tk.Label(frame, text=rivet_symbol, bg="gray12", fg="gray50", font=("Courier", 8))
            label.place(x=frame.winfo_width()-label.winfo_reqwidth(), y=y)
            frame._rivet_labels.append(label)

        # Force the Text widget to update after resizing
        text_area.update_idletasks()

    # Bind the place_rivets function to the border frame's configure event
    border_frame.bind("<Configure>", place_rivets)

    # Bind the spacebar to restart the app
    root.bind("<space>", lambda event: restart_app(text_area, message))

    # Bind the 'd' key to toggle dark mode
    root.bind("d", lambda event: toggle_dark_mode(text_area))

    # Run the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
# Python GUI to compare directories
import os
import filecmp
import customtkinter as ctk
from customtkinter import CTk, CTkEntry, CTkButton, CTkLabel, CTkToplevel, CTkScrollbar
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

def select_directory(text_input, title="Select a Directory"):
    """ 
    Opens a dialog to select a directory. 

    :param text_input: The directory path from the text input box
    :type text_input: String
    :return: Nothing
    """
    # First, clear existing data in text input entry field
    text_input.delete(0, tk.END)

    return filedialog.askdirectory(title=title)

def compare_directories(dir_a, dir_b):
    """ 
    Compares two directories and returns a DataFrame with the results. Results include file name, directory
    A status, directory B status, size difference, and last modified difference.

    :param dir_a: The directory path of Directory A
    :type dir_a: String
    :param dir_b: The directory path of Directory B
    :type dir_b: String
    :return: Nothing
    """
    # Check if directory paths exists
    if not os.path.isdir(dir_a) or not os.path.isdir(dir_a):
        messagebox.showerror(
            "Directory Not Found", 
            f"The directory {dir_a} or {dir_b} does not exist. Please check the path."
        )

        # If paths don't exist, exit function
        return

    only_in_a = []
    only_in_b = []
    different_files = []

    n_a_symbol = "-"
    present = "Present"
    missing = "Missing"
    different_size = "Different Size"

    # Get files in both dirs
    dir_a_files = set(os.listdir(dir_a))
    dir_b_files = set(os.listdir(dir_b))

    # Files only in Directory A
    for file in dir_a_files - dir_b_files:
        only_in_a.append((file, present, missing, n_a_symbol, n_a_symbol))

    # Files only in Directory B
    for file in dir_b_files - dir_a_files:
        only_in_b.append((file, missing, present, n_a_symbol, n_a_symbol))

    # Files that exist in both directories but may differ in size or modified date
    common_files = dir_a_files & dir_b_files
    for file in common_files:
        path_a = os.path.join(dir_a, file)
        path_b = os.path.join(dir_b, file)

        # Compare file sizes and modification times
        if not filecmp.cmp(path_a, path_b, shallow=False):
            stats_a = os.stat(path_a)
            stats_b = os.stat(path_b)

            # Calculate size and time stats
            size_diff = str(abs(stats_a.st_size - stats_b.st_size)) + " bytes"
            time_diff = str(abs(stats_a.st_mtime - stats_b.st_mtime) / 60) + " minutes earlier"

            # Check if there is a size difference or not, and print seperate messages for both cases
            if not size_diff == "0 bytes":
                different_files.append((file, different_size, different_size, size_diff, time_diff))
            else:
                different_files.append((file, present, present, n_a_symbol, n_a_symbol))

    # Combine results into a DataFrame
    all_results = only_in_a + only_in_b + different_files
    columns = ["File Name", "Directory A Status", "Directory B Status", "Size Difference", "Last Modified Difference"]
    df = pd.DataFrame(all_results, columns=columns)

    return df

def show_comparison_result(df):
    """ 
    Displays the comparison results in a table with sorting functionality. 

    :param df: A dataframe with rows for the comparison data of each file between Dir A and Dir B
                Columns are filename, dir a, dir b, size diff, time modified diff
    :type df: Panda dataframe
    :return: Nothing
    """

    # Create a new window to display results... should appear on top
    result_window = CTkToplevel()
    result_window.title("Directory Comparison Result")

    # ------ Set window size based on device resolution
    # Get screen width and height
    screen_width = result_window.winfo_screenwidth()
    screen_height = result_window.winfo_screenheight()

    # Set window size to 80% of the screen size
    window_width = int(screen_width * 0.8)
    window_height = int(screen_height * 0.4)

    result_window.geometry(f"{window_width}x{window_height}")

    # ------ Create custom style object for Treeview since using default Tkinter one
    style = ttk.Style()
    style.configure("Treeview",
                    font=("Arial", 14))  # Set font size to 12 for the entire Treeview
    style.configure("Treeview.Heading", font=("Arial", 16, "bold"))  # Make headings bigger

    # ------ Create a Treeview widget to display the table
    tree = ttk.Treeview(
        result_window, 
        style="Treeview",
        columns=df.columns.tolist(), 
        show="headings", 
        height=15)

    # Create columns for the Treeview
    for col in df.columns:
        tree.heading(col, text=col, command=lambda _col=col: sort_by_column(tree, _col))
        tree.column(col, anchor="w", width=200)

    # Insert data into the Treeview
    for row in df.itertuples(index=False):
        tree.insert("", "end", values=row)

    # Add a scrollbar
    scrollbar = CTkScrollbar(result_window, orientation="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)

    # Make sure window on top
    result_window.after(100, result_window.lift)

def sort_by_column(tree, column):
    """ 
    Sorts the table by the clicked column. 

    :param tree: TKInter.Treeview to sort the data of by column
    :type tree: TKInter.Treeview
    :param column: The column to sort the data by
    :type column: dataframe column
    :return: Nothing
    """
    items = [(tree.set(item, column), item) for item in tree.get_children()]
    items.sort(key=lambda x: x[0])
    for index, item in enumerate(items):
        tree.move(item[1], '', index)

def export_to_csv(df):
    """ 
    Exports the comparison results to a CSV file. 

    :param df: A dataframe with rows for the comparison data of each file between Dir A and Dir B
                Columns are filename, dir a, dir b, size diff, time modified diff
    :type df: Panda dataframe
    :return: Nothing
    """
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

    # Check if the file path exists
    if file_path:
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Export Successful", "The comparison result has been exported successfully!")

# Compare directories
def on_compare(dir_a_entry, dir_b_entry):
    '''
    Compares the contents of Dir A and Dir B

    :param dir_a_entry: Directory A TKInter.Entry element
    :type dir_a_entry: TKInter.Entry
    :param dir_b_entry: Directory B TKInter.Entry element
    :type dir_b_entry: TKInter.Entry
    :return: Nothing
    '''
    dir_a = dir_a_entry.get()
    dir_b = dir_b_entry.get()

    # Check if directories exist
    if not os.path.isdir(dir_a) or not os.path.isdir(dir_b):
        messagebox.showerror("Error", "Please select valid directories.")
        return

    # Compare the directories and show the result
    df = compare_directories(dir_a, dir_b)
    show_comparison_result(df)
    
def main():
    '''
    Create main window
    '''
    # Create main window
    root = CTk()
    root.title("Directory Comparison Tool")

    # Set theme to dark to match company site...
    ctk.set_appearance_mode("dark")

    # ------ Set window size based on device resolution
    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set window size to 80% of the screen size
    window_width = int(screen_width * 0.8)
    window_height = int(screen_height * 0.4)

    root.geometry(f"{window_width}x{window_height}")

    # ----- UI variables
    text_input_width = int(window_width * 0.7)
    
    font_family = "Ariel"
    font_header_size = 20
    font_text_size = 14
    text_colour_dark = "#525252"

    radius = 32
    button_colour = "#444444"
    button_hover_colour = "#666666"
    button_width = int(window_width * 0.05)
    placeholder_text_input_box = "Directory Path"

    button_colour_accent = "#f5d442"
    button_hover_colour_accent = "#ffec99"

    page_padding = int(window_width * 0.05)

    # Center elements
    # root.grid_rowconfigure(0, weight=1)
    # root.grid_columnconfigure(0, weight=1)

    # ----- Create, style, and arrange window elements
    # Header
    header = CTkLabel(
        root, 
        text="Directory Comparison Tool", 
        font=(font_family, font_header_size, "bold"))
    header.grid(row=0, column=0, columnspan=6, pady=10, padx=10, sticky="ew")

    # Directory A selection
    dir_a_label = CTkLabel(
        root, 
        text="Directory A:", 
        font=(font_family, font_text_size))
    dir_a_label.grid(row=1, column=0, padx=(page_padding, 10), pady=10, sticky="w")

    dir_a_entry = CTkEntry(
        root, 
        width=text_input_width, 
        border_width=0, 
        corner_radius=radius, 
        placeholder_text=placeholder_text_input_box)
    dir_a_entry.grid(row=1, column=1, pady=10)

    dir_a_button = CTkButton(
        root, 
        text="Browse", 
        corner_radius=radius, 
        fg_color=button_colour, 
        hover_color=button_hover_colour, 
        width=button_width, 
        font=(font_family, font_text_size), 
        command=lambda: dir_a_entry.insert(0, select_directory(dir_a_entry)))
    dir_a_button.grid(row=1, column=2, padx=(10, page_padding), pady=10)

    # Directory B selection
    dir_b_label = CTkLabel(
        root, 
        text="Directory B:", 
        font=(font_family, font_text_size))
    dir_b_label.grid(row=2, column=0, padx=(page_padding, 10), pady=10, sticky="w")

    dir_b_entry = CTkEntry(
        root, 
        width=text_input_width, 
        border_width=0, 
        corner_radius=radius, 
        placeholder_text=placeholder_text_input_box)
    dir_b_entry.grid(row=2, column=1, pady=10)

    dir_b_button = CTkButton(
        root, 
        text="Browse", 
        corner_radius=radius, 
        fg_color=button_colour, 
        hover_color=button_hover_colour, 
        width=button_width, 
        font=(font_family, font_text_size), 
        command=lambda: dir_b_entry.insert(0, select_directory(dir_b_entry)))
    dir_b_button.grid(row=2, column=2, padx=(10, page_padding), pady=10)

    # Compare button
    compare_button = CTkButton(
        root, 
        text="Compare Directories!", 
        command=lambda: on_compare(dir_a_entry, dir_b_entry), 
        corner_radius=radius, 
        fg_color=button_colour_accent, 
        hover_color=button_hover_colour_accent, 
        text_color=text_colour_dark, 
        font=(font_family, font_text_size, "bold"))
    compare_button.grid(row=3, column=1, pady=10)

    # Export button
    export_button = CTkButton(
        root, 
        text="Export to CSV", 
        command=lambda: export_to_csv(compare_directories(dir_a_entry.get(), dir_b_entry.get())), 
        corner_radius=radius, 
        fg_color=button_colour_accent, 
        hover_color=button_hover_colour_accent, 
        text_color=text_colour_dark, 
        font=(font_family, font_text_size, "bold"))
    export_button.grid(row=4, column=1, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
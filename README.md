# Simple GUI Tool for Directory Comparison
A Python GUI tool to compare the contents of two directories. Displays the differences between directories in terms of file presence, file size, and modification dates.

## Required Dependencies and Installations
The required dependencies and installations are as follows:
- Python 3.x.x
- os (included with Python)
- filecmp (included with Python)
- tkinter (included with Python)
- customtkinter (install via **pip install customtkinter**)
- pandas (install via **pip install pandas**)

## How To Run
1. Navigate to the directory where compare_directories.py is stored via terminal,
2. Run **python compare_directories.py**.

## Features
- Accepts two directory paths as input.
- Compares the contents of both directories and shows:
    - Files only present in Directory A.
    - Files only present in Directory B.
    - Files present in both but with different sizes or modification dates.
- Displays the results in a table with sorting functionality.
- Allows exporting the comparison result as a CSV file.
- Column sorting of diff results
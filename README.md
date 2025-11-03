💰 Daily Expenses Tracker
=========================

A comprehensive desktop application built with Python to help you manage, track, and analyze your daily expenses. It features a user-friendly graphical interface (GUI), persistent data storage using SQLite, and powerful visualization tools to give you clear insights into your spending habits.

Getty Images

✨ Features
----------

This application provides a complete toolkit for managing your personal finances:

*   **Full CRUD Operations:**
    
    *   **Add:** Easily add new expenses with details like date, payee, description, amount, payment mode, and category.
        
    *   **View:** See all your expenses in a clean, sortable table.
        
    *   **Edit:** Select any expense from the table to load its details back into the form for editing and saving.
        
    *   **Delete:** Remove individual expenses or delete all records at once.
        
*   **Intuitive Dashboard:**
    
    *   Get an at-a-glance view of your **Total Spent (All Time)** and the **Total Number of Expenses** recorded.
        
*   **Data-Entry Helpers:**
    
    *   A pop-up calendar (tkcalendar) for easy date selection.
        
    *   Dropdown menus for predefined categories and payment modes.
        
    *   Placeholder text in entry fields to guide the user.
        
*   **Powerful Analytics & Visualization:**
    
    *   Open a dedicated analytics window to see your data come to life with Matplotlib:
        
        *   **Monthly Trend:** A line graph showing your total spending month-over-month.
            
        *   **Category Breakdown:** A pie chart showing the percentage of your spending by category.
            
        *   **Payment Mode:** A bar chart comparing the total amount spent using different payment methods (e.g., Cash, Credit Card, Google Pay).
            
*   **Future Expense Prediction:**
    
    *   Includes a "Predict Future" feature that uses a **Linear Regression** model (scikit-learn) to forecast your spending for the next three months based on your historical data.
        
*   **Persistent Storage:**
    
    *   All your expense data is saved locally in an **SQLite database** (Expense Tracker.db), so your records are safe even after you close the app.
        

🛠️ Technology Stack
--------------------

This project is built entirely with Python and its rich ecosystem of libraries:

*   **GUI:** Tkinter (Python's standard GUI package)
    
*   **Database:** SQLite3 (for local, persistent data storage)
    
*   **Data Visualization:** Matplotlib (for plotting all graphs and charts)
    
*   **Machine Learning:** scikit-learn (specifically LinearRegression for the prediction feature)
    
*   **Numerical Operations:** Numpy (for handling data for the prediction model)
    
*   **GUI Widgets:** tkcalendar (for the friendly DateEntry widget)
    
*   **Date/Time:** datetime & dateutil (for handling dates and time-based calculations)
    

🏗️ Code Architecture
---------------------

The application is built with an object-oriented structure, divided into four main classes to separate concerns:

*   **DatabaseManager**: This class handles all direct interaction with the SQLite3 database. It is responsible for creating the ExpenseTracker table, adding new expenses, updating existing ones, deleting records, and fetching all data for display.
    
*   **ExpenseAnalytics**: A utility class containing only static methods. It performs all data processing and analysis. Its responsibilities include aggregating expenses by month, category, and payment mode. It also contains the predict\_future\_expenses method, which uses scikit-learn's LinearRegression model to forecast spending.
    
*   **VisualizationWindow**: This class manages the secondary Toplevel window used for displaying graphs. It takes the processed data from ExpenseAnalytics and uses Matplotlib to render the line, pie, bar, and prediction charts, embedding them directly into the Tkinter UI.
    
*   **ExpenseTrackerGUI**: This is the main application class. It builds the entire user interface, including the data entry form, the dashboard, the expense table (Treeview), and all the action buttons. It manages the application's state, handles all user events (like button clicks), and coordinates the other classes to function as a cohesive application.
    

🚀 Getting Started
------------------

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

You must have **Python 3** installed on your system.

### Installation

1.  git clone [https://github.com/Jitin2102/Daily-Expenses-Tracker.git](https://github.com/Jitin2102/Daily-Expenses-Tracker.git) cd Daily-Expenses-Tracker

    
3.  This project depends on several external libraries. You can install them all using pip.pip install tkcalendar matplotlib numpy scikit-learn python-dateutil_(Note: tkinter and sqlite3 are included with most standard Python installations.)_
    

### Usage

1.  Save your Python script as app.py (or your preferred name) inside the project folder.python app.py
    
2.  **How to Use:**
    
    *   Launch the application.
        
    *   Use the form on the left to enter your expense details.
        
    *   Click "**➕ Add Expense**" to save the transaction to the database.
        
    *   Your new expense will appear in the table on the right.
        
    *   Select an expense in the table and click "**✏️ Edit Expense**" to modify it or "**🗑️ Delete Expense**" to remove it.
        
    *   Click "**📊 Visualize Expenses**" to open the analytics window.
        
    *   Click "**🤖 Predict Future**" to see a forecast of your spending.
        

Contributing
------------

Contributions are welcome! Please feel free to fork the repository, make changes, and submit a pull request.

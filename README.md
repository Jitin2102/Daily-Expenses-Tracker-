# 💰 Daily Expenses Tracker

A comprehensive desktop application built with Python to help you manage, track, and analyze your daily expenses. It features a user-friendly graphical interface (GUI), persistent data storage using SQLite, and powerful visualization tools to give you clear insights into your spending habits.

---

## ✨ Features

This application provides a complete toolkit for managing your personal finances:

### ✅ Full CRUD Operations
- **Add**: Easily add new expenses with details like date, payee, description, amount, payment mode, and category.
- **View**: See all your expenses in a clean, sortable table.
- **Edit**: Select any expense from the table to load its details back into the form for editing and saving.
- **Delete**: Remove individual expenses or delete all records at once.

### 📊 Intuitive Dashboard
- View your **Total Spent (All Time)** and the **Total Number of Expenses** recorded at a glance.

### 🧾 Data-Entry Helpers
- Pop-up calendar using `tkcalendar` for easy date selection.
- Dropdown menus for predefined categories and payment modes.
- Placeholder text in entry fields to guide the user.

### 📈 Powerful Analytics & Visualization
Open a dedicated analytics window to see your data come to life with Matplotlib:
- **Monthly Trend**: Line graph showing your total spending month-over-month.
- **Category Breakdown**: Pie chart showing the percentage of your spending by category.
- **Payment Mode**: Bar chart comparing the total amount spent using different payment methods (e.g., Cash, Credit Card, Google Pay).

### 🤖 Future Expense Prediction
- Uses a **Linear Regression** model (via `scikit-learn`) to forecast your spending for the next three months based on historical data.

### 💾 Persistent Storage
- All your expense data is saved locally in an **SQLite** database (`Expense Tracker.db`), ensuring your records are safe even after closing the app.

---

## 🛠️ Technology Stack

This project is built entirely with Python and its rich ecosystem of libraries:

| Purpose              | Library             |
|----------------------|---------------------|
| GUI                  | Tkinter             |
| Database             | SQLite3             |
| Data Visualization   | Matplotlib          |
| Machine Learning     | scikit-learn        |
| Numerical Operations | NumPy               |
| Date Picker Widget   | tkcalendar          |
| Date Handling        | datetime, dateutil  |

---

## 🚀 Getting Started

### Prerequisites
- Python 3 must be installed on your system.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Daily-Expenses-Tracker.git
   cd Daily-Expenses-Tracker

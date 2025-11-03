import datetime
import sqlite3
from tkcalendar import DateEntry
import tkinter as tk
import tkinter.messagebox as mb
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from collections import defaultdict
from sklearn.linear_model import LinearRegression
from dateutil.relativedelta import relativedelta


class DatabaseManager:
    def __init__(self, db_name="Expense Tracker.db"):
        self.connector = sqlite3.connect(db_name)
        self.cursor = self.connector.cursor()
        self._create_table()

    def _create_table(self):
        self.connector.execute(
            """CREATE TABLE IF NOT EXISTS ExpenseTracker (
                ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                Date DATETIME,
                Payee TEXT,
                Description TEXT,
                Amount FLOAT,
                ModeOfPayment TEXT,
                Category TEXT
            )"""
        )
        self.connector.commit()

    def get_all_expenses(self):
        all_data = self.connector.execute("SELECT * FROM ExpenseTracker")
        return all_data.fetchall()

    def add_expense(self, date, payee, description, amount, mode_of_payment, category):
        self.connector.execute(
            """INSERT INTO ExpenseTracker
            (Date, Payee, Description, Amount, ModeOfPayment, Category)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (date, payee, description, amount, mode_of_payment, category),
        )
        self.connector.commit()

    def update_expense(
        self, expense_id, date, payee, description, amount, mode_of_payment, category
    ):
        self.connector.execute(
            """UPDATE ExpenseTracker
            SET Date = ?, Payee = ?, Description = ?, Amount = ?, ModeOfPayment = ?, Category = ?
            WHERE ID = ?""",
            (date, payee, description, amount, mode_of_payment, category, expense_id),
        )
        self.connector.commit()

    def delete_expense(self, expense_id):
        self.connector.execute("DELETE FROM ExpenseTracker WHERE ID=?", (expense_id,))
        self.connector.commit()

    def delete_all_expenses(self):
        self.connector.execute("DELETE FROM ExpenseTracker")
        self.connector.commit()

    def close(self):
        self.connector.close()


class ExpenseAnalytics:
    @staticmethod
    def get_monthly_expenses(expenses):
        monthly_data = defaultdict(float)
        for expense in expenses:
            date_str = expense[1]
            amount = expense[4]
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                monthly_data[month_key] += amount
            except:
                continue
        return dict(sorted(monthly_data.items()))

    @staticmethod
    def get_category_expenses(expenses):
        category_data = defaultdict(float)
        for expense in expenses:
            category = expense[6]
            amount = expense[4]
            category_data[category] += amount
        return dict(category_data)

    @staticmethod
    def get_payment_mode_expenses(expenses):
        mode_data = defaultdict(float)
        for expense in expenses:
            mode = expense[5]
            amount = expense[4]
            mode_data[mode] += amount
        return dict(mode_data)

    @staticmethod
    def predict_future_expenses(monthly_data, months_ahead=3):
        if len(monthly_data) < 2:
            return None

        months = list(monthly_data.keys())
        amounts = list(monthly_data.values())

        X = np.array(range(len(months))).reshape(-1, 1)
        y = np.array(amounts)

        model = LinearRegression()
        model.fit(X, y)

        future_X = np.array(range(len(months), len(months) + months_ahead)).reshape(
            -1, 1
        )
        predictions = model.predict(future_X)

        last_date = datetime.datetime.strptime(months[-1], "%Y-%m")
        future_months = []
        for i in range(1, months_ahead + 1):
            future_date = last_date + relativedelta(months=i)
            future_months.append(future_date.strftime("%Y-%m"))

        return dict(zip(future_months, predictions))


class VisualizationWindow:
    def __init__(self, parent, expenses, theme):
        self.window = tk.Toplevel(parent)
        self.window.title("Expense Visualizations")
        self.window.geometry("1200x700")
        self.expenses = expenses
        self.analytics = ExpenseAnalytics()
        self.theme = theme
        self.window.configure(bg=self.theme["bg"])

        self._create_widgets()

    def _create_widgets(self):
        control_frame = tk.Frame(self.window, bg=self.theme["frame_bg"])
        control_frame.pack(side=tk.TOP, fill=tk.X)

        def create_viz_button(text, command):
            btn = tk.Button(
                control_frame,
                text=text,
                command=command,
                font=self.theme["btn_font"],
                bg=self.theme["btn_bg"],
                fg="white",
                activebackground=self.theme["btn_hover"],
                relief=tk.FLAT,
                padx=10,
                pady=5,
            )
            btn.pack(side=tk.LEFT, padx=10, pady=10)
            return btn

        create_viz_button("Monthly Trend", self.show_monthly_trend)
        create_viz_button("Category Pie Chart", self.show_category_pie)
        create_viz_button("Payment Mode Chart", self.show_payment_mode)

        self.canvas_frame = tk.Frame(self.window)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.show_monthly_trend()

    def clear_canvas(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

    def show_monthly_trend(self):
        self.clear_canvas()
        if not self.expenses:
            tk.Label(
                self.canvas_frame,
                text="No data available to visualize",
                font=("Arial", 14),
            ).pack(pady=50)
            return

        monthly_data = self.analytics.get_monthly_expenses(self.expenses)
        if not monthly_data:
            tk.Label(
                self.canvas_frame, text="No monthly data available", font=("Arial", 14)
            ).pack(pady=50)
            return

        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        months = list(monthly_data.keys())
        amounts = list(monthly_data.values())

        ax.plot(months, amounts, marker="o", linewidth=2, markersize=8, color="#2196F3")
        ax.fill_between(range(len(months)), amounts, alpha=0.3, color="#2196F3")
        ax.set_xlabel("Month", fontsize=12, fontweight="bold")
        ax.set_ylabel("Amount Spent", fontsize=12, fontweight="bold")
        ax.set_title("Monthly Expense Trend", fontsize=14, fontweight="bold")
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_category_pie(self):
        self.clear_canvas()
        if not self.expenses:
            tk.Label(
                self.canvas_frame,
                text="No data available to visualize",
                font=("Arial", 14),
            ).pack(pady=50)
            return

        category_data = self.analytics.get_category_expenses(self.expenses)

        sorted_categories = sorted(
            category_data.items(), key=lambda x: x[1], reverse=True
        )
        if len(sorted_categories) > 10:
            top_10 = dict(sorted_categories[:10])
            others_sum = sum([x[1] for x in sorted_categories[10:]])
            top_10["Others"] = others_sum
            category_data = top_10

        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        labels = list(category_data.keys())
        sizes = list(category_data.values())
        colors = plt.cm.Set3(range(len(labels)))

        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90
        )
        for autotext in autotexts:
            autotext.set_color("black")
            autotext.set_fontweight("bold")

        ax.set_title("Expense Distribution by Category", fontsize=14, fontweight="bold")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_payment_mode(self):
        self.clear_canvas()
        if not self.expenses:
            tk.Label(
                self.canvas_frame,
                text="No data available to visualize",
                font=("Arial", 14),
            ).pack(pady=50)
            return

        mode_data = self.analytics.get_payment_mode_expenses(self.expenses)
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        modes = list(mode_data.keys())
        amounts = list(mode_data.values())
        colors = plt.cm.Paired(range(len(modes)))

        bars = ax.bar(modes, amounts, color=colors, edgecolor="black", linewidth=1.2)
        ax.set_xlabel("Payment Mode", fontsize=12, fontweight="bold")
        ax.set_ylabel("Total Amount", fontsize=12, fontweight="bold")
        ax.set_title("Expenses by Payment Mode", fontsize=14, fontweight="bold")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", alpha=0.3)

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"₹{height:.2f}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_prediction(self):
        self.clear_canvas()
        if not self.expenses or len(self.expenses) < 2:
            tk.Label(
                self.canvas_frame,
                text="Need at least 2 months of data for prediction",
                font=("Arial", 14),
            ).pack(pady=50)
            return

        monthly_data = self.analytics.get_monthly_expenses(self.expenses)
        if len(monthly_data) < 2:
            tk.Label(
                self.canvas_frame,
                text="Need at least 2 months of data for prediction",
                font=("Arial", 14),
            ).pack(pady=50)
            return

        predictions = self.analytics.predict_future_expenses(
            monthly_data, months_ahead=3
        )
        if predictions is None:
            tk.Label(
                self.canvas_frame,
                text="Could not generate prediction (not enough data)",
                font=("Arial", 14),
            ).pack(pady=50)
            return

        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        hist_months = list(monthly_data.keys())
        hist_amounts = list(monthly_data.values())
        pred_months = list(predictions.keys())
        pred_amounts = list(predictions.values())

        ax.plot(
            hist_months,
            hist_amounts,
            marker="o",
            linewidth=2,
            markersize=8,
            color="#2196F3",
            label="Historical",
        )
        ax.plot(
            pred_months,
            pred_amounts,
            marker="s",
            linewidth=2,
            markersize=8,
            color="#FF5722",
            linestyle="--",
            label="Predicted",
        )
        ax.plot(
            [hist_months[-1], pred_months[0]],
            [hist_amounts[-1], pred_amounts[0]],
            linewidth=2,
            color="gray",
            linestyle=":",
            alpha=0.5,
        )

        ax.set_xlabel("Month", fontsize=12, fontweight="bold")
        ax.set_ylabel("Amount", fontsize=12, fontweight="bold")
        ax.set_title(
            "Expense Prediction (Next 3 Months)", fontsize=14, fontweight="bold"
        )
        ax.legend(loc="best", fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis="x", rotation=45)

        for i, (month, amount) in enumerate(predictions.items()):
            ax.text(
                len(hist_months) + i,
                amount,
                f"₹{amount:.0f}",
                ha="center",
                va="bottom",
                fontweight="bold",
                color="#FF5722",
            )
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


class ExpenseTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.db_manager = DatabaseManager()

        self.bg_color = "#F4F6F7"
        self.frame_bg = "#FFFFFF"
        self.accent = "#1ABC9C"
        self.btn_bg = "#16A085"
        self.btn_hover = "#138D75"
        self.lbl_color = "#2C3E50"
        self.entry_bg = "#ECF0F1"
        self.entry_fg = "#2C3E50"
        self.tree_hover = "#138D75"

        self.lbl_font = ("Segoe UI", 11, "bold")
        self.entry_font = ("Segoe UI", 11)
        self.btn_font = ("Segoe UI Semibold", 11)
        self.dashboard_font = ("Segoe UI", 14, "bold")
        self.dashboard_val_font = ("Segoe UI", 18, "bold")

        self.theme = {
            "bg": self.bg_color,
            "frame_bg": self.frame_bg,
            "accent": self.accent,
            "btn_bg": self.btn_bg,
            "btn_hover": self.btn_hover,
            "lbl_font": self.lbl_font,
            "btn_font": self.btn_font,
        }

        self.desc = tk.StringVar()
        self.amnt = tk.DoubleVar()
        self.payee = tk.StringVar()
        self.MoP = tk.StringVar(value="Cash")
        self.category = tk.StringVar(value="Food")

        self._setup_window()
        self._create_widgets()
        self.list_all_expenses()

    def _setup_window(self):
        self.root.title("Expense Tracker")
        self.root.geometry("1300x670")
        self.root.resizable(0, 0)
        self.root.configure(bg=self.bg_color)

        tk.Label(
            self.root,
            text="💰 EXPENSE TRACKER DASHBOARD",
            font=("Segoe UI Black", 15, "bold"),
            bg=self.accent,
            fg="white",
            pady=8,
        ).pack(side=tk.TOP, fill=tk.X)

    def _create_widgets(self):
        self._create_frames()
        self._create_dashboard_widgets()
        self._create_data_entry_widgets()
        self._create_button_widgets()
        self._create_treeview()

    def _create_frames(self):
        title_bar_height = 40
        total_height = 600 - title_bar_height

        self.data_entry_frame = tk.Frame(
            self.root, bg=self.frame_bg, bd=2, relief=tk.GROOVE
        )
        self.data_entry_frame.place(
            x=0, y=title_bar_height, relwidth=0.30, relheight=0.933
        )

        self.dashboard_frame = tk.Frame(
            self.root, bg=self.frame_bg, bd=2, relief=tk.GROOVE
        )
        self.dashboard_frame.place(
            relx=0.30,
            y=title_bar_height,
            relwidth=0.70,
            relheight=0.20,
        )

        self.tree_frame = tk.Frame(self.root, bg=self.frame_bg, bd=2, relief=tk.GROOVE)
        self.tree_frame.place(
            relx=0.30,
            y=title_bar_height + (total_height * 0.20),
            relwidth=0.70,
            relheight=0.55,
        )

        self.buttons_frame = tk.Frame(
            self.root, bg=self.frame_bg, bd=2, relief=tk.GROOVE
        )
        self.buttons_frame.place(
            relx=0.30,
            y=title_bar_height + (total_height * (0.15 + 0.50)),
            relwidth=0.70,
            relheight=0.3875,
        )

    def _create_dashboard_widgets(self):
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(1, weight=1)
        self.dashboard_frame.grid_rowconfigure(0, weight=1)

        spent_frame = tk.Frame(self.dashboard_frame, bg=self.frame_bg)
        spent_frame.grid(row=0, column=0, sticky="nsew")

        tk.Label(
            spent_frame,
            text="Total Spent (All Time)",
            font=self.dashboard_font,
            bg=self.frame_bg,
            fg=self.lbl_color,
        ).pack(pady=(10, 0))
        self.total_spent_label = tk.Label(
            spent_frame,
            text="₹0.00",
            font=self.dashboard_val_font,
            bg=self.frame_bg,
            fg=self.btn_bg,
        )
        self.total_spent_label.pack(expand=True)

        count_frame = tk.Frame(self.dashboard_frame, bg=self.frame_bg)
        count_frame.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            count_frame,
            text="Total Expenses",
            font=self.dashboard_font,
            bg=self.frame_bg,
            fg=self.lbl_color,
        ).pack(pady=(10, 0))
        self.total_count_label = tk.Label(
            count_frame,
            text="0",
            font=self.dashboard_val_font,
            bg=self.frame_bg,
            fg=self.btn_bg,
        )
        self.total_count_label.pack(expand=True)

    def _create_data_entry_widgets(self):
        self.data_entry_frame.grid_columnconfigure(0, weight=1)
        self.data_entry_frame.grid_columnconfigure(1, weight=2)

        grid_pad_x = 10
        grid_pad_y = 15.65
        entry_width = 30

        tk.Label(
            self.data_entry_frame,
            text="Date(MM/DD/YY):",
            font=self.lbl_font,
            bg=self.frame_bg,
            fg=self.lbl_color,
        ).grid(row=0, column=0, sticky="w", padx=grid_pad_x, pady=grid_pad_y)
        self.date = DateEntry(
            self.data_entry_frame,
            date=datetime.datetime.now().date(),
            font=self.entry_font,
            background=self.accent,
            foreground="white",
            width=entry_width - 2,
        )
        self.date.grid(row=0, column=1, sticky="ew", padx=grid_pad_x, pady=grid_pad_y)

        tk.Label(
            self.data_entry_frame,
            text="Description:",
            font=self.lbl_font,
            bg=self.frame_bg,
            fg=self.lbl_color,
        ).grid(row=1, column=0, sticky="w", padx=grid_pad_x, pady=grid_pad_y)
        entrydesc = tk.Entry(
            self.data_entry_frame,
            font=self.entry_font,
            width=entry_width,
            textvariable=self.desc,
            bg=self.entry_bg,
            fg=self.entry_fg,
            relief=tk.FLAT,
        )
        entrydesc.grid(row=1, column=1, sticky="ew", padx=grid_pad_x, pady=grid_pad_y)
        entrydesc.insert(0, "e.g., Coffee, Bus fare")
        entrydesc.bind(
            "<FocusIn>",
            lambda e: entrydesc.delete(0, tk.END)
            if entrydesc.get() == "e.g., Coffee, Bus fare"
            else None,
        )

        tk.Label(
            self.data_entry_frame,
            text="Amount:",
            font=self.lbl_font,
            bg=self.frame_bg,
            fg=self.lbl_color,
        ).grid(row=2, column=0, sticky="w", padx=grid_pad_x, pady=grid_pad_y)
        tk.Entry(
            self.data_entry_frame,
            font=self.entry_font,
            width=entry_width,
            textvariable=self.amnt,
            bg=self.entry_bg,
            fg=self.entry_fg,
            relief=tk.FLAT,
        ).grid(row=2, column=1, sticky="ew", padx=grid_pad_x, pady=grid_pad_y)

        tk.Label(
            self.data_entry_frame,
            text="Payee/Store:",
            font=self.lbl_font,
            bg=self.frame_bg,
            fg=self.lbl_color,
        ).grid(row=3, column=0, sticky="w", padx=grid_pad_x, pady=grid_pad_y)
        entry_payee = tk.Entry(
            self.data_entry_frame,
            font=self.entry_font,
            width=entry_width,
            textvariable=self.payee,
            bg=self.entry_bg,
            fg=self.entry_fg,
            relief=tk.FLAT,
        )
        entry_payee.grid(row=3, column=1, sticky="ew", padx=grid_pad_x, pady=grid_pad_y)
        entry_payee.insert(0, "e.g. Madhav,V-Mart ")
        entry_payee.bind(
            "<FocusIn>",
            lambda e: entry_payee.delete(0, tk.END)
            if entry_payee.get() == "e.g. Madhav,V-Mart "
            else None,
        )

        tk.Label(
            self.data_entry_frame,
            text="Category:",
            font=self.lbl_font,
            bg=self.frame_bg,
            fg=self.lbl_color,
        ).grid(row=4, column=0, sticky="w", padx=grid_pad_x, pady=grid_pad_y)
        categories = [
            "Food",
            "Transport",
            "Groceries",
            "Utilities",
            "Rent",
            "Entertainment",
            "Health",
            "Shopping",
            "Other",
        ]
        self.category_dd = ttk.Combobox(
            self.data_entry_frame,
            textvariable=self.category,
            values=categories,
            font=self.entry_font,
            width=entry_width - 2,
        )
        self.category_dd.grid(
            row=4, column=1, sticky="ew", padx=grid_pad_x, pady=grid_pad_y
        )

        tk.Label(
            self.data_entry_frame,
            text="Payment Mode:",
            font=self.lbl_font,
            bg=self.frame_bg,
            fg=self.lbl_color,
        ).grid(row=5, column=0, sticky="w", padx=grid_pad_x, pady=grid_pad_y)
        dd1 = tk.OptionMenu(
            self.data_entry_frame,
            self.MoP,
            "Cash",
            "Credit Card",
            "Debit Card",
            "Google Pay",
            "PhonePe",
            "Paytm",
            "Cheque",
        )
        dd1.grid(row=5, column=1, sticky="ew", padx=grid_pad_x, pady=grid_pad_y)
        dd1.configure(
            font=self.entry_font,
            bg=self.entry_bg,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
        )

        btn_add = self._create_button(
            self.data_entry_frame, "➕ Add Expense", self.add_expense
        )
        btn_add.grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=grid_pad_x, pady=(20, 10)
        )
        btn_convert = self._create_button(
            self.data_entry_frame,
            "Convert to Words Before Adding",
            self.expense_to_words_before_adding,
        )
        btn_convert.grid(
            row=7, column=0, columnspan=2, sticky="ew", padx=grid_pad_x, pady=grid_pad_y
        )

    def _create_button_widgets(self):
        actions = [
            ("🔍 View Details", self.view_expense_details),
            ("✏️ Edit Expense", self.edit_expense),
            ("🧹 Clear Fields", self.clear_fields),
            ("🗑️ Delete Expense", self.remove_expense),
            ("⚠️ Delete All Expenses", self.remove_all_expenses),
            ("💬 Convert to Sentence", self.selected_expense_to_words),
            ("📊 Visualize Expenses", self.open_visualization),
            ("🤖 Predict Future", self.show_prediction_only),
            ("❌ Quit Application", self.exit_app),
        ]

        for i, (text, cmd) in enumerate(actions):
            row = i // 3
            col = i % 3
            btn = tk.Button(
                self.buttons_frame,
                text=text,
                font=self.btn_font,
                width=28,
                bg=self.btn_bg,
                fg="white",
                activebackground=self.btn_hover,
                relief=tk.FLAT,
                cursor="hand2",
                command=cmd,
            )
            btn.grid(row=row, column=col, padx=20, pady=15, sticky="ew")
            btn.bind("<Enter>", self._on_enter)
            btn.bind("<Leave>", self._on_leave)

        for i in range(3):
            self.buttons_frame.grid_columnconfigure(i, weight=1)

    def _create_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            font=self.btn_font,
            bg=self.btn_bg,
            fg="white",
            activebackground=self.btn_hover,
            relief=tk.FLAT,
            cursor="hand2",
            command=command,
        )
        btn.bind("<Enter>", self._on_enter)
        btn.bind("<Leave>", self._on_leave)
        return btn

    def _on_enter(self, e):
        e.widget["background"] = self.btn_hover

    def _on_leave(self, e):
        e.widget["background"] = self.btn_bg

    def _create_treeview(self):
        self.table = ttk.Treeview(
            self.tree_frame,
            selectmode=tk.BROWSE,
            columns=(
                "ID",
                "Date",
                "Payee",
                "Description",
                "Amount",
                "Mode of Payment",
                "Category",
            ),
        )

        X_Scroller = tk.Scrollbar(
            self.table, orient=tk.HORIZONTAL, command=self.table.xview
        )
        Y_Scroller = tk.Scrollbar(
            self.table, orient=tk.VERTICAL, command=self.table.yview
        )
        X_Scroller.pack(side=tk.BOTTOM, fill=tk.X)
        Y_Scroller.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.config(yscrollcommand=Y_Scroller.set, xscrollcommand=X_Scroller.set)

        columns_config = [
            ("ID", "S No.", 50),
            ("Date", "Date", 100),
            ("Payee", "Payee", 140),
            ("Description", "Description", 250),
            ("Amount", "Amount", 100),
            ("Mode of Payment", "Mode", 100),
            ("Category", "Category", 120),
        ]

        for col, text, width in columns_config:
            self.table.heading(col, text=text, anchor=tk.CENTER)
            self.table.column(col, width=width, anchor=tk.CENTER, stretch=True)

        self.table.column("#0", width=0, stretch=tk.NO)
        self.table.place(relx=0, y=0, relheight=1, relwidth=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background=self.frame_bg,
            foreground=self.lbl_color,
            rowheight=25,
            fieldbackground=self.frame_bg,
            bordercolor=self.bg_color,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI Semibold", 11),
            background=self.accent,
            foreground="white",
        )
        style.map(
            "Treeview",
            background=[("selected", self.btn_bg), ("active", self.tree_hover)],
            foreground=[("active", self.lbl_color)],
        )

    def list_all_expenses(self):
        self.table.delete(*self.table.get_children())
        data = self.db_manager.get_all_expenses()
        total_spent = 0.0
        total_count = 0
        for values in data:
            self.table.insert("", tk.END, values=values)
            total_spent += values[4]
            total_count += 1
        self.total_spent_label.config(text=f"₹{total_spent:,.2f}")
        self.total_count_label.config(text=str(total_count))

    def view_expense_details(self):
        if not self.table.selection():
            mb.showerror(
                "No expense selected",
                "Please select an expense to view.",
                parent=self.root,
            )
            return

        current_selected_expense = self.table.item(self.table.focus())
        values = current_selected_expense["values"]
        expenditure_date = datetime.date(
            int(values[1][:4]), int(values[1][5:7]), int(values[1][8:])
        )
        self.date.set_date(expenditure_date)
        self.payee.set(values[2])
        self.desc.set(values[3])
        self.amnt.set(values[4])
        self.MoP.set(values[5])
        self.category.set(values[6])

    def clear_fields(self):
        today_date = datetime.datetime.now().date()
        self.desc.set("e.g., Coffee, Bus fare")
        self.payee.set("e.g., V-Mart, Madhav")
        self.amnt.set(0.0)
        self.MoP.set("Cash")
        self.category.set("Food")
        self.date.set_date(today_date)
        self.table.selection_remove(*self.table.selection())

    def remove_expense(self):
        if not self.table.selection():
            mb.showerror(
                "No record selected!",
                "Please select a record to delete!",
                parent=self.root,
            )
            return

        current_selected_expense = self.table.item(self.table.focus())
        values_selected = current_selected_expense["values"]
        if mb.askyesno(
            "Confirm", f"Delete record of {values_selected[2]}?", parent=self.root
        ):
            self.db_manager.delete_expense(values_selected[0])
            self.list_all_expenses()
            mb.showinfo("Deleted", "Record deleted successfully.", parent=self.root)

    def remove_all_expenses(self):
        if mb.askyesno(
            "Confirm", "Delete all expenses?", icon="warning", parent=self.root
        ):
            self.db_manager.delete_all_expenses()
            self.clear_fields()
            self.list_all_expenses()
            mb.showinfo(
                "All Deleted", "All expenses deleted successfully.", parent=self.root
            )

    def add_expense(self):
        try:
            date = self.date.get_date()
            payee = self.payee.get()
            desc = self.desc.get()
            amount = self.amnt.get()
            mode = self.MoP.get()
            category = self.category.get()

            placeholders = ["e.g., Coffee, Bus fare", "e.g., V-Mart, Madhav"]
            if desc in placeholders or payee in placeholders:
                mb.showerror(
                    "Missing Fields", "Please fill all fields!", parent=self.root
                )
                return

            if not all([date, payee, desc, mode, category]):
                mb.showerror(
                    "Missing Fields", "Please fill all fields!", parent=self.root
                )
                return

            if amount <= 0:
                mb.showerror(
                    "Invalid Amount", "Amount must be greater than 0.", parent=self.root
                )
                return

        except tk.TclError:
            mb.showerror(
                "Invalid Amount",
                "Please enter a valid number for Amount.",
                parent=self.root,
            )
            return

        self.db_manager.add_expense(date, payee, desc, amount, mode, category)
        self.clear_fields()
        self.list_all_expenses()
        mb.showinfo("Expense Added", "Expense successfully added!", parent=self.root)

    def edit_expense(self):
        if not self.table.selection():
            mb.showerror("No Selection", "Select an expense to edit!", parent=self.root)
            return

        self.view_expense_details()

        def edit_existing_expense():
            current_selected_expense = self.table.item(self.table.focus())
            contents = current_selected_expense["values"]

            try:
                date = self.date.get_date()
                payee = self.payee.get()
                desc = self.desc.get()
                amount = self.amnt.get()
                mode = self.MoP.get()
                category = self.category.get()

                if amount <= 0:
                    mb.showerror(
                        "Invalid Amount",
                        "Amount must be greater than 0.",
                        parent=self.root,
                    )
                    return

            except tk.TclError:
                mb.showerror(
                    "Invalid Amount",
                    "Please enter a valid number for Amount.",
                    parent=self.root,
                )
                return

            self.db_manager.update_expense(
                contents[0], date, payee, desc, amount, mode, category
            )
            self.clear_fields()
            self.list_all_expenses()
            mb.showinfo("Edited", "Expense updated successfully!", parent=self.root)
            edit_btn.destroy()

        edit_btn = self._create_button(
            self.data_entry_frame, "✏️ Save Changes", edit_existing_expense
        )
        edit_btn.grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=(20, 10)
        )

    def selected_expense_to_words(self):
        if not self.table.selection():
            mb.showerror(
                "No expense selected!",
                "Please select an expense to read.",
                parent=self.root,
            )
            return

        values = self.table.item(self.table.focus())["values"]
        message = f"You paid ₹{values[4]} to {values[2]} for {values[3]} (Category: {values[6]}) on {values[1]} via {values[5]}"
        mb.showinfo("Expense Summary", message, parent=self.root)

    def expense_to_words_before_adding(self):
        try:
            amount = self.amnt.get()
            if amount <= 0:
                mb.showerror(
                    "Invalid Amount", "Amount must be greater than 0.", parent=self.root
                )
                return
        except tk.TclError:
            mb.showerror(
                "Invalid Amount",
                "Please enter a valid number for Amount.",
                parent=self.root,
            )
            return

        message = (
            f"You are about to add:\n\n"
            f"Amount: ₹{self.amnt.get()}\n"
            f"Payee: {self.payee.get()}\n"
            f"Category: {self.category.get()}\n"
            f"Date: {self.date.get_date()}\n"
            f"Mode: {self.MoP.get()}\n\n"
            "Add to database?"
        )

        if mb.askyesno("Confirm", message, parent=self.root):
            self.add_expense()

    def open_visualization(self):
        expenses = self.db_manager.get_all_expenses()
        if not expenses:
            mb.showinfo(
                "No Data", "Add some expenses before visualizing.", parent=self.root
            )
            return
        VisualizationWindow(self.root, expenses, self.theme)

    def show_prediction_only(self):
        expenses = self.db_manager.get_all_expenses()
        if not expenses:
            mb.showinfo(
                "Insufficient Data",
                "Add expenses to enable prediction.",
                parent=self.root,
            )
            return

        monthly_data = ExpenseAnalytics.get_monthly_expenses(expenses)
        if len(monthly_data) < 2:
            mb.showinfo(
                "Insufficient Data",
                "Need at least 2 months of data for prediction.",
                parent=self.root,
            )
            return

        viz_window = VisualizationWindow(self.root, expenses, self.theme)
        viz_window.show_prediction()

    def exit_app(self):
        if mb.askyesno(
            "Exit Application", "Are you sure you want to quit?", parent=self.root
        ):
            self.root.destroy()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.mainloop()

    def cleanup(self):
        self.db_manager.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerGUI(root)
    try:
        app.run()
    finally:
        app.cleanup()

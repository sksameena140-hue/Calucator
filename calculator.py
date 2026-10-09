
import ast
import operator
import tkinter as tk
from tkinter import messagebox


# Safe arithmetic operations
OPERATIONS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_calculate(expression):
    """Evaluate basic arithmetic without executing arbitrary code."""
    if len(expression) > 200:
        raise ValueError("Expression is too long")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value
            raise ValueError("Invalid number")

        if isinstance(node, ast.BinOp):
            operation = OPERATIONS.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported operation")

            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError("Cannot divide by zero")

            result = operation(left, right)
            if abs(result) > 1e100:
                raise ValueError("Result is too large")
            return result

        if isinstance(node, ast.UnaryOp):
            operation = OPERATIONS.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported operation")
            return operation(evaluate(node.operand))

        raise ValueError("Invalid expression")

    result = evaluate(tree)
    if isinstance(result, float):
        if not float("-inf") < result < float("inf"):
            raise ValueError("Invalid result")
    return result


class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Desktop Calculator")
        self.root.geometry("350x480")
        self.root.resizable(False, False)
        self.root.configure(bg="#172033")

        self.expression = tk.StringVar(value="0")
        self.just_calculated = False

        # Display
        display = tk.Entry(
            root,
            textvariable=self.expression,
            font=("Arial", 25),
            justify="right",
            state="readonly",
            readonlybackground="#263449",
            fg="white",
            bd=0,
            relief="flat",
            insertwidth=0
        )
        display.pack(fill="x", padx=15, pady=(20, 15), ipady=18)

        # Button layout
        buttons = [
            ["C", "DEL", "(", ")"],
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"],
        ]

        for row_index, row in enumerate(buttons):
            frame = tk.Frame(root, bg="#172033")
            frame.pack(expand=True, fill="both", padx=10)

            for col_index, label in enumerate(row):
                color = "#42536b"
                if label in ("+", "-", "*", "/"):
                    color = "#e58b35"
                elif label == "=":
                    color = "#218c74"
                elif label in ("C", "DEL"):
                    color = "#a84150"

                button = tk.Button(
                    frame,
                    text=label,
                    font=("Arial", 16, "bold"),
                    bg=color,
                    fg="white",
                    activebackground="#62758c",
                    activeforeground="white",
                    bd=0,
                    cursor="hand2",
                    command=lambda value=label: self.press(value)
                )
                button.grid(
                    row=0,
                    column=col_index,
                    sticky="nsew",
                    padx=4,
                    pady=4
                )
                frame.grid_columnconfigure(col_index, weight=1)

            frame.grid_rowconfigure(0, weight=1)

        # Keyboard support
        self.root.bind("<Key>", self.keyboard_input)
        self.root.bind("<Return>", lambda event: self.press("="))
        self.root.bind("<Escape>", lambda event: self.press("C"))
        self.root.bind("<BackSpace>", lambda event: self.press("DEL"))

    def press(self, value):
        current = self.expression.get()

        if value == "C":
            self.expression.set("0")
            self.just_calculated = False
            return

        if value == "DEL":
            if self.just_calculated:
                self.expression.set("0")
                self.just_calculated = False
            else:
                self.expression.set(current[:-1] or "0")
            return

        if value == "=":
            try:
                result = safe_calculate(current)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                self.expression.set(str(result))
                self.just_calculated = True
            except ZeroDivisionError:
                messagebox.showerror(
                    "Math Error", "Cannot divide by zero."
                )
                self.expression.set("0")
                self.just_calculated = False
            except (ValueError, SyntaxError, OverflowError):
                messagebox.showerror(
                    "Input Error", "Please enter a valid expression."
                )
                self.expression.set("0")
                self.just_calculated = False
            return

        allowed = "0123456789.+-*/()"
        if value not in allowed:
            return

        if self.just_calculated:
            if value in "+-*/":
                self.expression.set(current + value)
            else:
                self.expression.set(value)
            self.just_calculated = False
            return

        if current == "0":
            self.expression.set(value if value != "." else "0.")
        else:
            self.expression.set(current + value)

    def keyboard_input(self, event):
        char = event.char
        if char in "0123456789.+-*/()":
            self.press(char)


if __name__ == "__main__":
    window = tk.Tk()
    calculator = Calculator(window)
    window.mainloop()
import tkinter as tk
from tkinter import messagebox
import os

class StudyPlannerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Study Planner - Login/Register")
        self.root.geometry("450x400")
        self.root.configure(bg='#f0f0f0')
        self.current_user = None
        self.show_login()
    
    def show_login(self):
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Study Planner & Reminder App", 
                font=("Arial", 20, "bold"), bg='#f0f0f0').pack(pady=20)
        
        tk.Label(self.root, text="Username:", font=("Arial", 12), bg='#f0f0f0').pack()
        self.login_username = tk.Entry(self.root, font=("Arial", 12), width=25)
        self.login_username.pack(pady=5)
        self.login_username.focus()
        
        tk.Label(self.root, text="Password:", font=("Arial", 12), bg='#f0f0f0').pack()
        self.login_password = tk.Entry(self.root, font=("Arial", 12), show="*", width=25)
        self.login_password.pack(pady=5)
        
        tk.Button(self.root, text="Login", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                 command=self.login_user, width=15).pack(pady=10)
        
        tk.Button(self.root, text="Register New User", font=("Arial", 11), bg="#2196F3", fg="white",
                 command=self.show_register, width=20).pack(pady=5)
    
    def show_register(self):
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Register New Account", 
                font=("Arial", 20, "bold"), bg='#f0f0f0').pack(pady=20)
        
        tk.Label(self.root, text="New Username:", font=("Arial", 12), bg='#f0f0f0').pack()
        self.reg_username = tk.Entry(self.root, font=("Arial", 12), width=25)
        self.reg_username.pack(pady=5)
        self.reg_username.focus()
        
        tk.Label(self.root, text="New Password:", font=("Arial", 12), bg='#f0f0f0').pack()
        self.reg_password = tk.Entry(self.root, font=("Arial", 12), show="*", width=25)
        self.reg_password.pack(pady=5)
        
        tk.Label(self.root, text="Confirm Password:", font=("Arial", 12), bg='#f0f0f0').pack()
        self.reg_confirm = tk.Entry(self.root, font=("Arial", 12), show="*", width=25)
        self.reg_confirm.pack(pady=5)
        
        tk.Button(self.root, text="Register", font=("Arial", 12, "bold"), bg="#FF9800", fg="white",
                 command=self.register_user, width=15).pack(pady=10)
        
        tk.Button(self.root, text="Back to Login", font=("Arial", 11), bg="#757575", fg="white",
                 command=self.show_login, width=15).pack()
    
    def register_user(self):
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        confirm = self.reg_confirm.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Fill all fields!")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords don't match!")
            return
        
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be 4+ characters!")
            return
        
        # Check if user exists
        user_file = f"users/{username}.txt"
        if os.path.exists(user_file):
            messagebox.showerror("Error", "Username already exists!")
            return
        
        # Create users folder
        os.makedirs("users", exist_ok=True)
        
        # Save user
        with open(user_file, 'w') as f:
            f.write(password)
        
        messagebox.showinfo("Success", f"Account created for {username}!")
        self.show_login()
    
    def login_user(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Enter username and password!")
            return
        
        user_file = f"users/{username}.txt"
        if not os.path.exists(user_file):
            messagebox.showerror("Error", "User not found! Register first.")
            return
        
        # Check password
        with open(user_file, 'r') as f:
            saved_password = f.read().strip()
        
        if password == saved_password:
            self.current_user = username
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Wrong password!")
    
    def show_dashboard(self):
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title(f"Study Planner - Welcome {self.current_user}")
        self.root.geometry("400x500")
        
        tk.Label(self.root, text=f"Welcome to Study Planner & Reminder App, {self.current_user}!", 
                font=("Arial", 20, "bold"), bg='White').pack(pady=30)
        
        tk.Label(self.root, text="•Your Study Dashboard:\n• Add Tasks\n• Set Reminders\n• Notification for upcoming deadlines\n•", 
                font=("Arial", 14), bg='Light pink').pack(pady=20)

        tk.Button(self.root, text="Logout", font=("Arial", 12), bg="#f44336", fg="white",
                 command=self.show_login, width=15).pack(pady=20)
    
    def run(self):
        self.root.configure(bg='sky blue')
        self.root.mainloop()

if __name__ == "__main__":
    app = StudyPlannerApp()
    app.run()

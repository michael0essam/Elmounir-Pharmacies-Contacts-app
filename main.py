import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import atexit
import os.path
import logging
from drive_sync import queue_change, download_changes, upload_changes, upload_offline_changes, get_service


class ContactApp:
    def __init__(self, root):
        self.root = root
        self.conn = sqlite3.connect("contacts.db")
        self.cursor = self.conn.cursor()
        self.create_table()
        self.create_gui()
        self.root.title("Elmounir Contacts Application programmed by: Michael Essam")
        self.root.resizable(True, True)
        self.root.configure(bg="#333333")
    
    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY,
                name TEXT,
                company TEXT,
                card1 TEXT,
                card2 TEXT,
                phone TEXT
            )
        """)
        self.conn.commit()

    def create_gui(self):

        # Create main frame
        self.main_frame = tk.Frame(self.root,bg="#333333")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        for i in range(7):
            self.main_frame.grid_rowconfigure(i, weight=0)
            self.main_frame.grid_rowconfigure(7, weight=1)
        for i in range(5):
            self.main_frame.grid_columnconfigure(i, weight=1)

        # Input fields
        tk.Label(self.main_frame, text="ID:            ", font=("Arial", 20), bg="gray30", fg="#ffffff").grid(row=0, column=0, sticky="w")
        self.id_entry = tk.Entry(self.main_frame, font=("Arial", 18), width=25)
        self.id_entry.grid(row=0, column=1, sticky="ew")
        tk.Button(self.main_frame, text="ID Search", command=self.id_search, font=("Arial", 14), bg="#4CAF50", fg="#ffffff").grid(row=0, column=2, sticky="ew")

        tk.Label(self.main_frame, text="Name:      ", font=("Arial", 20), bg="gray30", fg="#ffffff").grid(row=1, column=0, sticky="w")
        self.name_entry = tk.Entry(self.main_frame, font=("Arial", 18), width=25)
        self.name_entry.grid(row=1, column=1, sticky="ew")
        tk.Button(self.main_frame, text="Name Search", command=self.name_search, font=("Arial", 14), bg="#4CAF50", fg="#ffffff").grid(row=1, column=2, sticky="ew")

        tk.Label(self.main_frame, text="Company: ", font=("Arial", 20), bg="gray30", fg="#ffffff").grid(row=2, column=0, sticky="w")
        self.company = tk.StringVar()
        companies = ["","MetLife", "AXA", "Limitless Care", "Others"]
        self.company_menu = ttk.OptionMenu(self.main_frame, self.company, companies[0], *companies)
        self.company_menu.grid(row=2, column=1, sticky="ew")
        tk.Button(self.main_frame, text="Company Search", command=self.Company_search, font=("Arial", 14), bg="#4CAF50", fg="#ffffff").grid(row=2, column=2, sticky="ew")
        tk.Button(self.main_frame, text="Update Company", command=self.update_company, font=("Arial", 14), bg="#4CAF50", fg="#ffffff").grid(row=2, column=3, sticky="ew")

        tk.Label(self.main_frame, text="Card 1:     ", font=("Arial", 20), bg="gray30", fg="#ffffff").grid(row=3, column=0, sticky="w")
        self.card1_entry = tk.Entry(self.main_frame, font=("Arial", 18), width=25)
        self.card1_entry.grid(row=3, column=1, sticky="ew")
        tk.Button(self.main_frame, text="Card 1 Search", command=self.card1_search, font=("Arial", 14), bg="#4CAF50", fg="#ffffff").grid(row=3, column=2, sticky="ew")
        tk.Button(self.main_frame, text="Update Card 1", command=self.update_card1, font=("Arial", 14), bg="#4CAF50", fg="#ffffff").grid(row=3, column=3, sticky="ew")

        tk.Label(self.main_frame, text="Card 2:     ", font=("Arial", 20), bg="gray30", fg="#ffffff").grid(row=4, column=0, sticky="w")
        self.card2_entry = tk.Entry(self.main_frame, font=("Arial", 18), width=25)
        self.card2_entry.grid(row=4, column=1, sticky="ew")
        tk.Button(self.main_frame, text="Card 2 Search", command=self.card2_search, font=("Arial", 14), bg="#4CAF50", fg="#ffffff").grid(row=4, column=2, sticky="ew")
        tk.Button(self.main_frame, text="Update Card 2", command=self.update_card2, font=("Arial", 14), bg="#4CAF50", fg="#ffffff").grid(row=4, column=3, sticky="ew")

        tk.Label(self.main_frame, text="Phone:      ", font=("Arial", 20), bg="gray30", fg="#ffffff").grid(row=5, column=0, sticky="w")
        self.phone_entry = tk.Entry(self.main_frame, font=("Arial", 18), width=25)
        self.phone_entry.grid(row=5, column=1, sticky="ew")
        tk.Button(self.main_frame, text="Phone Search", command=self.phone_search, font=("Arial", 14), bg="#4CAF50", fg="#ffffff").grid(row=5, column=2, sticky="ew")
        tk.Button(self.main_frame, text="Update Phone", command=self.update_phone, font=("Arial", 14), bg="#4CAF50", fg="#ffffff").grid(row=5, column=3, sticky="ew")

        # Buttons
        tk.Button(self.main_frame, text="Display Contacts", command=self.display_contacts, font=("Arial", 14), bg="#ff7300", fg="#ffffff").grid(row=6, column=0, sticky="ew")
        tk.Button(self.main_frame, text="Add Contact", command=self.add_contact, font=("Arial", 14), bg="#ff7300", fg="#ffffff").grid(row=6, column=1, sticky="ew")
        tk.Button(self.main_frame, text="Delete Contact", command=self.delete_contact, font=("Arial", 14), bg="#ff7300", fg="#ffffff").grid(row=6, column=2, sticky="ew")

        # Output field
        self.output_text = tk.Text(self.main_frame, font=("Arial", 20), bg="#333333", fg="#ffffff")
        self.output_text.grid(row=7, column=0, columnspan=5, sticky="nsew")

    def add_shortcuts(self):
            self.id_entry.bind("<Control-c>", self.copy)
            self.id_entry.bind("<Control-v>", self.paste)
            self.id_entry.bind("<Control-x>", self.cut)

            self.name_entry.bind("<Control-c>", self.copy)
            self.name_entry.bind("<Control-v>", self.paste)
            self.name_entry.bind("<Control-x>", self.cut)

            self.card1_entry.bind("<Control-c>", self.copy)
            self.card1_entry.bind("<Control-v>", self.paste)
            self.card1_entry.bind("<Control-x>", self.cut)

            self.card2_entry.bind("<Control-c>", self.copy)
            self.card2_entry.bind("<Control-v>", self.paste)
            self.card2_entry.bind("<Control-x>", self.cut)

            self.phone_entry.bind("<Control-c>", self.copy)
            self.phone_entry.bind("<Control-v>", self.paste)
            self.phone_entry.bind("<Control-x>", self.cut)

    def copy(self, event):
            self.root.clipboard_clear()
            self.root.clipboard_append(event.widget.selection_get())

    def paste(self, event):
            try:
                event.widget.insert(tk.INSERT, self.root.clipboard_get())
            except tk.TclError:
                pass

    def cut(self, event):
            self.copy(event)
            event.widget.delete("sel.first", "sel.last")
            
    def add_contact(self):
        id = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get()
        company = self.company.get()
        card1 = self.card1_entry.get()
        card2 = self.card2_entry.get()

        self.cursor.execute(f"select id from contacts where id = {id}")
        results = self.cursor.fetchone()
        if results == None:
            self.cursor.execute(f"INSERT INTO contacts (id, name, company, card1, card2, phone) VALUES ({id}, '{name}','{company}', '{card1}', '{card2}', '{phone}')")
            self.conn.commit()
            # Queue change for Drive DB
            queue_change(f"INSERT INTO contacts (id, name, company, card1, card2, phone) VALUES ({id}, '{name}','{company}', '{card1}', '{card2}', '{phone}')")
            messagebox.showinfo("Success", "Contact added")
        else:
            messagebox.showinfo("failed", "this client already exists")

    def id_search(self):
        id = self.id_entry.get().strip()
        self.cursor.execute(f"SELECT * FROM contacts WHERE id={id}")
        result = self.cursor.fetchone()
        if result:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"ID: {result[0]}\nName: {result[1]}\nCompany: {result[2]}\nCard1: {result[3]}\nCard2: {result[4]}\nPhone: {result[5]}")
        else:
            messagebox.showinfo("Not Found", "Contact not found")

    def name_search(self):
        name = self.name_entry.get().lower()
        query = "SELECT * FROM contacts WHERE LOWER(name) LIKE ?"
        self.cursor.execute(query, ('%' + name + '%',))
        results = self.cursor.fetchall()
    # Process results...
        if results:
            self.output_text.delete(1.0, tk.END)
            for row in results:
                self.output_text.insert(tk.END, f"ID: {row[0]}\nName: {row[1]}\nCompany: {row[2]}\nCard1: {row[3]}\nCard2: {row[4]}\nPhone: {row[5]}\n--------------------------------\n")
        else:
            messagebox.showinfo("Not Found", "Contact not found")

    def Company_search(self):
        company = self.company.get()
        self.cursor.execute(f"SELECT * FROM contacts WHERE company='{company}'")
        result = self.cursor.fetchone()
        if result:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"ID: {result[0]}\nName: {result[1]}\nCompany: {result[2]}\nCard1: {result[3]}\nCard2: {result[4]}\nPhone: {result[5]}")
        else:
            messagebox.showinfo("Not Found", "Contact not found")

    def card1_search(self):
        card1 = self.card1_entry.get().strip()
        self.cursor.execute(f"SELECT * FROM contacts WHERE card1='{card1}'")
        result = self.cursor.fetchone()
        if result:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"ID: {result[0]}\nName: {result[1]}\nCompany: {result[2]}\nCard1: {result[3]}\nCard2: {result[4]}\nPhone: {result[5]}")
        else:
            messagebox.showinfo("Not Found", "Contact not found")
    def card2_search(self):
        card2 = self.card2_entry.get().strip()
        self.cursor.execute(f"SELECT * FROM contacts WHERE card2='{card2}'")
        result = self.cursor.fetchone()
        if result:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"ID: {result[0]}\nName: {result[1]}\nCompany: {result[2]}\nCard1: {result[3]}\nCard2: {result[4]}\nPhone: {result[5]}")
        else:
            messagebox.showinfo("Not Found", "Contact not found")

    def phone_search(self):
        phone = self.phone_entry.get()
        self.cursor.execute(f"SELECT * FROM contacts WHERE phone='{phone}'")
        result = self.cursor.fetchone()
        if result:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"ID: {result[0]}\nName: {result[1]}\nCompany: {result[2]}\nCard1: {result[3]}\nCard2: {result[4]}\nPhone: {result[5]}")
        else:
            messagebox.showinfo("Not Found", "Contact not found")

    def display_contacts(self):
        self.cursor.execute("SELECT * FROM contacts")
        results = self.cursor.fetchall()
        self.output_text.delete(1.0, tk.END)
        for row in results:
            self.output_text.insert(tk.END, f"ID: {row[0]}\nName: {row[1]}\nCompany: {row[2]}\nCard1: {row[3]}\nCard2: {row[4]}\nPhone: {row[5]}\n--------------------------------\n")
            
    
    def delete_contact(self):
        name = self.name_entry.get().strip()
        id = self.id_entry.get().strip()
        self.cursor.execute(f"select name, id from contacts where name = '{name}' and id = {id}")
        results = self.cursor.fetchone()
        if results:
            if messagebox.askyesno(title="delete", message=f"DO you really want to delete {name} permanently?"):
                self.cursor.execute(f"delete from contacts where name = '{name}' and id = {id} ")
                self.conn.commit()
                # Queue change for Drive DB
                queue_change(f"DELETE FROM contacts WHERE name = '{name}' and id = {id} ")
                messagebox.showinfo("Success", "Contact deleted")
        else:
            messagebox.showinfo("Not Found", "Contact not found")
            
    def update_company(self):
        name = self.name_entry.get().strip()
        company = self.company.get()
        self.cursor.execute(f"SELECT company FROM contacts WHERE name='{name}'")
        results = self.cursor.fetchone()
        if results :
            self.cursor.execute(f"update contacts set company = '{company}' where name = '{name}'")
            self.conn.commit()
            queue_change(f"update contacts set company = '{company}' where name = '{name}'")
            messagebox.showinfo("Success", "company updated")
        else:
            messagebox.showinfo("Not Found", "Contact not found")
    
    def update_card1(self):
        name = self.name_entry.get().strip()
        card1 = self.card1_entry.get()
        self.cursor.execute(f"SELECT card1 FROM contacts WHERE name='{name}'")
        results = self.cursor.fetchone()
        if results :
            self.cursor.execute(f"update contacts set card1 = '{card1}' where name = '{name}'")
            self.conn.commit()
            queue_change(f"update contacts set card1 = '{card1}' where name = '{name}'")
            messagebox.showinfo("Success", "card1 number updated")
        else:
            messagebox.showinfo("Not Found", "Contact not found")
        
    def update_card2(self):
        name = self.name_entry.get().strip()
        card2 = self.card2_entry.get()
        self.cursor.execute(f"SELECT card2 FROM contacts WHERE name ='{name}'")
        results = self.cursor.fetchone()
        if results :
            self.cursor.execute(f"update contacts set card2 = '{card2}' where name = '{name}'")
            self.conn.commit()
            queue_change(f"update contacts set card2 = '{card2}' where name = '{name}'")
            messagebox.showinfo("Success", "card2 number updated")
        else:
            messagebox.showinfo("Not Found", "Contact not found")
        
    def update_phone(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get()
        self.cursor.execute(f"SELECT phone FROM contacts WHERE name='{name}'")
        results = self.cursor.fetchone()
        if results :
            self.cursor.execute(f"update contacts set phone = '{phone}' where name = '{name}'")
            self.conn.commit()
            queue_change(f"update contacts set phone = '{phone}' where name = '{name}'")
            messagebox.showinfo("Success", "phone updated")
        else:
            messagebox.showinfo("Not Found", "Contact not found")
    
    def close(self):
        self.conn.close()

def main():
    root = tk.Tk()
    root.title("Elmounir Contacts Application programmed by: Michael Essam")
    root.iconbitmap("contacts.ico")
    app = ContactApp(root)
#    service = get_service()
    try:
        service = get_service()
        upload_offline_changes(service)
    except Exception as e:
        logging.error(f"Error uploading offline changes: {e}")    

    try:
        service = get_service()
        download_changes(service)
    except Exception as e:
        logging.error(f"Error downloading changes: {e}")

    def upload_on_exit():
        try:
            service = get_service()
            if os.path.exists("changes.txt"):
                with open("changes.txt", "r") as f:
                    local_changes = [line.strip() for line in f.readlines()]
                upload_changes(service, local_changes)
        except Exception as e:
            logging.error(f"Error uploading changes: {e}")
#        upload_changes(service)
    atexit.register(upload_on_exit)
    root.mainloop()

if __name__ == "__main__":
    main()

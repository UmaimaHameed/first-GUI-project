import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os
import random
import time

# =============== ROOM PRICES ===============
ROOM_PRICES = {
    "Single": 3000,
    "Double": 5000,
    "Deluxe": 8000,
    "Suite": 12000
}

# =============== SERVICE PRICES ===============
SERVICE_PRICES = {
    "Breakfast": 500,
    "Lunch": 800,
    "Dinner": 1000,
    "Wi-Fi (High-Speed)": 300,
    "Laundry": 400,
    "Spa Session": 2000,
    "Airport Transfer": 2500,
    "Room Cleaning": 0  # Free service
}

# =============== GENERATE 4-DIGIT CUSTOMER ID ===============
def generate_customer_id():
    while True:
        cid = str(random.randint(1000, 9999))
        if cid not in customers:
            return cid

# =============== MAIN WINDOW ===============
root = tk.Tk()
root.title("Grand Heritage Hotel - Management System")
root.state("zoomed")
root.configure(bg="#ecf0f1")

# =============== HEADER ===============
header = tk.Frame(root, bg="#2c3e50", height=90)
header.pack(fill="x")
header.pack_propagate(False)
tk.Label(header, text="GRAND HERITAGE HOTEL",
         font=("Arial", 32, "bold"),
         bg="#2c3e50", fg="#f1c40f").pack(pady=15)

# =============== NOTEBOOK ===============
nb = ttk.Notebook(root)
nb.pack(fill="both", expand=True, padx=20, pady=20)

customers = {}
active_bookings = {}

# =============== LOAD DATA ===============
def load_customers():
    customers.clear()
    if os.path.exists("customers.csv"):
        with open("customers.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            try: next(reader)  # Skip header
            except: pass
            for row in reader:
                if len(row) >= 4:
                    customers[row[0]] = (row[1], row[2], row[3])

def load_bookings():
    active_bookings.clear()
    if os.path.exists("active_bookings.csv"):
        with open("active_bookings.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            try: next(reader)
            except: pass
            for row in reader:
                if len(row) >= 7:
                    services = row[7].split(",") if len(row) > 7 and row[7] != "None" else []
                    active_bookings[row[1]] = (row[3], int(row[4]), int(row[5]), row[6], row[0], services)

load_customers()
load_bookings()

# =============== CUSTOMER MANAGEMENT TAB ===============
cust_tab = ttk.Frame(nb)
nb.add(cust_tab, text="Customer Management")

tk.Label(cust_tab, text="Add New Customer", font=("Arial", 18, "bold")).pack(pady=10)
form = tk.Frame(cust_tab)
form.pack(pady=20)

tk.Label(form, text="Full Name").grid(row=0, column=0, padx=10, pady=10)
tk.Label(form, text="Phone (11 digits)").grid(row=0, column=2, padx=10, pady=10)
tk.Label(form, text="Address").grid(row=1, column=0, padx=10, pady=10)

name_entry = tk.Entry(form, width=30)
phone_entry = tk.Entry(form, width=30)
addr_entry = tk.Entry(form, width=70)

name_entry.grid(row=0, column=1)
phone_entry.grid(row=0, column=3)
addr_entry.grid(row=1, column=1, columnspan=3)

customer_tree = ttk.Treeview(cust_tab, columns=("ID", "Name", "Phone", "Address"), show="headings")
for c in ("ID", "Name", "Phone", "Address"):
    customer_tree.heading(c, text=c)
    customer_tree.column(c, width=200)
customer_tree.pack(fill="both", expand=True, padx=20, pady=10)

def refresh_customers():
    customer_tree.delete(*customer_tree.get_children())
    for cid, (n, p, a) in customers.items():
        customer_tree.insert("", "end", values=(cid, n, p, a))

refresh_customers()

def add_customer():
    name = name_entry.get().strip()
    phone = phone_entry.get().strip()
    addr = addr_entry.get().strip()

    if not name or not phone:
        return messagebox.showerror("Error", "Name & Phone required!")
    
    if not phone.isdigit() or len(phone) != 11:
        return messagebox.showerror("Error", "Phone must be exactly 11 digits (only numbers)!")

    if phone in [p for _, p, _ in customers.values()]:
        return messagebox.showerror("Error", "This phone number is already registered!")

    existing_names = [n for n, _, _ in customers.values()]
    if name in existing_names:
        return messagebox.showerror("Error", "Customer with same name already exists!")

    cid = generate_customer_id()
    customers[cid] = (name, phone, addr)

    file_exists = os.path.exists("customers.csv")
    with open("customers.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["ID", "Name", "Phone", "Address"])
        w.writerow([cid, name, phone, addr])

    refresh_customers()
    messagebox.showinfo("Success", f"Customer Added! ID: {cid}")

    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    addr_entry.delete(0, tk.END)

tk.Button(cust_tab, text="Add Customer", font=("Arial", 14), bg="#27ae60", fg="white", command=add_customer).pack(pady=15)

# =============== BOOKINGS TAB ===============
book_tab = ttk.Frame(nb)
nb.add(book_tab, text="Bookings")

tk.Label(book_tab, text="Check In Guest", font=("Arial", 18, "bold")).pack(pady=10)

bform = tk.Frame(book_tab)
bform.pack(pady=20)

tk.Label(bform, text="Customer ID").grid(row=0, column=0, padx=10, sticky="e")
cid_entry = tk.Entry(bform, width=20)
cid_entry.grid(row=0, column=1, padx=10)

tk.Label(bform, text="Room Type").grid(row=1, column=0, padx=10, sticky="e")
room_combo = ttk.Combobox(bform, values=list(ROOM_PRICES.keys()), state="readonly")
room_combo.grid(row=1, column=1, padx=10)

tk.Label(bform, text="Nights").grid(row=1, column=2, padx=10, sticky="e")
nights_entry = tk.Entry(bform, width=10)
nights_entry.insert(0, "1")
nights_entry.grid(row=1, column=3, padx=10)

# Services Section
tk.Label(bform, text="Additional Services", font=("Arial", 12, "bold")).grid(row=2, column=0, columnspan=4, pady=(15,5), sticky="w")

services_frame = tk.Frame(bform)
services_frame.grid(row=3, column=0, columnspan=4, pady=10, padx=20, sticky="w")

service_vars = {}
for i, (service, price) in enumerate(SERVICE_PRICES.items()):
    var = tk.BooleanVar()
    service_vars[service] = var
    chk = tk.Checkbutton(services_frame, text=f"{service} (+₹{price})", variable=var)
    chk.grid(row=i//2, column=i%2, padx=25, pady=5, sticky="w")

# Bill Label
bill_label = tk.Label(book_tab, text="Total: ₹0", font=("Arial", 20, "bold"), fg="#c0392b")
bill_label.pack(pady=10)

def update_bill(*args):
    try:
        room_price = ROOM_PRICES[room_combo.get()]
        nights = int(nights_entry.get())
        room_total = room_price * nights
        services_total = sum(SERVICE_PRICES[s] for s, v in service_vars.items() if v.get())
        total = room_total + services_total
        bill_label.config(text=f"Total: ₹{total}")
    except:
        bill_label.config(text="Total: ₹0")

room_combo.bind("<<ComboboxSelected>>", update_bill)
nights_entry.bind("<KeyRelease>", update_bill)
for var in service_vars.values():
    var.trace("w", update_bill)

def check_in():
    cid = cid_entry.get().strip()
    room = room_combo.get()
    nights_str = nights_entry.get()

    if not cid or not room or not nights_str.isdigit():
        return messagebox.showerror("Error", "All fields required!")

    if cid not in customers:
        return messagebox.showerror("Error", "Customer not found!")

    if cid in active_bookings:
        return messagebox.showerror("Error", "Already checked in!")

    nights = int(nights_str)
    room_total = ROOM_PRICES[room] * nights
    selected_services = [s for s, v in service_vars.items() if v.get()]
    services_total = sum(SERVICE_PRICES[s] for s in selected_services)
    total = room_total + services_total

    services_str = ",".join(selected_services) if selected_services else "None"

    rid = str(random.randint(1000, 9999))
    date = datetime.now().strftime("%Y-%m-%d")
    name = customers[cid][0]

    file_exists = os.path.exists("active_bookings.csv")
    with open("active_bookings.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["ResID", "CID", "Name", "Room", "Nights", "Total", "Date", "Services"])
        w.writerow([rid, cid, name, room, nights, total, date, services_str])

    active_bookings[cid] = (room, nights, total, date, rid, selected_services)

    refresh_bookings()
    messagebox.showinfo("Success", f"{name} checked in!")

    cid_entry.delete(0, tk.END)
    room_combo.set("")
    nights_entry.delete(0, tk.END)
    nights_entry.insert(0, "1")
    for var in service_vars.values():
        var.set(False)
    update_bill()

tk.Button(book_tab, text="CHECK IN", font=("Arial", 14), bg="#2980b9", fg="white", command=check_in).pack(pady=20)

booking_tree = ttk.Treeview(book_tab, columns=("ResID", "CID", "Name", "Room", "Nights", "Total", "Date", "Services"), show="headings")
for c in ("ResID", "CID", "Name", "Room", "Nights", "Total", "Date", "Services"):
    booking_tree.heading(c, text=c)
    booking_tree.column(c, width=120 if c == "Services" else 140)
booking_tree.pack(fill="both", expand=True, padx=20, pady=10)

def refresh_bookings():
    booking_tree.delete(*booking_tree.get_children())
    for cid, data in active_bookings.items():
        room, nights, total, date, rid, services_list = data
        name = customers.get(cid, ("Unknown",))[0]
        services_display = ", ".join(services_list) if services_list else "None"
        booking_tree.insert("", "end", values=(rid, cid, name, room, nights, total, date, services_display))

refresh_bookings()

# =============== PAYMENTS TAB ===============
pay_tab = ttk.Frame(nb)
nb.add(pay_tab, text="Payments")

pform = tk.Frame(pay_tab)
pform.pack(pady=30)

tk.Label(pform, text="Customer ID").grid(row=0, column=0, padx=10)
tk.Label(pform, text="Amount").grid(row=0, column=2, padx=10)

pcid = tk.Entry(pform, width=20)
pamt = tk.Entry(pform, state="readonly", width=20)

pcid.grid(row=0, column=1)
pamt.grid(row=0, column=3)

def autofill_amount(_=None):
    cid = pcid.get().strip()
    pamt.config(state="normal")
    pamt.delete(0, tk.END)
    if cid in active_bookings:
        pamt.insert(0, str(active_bookings[cid][2]))
    pamt.config(state="readonly")

pcid.bind("<KeyRelease>", autofill_amount)

def generate_invoice(cid):
    if cid not in active_bookings:
        return
    room, nights, total, date, rid, services_list = active_bookings[cid]
    name, phone, addr = customers[cid]
    services_text = ", ".join(services_list) if services_list else "None"

    invoice_text = f"""GRAND HERITAGE HOTEL INVOICE

Invoice ID: {rid}
Date: {date}

Customer ID: {cid}
Name: {name}
Phone: {phone}
Address: {addr}

Room Type: {room}
Nights: {nights}
Services: {services_text}

TOTAL BILL: ₹{total}

Thank you for staying with us!
"""
    path = f"invoice_{cid}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(invoice_text)
    time.sleep(0.1)
    try:
        os.startfile(path)
    except:
        try:
            os.system(f"open '{path}'" if "darwin" in os.sys.platform else f"xdg-open '{path}'")
        except:
            messagebox.showinfo("Saved", f"Invoice saved as {path}")

def open_invoice():
    cid = pcid.get().strip()
    if cid not in active_bookings:
        return messagebox.showerror("Error", "No active booking!")
    generate_invoice(cid)

tk.Button(pay_tab, text="GENERATE INVOICE", font=("Arial", 14), bg="#f39c12", fg="white", command=open_invoice).pack(pady=10)

def record_payment():
    cid = pcid.get().strip()
    if cid not in active_bookings:
        return messagebox.showerror("Error", "No active booking!")
    
    total = active_bookings[cid][2]
    pid = str(random.randint(1000, 9999))
    date = datetime.now().strftime("%Y-%m-%d")

    # Write payment to CSV
    file_exists = os.path.exists("payments.csv")
    with open("payments.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["PID", "CID", "Amount", "Date"])
        w.writerow([pid, cid, total, date])
        f.flush()  # Ensure data is written
        os.fsync(f.fileno())

    generate_invoice(cid)
    active_bookings.pop(cid)

    # Refresh both tables immediately
    refresh_bookings()
    refresh_history()

    messagebox.showinfo("Success", "Payment recorded & Invoice generated!")
    pcid.delete(0, tk.END)
    pamt.config(state="normal")
    pamt.delete(0, tk.END)
    pamt.config(state="readonly")

tk.Button(pay_tab, text="RECORD PAYMENT", font=("Arial", 14), bg="#27ae60", fg="white", command=record_payment).pack(pady=20)

# =============== TRANSACTION HISTORY TAB ===============
history_tab = ttk.Frame(nb)
nb.add(history_tab, text="Transaction History")

history_tree = ttk.Treeview(history_tab, columns=("PID", "CID", "Amount", "Date"), show="headings")
for c in ("PID", "CID", "Amount", "Date"):
    history_tree.heading(c, text=c)
    history_tree.column(c, width=250)
history_tree.pack(fill="both", expand=True, padx=20, pady=20)

def refresh_history():
    history_tree.delete(*history_tree.get_children())
    if not os.path.exists("payments.csv"):
        return
    with open("payments.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            next(reader)  # Skip header
        except StopIteration:
            return
        for row in reader:
            if len(row) == 4:
                history_tree.insert("", "end", values=row)

refresh_history()  # Load on startup

def on_tab_change(event):
    tab = event.widget.tab(event.widget.select(), "text")
    if tab == "Transaction History":
        refresh_history()

nb.bind("<<NotebookTabChanged>>", on_tab_change)

root.mainloop()
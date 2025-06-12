import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import random
from PIL import Image, ImageTk
import os
import sqlite3

# Data structure for storing items with categories
menu_items = {
    # Makanan
    'Indomie   ': {'price': 3500, 'image': 'indomie.png', 'category': 'Makanan'},
    'Roti Tawar': {'price': 12000, 'image': 'sariroti.png', 'category': 'Makanan'},
    'Roti Roma ': {'price': 8000, 'image': 'roma_kelapa.png', 'category': 'Makanan'},
    'Sosis     ': {'price': 10000, 'image': 'sosis.png', 'category': 'Makanan'},
    'Coklat    ': {'price': 15000, 'image': 'silverqueen.png', 'category': 'Makanan'},
    
    # Minuman
    'Aqua 600ml': {'price': 4000, 'image': 'aqua.png', 'category': 'Minuman'},
    'Teh Sosro ': {'price': 5000, 'image': 'teh_sosro.png', 'category': 'Minuman'},
    'Good Day  ': {'price': 2500, 'image': 'good_day.png', 'category': 'Minuman'},
    'Ultra Milk': {'price': 6000, 'image': 'ultramilk.png', 'category': 'Minuman'},
    'Sprite    ': {'price': 6500, 'image': 'sprite.png', 'category': 'Minuman'},
    
    # Kebersihan
    'Sabun Mandi': {'price': 3500, 'image': 'sabun.png', 'category': 'Kebersihan'},
    'Pasta Gigi ': {'price': 7000, 'image': 'pepsodent.png', 'category': 'Kebersihan'},
    'Detergen   ': {'price': 10000, 'image': 'rinso.png', 'category': 'Kebersihan'},
    'Shampoo    ': {'price': 9000, 'image': 'sampo.png', 'category': 'Kebersihan'},
    'Sabun Cuci ': {'price': 6500, 'image': 'sunlight.png', 'category': 'Kebersihan'},
    
    # Rumah Tangga
    'Sapu Lidi': {'price': 10000, 'image': 'sapu_lidi.png', 'category': 'Rumah Tangga'},
    'Ember    ': {'price': 15000, 'image': 'ember.png', 'category': 'Rumah Tangga'},
    'Lap      ': {'price': 8000, 'image': 'lap.png', 'category': 'Rumah Tangga'},
    'Gayung   ': {'price': 7000, 'image': 'gayung.png', 'category': 'Rumah Tangga'},
    'Alat Makan': {'price': 12000, 'image': 'sendok_garpu.png', 'category': 'Rumah Tangga'}
}

# Store
images = {}

# Load and resize images
def load_images():
    image_path = os.path.join(os.path.dirname(__file__), 'images')
    for item, details in menu_items.items():
        try:
            img = Image.open(os.path.join(image_path, details['image']))
            img = img.resize((200, 200))  # Resize images to 100x100
            images[item] = ImageTk.PhotoImage(img)
        except:
            print(f"Could not load image for {item}")

cart = []
cart_table = None
total_label = None

# Replace the old add_to_cart function with this new one
def add_to_cart(item, price):
    add_to_cart_with_customization(item, price)


def update_cart_display():
    # Bersihin isi tampilan keranjang
    for widget in cart_scrollable_frame.winfo_children():
        widget.destroy()

    # Header
    header = tk.Frame(cart_scrollable_frame, bg='#d0d0d0')
    header.pack(fill='x')
    tk.Label(header, text="Item", width=20, anchor='center', bg='#d0d0d0', font=('Arial', 10, 'bold')).pack(side='left')
    tk.Label(header, text="Price", width=10, anchor='center', bg='#d0d0d0', font=('Arial', 10, 'bold')).pack(side='left')
    tk.Label(header, text="Qty", width=12, anchor='center', bg='#d0d0d0', font=('Arial', 10, 'bold')).pack(side='left')
    tk.Label(header, text="Total", width=10, anchor='center', bg='#d0d0d0', font=('Arial', 10, 'bold')).pack(side='left')

    total = 0
    for item in cart:
        row = tk.Frame(cart_scrollable_frame, bg='white')
        row.pack(fill='x', pady=2)

        # Kolom Item
        tk.Label(row, text=item['item'], width=20, anchor='w', bg='white').pack(side='left')

        # Kolom Harga
        tk.Label(row, text=f"Rp {item['price']:,}", width=10, anchor='center', bg='white').pack(side='left')

        # Kolom Qty + Tombol - dan +
        qty_frame = tk.Frame(row, bg='white')
        qty_frame.pack(side='left', padx=5)
        tk.Button(qty_frame, text='-', width=2, command=lambda i=item: change_qty(i, -1)).pack(side='left')
        tk.Label(qty_frame, text=str(item['qty']), width=3, anchor='center', bg='white').pack(side='left')
        tk.Button(qty_frame, text='+', width=2, command=lambda i=item: change_qty(i, 1)).pack(side='left')

        # Kolom Total
        tk.Label(row, text=f"Rp {item['total']:,}", width=10, anchor='e', bg='white').pack(side='left')

        # Tombol Hapus (seperti awal)
        hapus_btn = tk.Button(
            row, 
            text="Hapus", 
            font=('Arial', 9, 'bold'),
            bg='#f44336', 
            fg='white', 
            width=6,
            command=lambda i=item: remove_item(i)
        )
        hapus_btn.pack(side='left', padx=5)

        # Perbaikan: total harus diakumulasi di dalam loop
        total += item['total']

    total_label.config(text=f": Rp {total:,}")
    # Update total_var agar bisa diakses untuk perhitungan kembalian
    total_var.set(total)
    update_change()


def update_change(*args):
    try:
        bayar = int(payment_var.get())
    except:
        bayar = 0
    total = total_var.get()
    kembalian = bayar - total if bayar >= total else 0
    change_var.set(kembalian)
    payment_label.config(text=f": Rp {bayar:,}")
    change_label.config(text=f": Rp {kembalian:,}")


def process_payment():
    if not cart:
        messagebox.showwarning("Peringatan", "Pesanan Kosong!")
        return

    try:
        bayar = int(payment_var.get())
    except:
        bayar = 0

    total = sum(item['total'] for item in cart)
    if bayar < total:
        messagebox.showwarning("Peringatan", "Uang pembayaran kurang!")
        return

    kembalian = bayar - total

    # --- Simpan ke database ---
    waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    invoice = f"INV/{datetime.now().strftime('%Y%m%d')}/{random.randint(1000,9999)}"
    for item in cart:
        cur.execute(
            "INSERT INTO transaksi (waktu, invoice, item, qty, harga, total_item, total_belanja, bayar, kembalian) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                waktu,
                invoice,
                item['item'],
                item['qty'],
                item['price'],
                item['total'],
                total,
                bayar,
                kembalian
            )
        )
    conn.commit()

    # Rapiin struk
    receipt = "=" * 30 + "\n"
    receipt += "                            CERIA MART\n"
    receipt += "                    Jl. Raya Banaran No. 123\n"
    receipt += "                       Telp: 0812-3456-7890\n"
    receipt += "=" * 30 + "\n"
    receipt += f"Tanggal :  {waktu}\n"
    receipt += f"Invoice   :  {invoice}\n"
    receipt += f"Kasir       :  ADMIN\n"
    receipt += "=" * 30 + "\n"
    receipt += f"{'Item':<15}                {'Qty':^5}                     {'Harga':>10}\n"
    receipt += "=" * 30 + "\n"

    for item in cart:
        name = item['item'][:22]  # biar tidak terlalu panjang
        qty = f"x{item['qty']}"
        price = f"Rp {item['total']:,}"
        receipt += f"{name:<15}            {qty:^5}                   {price:>10}\n"

    receipt += "=" * 30 + "\n"
    receipt += f"{'TOTAL':<20}                                   {f'Rp {total:,}':>11}\n"
    receipt += f"{'BAYAR':<20}                                   {f'Rp {bayar:,}':>11}\n"
    receipt += f"{'KEMBALIAN':<20}                               {f'Rp {kembalian:,}':>11}\n"
    receipt += "=" * 30 + "\n"
    receipt += "               Terima kasih atas kunjungannya!\n"
    receipt += "                         Simpan struk ini ya!\n"

    messagebox.showinfo("Receipt", receipt)
    cart.clear()
    update_cart_display()
    payment_var.set("0")
    change_var.set(0)

def show_receipt_window(text):
    receipt_win = tk.Toplevel(root)
    receipt_win.title("Struk Pembayaran")
    receipt_win.geometry("400x500")
    
    tk.Label(receipt_win, text="Struk Pembayaran", font=("Segoe UI", 12, "bold")).pack(pady=5)

    receipt_text = tk.Text(receipt_win, wrap="none", font=("Courier New", 10))
    receipt_text.insert("1.0", text)
    receipt_text.config(state="disabled")  # Biar user nggak bisa ngedit
    receipt_text.pack(fill="both", expand=True, padx=10, pady=10)

    tk.Button(receipt_win, text="Tutup", command=receipt_win.destroy).pack(pady=5)

# In the create_category_frame function, update the grid configuration
def create_category_frame(parent, category):
    # Create frame for the category
    category_frame = tk.Frame(parent, bg='white')
    
    # Create a canvas with scrollbar for scrolling
    canvas = tk.Canvas(category_frame, bg='white')
    scrollbar = ttk.Scrollbar(category_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='white')
    
    # Configure the canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Create menu buttons grid in the scrollable frame
    menu_frame = tk.Frame(scrollable_frame, bg='white')
    menu_frame.pack(pady=10, padx=10, fill='both', expand=True)
    
    # Filter items by category
    category_items = {item: details for item, details in menu_items.items() 
                     if details['category'] == category}
    
    # Calculate how many items can fit in a row based on frame width
    items_per_row = 3
    
    # Configure all columns to have equal weight for consistent sizing
    for i in range(items_per_row):
        menu_frame.grid_columnconfigure(i, weight=1)
    
    row = 0
    col = 0
    for item, details in category_items.items():
        # Create frame for each menu item
        item_frame = tk.Frame(menu_frame, bg='white')
        item_frame.grid(row=row, column=col, padx=5, pady=10, sticky="nsew")
        
        # Add image
        if item in images:
            img_label = tk.Label(item_frame, image=images[item], bg='white')
            img_label.pack(fill='both', expand=True)

        # Add item name and price
        tk.Label(item_frame, text=item, font=('Arial', 12, 'bold'), bg='white').pack()
        tk.Label(item_frame, text=f"Rp {details['price']:,}", font=('Arial', 10), bg='white').pack()
        
        customization_var = None # Template text instead of default value
        
        # Add button with customization variable
        add_button = tk.Button(
            item_frame, 
            text="Tambahkan ke pesanan", 
            bg='#4CAF50', 
            fg='white',
            command=lambda x=item, y=details['price']: 
                add_to_cart_with_customization(x, y)
        )
        add_button.pack(pady=5)

        col += 1
        if col >= items_per_row:
            col = 0
            row += 1
    
    # Add mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    # Add touchpad scrolling support
    def _on_touch_scroll(event):
        # For touchpad scrolling
        if event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")
    
    # Bind mouse wheel for Windows
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Bind touchpad events for Windows
    canvas.bind("<Enter>", lambda _: canvas.bind_all("<Button-4>", _on_touch_scroll))
    canvas.bind("<Enter>", lambda _: canvas.bind_all("<Button-5>", _on_touch_scroll))
    canvas.bind("<Leave>", lambda _: canvas.unbind_all("<Button-4>"))
    canvas.bind("<Leave>", lambda _: canvas.unbind_all("<Button-5>"))
    
    # Add keyboard scrolling support
    def _on_up_key(event):
        canvas.yview_scroll(-1, "units")
    
    def _on_down_key(event):
        canvas.yview_scroll(1, "units")
    
    # Bind arrow keys
    canvas.bind("<Up>", _on_up_key)
    canvas.bind("<Down>", _on_down_key)
    
    return category_frame

def add_to_cart_with_customization(item, price):
    # Get customization value
    customization = ""
    
    # Create the full item name with customization
    full_item_name = item + customization
    
    # Check if item already in cart
    for cart_item in cart:
        if cart_item['item'] == full_item_name:
            cart_item['qty'] += 1
            cart_item['total'] = cart_item['qty'] * cart_item['price']
            update_cart_display()
            return

    # Add new item to cart
    cart.append({
        'item': full_item_name,
        'price': price,
        'qty': 1,
        'total': price
    })
    update_cart_display()

# --- Database setup ---
db_path = os.path.join(os.path.dirname(__file__), "transaksi.db")
# Cek dan buat koneksi database hanya sekali di awal
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS transaksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    waktu TEXT,
    invoice TEXT,
    item TEXT,
    qty INTEGER,
    harga INTEGER,
    total_item INTEGER,
    total_belanja INTEGER,
    bayar INTEGER,
    kembalian INTEGER
)
""")
conn.commit()

# Create main window
root = tk.Tk()
root.title("CERIA MART")
root.geometry("1200x700")
root.configure(bg='#f0f0f0')

# Load images before creating buttons
load_images()

# Left Frame - Menu Items
left_frame = tk.Frame(root, bg='white')
left_frame.place(relx=0, rely=0, relwidth=0.6, relheight=1)

# Menu Title
tk.Label(left_frame, text="Menu", font=('Segoe UI', 20, 'bold'), bg='white').pack(pady=10)

# Create a frame for category buttons
category_buttons_frame = tk.Frame(left_frame, bg='white')
category_buttons_frame.pack(fill='x', padx=10)

# Create a frame for content display
content_frame = tk.Frame(left_frame, bg='white')
content_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Function to show category content
def show_category(category):
    # Hide all frames
    for frame in category_frames.values():
        frame.pack_forget()
    
    # Show selected frame
    if category in category_frames:
        category_frames[category].pack(fill='both', expand=True)

# Create frames for each category
category_frames = {}

# Create "All" category frame that shows all items organized by category
all_frame = tk.Frame(content_frame, bg='white')
all_canvas = tk.Canvas(all_frame, bg='white')
all_scrollbar = ttk.Scrollbar(all_frame, orient="vertical", command=all_canvas.yview)
all_scrollable_frame = tk.Frame(all_canvas, bg='white')

all_scrollable_frame.bind(
    "<Configure>",
    lambda e: all_canvas.configure(scrollregion=all_canvas.bbox("all"))
)

all_canvas.create_window((0, 0), window=all_scrollable_frame, anchor="nw")
all_canvas.configure(yscrollcommand=all_scrollbar.set)

all_canvas.pack(side="left", fill="both", expand=True)
all_scrollbar.pack(side="right", fill="y")

# Add sections for each category in the "All" tab
categories = ['Makanan', 'Minuman', 'Kebersihan', 'Rumah Tangga']

# In the "Semua" tab creation section
for cat in categories:
    # Create section header
    section_frame = tk.Frame(all_scrollable_frame, bg='white')
    section_frame.pack(fill='x', pady=(20, 10))
    
    # Add a separator line before the category header (except for the first one)
    if cat != categories[0]:
        ttk.Separator(all_scrollable_frame, orient='horizontal').pack(fill='x', pady=10)
    
    # Category header with dark green background
    header_frame = tk.Frame(section_frame, bg='#0B5345', padx=10, pady=5)
    header_frame.pack(fill='x')
    tk.Label(header_frame, text=cat, font=('Segoe UI', 14, 'bold'), bg='#0B5345', fg='white').pack(anchor='w')
    
    # Create grid for items in this category
    items_frame = tk.Frame(all_scrollable_frame, bg='white')
    items_frame.pack(fill='x', padx=10)
    
    # Filter items for this category
    category_items = {item: details for item, details in menu_items.items() 
                     if details['category'] == cat}
    
    # Calculate how many items can fit in a row
    items_per_row = 3
    
    # Configure all columns to have equal weight for consistent sizing
    for i in range(items_per_row):
        items_frame.grid_columnconfigure(i, weight=1)
    
    row = 0
    col = 0
    for item, details in category_items.items():
        # Create frame for each menu item
        item_frame = tk.Frame(items_frame, bg='white')
        item_frame.grid(row=row, column=col, padx=5, pady=10, sticky="nsew")
        
        # Add image
        if item in images:
            img_label = tk.Label(item_frame, image=images[item], bg='white')
            img_label.pack(fill='both', expand=True)

        # Add item name and price
        tk.Label(item_frame, text=item, font=('Arial', 12, 'bold'), bg='white').pack()
        tk.Label(item_frame, text=f"Rp {details['price']:,}", font=('Arial', 10), bg='white').pack()
        
        # Add button
        add_button = tk.Button(
            item_frame, 
            text="Tambahkan ke pesanan", 
            bg='#4CAF50', 
            fg='white',
            command=lambda x=item, y=details['price']: add_to_cart(x, y)
        )
        add_button.pack(pady=5)

        col += 1
        if col >= items_per_row:
            col = 0
            row += 1

# Add mouse wheel scrolling for all_canvas
def _on_all_mousewheel(event):
    all_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Add touchpad scrolling support for all_canvas
def _on_all_touch_scroll(event):
    # For touchpad scrolling
    if event.num == 5 or event.delta < 0:
        all_canvas.yview_scroll(1, "units")
    elif event.num == 4 or event.delta > 0:
        all_canvas.yview_scroll(-1, "units")

# Bind mouse wheel for Windows
all_canvas.bind_all("<MouseWheel>", _on_all_mousewheel)

# Bind touchpad events for Windows
all_canvas.bind("<Enter>", lambda _: all_canvas.bind_all("<Button-4>", _on_all_touch_scroll))
all_canvas.bind("<Enter>", lambda _: all_canvas.bind_all("<Button-5>", _on_all_touch_scroll))
all_canvas.bind("<Leave>", lambda _: all_canvas.unbind_all("<Button-4>"))
all_canvas.bind("<Leave>", lambda _: all_canvas.unbind_all("<Button-5>"))

# Add keyboard scrolling support
def _on_all_up_key(event):
    all_canvas.yview_scroll(-1, "units")

def _on_all_down_key(event):
    all_canvas.yview_scroll(1, "units")

# Bind arrow keys
all_canvas.bind("<Up>", _on_all_up_key)
all_canvas.bind("<Down>", _on_all_down_key)

# Add the all frame to category frames
category_frames['Semua'] = all_frame

# Create individual category frames
for category in categories:
    category_frames[category] = create_category_frame(content_frame, category)

# Create category buttons that look like the image
button_style = {
    'font': ('Segoe UI', 12),
    'bg': '#0B5345',  # Dark green background
    'fg': 'white',    # White text
    'relief': 'raised',
    'borderwidth': 1,
    'padx': 20,
    'pady': 5
}

# Create the buttons
# Ubah definisi kategori
categories = ['Makanan', 'Minuman', 'Kebersihan', 'Rumah Tangga']

# Add mouse wheel scrolling for all_canvas
def _on_all_mousewheel(event):
    all_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Add touchpad scrolling support for all_canvas
def _on_all_touch_scroll(event):
    # For touchpad scrolling
    if event.num == 5 or event.delta < 0:
        all_canvas.yview_scroll(1, "units")
    elif event.num == 4 or event.delta > 0:
        all_canvas.yview_scroll(-1, "units")

# Bind mouse wheel for Windows
all_canvas.bind_all("<MouseWheel>", _on_all_mousewheel)

# Bind touchpad events for Windows
all_canvas.bind("<Enter>", lambda _: all_canvas.bind_all("<Button-4>", _on_all_touch_scroll))
all_canvas.bind("<Enter>", lambda _: all_canvas.bind_all("<Button-5>", _on_all_touch_scroll))
all_canvas.bind("<Leave>", lambda _: all_canvas.unbind_all("<Button-4>"))
all_canvas.bind("<Leave>", lambda _: all_canvas.unbind_all("<Button-5>"))

# Add keyboard scrolling support
def _on_all_up_key(event):
    all_canvas.yview_scroll(-1, "units")

def _on_all_down_key(event):
    all_canvas.yview_scroll(1, "units")

# Bind arrow keys
all_canvas.bind("<Up>", _on_all_up_key)
all_canvas.bind("<Down>", _on_all_down_key)

# Add the all frame to category frames
category_frames['Semua'] = all_frame

# Create individual category frames
for category in categories:
    category_frames[category] = create_category_frame(content_frame, category)

# Create category buttons that look like the image
button_style = {
    'font': ('Segoe UI', 12),
    'bg': '#0B5345',  # Dark green background
    'fg': 'white',    # White text
    'relief': 'raised',
    'borderwidth': 1,
    'padx': 20,
    'pady': 5
}

# Create the buttons
# Ubah pembuatan tombol kategori
semua_btn = tk.Button(category_buttons_frame, text="Semua", command=lambda: show_category('Semua'), **button_style)
makanan_btn = tk.Button(category_buttons_frame, text="Makanan", command=lambda: show_category('Makanan'), **button_style)
minuman_btn = tk.Button(category_buttons_frame, text="Minuman", command=lambda: show_category('Minuman'), **button_style)
kebersihan_btn = tk.Button(category_buttons_frame, text="Kebersihan", command=lambda: show_category('Kebersihan'), **button_style)
rumah_tangga_btn = tk.Button(category_buttons_frame, text="Rumah Tangga", command=lambda: show_category('Rumah Tangga'), **button_style)

# Pack the buttons side by side
semua_btn.pack(side='left', padx=5, pady=10)
makanan_btn.pack(side='left', padx=5, pady=10)
minuman_btn.pack(side='left', padx=5, pady=10)
kebersihan_btn.pack(side='left', padx=5, pady=10)
rumah_tangga_btn.pack(side='left', padx=5, pady=10)

# Show the "Semua" category by default
show_category('Semua')

# Right Frame - Cart
right_frame = tk.Frame(root, bg='#e0e0e0')
right_frame.place(relx=0.6, rely=0, relwidth=0.4, relheight=1)

# Cart Title + Riwayat Button
cart_title_frame = tk.Frame(right_frame, bg='#e0e0e0')
cart_title_frame.pack(pady=10, fill='x')

tk.Label(cart_title_frame, text="Pesanan", font=('Segoe UI', 20, 'bold'), bg='#e0e0e0').pack(side='left')

def show_history():
    history_win = tk.Toplevel(root)
    history_win.title("Riwayat Pembelian")
    history_win.geometry("800x400")
    
    # Table
    cols = ("Waktu", "Invoice", "Item", "Qty", "Harga", "Total Item", "Total Belanja", "Bayar", "Kembalian")
    tree = ttk.Treeview(history_win, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')
    tree.pack(fill='both', expand=True)

    # Fetch data from DB
    cur.execute("SELECT waktu, invoice, item, qty, harga, total_item, total_belanja, bayar, kembalian FROM transaksi ORDER BY id DESC")
    for row in cur.fetchall():
        tree.insert('', 'end', values=row)

    # Close button
    tk.Button(history_win, text="Tutup", command=history_win.destroy).pack(pady=5)

# Tombol Riwayat di pojok kanan atas
riwayat_btn = tk.Button(
    cart_title_frame, 
    text="Riwayat", 
    font=('Segoe UI', 12, 'bold'), 
    bg='#2196F3', 
    fg='white', 
    command=show_history
)
riwayat_btn.pack(side='right', padx=10)

# Custom Cart Table (Canvas-based)
cart_display_frame = tk.Frame(right_frame, bg='#e0e0e0')
cart_display_frame.pack(pady=10, padx=10, fill='both', expand=True)

cart_canvas = tk.Canvas(cart_display_frame, bg='#e0e0e0', highlightthickness=0)
cart_scrollbar = ttk.Scrollbar(cart_display_frame, orient="vertical", command=cart_canvas.yview)
cart_scrollable_frame = tk.Frame(cart_canvas, bg='#e0e0e0')

cart_scrollable_frame.bind(
    "<Configure>",
    lambda e: cart_canvas.configure(scrollregion=cart_canvas.bbox("all"))
)

cart_canvas.create_window((0, 0), window=cart_scrollable_frame, anchor="nw")
cart_canvas.configure(yscrollcommand=cart_scrollbar.set)

cart_canvas.pack(side="left", fill="both", expand=True)
cart_scrollbar.pack(side="right", fill="y")

# Total Label (rata kiri-kanan, titik dua rata)
total_var = tk.IntVar(value=0)
payment_var = tk.StringVar(value="0")
change_var = tk.IntVar(value=0)

total_frame = tk.Frame(right_frame, bg='#e0e0e0')
total_frame.pack(pady=(10,0), fill='x', padx=10)
total_text_label = tk.Label(total_frame, text="Total", font=('Arial', 15, 'bold'), bg='#e0e0e0')
total_text_label.pack(side='left')
total_label = tk.Label(total_frame, text=": Rp 0", font=('Arial', 15, 'bold'), bg='#e0e0e0', anchor='e')
total_label.pack(side='right')

# Entry pembayaran
payment_frame = tk.Frame(right_frame, bg='#e0e0e0')
payment_frame.pack(pady=(5,0), fill='x', padx=10)
tk.Label(payment_frame, text="Pembayaran", font=('Arial', 12), bg='#e0e0e0').pack(side='left')
payment_entry = tk.Entry(payment_frame, textvariable=payment_var, font=('Arial', 12), width=15)
payment_entry.pack(side='right')

# Label pembayaran (rata kiri-kanan, titik dua rata)
payment_disp_frame = tk.Frame(right_frame, bg='#e0e0e0')
payment_disp_frame.pack(fill='x', padx=10)
payment_text_label = tk.Label(payment_disp_frame, text="Pembayaran", font=('Arial', 12), bg='#e0e0e0')
payment_text_label.pack(side='left')
payment_label = tk.Label(payment_disp_frame, text=": Rp 0", font=('Arial', 12), bg='#e0e0e0', anchor='e')
payment_label.pack(side='right')

# Label kembalian (rata kiri-kanan, titik dua rata)
change_disp_frame = tk.Frame(right_frame, bg='#e0e0e0')
change_disp_frame.pack(fill='x', padx=10)
change_text_label = tk.Label(change_disp_frame, text="Kembalian", font=('Arial', 12), bg='#e0e0e0')
change_text_label.pack(side='left')
change_label = tk.Label(change_disp_frame, text=": Rp 0", font=('Arial', 12), bg='#e0e0e0', anchor='e')
change_label.pack(side='right')

# Update kembalian saat entry berubah
payment_var.trace_add('write', update_change)

# Tambahkan kembali tombol proses pembayaran
tk.Button(
    right_frame,
    text="Proses Pembayaran",
    command=process_payment,
    bg='#2196F3',
    fg='white',
    font=('Arial', 12, 'bold'),
    width=20,
    height=2
).pack(pady=10)

# Start the application
root.mainloop()

# Tutup koneksi database saat aplikasi ditutup
conn.close()

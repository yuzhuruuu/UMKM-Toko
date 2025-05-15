import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import random
from PIL import Image, ImageTk
import os

# Data structure for storing items with image filenames and categories
menu_items = {
    # Food items with customization options
    'Mie Level': {'price': 10000, 'image': 'Gacoan.png', 'category': 'Makanan', 'customizable': True, 'type': 'mie'},
    'Chicken Ricebowl': {'price': 10000, 'image': 'chicken_ricebowl.png', 'category': 'Makanan', 'customizable': True, 'type': 'ricebowl'},
    
    # Drinks
    'Es Teh': {'price': 5000, 'image': 'es_teh.png', 'category': 'Minuman'},
    'Teh Hangat': {'price': 5000, 'image': 'teh_hangat.png', 'category': 'Minuman'},
    'Es Jeruk': {'price': 7000, 'image': 'es_jeruk.png', 'category': 'Minuman'},
    'Jeruk Hangat': {'price': 7000, 'image': 'jeruk_hangat.png', 'category': 'Minuman'},
    'Lemon Tea': {'price': 8000, 'image': 'lemon_tea.png', 'category': 'Minuman'},
    'Leci Tea': {'price': 8000, 'image': 'lychee_tea.png', 'category': 'Minuman'},
    'Air Mineral': {'price': 3000, 'image': 'air_mineral.png', 'category': 'Minuman'},
    
    # Snacks
    'Siomay': {'price': 10000, 'image': 'siomay.png', 'category': 'Cemilan'},
    'Udang Keju': {'price': 10000, 'image': 'udang_keju.png', 'category': 'Cemilan'},
    'Sushi': {'price': 20000, 'image': 'sushi.png', 'category': 'Cemilan'},
    'Pangsit Goreng': {'price': 10000, 'image': 'pangsit_goreng.png', 'category': 'Cemilan'},
}

# Customization options
mie_levels = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]
ricebowl_sauces = ["Saus BBQ", "Sambal Matah", "Blackpaper"]
# tea_types = ["Teh Hangat", "Teh Manis", "Teh Tarik"]

# Store loaded images
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
    # This function is kept for backward compatibility
    # It will be called by any existing buttons that haven't been updated
    add_to_cart_with_customization(item, price, None, None)
    # Handle customizable items
    customization = ""
    if menu_items[item].get('customizable', False):
        if menu_items[item]['type'] == 'mie':
            # Create a simple dialog for mie level selection
            level = simpledialog.askinteger("Mie Level", "Choose spice level (1-5):", 
                                          minvalue=1, maxvalue=5)
            if level is None:  # User cancelled
                return
            customization = f" - Level {level}"
            
        elif menu_items[item]['type'] == 'ricebowl':
            # Create a dialog for sauce selection
            sauce_window = tk.Toplevel()
            sauce_window.title("Choose Sauce")
            sauce_window.geometry("300x200")
            
            # Center the window on the screen
            sauce_window.update_idletasks()
            width = sauce_window.winfo_width()
            height = sauce_window.winfo_height()
            x = (sauce_window.winfo_screenwidth() // 2) - (width // 2)
            y = (sauce_window.winfo_screenheight() // 2) - (height // 2)
            sauce_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            
            sauce_var = tk.StringVar(value=ricebowl_sauces[0])
            
            tk.Label(sauce_window, text="Pilih Saus:").pack(pady=10)
            
            for sauce in ricebowl_sauces:
                tk.Radiobutton(sauce_window, text=sauce, variable=sauce_var, value=sauce).pack(anchor='w', padx=20)
            
            selected_sauce = [None]  # Using list to store the result
            
            def confirm_sauce():
                selected_sauce[0] = sauce_var.get()
                sauce_window.destroy()
                
            def cancel():
                sauce_window.destroy()
                
            tk.Button(sauce_window, text="Confirm", command=confirm_sauce).pack(side='left', padx=30, pady=20)
            tk.Button(sauce_window, text="Cancel", command=cancel).pack(side='right', padx=30, pady=20)
            
            # Wait for the window to be closed
            sauce_window.transient(root)
            sauce_window.grab_set()
            root.wait_window(sauce_window)
            
            if selected_sauce[0] is None:  # User cancelled
                return
                
            customization = f" - {selected_sauce[0]}"
    
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

def update_cart_display():
    # Clear current display
    for item in cart_table.get_children():
        cart_table.delete(item)

    # Update display
    total = 0
    for item in cart:
        cart_table.insert('', 'end', values=(
            item['item'],
            f"Rp {item['price']:,}",
            item['qty'],
            f"Rp {item['total']:,}"
        ))
        total += item['total']

    total_label.config(text=f"Total: Rp {total:,}")

def process_payment():
    if not cart:
        messagebox.showwarning("Peringatan", "Pesanan Kosong!")
        return

    total = sum(item['total'] for item in cart)
    receipt = f"""
    ===================================
                BOWL&BITE
    ===================================
    Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Invoice: INV/{datetime.now().strftime('%Y%m%d')}/{random.randint(1000,9999)}
    -----------------------------------
    """
    for item in cart:
        receipt += f"\n{item['item']} x{item['qty']}"
        receipt += f"\n@ Rp {item['price']:,}"
        receipt += f"\nRp {item['total']:,}\n"
    
    receipt += f"""
    -----------------------------------
    Total: Rp {total:,}
    ===================================
    Thank you for your purchase!
    """

    messagebox.showinfo("Receipt", receipt)
    cart.clear()
    update_cart_display()

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
        
        # In the create_category_frame function, update the sauce dropdown
        # Add customization options directly in the menu
        customization_var = None
        if details.get('customizable', False):
            if details['type'] == 'mie':
                tk.Label(item_frame, text="Level Pedas:", font=('Arial', 9), fg='blue', bg='white').pack(anchor='w', padx=5)
                customization_var = tk.StringVar()  # No default value
                
                # Create dropdown for level selection
                level_options = [f"Level {i}" for i in range(1, 6)]
                level_dropdown = ttk.Combobox(item_frame, textvariable=customization_var, values=level_options, state="readonly", width=15)
                level_dropdown.pack(pady=5)
                level_dropdown.set("Pilih level")  # Template text instead of default value
                
            elif details['type'] == 'ricebowl':
                tk.Label(item_frame, text="Saus:", font=('Arial', 9), fg='blue', bg='white').pack(anchor='w', padx=5)
                customization_var = tk.StringVar()  # No default value
                
                # Create dropdown for sauce selection
                sauce_options = ["Tanpa saus"] + ricebowl_sauces
                sauce_dropdown = ttk.Combobox(item_frame, textvariable=customization_var, values=sauce_options, state="readonly", width=15)
                sauce_dropdown.pack(pady=5)
                sauce_dropdown.set("Pilih saus")  # Template text instead of default value
        
        # Add button with customization variable
        add_button = tk.Button(
            item_frame, 
            text="Tambahkan ke pesanan", 
            bg='#4CAF50', 
            fg='white',
            command=lambda x=item, y=details['price'], z=customization_var, t=details.get('type', None): 
                add_to_cart_with_customization(x, y, z, t)
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

def add_to_cart_with_customization(item, price, customization_var, item_type):
    # Get customization value
    customization = ""
    if customization_var:
        selected_value = customization_var.get()
        
        # Check if user has made a selection
        if item_type == 'mie' and selected_value == "Pilih level":
            messagebox.showwarning("Peringatan", "Silakan pilih level pedas")
            return
        elif item_type == 'ricebowl' and selected_value == "Pilih saus":
            messagebox.showwarning("Peringatan", "Silakan pilih saus")
            return
            
        # Process the selection
        if item_type == 'mie':
            customization = f" - {selected_value}"
        elif item_type == 'ricebowl':
            if selected_value != "Tanpa saus":  # Only add sauce to name if it's not "Tanpa saus"
                customization = f" - {selected_value}"
    
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

# Create main window
root = tk.Tk()
root.title("BOWL&BITE")
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
categories = ['Makanan', 'Minuman', 'Cemilan']
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
        
        # Add customization options directly in the menu
        customization_var = None
        if details.get('customizable', False):
            if details['type'] == 'mie':
                tk.Label(item_frame, text="Level Pedas:", font=('Arial', 9), fg='blue', bg='white').pack(anchor='w', padx=5)
                customization_var = tk.StringVar()  # No default value
                
                level_options = [f"Level {i}" for i in range(1, 6)]
                level_dropdown = ttk.Combobox(item_frame, textvariable=customization_var, values=level_options, state="readonly", width=15)
                level_dropdown.pack(pady=5)
                level_dropdown.set("Pilih level")
                
            elif details['type'] == 'ricebowl':
                tk.Label(item_frame, text="Saus:", font=('Arial', 9), fg='blue', bg='white').pack(anchor='w', padx=5)
                customization_var = tk.StringVar()  # No default value
                
                sauce_options = ["Tanpa saus"] + ricebowl_sauces
                sauce_dropdown = ttk.Combobox(item_frame, textvariable=customization_var, values=sauce_options, state="readonly", width=15)
                sauce_dropdown.pack(pady=5)
                sauce_dropdown.set("Pilih saus")
        
        # Add button with customization variable
        add_button = tk.Button(
            item_frame, 
            text="Tambahkan ke pesanan", 
            bg='#4CAF50', 
            fg='white',
            command=lambda x=item, y=details['price'], z=customization_var, t=details.get('type', None): 
                add_to_cart_with_customization(x, y, z, t)
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
semua_btn = tk.Button(category_buttons_frame, text="Semua", command=lambda: show_category('Semua'), **button_style)
makanan_btn = tk.Button(category_buttons_frame, text="Makanan", command=lambda: show_category('Makanan'), **button_style)
minuman_btn = tk.Button(category_buttons_frame, text="Minuman", command=lambda: show_category('Minuman'), **button_style)
cemilan_btn = tk.Button(category_buttons_frame, text="Cemilan", command=lambda: show_category('Cemilan'), **button_style)

# Pack the buttons side by side
semua_btn.pack(side='left', padx=5, pady=10)
makanan_btn.pack(side='left', padx=5, pady=10)
minuman_btn.pack(side='left', padx=5, pady=10)
cemilan_btn.pack(side='left', padx=5, pady=10)

# Show the "Semua" category by default
show_category('Semua')

# Right Frame - Cart
right_frame = tk.Frame(root, bg='#e0e0e0')
right_frame.place(relx=0.6, rely=0, relwidth=0.4, relheight=1)

# Cart Title
tk.Label(right_frame, text="Pesanan", font=('Segoe UI', 20, 'bold'), bg='#e0e0e0').pack(pady=10)

# Function to remove item from cart
def remove_from_cart():
    selected_item = cart_table.focus()
    if not selected_item:
        messagebox.showwarning("Peringatan", "Pilih item untuk dihapus")
        return
    
    # Get the item name from the selected row
    item_name = cart_table.item(selected_item)['values'][0]
    
    # Find the item in the cart and decrease quantity by 1
    for i, item in enumerate(cart):
        if item['item'] == item_name:
            # Decrease quantity by 1
            item['qty'] -= 1
            # Update total price
            item['total'] = item['qty'] * item['price']
            
            # If quantity is 0, remove the item completely
            if item['qty'] <= 0:
                cart.pop(i)
            
            break
    
    # Update the display
    update_cart_display()

# Cart Table with scrollbar
cart_frame = tk.Frame(right_frame, bg='#e0e0e0')
cart_frame.pack(pady=10, padx=10, fill='both', expand=True)

cart_table = ttk.Treeview(cart_frame, columns=('Item', 'Price', 'Qty', 'Total'), show='headings')
cart_table.heading('Item', text='Item')
cart_table.heading('Price', text='Price')
cart_table.heading('Qty', text='Qty')
cart_table.heading('Total', text='Total')

# Set column widths
cart_table.column('Item', width=150)
cart_table.column('Price', width=80)
cart_table.column('Qty', width=40)
cart_table.column('Total', width=80)

# Add scrollbar to cart table
cart_scroll = ttk.Scrollbar(cart_frame, orient="vertical", command=cart_table.yview)
cart_table.configure(yscrollcommand=cart_scroll.set)

cart_table.pack(side='left', fill='both', expand=True)
cart_scroll.pack(side='right', fill='y')

# Remove Button
remove_button = tk.Button(right_frame, text="Hapus Pesanan yang Dipilih", 
                         command=remove_from_cart,
                         bg='#f44336', fg='white',
                         font=('Arial', 10))
remove_button.pack(pady=5)

# Total Label
total_label = tk.Label(right_frame, text="Total: Rp 0", 
                      font=('Arial', 15, 'bold'), bg='#e0e0e0')
total_label.pack(pady=10)

# Payment Button
tk.Button(right_frame, text="Proses Pembayaran", 
         command=process_payment,
         bg='#2196F3', fg='white',
         font=('Arial', 12, 'bold'),
         width=20, height=2).pack(pady=10)

# Start the application
root.mainloop()
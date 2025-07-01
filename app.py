import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from pdf_generator import PurchaseOrderPDF

def initialize_session_state():
    """Initialize session state variables"""
    if 'items' not in st.session_state:
        st.session_state['items'] = []
    if 'po_counter' not in st.session_state:
        st.session_state['po_counter'] = 1
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'user_email' not in st.session_state:
        st.session_state['user_email'] = ''

# Sample credentials - In production, use proper authentication
SAMPLE_USERS = {
    "admin@kovanlabs.com": "admin123",
    "manager@kovanlabs.com": "manager123",
    "user@kovanlabs.com": "password123"
}

def authenticate_user(email, password):
    """Authenticate user with sample credentials"""
    return email in SAMPLE_USERS and SAMPLE_USERS[email] == password

def show_login_form():
    """Display login form"""
    st.markdown("""
    <div style="text-align: center; padding: 50px 0;">
        <h1>🔐 Kovan Labs Purchase Order System</h1>
        <p style="font-size: 18px; color: #666;">Please login to access the Purchase Order Generator</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("### Login")
            
            with st.form("login_form"):
                email = st.text_input("📧 Email Address", placeholder="Enter your email")
                password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    login_button = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
                
                if login_button:
                    if authenticate_user(email, password):
                        st.session_state['authenticated'] = True
                        st.session_state['user_email'] = email
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password. Please try again.")
            
            # Show sample credentials
            with st.expander("📋 Sample Login Credentials"):
                st.markdown("""
                **For testing purposes, use any of these credentials:**
                
                🔹 **Admin**: admin@kovanlabs.com / admin123  
                🔹 **Manager**: manager@kovanlabs.com / manager123  
                🔹 **User**: user@kovanlabs.com / password123
                """)

def show_header():
    """Show header with user info and logout"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"👋 Welcome, **{st.session_state['user_email']}**")
    
    with col2:
        if st.button("🚪 Logout", type="secondary"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def add_item():
    """Add new item to the list"""
    if st.session_state.item_name and st.session_state.item_qty > 0 and st.session_state.item_price > 0:
        total = st.session_state.item_qty * st.session_state.item_price
        st.session_state['items'].append({
            'item': st.session_state.item_name,
            'quantity': st.session_state.item_qty,
            'unit_price': st.session_state.item_price,
            'total': total
        })
        st.success(f"✅ Added: {st.session_state.item_name} (Qty: {st.session_state.item_qty}, Price: Rs.{st.session_state.item_price:,.2f})")
        # Note: Clear fields manually after adding

def remove_item(index):
    """Remove item from the list"""
    st.session_state['items'].pop(index)

def calculate_totals():
    """Calculate subtotal and total"""
    if st.session_state['items']:
        subtotal = sum(item['total'] for item in st.session_state['items'])
        return subtotal, subtotal  # No tax calculation for now
    return 0.0, 0.0

def main():
    st.set_page_config(page_title="Purchase Order Generator", page_icon="📋", layout="wide")
    
    # Initialize session state
    initialize_session_state()
    
    # Check authentication
    if not st.session_state['authenticated']:
        show_login_form()
        return
    
    # Show header with user info
    show_header()
    
    st.title("📋 Purchase Order Generator")
    st.markdown("---")
    
    # Company Information Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Company Information")
        company_name = st.text_input("Company Name", value="Kovan Labs", key="company_name")
        company_address = st.text_area("Company Address", 
                                     value="GF44, Tidel park, Coimbatore, India - 641 014", 
                                     key="company_address")
        company_phone = st.text_input("Phone Number", value="8675955999", key="company_phone")
    
    with col2:
        st.header("Order Details")
        # Generate PO number
        po_number = st.text_input("PO Number", 
                                value=f"PO{datetime.now().strftime('%Y%m%d')}{st.session_state['po_counter']:03d}", 
                                key="po_number")
        order_date = st.date_input("Order Date", value=datetime.now().date(), key="order_date")
        due_date = st.date_input("Due Date", 
                               value=(datetime.now() + timedelta(days=2)).date(), 
                               key="due_date")
    
    st.markdown("---")
    
    # Bill To and Ship To Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Bill To:")
        bill_to_name = st.text_input("Bill To Company", key="bill_to_name")
        bill_to_address = st.text_area("Bill To Address", key="bill_to_address")
        bill_to_phone = st.text_input("Bill To Phone", key="bill_to_phone")
    
    with col2:
        st.header("Ship To:")
        ship_to_same = st.checkbox("Same as Bill To", key="ship_to_same")
        if ship_to_same:
            ship_to_name = bill_to_name
            ship_to_address = bill_to_address
            ship_to_phone = bill_to_phone
        else:
            ship_to_name = st.text_input("Ship To Company", key="ship_to_name")
            ship_to_address = st.text_area("Ship To Address", key="ship_to_address")
            ship_to_phone = st.text_input("Ship To Phone", key="ship_to_phone")
    
    st.markdown("---")
    
    # Items Section
    st.header("Items")
    
    # Add new item form
    with st.expander("Add New Item", expanded=True):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.text_input("Item Description", key="item_name", placeholder="Enter item description")
        
        with col2:
            st.number_input("Quantity", min_value=1, value=1, key="item_qty")
        
        with col3:
            st.number_input("Unit Price (Rs.)", min_value=0.0, format="%.2f", key="item_price")
        
        with col4:
            st.write("")  # Empty space for alignment
            if st.button("Add Item", type="primary"):
                add_item()
        
        st.info("💡 Tip: After adding an item, manually clear the fields above to add another item.")
    
    # Display current items
    if st.session_state['items']:
        st.subheader("Current Items")
        
        # Create DataFrame for display
        df = pd.DataFrame(st.session_state['items'])
        
        # Display items with remove buttons
        for i, item in enumerate(st.session_state['items']):
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.write(item['item'])
            with col2:
                st.write(f"{item['quantity']}")
            with col3:
                st.write(f"Rs.{item['unit_price']:,.2f}")
            with col4:
                st.write(f"Rs.{item['total']:,.2f}")
            with col5:
                if st.button("Remove", key=f"remove_{i}"):
                    remove_item(i)
                    st.rerun()
        
        # Calculate totals
        subtotal, total = calculate_totals()
        
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col2:
            st.write(f"**Subtotal: Rs.{subtotal:,.2f}**")
            st.write(f"**Total: Rs.{total:,.2f}**")
    
    st.markdown("---")
    
    # Notes and Terms
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Notes")
        notes = st.text_area("Additional Notes", key="notes", height=100)
    
    with col2:
        st.header("Terms & Conditions")
        terms = st.text_area("Terms & Conditions", 
                           value="Upon accepting this purchase order, you hereby agree to the terms & conditions.",
                           key="terms", height=100)
    
    st.markdown("---")
    
    # Generate PDF Button
    if st.session_state['items'] and bill_to_name:
        if st.button("Generate Purchase Order PDF", type="primary", use_container_width=True):
            try:
                # Prepare data for PDF generation
                po_data = {
                    'company_name': company_name,
                    'company_address': company_address,
                    'company_phone': company_phone,
                    'po_number': po_number,
                    'order_date': order_date.strftime('%Y-%m-%d'),
                    'due_date': due_date.strftime('%Y-%m-%d'),
                    'bill_to_name': bill_to_name,
                    'bill_to_address': bill_to_address,
                    'bill_to_phone': bill_to_phone,
                    'ship_to_name': ship_to_name,
                    'ship_to_address': ship_to_address,
                    'ship_to_phone': ship_to_phone,
                    'items': st.session_state['items'],
                    'subtotal': subtotal,
                    'total': total,
                    'notes': notes,
                    'terms': terms
                }
                
                # Generate PDF
                pdf_generator = PurchaseOrderPDF()
                pdf_buffer = pdf_generator.generate_pdf(po_data)
                
                # Download button
                st.download_button(
                    label="Download Purchase Order PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"PO_{po_number}.pdf",
                    mime="application/pdf",
                    type="secondary",
                    use_container_width=True
                )
                
                st.success("Purchase Order PDF generated successfully!")
                
                # Increment PO counter for next order
                st.session_state['po_counter'] += 1
                
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    
    else:
        if not st.session_state['items']:
            st.warning("Please add at least one item to generate the purchase order.")
        if not bill_to_name:
            st.warning("Please fill in the Bill To information.")

if __name__ == "__main__":
    main() 
import random
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

# --- Configuration ---
FILENAME = "20_Page_Invoice.pdf"
# ~35 items per page * 20 pages = 700 items
NUM_ITEMS = 700  
COMPANY_NAME = "NEXUS SYSTEMS INTEGRATION"
INVOICE_NUM = "NEX-2024-882"

def get_date():
    """Returns a random date in 2024"""
    start = datetime.date(2024, 1, 1)
    return (start + datetime.timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")

def add_footer(canvas, doc):
    """Adds page numbers to the bottom of every page"""
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    page_num = canvas.getPageNumber()
    
    # Bottom Left text
    canvas.drawString(inch, 0.75 * inch, f"Invoice: {INVOICE_NUM}")
    
    # Bottom Right Page Number
    text = f"Page {page_num}"
    canvas.drawRightString(letter[0] - inch, 0.75 * inch, text)
    
    # Footer Line
    canvas.setStrokeColor(colors.darkgreen)
    canvas.line(inch, 0.85 * inch, letter[0] - inch, 0.85 * inch)
    canvas.restoreState()

def create_20_page_invoice():
    doc = SimpleDocTemplate(FILENAME, pagesize=letter, topMargin=0.5*inch, bottomMargin=1*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    style_title = ParagraphStyle(name='Header', parent=styles['Heading1'], textColor=colors.darkgreen, fontSize=22)
    style_right = ParagraphStyle(name='Right', parent=styles['Normal'], alignment=TA_RIGHT)

    # --- 1. Header Section ---
    # Logo area (left) and Address (right)
    header_text = f"""
    <b>{COMPANY_NAME}</b><br/>
    Tech Park Plaza, Building 4<br/>
    San Francisco, CA 94105<br/>
    support@nexussystems.com
    """
    
    invoice_info = f"""
    <b>INVOICE DETAILS</b><br/>
    Invoice #: {INVOICE_NUM}<br/>
    Date: {datetime.date.today()}<br/>
    PO #: PO-9982-A
    """
    
    data_header = [[Paragraph(header_text, styles['Normal']), Paragraph(invoice_info, style_right)]]
    t_header = Table(data_header, colWidths=[4*inch, 3*inch])
    elements.append(t_header)
    elements.append(Spacer(1, 20))

    # --- 2. Bill To / Ship To ---
    data_addr = [
        ['BILL TO:', 'SHIP TO:'],
        ['CyberDyne Corp\nAttn: Accounts Payable\n101 Robot Way\nAustin, TX 78701', 
         'CyberDyne Warehouse 4\nLoading Dock B\n101 Robot Way\nAustin, TX 78701']
    ]
    t_addr = Table(data_addr, colWidths=[3.5*inch, 3.5*inch])
    t_addr.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # Headers Bold
        ('TEXTCOLOR', (0,0), (-1,0), colors.darkgreen), # Green Headers
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t_addr)
    elements.append(Spacer(1, 30))

    # --- 3. Main Data Table ---
    # Required Columns: Item code, Description, Delivery date, Quantity, Unit price, Total amount
    headers = ['Item Code', 'Description', 'Delivery Date', 'Qty', 'Unit Price', 'Total Amount']
    data = [headers]

    # Generate 700 line items
    services = [
        ('SVR-X1', 'Cloud Server Instance (Standard)', 45.00),
        ('DB-SQL', 'SQL Database License (Per Core)', 120.00),
        ('NET-5G', '5G Network Module Adapter', 85.50),
        ('SEC-FW', 'Firewall Security Patching', 250.00),
        ('DEV-HR', 'Developer Hourly Rate', 150.00),
        ('API-CALL', 'API Gateway Usage (10k units)', 15.00)
    ]

    total_invoice = 0.0

    for i in range(NUM_ITEMS):
        code_prefix, name, base_price = random.choice(services)
        
        item_code = f"{code_prefix}-{random.randint(1000, 9999)}"
        description = f"{name} - Batch {random.randint(1,50)}"
        del_date = get_date()
        qty = random.randint(1, 20)
        price = base_price
        total = qty * price
        total_invoice += total
        
        row = [
            item_code,
            description,
            del_date,
            str(qty),
            f"${price:,.2f}",
            f"${total:,.2f}"
        ]
        data.append(row)

    # Table Styling
    # repeatRows=1 ensures the header appears on every new page
    t_main = Table(data, colWidths=[1.2*inch, 2.8*inch, 1*inch, 0.6*inch, 0.9*inch, 1*inch], repeatRows=1)
    
    t_main.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkgreen),   # Green Header
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),        # White Header Text
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),                # Right align numbers
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),   # Grid lines
        ('FONTSIZE', (0,0), (-1,-1), 8),                   # Slightly smaller font for density
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.Color(0.95, 0.95, 0.95)]) # Subtle zebra striping
    ]))
    
    elements.append(t_main)
    elements.append(Spacer(1, 10))

    # --- 4. Grand Total ---
    total_data = [
        ['', '', 'Subtotal:', f"${total_invoice:,.2f}"],
        ['', '', 'Tax (8%):', f"${total_invoice*0.08:,.2f}"],
        ['', '', 'TOTAL DUE:', f"${total_invoice*1.08:,.2f}"]
    ]
    t_total = Table(total_data, colWidths=[3*inch, 2*inch, 1*inch, 1.5*inch])
    t_total.setStyle(TableStyle([
        ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (-1,-1), (-1,-1), colors.darkgreen),
        ('LINEABOVE', (-2,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(t_total)

    # Build PDF
    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    print(f"Success! Generated {FILENAME} (~20 pages)")

if __name__ == "__main__":
    create_20_page_invoice()
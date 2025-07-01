import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Try to import SVG support
try:
    from svglib.svglib import svg2rlg
    SVG_AVAILABLE = True
except ImportError:
    SVG_AVAILABLE = False

class PurchaseOrderPDF:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Company name style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.black,
            spaceAfter=0,
            alignment=TA_LEFT
        ))
        
        # Tagline style
        self.styles.add(ParagraphStyle(
            name='Tagline',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            spaceAfter=20,
            alignment=TA_LEFT
        ))
        
        # Purchase Order title style - aligned to start at same level as logo
        self.styles.add(ParagraphStyle(
            name='POTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.black,
            spaceAfter=15,  # Add proper space after title
            spaceBefore=0,
            leading=20,  # Set line height to match font size for precise alignment
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Address style
        self.styles.add(ParagraphStyle(
            name='Address',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=4,
            alignment=TA_LEFT
        ))
        
        # Right aligned style with better spacing
        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_RIGHT,
            spaceAfter=3,
            spaceBefore=0,
            leading=14  # Better line spacing
        ))
        
        # Style for item descriptions with word wrapping
        self.styles.add(ParagraphStyle(
            name='ItemDescription',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0,
            wordWrap='CJK'
        ))
    
    def create_logo(self):
        """Load and create the Kovan Labs logo from SVG"""
        try:
            # Check if SVG file exists
            if os.path.exists('kovan.svg') and SVG_AVAILABLE:
                # Use the correct svglib function to convert SVG to ReportLab drawing
                logo = svg2rlg('kovan.svg')
                # Scale the logo to appropriate size for header
                logo.width = 70
                logo.height = 55
                logo.scale(0.35, 0.35)
                return logo
            else:
                # SVG file doesn't exist or svglib not available, use text fallback
                return Paragraph("<b>KOVAN LABS</b>", self.styles['CompanyName'])
                
        except Exception as e:
            print(f"Error loading SVG logo: {e}")
            # Any other error, use text fallback
            return Paragraph("<b>KOVAN LABS</b>", self.styles['CompanyName'])

    
    def generate_pdf(self, po_data):
        """Generate the complete purchase order PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=0.75*inch, leftMargin=0.5*inch,  # Reduced left margin for better left alignment
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        story = []
        
        # Header with logo and purchase order title - perfect alignment and spacing
        header_data = [
            [self.create_logo(), 
             '',
             [Paragraph("PURCHASE ORDER", self.styles['POTitle']),
              Paragraph(f"PO Number: {po_data['po_number']}", self.styles['RightAlign']),
              Paragraph(f"Order Date: {po_data['order_date']}", self.styles['RightAlign']),
              Paragraph(f"Purchase Date: {po_data['due_date']}", self.styles['RightAlign'])]]
        ]
        
        header_table = Table(header_data, colWidths=[1.8*inch, 2.2*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (0, 0), 'TOP'),    # Logo aligned to top
            ('VALIGN', (2, 0), (2, 0), 'TOP'),    # Purchase order section aligned to top
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),    # Logo left aligned
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),   # Purchase order right aligned
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (0, 0), 0),   # No left padding for logo - flush left
            ('RIGHTPADDING', (2, 0), (2, 0), 0),  # No right padding for PO section
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # Company details - properly aligned with logo
        company_info = f"{po_data['company_name']}<br/>{po_data['company_address']}<br/>{po_data['company_phone']}"
        company_para = Paragraph(company_info, self.styles['Address'])
        
        # Create table for company info to ensure left alignment
        company_table = Table([[company_para]], colWidths=[6.5*inch])
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 0),
        ]))
        
        story.append(company_table)
        story.append(Spacer(1, 25))
        
        # Bill To and Ship To section - perfectly aligned
        bill_ship_data = [
            [Paragraph("Bill To:", self.styles['SectionHeader']),
             Paragraph("Ship To:", self.styles['SectionHeader'])],
            [Paragraph(f"{po_data['bill_to_name']}<br/>{po_data['bill_to_address']}<br/>{po_data['bill_to_phone']}", 
                      self.styles['Address']),
             Paragraph(f"{po_data['ship_to_name']}<br/>{po_data['ship_to_address']}<br/>{po_data['ship_to_phone']}", 
                      self.styles['Address'])]
        ]
        
        bill_ship_table = Table(bill_ship_data, colWidths=[3.25*inch, 3.25*inch])
        bill_ship_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),   # Bill To aligned left
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),   # Ship To aligned left
            ('LEFTPADDING', (0, 0), (0, 0), 0),  # No left padding for first column
            ('LEFTPADDING', (1, 0), (1, -1), 20), # Some left padding for Ship To
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(bill_ship_table)
        story.append(Spacer(1, 25))
        
        # Items table with proper text wrapping
        items_data = [['Item', 'Quantity', 'Unit Price', 'Total']]
        
        for item in po_data['items']:
            # Create paragraph for item description to enable word wrapping
            item_para = Paragraph(item['item'], self.styles['ItemDescription'])
            items_data.append([
                item_para,
                str(item['quantity']),
                f"Rs.{item['unit_price']:,.2f}",
                f"Rs.{item['total']:,.2f}"
            ])
        
        # Adjust column widths to give more space for item descriptions
        items_table = Table(items_data, colWidths=[4*inch, 0.8*inch, 1.1*inch, 1.1*inch])
        items_table.setStyle(TableStyle([
            # Header row - Light gray background instead of black
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Center align quantity, price, total
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),    # Align content to top for better text wrapping
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),  # Alternating row colors
            ('LEFTPADDING', (0, 1), (0, -1), 8),   # Add padding for item descriptions
            ('RIGHTPADDING', (0, 1), (0, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 15))
        
        # Totals section - properly aligned with adjusted column widths
        totals_data = [
            ['', '', 'Subtotal:', f"Rs.{po_data['subtotal']:,.2f}"],
            ['', '', 'Total:', f"Rs.{po_data['total']:,.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[4*inch, 0.8*inch, 1.1*inch, 1.1*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (2, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (2, 0), (-1, -1), 11),
            ('LINEABOVE', (2, 1), (-1, 1), 2, colors.black),
            ('TOPPADDING', (2, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (2, 0), (-1, -1), 8),
        ]))
        
        story.append(totals_table)
        story.append(Spacer(1, 25))
        
        # Notes section with proper title
        if po_data.get('notes'):
            story.append(Paragraph("Notes:", self.styles['SectionHeader']))
            story.append(Paragraph(po_data['notes'], self.styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Terms and Conditions
        if po_data.get('terms'):
            story.append(Paragraph(po_data['terms'], self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer 
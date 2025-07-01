# Purchase Order Generator

A dynamic Purchase Order application built with Streamlit that allows you to create professional purchase orders and download them as PDF files.

## Features

- **Dynamic Form Interface**: Easy-to-use web interface for creating purchase orders
- **Company Branding**: Customizable company information and logo
- **Dynamic Item Management**: Add/remove multiple items with automatic total calculations
- **Professional PDF Generation**: Creates properly formatted PDF documents
- **Instant Download**: Download generated PDFs immediately
- **Responsive Design**: Works on desktop and mobile devices

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:

```bash
streamlit run app.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. Fill out the purchase order form:
   - **Company Information**: Enter your company details
   - **Order Details**: Set PO number, dates
   - **Bill To/Ship To**: Enter vendor information
   - **Items**: Add products/services with quantities and prices
   - **Notes & Terms**: Add any additional information

4. Click "Generate Purchase Order PDF" to create the PDF

5. Download the generated PDF file

## Features in Detail

### Dynamic Item Management
- Add unlimited items to your purchase order
- Automatic calculation of line totals and grand total
- Easy removal of items with dedicated remove buttons

### Professional PDF Output
- Clean, professional layout matching business standards
- Company logo and branding
- Properly formatted tables and totals
- Terms and conditions section

### Customizable Company Information
- Company name and address
- Contact information
- Logo integration (placeholder included)

## File Structure

```
purchase-order-app/
├── app.py                 # Main Streamlit application
├── pdf_generator.py       # PDF generation utilities
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Customization

### Adding Your Company Logo
1. Place your logo image file in the project directory
2. Update the `create_logo_placeholder()` method in `pdf_generator.py`
3. Replace the placeholder with actual image loading code

### Styling
- Modify styles in `pdf_generator.py` to match your brand colors
- Adjust layout and formatting as needed
- Customize form fields in `app.py`

## Dependencies

- **Streamlit**: Web application framework
- **ReportLab**: PDF generation library
- **Pandas**: Data manipulation
- **Pillow**: Image processing

## License

This project is open source and available under the MIT License.

## Support

For questions or issues, please refer to the documentation or create an issue in the project repository. 
# Packages
import os
import json
import pdfplumber

# Parsed invoices database
invoices = []

# Loop over files in current directory
for filename in sorted(os.listdir()):
  # Skip non PDF files
  if '.pdf' not in filename: continue
  
  # Parsed invoice holder
  invoice = {}
  
  # Read PDF file
  with pdfplumber.open(filename) as pdf:
    # Extract tect from PDF
    text = pdf.pages[0].extract_text() + '\n'
    
    # Extract header
    invoice['File Name'] = filename
    invoice['Invoice No'] = text.split('Invoice No:')[-1].split('\n')[0].strip()
    invoice['Customer'] = text.split('Customer:')[-1].split('\n')[0].strip()
    invoice['Date'] = text.split('Date:')[-1].split('\n')[0].strip()
    invoice['Reference Code'] = text.split('Reference Code:')[-1].split('\n')[0].strip()
    
    # Extract table data
    services = []
    for i, row in enumerate(text.split('\n')):
      if i < 6: continue
      if 'Subtotal' in row: break
      services.append({
        'Service Description': ' '.join(row.split(' ')[:-3]),
        'Hours': row.split(' ')[-3],
        'Rate (USD)': row.split(' ')[-2],
        'Line Total': row.split(' ')[-1]
      })
    
    # Append services
    invoice['services'] = services
    
    # Extract footer
    invoice['Subtotal'] = text.split('Subtotal:')[-1].split('\n')[0].strip()
    invoice['Tax (15%)'] = text.split('Tax (15%):')[-1].split('\n')[0].strip()
    invoice['Total Due'] = text.split('Total Due:')[-1].split('\n')[0].strip()
    invoice['Payment Terms'] = text.split('Payment Terms:')[-1].split('\n')[0].strip()
    invoice['Bank Reference'] = text.split('Bank Reference:')[-1].split('\n')[0].strip()
    
    # Append parsed invoice to database
    invoices.append(invoice)
    
# Write parsed invoice database to JSON file
with open('invoices.json', 'w') as out:
  out.write(json.dumps(invoices, indent=2))
  print('All done. See file "invoices.json"')





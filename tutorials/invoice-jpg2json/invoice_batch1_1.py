# Packages
from PIL import Image
import pytesseract
import json
import os

# Database of invoices
invoices = []
  
# Convert Invoice from JPG to JSON
def parse_invoice(filename):
  # Load image
  invoice_img = Image.open(filename)
  
  # Extract text from image (OCR)
  custom_config = r'-c preserve_interword_spaces=1'
  invoice_text = pytesseract.image_to_string(invoice_img, config=custom_config)
  
  # Temp variables
  seller_name = ''
  seller_address = ''
  seller_tax_id = ''
  seller_iban = ''
  client_name = ''
  client_address = ''
  client_tax_id = ''
  items = []
  
  # Extract seller & client rows
  for i, row in enumerate(invoice_text.split('\n')):
    if i < 5: continue
    if 'ITEMS' in row: break
    if i == 6:
      seller_name = row.split('  ')[0].strip()
      client_name = row.split('  ')[-1].strip()
    if i == 8:
      seller_address = row.split('  ')[0].strip() + ', '
      client_address = row.split('  ')[-1].strip() + ', '
    if i == 9:
      seller_address += row.split('  ')[0].strip()
      client_address += row.split('  ')[-1].strip()
    if i == 11:
      seller_tax_id += row.split('  ')[0].strip().split('Tax Id:')[-1].strip()
      client_tax_id += row.split('  ')[-1].strip().split('Tax Id:')[-1].strip()
    if i == 13: seller_iban += row.split('  ')[0].strip().split('IBAN:')[-1].strip()
  
  # Extract items
  more_rows = 0
  items = []
  item = {}
  
  # Find items row id
  items_id = [i for i, row in enumerate(invoice_text.split('\n')) if 'ITEMS' in row][0]
  
  # loop over table rows
  for i, row in enumerate(invoice_text.split('\n')):
    more_rows = 0
    
    # Skip rows
    if i < items_id+3: continue
    if 'SUMMARY' in row: break
    
    # Find additional description lines
    if len(row.split('  ')) == 1: more_rows = 1
    
    # Find first description line
    if more_rows == 0:
      # Store table row
      if len(item.keys()):
        item['Description'] = ' '.join(item['Description']).strip()
        items.append(item)
      
      # Filter columns
      cols = list(filter(None, row.split('   ')))
      
      # Create table row item
      item = { 
        'Description': [row.split('   ')[1]],
        'Qty': cols[-6],
        'UM': cols[-5],
        'Net price': cols[-4],
        'Net worth': cols[-3],
        'VAT [%]': cols[-2],
        'Gross worth': cols[-1]
      }
  
    # Populate description
    if more_rows == 1:
      item['Description'].append(row.split('   ')[0])
  
  # Store last table row
  item['Description'] = ' '.join(item['Description']).strip()
  items.append(item)
  
  # Find SUMMARY row index
  summary_id = [i for i, row in enumerate(invoice_text.split('\n')) if 'SUMMARY' in row][0]
  
  # Loop over the table rows
  for i, row in enumerate(invoice_text.split('\n')):
    if i < summary_id + 2: continue
    
    # Filter columns
    cols = list(filter(None, row.split('   ')))
    
    # Append summary line 1
    if 'Total' not in row and len(row):
      summary = {
        'VAT [%]': cols[-4],
        'Net worth': cols[-3],
        'VAT': cols[-2],
        'Gross worth': cols[-1]
      }
  
  # Parsed invoice
  invoice = {
    'Invoice no': invoice_text.split('Invoice no:')[-1].split('\n')[0].strip(),
    'Date of issue': invoice_text.split('Date of issue:')[-1].split('\n')[0].strip(),
    'Seller name': seller_name,
    'Seller address': seller_address,
    'Seller tax Id': seller_tax_id,
    'Seller IBAN': seller_iban,
    'Client name': client_name,
    'Client address': client_address,
    'Client tax id': client_tax_id,
    'Items': items,
    'Summary': summary
  }
  
  # Append invoice to DB
  invoices.append(invoice)

# Read all invoices
for filename in sorted(os.listdir('./batch1_1/')):
  if '.jpg' not in filename: continue
  print(f'parsing file: {filename}')
  parse_invoice('./batch1_1/' + filename)

# Write invoices to JSON file
with open('invoices.json', 'w') as out:
  out.write(json.dumps(invoices, indent=2))
  print('All done. See file "invoices.json"')

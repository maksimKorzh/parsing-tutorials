# Package
import numpy as np
import easyocr

# Read the file
reader = easyocr.Reader(['en'])
result = reader.readtext('./invoices-easyocr/batch1-0003.jpg')

# Token Y coord
def get_center_y(bbox):
  return np.mean([point[1] for point in bbox])

# Token X coord
def get_min_x(bbox):
  return min(point[0] for point in bbox)

# Arrange lines
def cluster_lines(results, y_threshold=15):
  lines = []
  for bbox, text, conf in results:
    cy = get_center_y(bbox)
    placed = False
    for line in lines:
      if abs(line['y'] - cy) < y_threshold:
        line['items'].append((bbox, text))
        placed = True
        break
    if not placed:
      lines.append({'y': cy, 'items': [(bbox, text)]})
  return lines

# Restore original layout
def sort_lines(lines):
  lines = sorted(lines, key=lambda l: l['y'])
  structured_text = []
  for line in lines:
    items = sorted(line['items'], key = lambda x: get_min_x(x[0]))
    if len(items) > 2: line_text = '     '.join([text for _,text in items])
    else: line_text = ne_text = '   '.join([text for _,text in items])
    structured_text.append(line_text)
  return '\n'.join(structured_text)

# Parse lines
lines = cluster_lines(result)
structured_text = sort_lines(lines)

# Print output
print(structured_text)

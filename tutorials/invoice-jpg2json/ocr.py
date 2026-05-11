import numpy as np
import easyocr

def extract_text(filename):
  reader = easyocr.Reader(['en'])
  result = reader.readtext(filename)
  
  def get_center_y(bbox):
    return np.mean([point[1] for point in bbox])
  
  def get_min_x(bbox):
    return min(point[0] for point in bbox)
  
  def cluster_lines(results, y_threshold=15):
    lines = []
    for bbox, text, conf in results:
      cy = get_center_y(bbox)
      placed = False
      for line in lines:
        if abs(line["y"] - cy) < y_threshold:
          line["items"].append((bbox, text))
          placed = True
          break
      if not placed:
        lines.append({"y": cy, "items": [(bbox, text)]})
    return lines
  
  def sort_lines(lines):
    # sort lines vertically
    lines = sorted(lines, key=lambda l: l["y"])
    structured_text = []
    for line in lines:
      # sort words horizontally
      items = sorted(line["items"], key=lambda x: get_min_x(x[0]))
      if len(items) > 2: line_text = "     ".join([text for _, text in items])
      else: line_text = " ".join([text for _, text in items])
      structured_text.append(line_text)
    return structured_text
  
  # ---------- PROCESS ----------
  lines = cluster_lines(result)
  structured_text = sort_lines(lines)
  
  # ---------- OUTPUT ----------
  structured_text.insert(1, '')
  structured_text.insert(3, '')
  structured_text.insert(5, '')
  structured_text.insert(7, '')
  structured_text.insert(10, '')
  structured_text.insert(12, '')
  structured_text.insert(14, '')
  structured_text.insert(len(structured_text)-1, '')
  structured_text[0] = structured_text[0].replace('Invoice     no:', 'Invoice no:')
  print(structured_text)  
  return '\n'.join(structured_text)

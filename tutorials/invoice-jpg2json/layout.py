import easyocr

reader = easyocr.Reader(['en'])

result = reader.readtext('./batch1_1/batch1-0002.jpg')

# Extract positioned text
items = []

for bbox, text, conf in result:
    x = bbox[0][0]
    y = bbox[0][1]

    items.append({
        "x": x,
        "y": y,
        "text": text
    })

# Sort top-to-bottom then left-to-right
items.sort(key=lambda i: (i["y"], i["x"]))

# Group into rows
rows = []
y_threshold = 15

for item in items:
    added = False

    for row in rows:
        if abs(row[0]["y"] - item["y"]) < y_threshold:
            row.append(item)
            added = True
            break

    if not added:
        rows.append([item])

# Sort each row by X coordinate
for row in rows:
    row.sort(key=lambda i: i["x"])

# Preserve approximate layout
output = []

for row in rows:
    line = ""
    current_x = 0

    for item in row:
        x = int(item["x"])

        # Convert pixel distance into spaces
        spaces = max(1, (x - current_x) // 10)

        line += " " * spaces + item["text"]

        current_x = x + len(item["text"]) * 10

    output.append(line)

formatted_text = "\n".join(output)

print(formatted_text)


import os
import re
import json
import pdfplumber

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def extract_form_fields(pdf_path):
    """
    Extracts structured fields from a form-based PDF.
    This logic is specifically tailored to parse forms with numbered items.
    """
    with pdfplumber.open(pdf_path) as pdf:
        # Extract the title from the first page
        title = pdf.pages[0].extract_text().split('\n')[0]

        all_lines = []
        for page in pdf.pages:
            # Use extract_text with layout preservation to handle spacing better
            text = page.extract_text(layout=True)
            if text:
                all_lines.extend(text.split('\n'))

    fields = []
    current_field = None

    for line in all_lines:
        line = line.strip()
        if not line:
            continue

        # Use regex to find lines that start a new field (e.g., "1.", "2.", "(a)")
        match = re.match(r"^\s*(\d+|\(\w\))\.\s*(.*)", line)

        if match:
            # If a new field starts, save the previous one (if it exists)
            if current_field:
                # Clean up the label text before saving
                current_field['label'] = ' '.join(current_field['label'].split())
                fields.append(current_field)
            
            # Start a new field
            field_id = match.group(1).replace('(', '').replace(')', '')
            label_text = match.group(2).strip()
            current_field = {"id": field_id, "label": label_text}
        
        elif current_field:
            # If it's not a new field, it's a continuation of the previous one
            current_field["label"] += " " + line

    # Add the last processed field to the list
    if current_field:
        current_field['label'] = ' '.join(current_field['label'].split())
        fields.append(current_field)

    # Structure the final output
    # This is a simplified output; a more advanced one could handle the table in item 11
    final_json = {
        "title": title,
        "fields": fields
    }

    return final_json


def main():
    """Main execution function."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for filename in os.listdir(INPUT_DIR):
        if not filename.lower().endswith(".pdf"):
            continue

        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))

        print(f"Processing form {filename}...")
        try:
            data = extract_form_fields(input_path)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Successfully created {output_path}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
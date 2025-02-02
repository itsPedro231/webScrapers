import csv
import json


def read_jsonl_to_csv(input_path: str, output_path: str) -> None:
    """
    Reads data from a JSON Lines (JSONL) file and converts it into a CSV file.

    Args:
        input_path (str): Path to the JSONL file.
        output_path (str): Path where the CSV file will be saved.

    This function processes each line of the JSONL file, extracting relevant fields
    such as company, quote, category, and subcategory. It then writes these
    processed data into a CSV file with headers: Category, Subcategory,
    Company, Slogan. The resulting data is sorted by Category before being saved.
    """
    lst = []
    with open(input_path, "r", encoding="utf-8") as file:
        line = file.readline()
        with open(output_path, "w", encoding="utf-8", newline='') as newFile:
            while line != "":
                # Remove any \n or \t characters
                line = line.replace('\\n', '').replace('\\t', '')

                try:
                    res = json.loads(line)
                except json.JSONDecodeError:
                    line = file.readline()
                    continue

                company = " ".join(str(res["company"]).strip().split())
                quote = str(res.get("quote", "")).strip()

                if company and (quote or quote.strip()):
                    lst.append({
                        "Category": str(res.get("cat", "")).strip(),
                        "Subcategory": str(res.get("subcat", "")).strip(),
                        "Company": company,
                        "Slogan": quote
                    })

                line = file.readline()

    fieldnames = ['Category', 'Subcategory', 'Company', 'Slogan']
    writer = csv.DictWriter(newFile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(sorted(lst, key=lambda d: d['Category']))
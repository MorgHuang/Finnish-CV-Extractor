# extractor.py
import pdfplumber
import re
import pandas as pd

def extract_cv_data(pdf_path: str, output_path: str = "output.xlsx"):
    results = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                blocks = re.split(r'\n{2,}', text)  # assume every CV block is seperated by two linebreak

                for block in blocks:
                    entry = {
                        "Last Name": re.search(r"Sukunimi:\s*(.*)", block),
                        "First Name": re.search(r"Etunimi:\s*(.*)", block),
                        "City": re.search(r"Paikkakunta:\s*(.*)", block),
                        "University": re.search(r"Yliopisto:\s*(.*)", block),
                        "Work History": re.search(r"Työhistoria:\s*(.*)", block),
                    }
                    clean = {k: (v.group(1).strip() if v else "") for k, v in entry.items()}
                    results.append(clean)

    df = pd.DataFrame(results)
    df.to_excel(output_path, index=False)

if __name__ == "__main__":
    extract_cv_data("sample_input/sample_cv_10pages.pdf")

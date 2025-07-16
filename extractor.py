# extractor.py
import re
import pdfplumber
import pandas as pd

# Mock list of Finnish cities for validation
finnish_cities = {
    "Helsinki", "Espoo", "Tampere", "Vantaa", "Oulu", "Turku", "Jyväskylä", "Hameenlinna", "Jyvaskyla", "Jarvenpaa", 
    "Lahti", "Kuopio", "Pori", "Joensuu", "Lappeenranta", "Rovaniemi", "Kotka", "Vantaa", "Porvoo", "Hyvinkaa", "Rauma", 
    "Pietarsaari", "Vaasa", "Seinäjoki", "Kokkola", "Porvoo", "Mikkeli", "Nurmijarvi", "Kajaani", "Tuusula", "Kerava", 
    "Nokia", "Savonlinna", "Imatra", "Kouvola", "Seinajoki", "Kirkkonummi"
}

def clean_ocr_text(text):
    text = re.sub(r'(?<=\w)\s(?=\w)', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text

def is_clean_name(name):
    return bool(re.match(r"^[A-ZÅÄÖ][a-zåäö]+(?: [A-ZÅÄÖa-zåäö]+)*$", name))

def is_clean_first_names(s):
    return (
        len(s) >= 3
        and not any(c.isdigit() for c in s)
        and re.match(r"^[A-ZÅÄÖa-zåäö .\-]+$", s)
        and not re.fullmatch(r"[a-z]{2,3}", s)
    )

def is_valid_city(city):
    return city in finnish_cities

def is_valid_entry_v5(last_name, first_names, city):
    blacklist = ['Språk', 'Barn', 'Spec', 'Stud', 'LL', 'ML', 'F', 'HU', 'HY', 'TY', 'LT', 'Pension']
    if any(kw.lower() in f"{last_name} {first_names} {city}".lower() for kw in blacklist):
        return False
    if not is_clean_name(last_name) or not is_clean_first_names(first_names):
        return False
    if not is_valid_city(city):
        return False
    return True

def extract_cv_data(pdf_path, output_path):
    with pdfplumber.open(pdf_path) as pdf:
        raw_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    clean_text = clean_ocr_text(raw_text)

    entries = []
    for match in re.finditer(r'([A-ZÅÄÖ][a-zåäö]+),\s+(.*?),\s+([A-ZÅÄÖa-zåäö\s]+?)\.', clean_text):
        last_name = match.group(1).strip()
        first_names = match.group(2).strip()
        city = match.group(3).strip()

        if not is_valid_entry_v5(last_name, first_names, city):
            continue

        nearby_text = clean_text[match.end():match.end() + 300]
        birth_date_match = re.search(r'\b(\d{2}\.\d{2}\.\d{2,4})\b', nearby_text)
        birth_date = birth_date_match.group(1) if birth_date_match else ""

        entries.append({
            "Last Name": last_name,
            "First Names": first_names,
            "City": city,
            "Date of Birth": birth_date
        })

    df = pd.DataFrame(entries)
    df.to_excel(output_path, index=False)

if __name__ == "__main__":
    extract_cv_data("sample_cv.pdf", "output_structured_cv_v5.xlsx")


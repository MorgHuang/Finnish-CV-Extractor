# extractor.py v8.1
import re
import pdfplumber
import pandas as pd
import difflib

# --- Blacklist for non-person entries and language codes ---
BLACKLIST = [
    'Språk', 'Barn', 'Spec', 'Stud', 'LL', 'ML', 'F', 'HU', 'HY', 'TY', 'LT', 'Pension',
    'osasto', 'lääkäri', 'yliopisto', 'professori', 'osastonhoitaja', 'opiskelija'
]
LANG_CODES = {'en', 'fi', 'ru', 'se', 'sv', 'de', 'fr', 'es'}

# --- Finnish city list for fuzzy city matching ---
FINNISH_CITIES = [
    "Helsinki", "Espoo", "Tampere", "Vantaa", "Oulu", "Turku", "Jyväskylä", "Hameenlinna", "Jyvaskyla", "Jarvenpaa", 
    "Lahti", "Kuopio", "Pori", "Joensuu", "Lappeenranta", "Rovaniemi", "Kotka", "Porvoo", "Hyvinkaa", "Rauma", 
    "Pietarsaari", "Vaasa", "Seinäjoki", "Kokkola", "Mikkeli", "Nurmijarvi", "Kajaani", "Tuusula", "Kerava", 
    "Nokia", "Savonlinna", "Imatra", "Kouvola", "Seinajoki", "Kirkkonummi"
]

def clean_ocr_text(text):
    """Remove excessive spaces and clean up OCR text."""
    text = re.sub(r'(?<=\w)\s(?=\w)', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text

def is_blacklisted(block):
    """Check if the block contains blacklisted words."""
    for word in BLACKLIST:
        if word.lower() in block.lower():
            return True
    return False

def clean_city_name(city):
    """Normalize city string for fuzzy matching."""
    return city.lower().replace('ä', 'a').replace('ö', 'o').replace('å', 'a').replace('-', '').replace('.', '').replace(',', '').strip()

def fuzzy_city(city):
    """Fuzzy match input city string with Finnish city list."""
    cleaned = clean_city_name(city)
    for known in FINNISH_CITIES:
        if difflib.SequenceMatcher(None, cleaned, clean_city_name(known)).ratio() > 0.85:
            return known
    return ""

def is_reasonable_name(s):
    """
    Simple validation for names and city fields:
    - Not too short, no digits, not a language code, must have a vowel, not all caps.
    """
    s_strip = s.strip()
    if len(s_strip) < 2 or any(c.isdigit() for c in s_strip):
        return False
    if s_strip.lower() in LANG_CODES:
        return False
    if not re.search(r'[aeiouyäöå]', s_strip.lower()):
        return False
    if re.fullmatch(r"[A-ZÄÖÅ]{2,}$", s_strip):
        return False
    return True

def extract_birth_date(search_area):
    """
    Extract the birth date from text area using multiple flexible patterns:
    - Supports Syntymäaika/S/F/D/d/f/t prefix
    - Accepts both dots and dashes as separators
    - Matches both 2- and 4-digit years
    """
    patterns = [
        r'(?:Syntymäaika|S|F|D|s|f|d|t)?\.?\s*[:\-]?\s*(\d{1,2}[\.|\-]\d{1,2}[\.|\-]\d{2,4})',
        r'(\d{1,2}[\.|\-]\d{1,2}[\.|\-]\d{2,4})',
    ]
    for pat in patterns:
        match = re.search(pat, search_area)
        if match:
            return match.group(1)
    return ""

def extract_entries(pdf_path):
    """
    Main extraction loop:
    - Uses a forgiving regex to find likely entries.
    - Applies blacklist and name/city reasonableness filters.
    - Fuzzy matches city names.
    - Attempts to extract a birth date using multiple patterns in a wider search area.
    - Skipped entries are logged with a reason.
    """
    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                all_text += txt + "\n"
    all_text = clean_ocr_text(all_text)

    entry_regex = re.compile(
        r"([A-ZÅÄÖ][a-zåäö\-\(\) ]+)[,]?\s+([A-ZÅÄÖa-zåäö\-\(\) ]+)[,]?\s+([A-ZÅÄÖa-zåäö\s\-\.\,]+?)[\.\,\;\:](?=\s|$)",
        re.UNICODE
    )
    entries, skipped = [], []
    for match in entry_regex.finditer(all_text):
        last_name = match.group(1).strip()
        first_names = match.group(2).strip()
        city = match.group(3).strip()
        # Search a wider area after the entry for the date
        search_area = all_text[match.end():match.end()+220]
        birth_date = extract_birth_date(search_area)

        reason = ""
        if is_blacklisted(f"{last_name} {first_names} {city}"):
            reason = "Blacklisted term"
        elif not is_reasonable_name(last_name):
            reason = "Unreasonable last name"
        elif not is_reasonable_name(first_names):
            reason = "Unreasonable first names"
        elif not is_reasonable_name(city):
            reason = "Unreasonable city"
        else:
            fuzzy_city_result = fuzzy_city(city)
            if not fuzzy_city_result:
                reason = "City not recognized"
        if reason:
            skipped.append({
                "Last Name": last_name,
                "First Names": first_names,
                "City": city,
                "Date of Birth": birth_date,
                "Reason": reason
            })
            continue

        entries.append({
            "Last Name": last_name,
            "First Names": first_names,
            "City": fuzzy_city(city),
            "Date of Birth": birth_date
        })
    return entries, skipped

if __name__ == "__main__":
    pdf_path = "sample_cv.pdf"
    output_path = "output_structured_cv_v81.xlsx"
    debug_path = "output_skipped_v81.xlsx"
    entries, skipped = extract_entries(pdf_path)
    pd.DataFrame(entries).to_excel(output_path, index=False)
    pd.DataFrame(skipped).to_excel(debug_path, index=False)
    print(f"Done! Extracted: {len(entries)}, Skipped: {len(skipped)}. See {output_path} and {debug_path}.")

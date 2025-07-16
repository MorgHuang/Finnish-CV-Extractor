### Finnish-CV-Extractor (prototype v5)
A Python-based prototype that extracts structured CV data from OCR-processed Finnish-language PDFs (e.g., directory-style scanned books). Outputs clean, tabular Excel files.

Finnish-CV-Extractor/                  
│                                    
├── sample_input/                  
│   └── sample_cv.pdf     ← placeholder                  
│                                    
├── extractor.py                  
├── requirements.txt              
├── README.md                     
└── .gitignore

#### Features

- OCR cleanup and broken-text normalization
- Flexible entry detection using `Lastname, Firstname, City.` format
- Filters out false positives (language codes, invalid names, OCR noise)
- Finnish city name validation
- Strict `dd.mm.yy` date of birth extraction

#### Sample Input

To run this prototype, place a sample 10–20 page PDF in the `sample_input/` folder and name it `sample_cv_10pages.pdf`.  
> *(Sample input not included due to confidentiality. Please contact the project owner.)*

#### Dependencies

Install required packages via pip:

```bash
pip install pdfplumber pandas
pip install -r requirements.txt
python extractor_v5.py

####Output
output_structured_cv_v81.xlsx（主要結構化欄位結果）
output_skipped_v81.xlsx（被過濾的 entry 與過濾原因）

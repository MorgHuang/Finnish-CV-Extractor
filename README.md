### Finnish-CV-Extractor
Extract structured CVs data from PDF file (of a OCR-scanned professionals directory book) into Excel (Names, Employers, Work History etc.). OUTPUT FORMAT: Excel (.xlsx). One row per person, one column per each data field.

Finnish-CV-Extractor/                  
│                                    
├── sample_input/                  
│   └── sample_cv_10pages.pdf     ← placeholder                  
│                                    
├── extractor.py                  
├── requirements.txt              
├── README.md                     
└── .gitignore

### Finnish CV Extractor (Prototype)

This is a Python prototype for extracting structured CV data from an OCR-scanned Finnish PDF directory.  
The script extracts key fields (name, city, university, work history, etc.) and exports results to Excel.

#### Sample Input

To run this prototype, place a sample 10–20 page PDF in the `sample_input/` folder and name it `sample_cv_10pages.pdf`.  
> *(Sample input not included due to confidentiality. Please contact the project owner.)*

#### Dependencies

Install required packages via pip:

```bash
pip install -r requirements.txt

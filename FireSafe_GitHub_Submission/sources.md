# NASA references and evidence provenance

FireSafe currently indexes **five NASA publication PDF files**. These references are source documents, not necessarily complete PSI experiment datasets. The application includes a small manually curated set of experiment descriptions and findings, which must be interpreted within their original test conditions.

| FireSafe key | Local PDF file | NASA NTRS reference | Notes |
| --- | --- | --- | --- |
| BASS | `BASS-20140011099.pdf` | https://ntrs.nasa.gov/citations/20140011099 | PDF p. 2: atmospheric O₂ 17–21.5%, wind-tunnel airflow up to 40 cm/s. PDF p. 22: opposed/concurrent flame-spread trends and low-flow quenching. |
| BASS-II | `BASSII-20160000593.pdf` | https://ntrs.nasa.gov/citations/20160000593 | PDF p. 12: 22 test points and thin PMMA sheet configurations of 0.1–0.4 mm. |
| Saffire | `saffire_research.pdf` | https://ntrs.nasa.gov/citations/20210011521 | PDF pp. 8–9: IV-2 and V-3 thick PMMA observations. Conditions differ, so this is not a controlled oxygen-only comparison. |
| BRE | `BRE-20160010073.pdf` | https://ntrs.nasa.gov/citations/20160010073 | PDF p. 6: specified ethylene-burner heat flux under reported conditions. |
| ACME-BRE overview | `ACME-BRE-OVERVIEW.pdf` | Refer to original PDF/metadata | Background documentation; check the source record before citing measurements. |

## How page references work

A citation such as `BASS:pdf-p22` means the 22nd **PDF page**, counting from 1; this may differ from a printed page number within the document. Review the original PDF page before quoting or interpreting a finding.

## Reproducibility

To run the local indexer, attach the existing `FireSafe AI v3 Training Data` Kaggle dataset or provide the five PDF files in a local `papers/` directory. The PDF files are intentionally **not** duplicated in this code package. Use the authoritative research sources and respect each source's applicable rights and attribution.

## Scientific limitations

FireSafe is a research-assistance prototype. Numerical observations, experimental conditions, model-generated interpretations, and predictive simulations are not interchangeable. The application does **not** certify spacecraft fire safety.

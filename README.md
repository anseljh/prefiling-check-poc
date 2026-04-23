# prefiling-check-poc

Proof of concept for a pre-filing brief checker

## Purpose

Provide a simple graphical interface to select a PDF or DOCX file on the user's computer.

Run checks and show the results at a high level, and generate a more detailed report that can be saved as a PDF or DOCX file.

## Steps

1. Extract text from the PDF or DOCX file and save it to disk.
    - For PDFs, use Liteparse (Python package: `liteparse`)
    - For DOCX, use `python-docx` (Python package: `python-docx`)
2. Extract citations using Eyecite (Python package: `eyecite`)
3. Run checks against each extracted citation.
4. Display high-level results in the GUI:
    - Number of citations found
    - Number of citations verified as existing and facially correct
        - Citation exists
        - Court is correct
        - Year of decision is correct
        - Page range is correct
        - Name is at least partially correct (at least one word on each side of `"v."` matches, 
          or for cases without `"v."` then at least one word of the name matches, excluding "In",
          "re", "ex", "rel", and other words commonly used in case captions)
    - Number of citations that are verified to be incorrect
        - Different case name
        - Different court
        - Different year
        - Different page range
        - Different reporter/volume/page (if available in citation)
    - Number of citations not verified
        - Could not be parsed by eyecite
        - No match in CourtListener database
5. Generate a more detailed report that can be saved as a PDF or DOCX file.

## GUI Design

- File selection dialog to select a PDF or DOCX file
- "Check" button to run the checks
- Results display area to show the high-level results
- "Save Report" button to save the detailed report

## Links and Documentation

- Liteparse: https://github.com/run-llama/liteparse
- Eyecite: https://github.com/freelawproject/eyecite and https://freelawproject.github.io/eyecite/
- CourtListener API Client: https://github.com/freelawproject/courtlistener-api-client
- CourtListener citation lookup REST API: https://www.courtlistener.com/help/api/rest/citation-lookup/

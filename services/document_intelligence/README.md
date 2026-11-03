# Document intelligence

Parsing, OCR, layout, tables, figures, and page-level provenance.

## Current task

Task 3 adds a deterministic plain-text parser. It converts UTF-8 bytes into
page-level `DocumentPage` contracts and uses form-feed characters as page
boundaries. PDF parsing, OCR, and layout analysis are separate later tasks.

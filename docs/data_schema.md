# Data schema

Every page evidence record keeps:

- document_id
- source_file
- page
- width / height
- page type
- text blocks
- image metadata
- vector metadata
- OCR records
- layout records
- warnings

Text bbox is in the PDF/page coordinate system.
OCR/Layout bbox is in rendered-image coordinates in V1.

A later V1.1 step should normalize those coordinate systems.

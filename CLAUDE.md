# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project for researching data and generating analysis reports.

## Project Structure

```
./
├── reference/                  # Original reference documents directory
│   ├── data.xlsx               # Research data file
│   ├── presentation.pdf        # PDF presentation
│   └── ...                     # Other reference documents (subdirectories supported)
├── transformed/                # Parsed markdown resources directory
│   ├── data.png.md            # Textual description of data file
│   ├── presentation.pdf.md     # Textual description of PDF file
│   └── ...                     # One-to-one correspondence with reference structure
├── generated/                  # Generated derivative content directory
│   ├── chart_*.png             # Generated charts
│   ├── chart_*.png.desc.md     # Chart description document (required for non-text files)
│   └── ...                     # Other generated files
├── temp/                       # Temporary files directory
│   └── ...                     # Temporary scripts and files (subdirectories supported)
└── output/                     # Final output directory
    └── report.md               # Generated final report
```

**Directory Descriptions:**
- **reference/**: Stores original reference files (Excel, Word, PDF, images, etc.), supports subdirectories
- **transformed/**: Stores markdown parsing results of files in reference, filenames remain consistent with `.md` suffix added
- **generated/**: Stores generated charts and visualizations. Non-text files (images, etc.) must be accompanied by `.desc.md` description files that describe content only without analysis
- **temp/**: Stores temporary code scripts and other temporary files, subdirectories can be created inside
- **output/**: Stores the generated final report

## Key Skills

Prioritize using existing skills to complete tasks. Read the `.claude/skills` directory.

## Basic Workflow

1. **Environment Check**: Confirm that the `reference/` directory contains files
2. **Preprocessing**: Convert non-plain-text files (images, etc.) from reference to markdown in `transformed/`. xlsx files do not need conversion. For PDF conversion, evaluate the internal structure; if images dominate, convert to images first and then use image recognition
3. **Analysis & Generation**: Generate reports to `output/` based on transformed content
4. **Chart Generation**: Use skills to generate charts to `generated/` and reference them in reports
5. **Quality Check**: Verify data accuracy
6. **Traceability**: Add text citation markers for all related reference information

## Formatting Requirements

* Add a half-width space between Chinese and English characters
* Add a half-width space between numbers and text
* Tables and report content must not use ellipsis to omit data

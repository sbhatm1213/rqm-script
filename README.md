### ETL script done for QA teams
### IBM RQM (Jazz) Test Case Extractor
### Overview

Python automation to extract **Projects, Test Cases, and Test Scripts** from IBM Rational Quality Manager (Jazz) using a combination of Selenium and API calls.

Built to archive large volumes of QA assets for reporting, analysis, and backup.

---

### What it does

* Logs into Jazz (RQM) via Selenium
* Retrieves all available **Projects**
* Fetches **Test Cases** project-wise using pagination
* Extracts detailed:

  * Test Case information
  * Associated Test Scripts
* Calls Jazz REST APIs via a utility JAR
* Converts XML responses to JSON
* Stores structured output in local folders
* Skips already-downloaded records to avoid duplicates

---

### Tech Stack

Python, Selenium, xmltodict, subprocess, REST APIs

---

### How to run

1. Update:

   * ChromeDriver path
   * RQM utility JAR path
   * Output folder locations
2. Run with credentials and start page:

```bash
python script.py <password> <start_page>
```

---

### Notes

* Designed for internal enterprise Jazz/RQM environment
* Requires network access and valid credentials
* Handles large data volumes using pagination
* Element/API paths may require updates if system changes

---

**Year:** ~2019–2020
Reference project demonstrating large-scale data extraction ETL for QA Teams

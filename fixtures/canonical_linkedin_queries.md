# Canonical LinkedIn Spider Queries — auto-generated from 9-subtier × 5-role matrix
Source: scripts/generate_spider_queries.py (do not hand-edit — re-run the generator)
Total cells: 37
Sorted by priority (First → First co-equal → Second → ...), then subtier code.

---

### Q1A-OO — 1A | Operational Owner
- **Cluster:** OO (Operational Owner)
- **Boolean:** ("Director of Operations" OR "VP Operations" OR "Director of Care Management" OR "Population Health Director" OR "Director of Clinical Programs" OR "Director of Quality" OR "VP Clinical Operations") AND ("medical group" OR "physicians group" OR "physician practice" OR "multi-specialty")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1A
- **Why this slot:** First priority — primary theme Workflow / Ops, secondary ROI / Revenue

### Q1B-OO — 1B | Operational Owner
- **Cluster:** OO (Operational Owner)
- **Boolean:** ("Practice Administrator" OR "Office Manager" OR "Practice Manager" OR "Director of Practice Operations" OR "Operations Manager" OR "Clinic Administrator") AND ("primary care" OR "family practice" OR "family medicine" OR "PCP")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1B
- **Why this slot:** First priority — primary theme Workflow / Ops, secondary ROI / Revenue

### Q1C-OO — 1C | Operational Owner
- **Cluster:** OO (Operational Owner)
- **Boolean:** ("VP Population Health" OR "Director of Population Health" OR "Director of Care Management" OR "Director of Quality" OR "Director of Risk Adjustment" OR "Care Transformation Lead" OR "Director of Value-Based Programs") AND ("value-based care" OR "VBC" OR "shared savings" OR "MSSP")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1C
- **Why this slot:** First priority — primary theme Quality / Compliance, secondary Workflow / Ops

### Q2A-OO — 2A | Operational Owner
- **Cluster:** OO (Operational Owner)
- **Boolean:** ("VP Population Health" OR "Director of Population Health" OR "Director of Care Coordination" OR "Quality Director" OR "Director of Network Performance" OR "Risk Operations Leader" OR "Director of Value-Based Operations") AND ("ACO" OR "Accountable Care Organization" OR "MSSP ACO")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2A
- **Why this slot:** First priority — primary theme Quality / Compliance, secondary ROI / Revenue

### Q2B-PCL — 2B | Partnership / Channel Lead
- **Cluster:** PCL (Partnership / Channel Lead)
- **Boolean:** ("VP Partnerships" OR "VP Business Development" OR "VP Strategic Alliances" OR "Director of Partnerships" OR "GM Provider Solutions" OR "Head of Partnerships" OR "SVP Business Development") AND ("Aledade" OR "Privia Health" OR "Pearl Health" OR "Evolent" OR "agilon health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2B
- **Why this slot:** First priority — primary theme ROI / Revenue, secondary Workflow / Ops

### Q2C-OO — 2C | Operational Owner
- **Cluster:** OO (Operational Owner)
- **Boolean:** ("VP Clinical Operations" OR "Director of Care Management" OR "Director of Care Navigation" OR "Director of Clinical Programs" OR "Director of Behavioral Health" OR "Director of Patient Engagement" OR "VP Care Delivery") AND ("care management" OR "chronic care management" OR "CCM" OR "remote patient monitoring")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2C
- **Why this slot:** First priority — primary theme Workflow / Ops, secondary Clinical Outcomes

### Q3A-OO — 3A | Operational Owner
- **Cluster:** OO (Operational Owner)
- **Boolean:** ("VP Ambulatory" OR "VP Population Health" OR "Director of Ambulatory Operations" OR "Director of Care Management" OR "VP Primary Care Service Line" OR "VP Clinical Transformation" OR "Director of Ambulatory Strategy") AND ("health system" OR "regional health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 3A
- **Why this slot:** First priority — primary theme Workflow / Ops, secondary ROI / Revenue

### Q3B-OO — 3B | Operational Owner
- **Cluster:** OO (Operational Owner)
- **Boolean:** ("VP Population Health" OR "VP Care Transformation" OR "Director of Care Transformation" OR "Enterprise Care Management Director" OR "Director of Ambulatory Strategy" OR "VP Ambulatory Operations") AND ("IDN" OR "integrated delivery network" OR "integrated health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 3B
- **Why this slot:** First priority — primary theme Workflow / Ops, secondary Quality / Compliance

### Q3C-OO — 3C | Operational Owner
- **Cluster:** OO (Operational Owner)
- **Boolean:** ("VP Medical Management" OR "VP Quality" OR "Director of Quality" OR "Director of Behavioral Health Programs" OR "VP Stars" OR "Director of Risk Adjustment" OR "Director of Care Management" OR "VP Clinical Operations") AND ("Medicare Advantage" OR "Blue Cross" OR "health plan" OR "regional payer")
- **Industry filter:** Insurance
- **Location:** United States
- **Expected subtiers:** 3C
- **Why this slot:** First priority — primary theme Quality / Compliance, secondary ROI / Revenue

### Q1B-EB — 1B | Economic Buyer
- **Cluster:** EB (Economic Buyer)
- **Boolean:** ("Physician Owner" OR "Managing Partner" OR "Practice Owner" OR "Founding Physician" OR "Senior Partner" OR "Principal Physician") AND ("primary care" OR "family practice" OR "family medicine" OR "PCP")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1B
- **Why this slot:** First (co-equal) priority — primary theme ROI / Revenue, secondary Clinical Outcomes

### Q1C-CC — 1C | Clinical Champion
- **Cluster:** CC (Clinical Champion)
- **Boolean:** ("CMO" OR "VP Medical Affairs" OR "Medical Director of Population Health" OR "VP Medical Director Value-Based Care" OR "Chief Clinical Officer" OR "Medical Director Quality Programs") AND ("value-based care" OR "VBC" OR "shared savings" OR "MSSP")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1C
- **Why this slot:** First (co-equal) priority — primary theme Clinical Outcomes, secondary Quality / Compliance

### Q2A-CC — 2A | Clinical Champion
- **Cluster:** CC (Clinical Champion)
- **Boolean:** ("CMO" OR "VP Medical Affairs" OR "Medical Director Population Health" OR "Physician Executive VBC" OR "Chief Clinical Officer" OR "Medical Director Quality" OR "VP Clinical Affairs") AND ("ACO" OR "Accountable Care Organization" OR "MSSP ACO")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2A
- **Why this slot:** First (co-equal) priority — primary theme Clinical Outcomes, secondary Quality / Compliance

### Q2B-PCO — 2B | Product / Clinical Owner
- **Cluster:** PCO (Product / Clinical Owner)
- **Boolean:** ("VP Product" OR "VP Clinical Programs" OR "Chief Product Officer" OR "Director of Product Management" OR "VP Product Strategy" OR "Head of Product" OR "SVP Product") AND ("Aledade" OR "Privia Health" OR "Pearl Health" OR "Evolent" OR "agilon health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2B
- **Why this slot:** First (co-equal) priority — primary theme Workflow / Ops, secondary Clinical Outcomes

### Q3A-CC — 3A | Clinical Champion
- **Cluster:** CC (Clinical Champion)
- **Boolean:** ("CMO" OR "Chief Medical Officer" OR "VP Medical Affairs" OR "Behavioral Health Service Line Medical Director" OR "Primary Care Medical Executive" OR "VP Medical Operations" OR "Associate CMO Ambulatory") AND ("health system" OR "regional health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 3A
- **Why this slot:** First (co-equal) priority — primary theme Clinical Outcomes, secondary Quality / Compliance

### Q3B-CC — 3B | Clinical Champion
- **Cluster:** CC (Clinical Champion)
- **Boolean:** ("CMO" OR "CMIO" OR "VP Medical Affairs" OR "Enterprise Physician Executive" OR "VP Ambulatory Strategy" OR "Chief Clinical Officer" OR "Associate CMO Population Health") AND ("IDN" OR "integrated delivery network" OR "integrated health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 3B
- **Why this slot:** First (co-equal) priority — primary theme Clinical Outcomes, secondary Workflow / Ops

### Q3C-CC — 3C | Clinical Champion
- **Cluster:** CC (Clinical Champion)
- **Boolean:** ("CMO" OR "Chief Medical Officer" OR "VP Clinical Affairs" OR "Behavioral Health Medical Director" OR "Population Health Medical Director" OR "VP Medical Director" OR "Chief Behavioral Health Officer") AND ("Medicare Advantage" OR "Blue Cross" OR "health plan" OR "regional payer")
- **Industry filter:** Insurance
- **Location:** United States
- **Expected subtiers:** 3C
- **Why this slot:** First (co-equal) priority — primary theme Clinical Outcomes, secondary Quality / Compliance

### Q1A-CC — 1A | Clinical Champion
- **Cluster:** CC (Clinical Champion)
- **Boolean:** ("CMO" OR "Chief Medical Officer" OR "Medical Director" OR "Primary Care Medical Director" OR "VP Medical Affairs" OR "Associate Medical Director") AND ("medical group" OR "physicians group" OR "physician practice" OR "multi-specialty")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1A
- **Why this slot:** Second priority — primary theme Clinical Outcomes, secondary Quality / Compliance

### Q1B-CC — 1B | Clinical Champion
- **Cluster:** CC (Clinical Champion)
- **Boolean:** ("Medical Director" OR "Lead Physician" OR "Behavioral Health Champion" OR "Clinical Director" OR "Chief of Medicine" OR "Supervising Physician") AND ("primary care" OR "family practice" OR "family medicine" OR "PCP")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1B
- **Why this slot:** Second priority — primary theme Clinical Outcomes, secondary Workflow / Ops

### Q1C-EB — 1C | Economic Buyer
- **Cluster:** EB (Economic Buyer)
- **Boolean:** ("VP Value-Based Care" OR "CFO" OR "COO" OR "President" OR "VP Finance" OR "VP Revenue Cycle" OR "Chief Strategy Officer") AND ("value-based care" OR "VBC" OR "shared savings" OR "MSSP")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1C
- **Why this slot:** Second priority — primary theme ROI / Revenue, secondary Quality / Compliance

### Q2A-EB — 2A | Economic Buyer
- **Cluster:** EB (Economic Buyer)
- **Boolean:** ("CEO" OR "President" OR "CFO" OR "VP Network Performance" OR "SVP Clinical Affairs" OR "Executive Director") AND ("ACO" OR "Accountable Care Organization" OR "MSSP ACO")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2A
- **Why this slot:** Second priority — primary theme ROI / Revenue, secondary Quality / Compliance

### Q2B-CC — 2B | Clinical Champion
- **Cluster:** CC (Clinical Champion)
- **Boolean:** ("CMO" OR "VP Clinical Strategy" OR "Medical Director" OR "VP Clinical Operations" OR "Chief Clinical Officer" OR "SVP Clinical") AND ("Aledade" OR "Privia Health" OR "Pearl Health" OR "Evolent" OR "agilon health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2B
- **Why this slot:** Second priority — primary theme Clinical Outcomes, secondary Workflow / Ops

### Q2C-EB — 2C | Economic Buyer
- **Cluster:** EB (Economic Buyer)
- **Boolean:** ("CEO" OR "GM" OR "President" OR "VP Operations" OR "COO" OR "Executive Director" OR "CFO") AND ("care management" OR "chronic care management" OR "CCM" OR "remote patient monitoring")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2C
- **Why this slot:** Second priority — primary theme ROI / Revenue, secondary Workflow / Ops

### Q3A-TG — 3A | Technical Gatekeeper
- **Cluster:** TG (Technical Gatekeeper)
- **Boolean:** ("CMIO" OR "CIO" OR "VP Clinical Informatics" OR "Director of EHR Applications" OR "VP Interoperability" OR "Digital Health Director" OR "Director of Clinical Systems") AND ("health system" OR "regional health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 3A
- **Why this slot:** Second priority — primary theme Technical / Integration, secondary Workflow / Ops

### Q3B-TG — 3B | Technical Gatekeeper
- **Cluster:** TG (Technical Gatekeeper)
- **Boolean:** ("CMIO" OR "VP Enterprise Applications" OR "VP Interoperability" OR "Digital Health Officer" OR "Director of Clinical Systems" OR "VP Health IT" OR "Director of Enterprise Architecture") AND ("IDN" OR "integrated delivery network" OR "integrated health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 3B
- **Why this slot:** Second priority — primary theme Technical / Integration, secondary Workflow / Ops

### Q3C-EB — 3C | Economic Buyer
- **Cluster:** EB (Economic Buyer)
- **Boolean:** ("CFO" OR "VP Medical Management" OR "VP Stars Performance" OR "COO" OR "VP Finance" OR "Chief Strategy Officer" OR "SVP Health Plan Operations") AND ("Medicare Advantage" OR "Blue Cross" OR "health plan" OR "regional payer")
- **Industry filter:** Insurance
- **Location:** United States
- **Expected subtiers:** 3C
- **Why this slot:** Second priority — primary theme ROI / Revenue, secondary Quality / Compliance

### Q2C-CC — 2C | Clinical Champion
- **Cluster:** CC (Clinical Champion)
- **Boolean:** ("Medical Director" OR "VP Clinical Programs" OR "Chief Clinical Officer" OR "Clinical Director" OR "VP Medical Affairs" OR "Chief Nursing Officer") AND ("care management" OR "chronic care management" OR "CCM" OR "remote patient monitoring")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2C
- **Why this slot:** Second (co-equal) priority — primary theme Clinical Outcomes, secondary Workflow / Ops

### Q1A-EB — 1A | Economic Buyer
- **Cluster:** EB (Economic Buyer)
- **Boolean:** ("COO" OR "CEO" OR "President" OR "CFO" OR "Managing Director" OR "Executive Director" OR "VP Finance") AND ("medical group" OR "physicians group" OR "physician practice" OR "multi-specialty")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1A
- **Why this slot:** Third priority — primary theme ROI / Revenue, secondary Workflow / Ops

### Q1B-TG — 1B | Technical Gatekeeper
- **Cluster:** TG (Technical Gatekeeper)
- **Boolean:** ("EHR Administrator" OR "IT Manager" OR "Operations Lead" OR "EHR Coordinator" OR "Practice Technology Lead") AND ("primary care" OR "family practice" OR "family medicine" OR "PCP")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1B
- **Why this slot:** Third priority — primary theme Technical / Integration, secondary Workflow / Ops

### Q1C-TG — 1C | Technical Gatekeeper
- **Cluster:** TG (Technical Gatekeeper)
- **Boolean:** ("Analytics Director" OR "VP Analytics" OR "IT/EHR Lead" OR "Interoperability Lead" OR "Director of Clinical Informatics" OR "Director of Health Information Exchange") AND ("value-based care" OR "VBC" OR "shared savings" OR "MSSP")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1C
- **Why this slot:** Third priority — primary theme Technical / Integration, secondary Workflow / Ops

### Q2A-TG — 2A | Technical Gatekeeper
- **Cluster:** TG (Technical Gatekeeper)
- **Boolean:** ("Director of Analytics" OR "VP Data & Analytics" OR "Interoperability Lead" OR "Director of Reporting" OR "Health IT Director" OR "Director of Clinical Analytics") AND ("ACO" OR "Accountable Care Organization" OR "MSSP ACO")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2A
- **Why this slot:** Third priority — primary theme Technical / Integration, secondary Quality / Compliance

### Q2B-EB — 2B | Economic Buyer
- **Cluster:** EB (Economic Buyer)
- **Boolean:** ("CEO" OR "GM" OR "COO" OR "VP Revenue" OR "Chief Revenue Officer" OR "President" OR "CFO") AND ("Aledade" OR "Privia Health" OR "Pearl Health" OR "Evolent" OR "agilon health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2B
- **Why this slot:** Third priority — primary theme ROI / Revenue, secondary Workflow / Ops

### Q2C-TG — 2C | Technical Gatekeeper
- **Cluster:** TG (Technical Gatekeeper)
- **Boolean:** ("VP Product" OR "IT Director" OR "Director of Integrations" OR "VP Technology" OR "CTO" OR "Director of Clinical Systems") AND ("care management" OR "chronic care management" OR "CCM" OR "remote patient monitoring")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2C
- **Why this slot:** Third priority — primary theme Technical / Integration, secondary Workflow / Ops

### Q3A-EB — 3A | Economic Buyer
- **Cluster:** EB (Economic Buyer)
- **Boolean:** ("VP Ambulatory" OR "COO" OR "CFO" OR "SVP Clinical Affairs" OR "VP Finance" OR "SVP Operations") AND ("health system" OR "regional health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 3A
- **Why this slot:** Third priority — primary theme ROI / Revenue, secondary Workflow / Ops

### Q3B-EB — 3B | Economic Buyer
- **Cluster:** EB (Economic Buyer)
- **Boolean:** ("SVP Enterprise Operations" OR "VP Care Transformation" OR "VP Population Health" OR "SVP Strategy" OR "CFO" OR "COO") AND ("IDN" OR "integrated delivery network" OR "integrated health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 3B
- **Why this slot:** Third priority — primary theme ROI / Revenue, secondary Workflow / Ops

### Q3C-TG — 3C | Technical Gatekeeper
- **Cluster:** TG (Technical Gatekeeper)
- **Boolean:** ("VP Data & Analytics" OR "Director of Clinical Analytics" OR "VP Interoperability" OR "Product/Program Operations Director" OR "Director of Health Informatics" OR "Director of Data Science") AND ("Medicare Advantage" OR "Blue Cross" OR "health plan" OR "regional payer")
- **Industry filter:** Insurance
- **Location:** United States
- **Expected subtiers:** 3C
- **Why this slot:** Third priority — primary theme Technical / Integration, secondary Quality / Compliance

### Q2B-TG — 2B | Technical Gatekeeper
- **Cluster:** TG (Technical Gatekeeper)
- **Boolean:** ("CTO" OR "VP Engineering" OR "VP Integrations" OR "Director of Platform Engineering" OR "VP Technology" OR "Head of Engineering") AND ("Aledade" OR "Privia Health" OR "Pearl Health" OR "Evolent" OR "agilon health")
- **Industry filter:** Hospital & Health Care
- **Location:** United States
- **Expected subtiers:** 2B
- **Why this slot:** Third (co-equal) priority — primary theme Technical / Integration, secondary Workflow / Ops

### Q1A-TG — 1A | Technical Gatekeeper
- **Cluster:** TG (Technical Gatekeeper)
- **Boolean:** ("IT Director" OR "Director of Health IT" OR "EHR Administrator" OR "Director of Clinical Informatics" OR "CMIO" OR "Health IT Manager") AND ("medical group" OR "physicians group" OR "physician practice" OR "multi-specialty")
- **Industry filter:** Medical Practice
- **Location:** United States
- **Expected subtiers:** 1A
- **Why this slot:** Fourth priority — primary theme Technical / Integration, secondary Workflow / Ops


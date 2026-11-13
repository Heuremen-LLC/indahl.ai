# RANK public-record sources

Read 2026-11-10 with curl (user agent `HeuremenRANK/0.1 (+https://indahl.ai/oy)`), WebFetch and WebSearch. No browser automation, no usnews.com. Results: hs_public.json. Raw downloads: files/. Scripts: code/.

## NCES Common Core of Data
- Urban Institute Education Data API, CCD directory and enrollment-by-grade endpoints: https://educationdata.urban.org/api/v1/schools/ccd/ (years 2023 = 2023-24 and 2024 = 2024-25 both present). Terms: https://educationdata.urban.org/documentation/ (not read). Files: files/nces/.

## TN: Central Magnet School
- https://www.tn.gov/education/districts/federal-programs-and-oversight/data/data-downloads.html
- REFUSED/FAILED: https://tdepreportcard.tnedu.gov/ (DNS did not resolve (curl); not read)
- REFUSED/FAILED: https://www.tn.gov/content/dam/tn/education/data/ (grad, profile files) and Data Downloads page (first curl attempts returned HTTP 403, and the 2024 assessment file timed out once; the same URLs returned 200 on later retries with the same HeuremenRANK user agent (intermittent). No workaround used.)
- REFUSED/FAILED: https://www.tn.gov/education/data/data-downloads.html (404)

## IN: Signature School
- https://www.in.gov/doe/it/data-center-and-reports/
- https://www.in.gov/doe/it/data-center-and-reports/data-reports-archive
- REFUSED/FAILED: https://inview.doe.in.gov/ (DNS did not resolve (curl); not read)

## PA: Julia R. Masterman Secondary School
- https://www.pa.gov/agencies/education/data-and-reporting/assessment-reporting.html
- https://www.pa.gov/agencies/education/data-and-reporting/high-school-graduation.html
- https://www.pa.gov/agencies/education/data-and-reporting/enrollment
- https://futurereadypa.org/
- REFUSED/FAILED: https://www.pa.gov/agencies/education/data-and-reporting/cohort-graduation-rate (404 (wrong guessed path; correct page is /high-school-graduation.html))
- REFUSED/FAILED: https://futurereadypa.org/Search/Location (school search is map/location driven (ajax); not scraped, school page reached via search result link only)

## NV: Davidson Academy
- https://nevadareportcard.nv.gov/DI/
- https://nevadareportcard.nv.gov/DIWAPI-NVReportCard/api/Dashboard
- https://nevadareportcard.nv.gov/DI/nspf/84406/2024/pdf
- REFUSED/FAILED: https://nevadareportcard.nv.gov/DI/MoreDownload (404 without filename parameter)
- REFUSED/FAILED: https://nevadareportcard.nv.gov/DIWAPI-NVReportCard/api/summary?report=summary_1&scope=e25.y21&organization=65758 (returned 200 with empty rows (also empty for state); report API parameters not resolved, so ACT/EOC summary tables by grade 11 were not read. Not a block, a failure to find correct parameters.)

## DC: School Without Walls High School
- https://osse.dc.gov/page/data-and-reports (terms: not seen)
- https://osse.dc.gov/assessmentresults2024 (terms: not seen)
- https://osse.dc.gov/assessmentresults2025 (terms: not seen)
- https://osse.dc.gov/node/1745186 (terms: not seen)
- https://osse.dc.gov/node/1839956 (terms: not seen)
- https://osse.dc.gov/page/dc-school-report-card-resource-library (terms: not seen)
- https://osse.dc.gov/page/2023-24-school-year-enrollment-audit-report-and-data (terms: not seen)
- https://app.box.com (terms: OSSE hosts school-level assessment files on Box shared links linked from its pages; downloaded with the shared-link download URL, no login or bot check bypassed)
- REFUSED/FAILED: https://dcschoolreportcard.org/ (503 on curl (service unavailable), so figures taken from OSSE data files instead)

## VA: Thomas Jefferson High School for Science and Technology
- https://schoolquality.virginia.gov/schools/thomas-jefferson-high-for-science-and-technology (terms: not seen)
- https://schoolquality.virginia.gov/divisions/fairfax-county-public-schools (terms: not seen)
- REFUSED/FAILED: https://www.doe.virginia.gov/data-policy-funding/data-reports/statistics-reports/accreditation-agency-reports (403 Forbidden (curl with HeuremenRANK user agent and WebFetch); SOL pass-rate download files not obtained)
- REFUSED/FAILED: https://www.doe.virginia.gov/data-policy-funding/data-reports/statistics-reports/graduation-completion-reports (403 Forbidden (curl))
- REFUSED/FAILED: https://www.doe.virginia.gov/data-policy-funding/data-reports/data-collection/free-reduced-price-lunch-eligibility (403 Forbidden (curl))
- REFUSED/FAILED: https://www.doe.virginia.gov/home/showpublisheddocument/76370/639090120489604273 (403 Forbidden (curl))
- REFUSED/FAILED: https://schoolquality.virginia.gov/schools/thomas-jefferson-high-school-for-science-and-technology (404 (wrong slug; correct slug used))

## GA: Gwinnett School of Mathematics, Science and Technology
- https://download.gosa.ga.gov/
- https://gosa.georgia.gov/changes-freereduced-priced-lunch-measure-student-poverty

## TX: School for the Talented and Gifted
- https://rptsvr1.tea.texas.gov/perfreport/tapr/tapr_dd_download.html?year=2024
- https://rptsvr1.tea.texas.gov/perfreport/tapr/2024/masking.html
- REFUSED/FAILED: https://rptsvr1.tea.texas.gov/perfreport/tapr/2024/static/campus/c057905039.pdf (404 (guessed path; not an official link))
- REFUSED/FAILED: https://rptsvr1.tea.texas.gov/perfreport/tapr/2024/download/DownloadData.html (404 (guessed path))

## WA: Nikola Tesla STEM High School
- https://data.wa.gov/ (terms: http://creativecommons.org/licenses/by-nd/4.0/legalcode (CC BY-ND 4.0 shown on the 5i5h-c5pk dataset; attribution OSPI Student Information))

## CA: Science Academy STEM Magnet
- https://caaspp-elpac.ets.org/caaspp/ResearchFileListSB?ps=2024&lstTestYear=2024&lstTestType=B&lstCounty=00&lstDistrict=00000
- https://www.cde.ca.gov/ds/ad/filesacgr.asp
- https://www.cde.ca.gov/ds/ad/documents/frpm2324.xlsx
- REFUSED/FAILED: https://www.cde.ca.gov/ds/ad/filessp.asp (and filesfrpm.asp, filesenrcum.asp) (Pages returned a '302 Found' HTML body to curl; file URLs guessed from the documents/ path pattern worked (frpm2324.xlsx, frpm2425.xlsx).)

## National Blue Ribbon Schools
- REFUSED 403 (curl and WebFetch): nationalblueribbonschools.ed.gov (home, /awardwinners/, 2014 application PDF); ed.gov/teaching-and-administration/nclbbrs; ed.gov award pages; ed.gov/sites/ed/files/programs/nclbbrs/2018/national.pdf; tn.gov 2020 TDOE release (403 to curl).
- READ: US ED 2018 national list as archived by NARA web harvest: https://www.webharvest.gov/congress115th/20181222103750/https://www2.ed.gov/programs/nclbbrs/2018/national.pdf (files/blueribbon/nbrs2018_webharvest/national.pdf)
- READ: TEA release, 31 Texas schools named 2022 National Blue Ribbon Schools: https://tea.texas.gov/about-tea/news-and-multimedia/news-releases/news-2022/31-texas-schools-named-2022-national-blue-ribbon-schools
- READ: GaDOE release 28 Sep 2016 in Digital Library of Georgia: https://dlg.usg.edu/record/dlg_ggpd_i-ga-be300-b-pp1-bp7-b2016-s9-h28-belec-p-btext

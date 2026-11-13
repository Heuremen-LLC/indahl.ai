# MBA public record pull, 10 Nov 2026

Client: curl with User-Agent "HeuremenRANK/0.1 (+https://indahl.ai/oy)". Only school-owned pages and documents.
Text copies (*.txt) sit beside each saved file. PDFs converted with PyMuPDF, xlsx read from their XML, HTML stripped of tags.
mba_public.json: one object per figure. quote_verified_in_saved_text is true when the quote appears in the saved text copy.
manual_reads.json: pages that refused automated reads or whose data is not in the page text.
Pages marked "rendered_" were loaded in headless Chrome so page scripts could run; no challenge was bypassed.

## Files and URLs
Stanford GSB
- gsb_classprofile.html, rendered_gsb_classprofile.html: https://www.gsb.stanford.edu/programs/mba/admission/class-profile
- rendered_gsb_infogram.html: infogram embedded on that page, https://e.infogram.com/_/L8xtLdw2l5iK16bZYoFE (title reads DRAFT, some captions name older classes)
- gsb_2025_employment.pdf: https://www.gsb.stanford.edu/sites/default/files/2025-12/report-2025-mba-employment-report.pdf
- gsb_2024_employment.pdf: https://www.gsb.stanford.edu/sites/default/files/2024-12/2024%20MBA%20Employment%20Report.pdf
- gsb_employment_reports.html, gsb_employment_fulltime.html: index pages for the employment reports
Wharton
- wharton_classprofile.html, rendered_wharton_classprofile.html: https://mba.wharton.upenn.edu/class-profile/ (Class of 2028 now)
- wharton_2025_career_report.pdf: https://statistics.mbacareers.wharton.upenn.edu/wp-content/uploads/2025/12/2025-Career-Report.pdf
- wharton_2024_career_report.pdf: https://statistics.mbacareers.wharton.upenn.edu/wp-content/uploads/2024/12/2024-Career-Report-FINAL.pdf
- wharton_fulltime.html: https://statistics.mbacareers.wharton.upenn.edu/full-time/
Chicago Booth
- booth_classprofile.html: https://www.chicagobooth.edu/mba/full-time/admissions/class-profile
- booth_employment_report.html: https://www.chicagobooth.edu/mba/full-time/career-impact/employment-report
- booth_employment_2025_story.html: https://www.chicagobooth.edu/why-booth/stories/mba-employment-report-2025
- booth_2024_data.html: https://chicagobooth.edu/why-booth/stories/admissions/full-time-mba/2025/may/class-of-2024-full-time-employment-report-data
- booth_employmentreport.html: https://www.chicagobooth.edu/employmentreport
Harvard Business School
- hbs_classprofile.html: https://www.hbs.edu/mba/admissions/class-profile
- hbs_blog_2025_employment.html: https://www.hbs.edu/mba/blog/class-of-2025-employment-report
- employment-data pages: challenge response, nothing saved (see manual_reads.json)
Kellogg
- kellogg_classprofile.html, rendered_kellogg_classprofile.html: https://www.kellogg.northwestern.edu/programs/full-time-mba/class-profile/
- kellogg_blog_class2027.html: https://www.kellogg.northwestern.edu/news/blog/2025/11/05/welcoming-class-2027-high-achievers/
- kellogg_career_outcomes.html, kellogg_recruiter_outcomes.html, kellogg_blog_2025_outcomes.html: career outcomes pages
- kellogg_2025_employment.zip and kellogg_2025/: workbooks from https://www.kellogg.northwestern.edu/-/media/files/careers/2025/2025-employment-report.zip (2Y workbook used)
- kellogg_2024_employment.zip and kellogg_2024/: workbooks from .../kellogg-employment-report/employment_outcomes_2024.zip (2YMBA workbook used)
  Kellogg figures are for the Two-Year MBA; 1Y, MMM and MBAi workbooks are saved but not extracted.
MIT Sloan
- sloan_classprofile.html, sloan_meet_class.html, sloan_employment_reports.html
- sloan_2025_employment.pdf: https://mitsloan.mit.edu/sites/default/files/2025-12/2025-2026-MBA-Employment-Report.pdf (a later file dated 2026-03 exists at .../2026-03/2025-2026-MBA-Employment-Report.pdf and was not read)
- sloan_2024_employment.pdf: https://mitsloan.mit.edu/sites/default/files/2024-12/MBA-Employment-Report-2024-2025.pdf
Columbia: only cbs_2024_employment_pdf.pdf (https://business.columbia.edu/sites/default/files-efs/imce-uploads/CMC/cmc-employment-report-2025-3-ada2.pdf, titled 2024 Employment Report). cbs_employment_report.html and cbs_2025_press.html are 403 pages.
NYU Stern
- stern_employment_reports.html/.md, stern_yoy.html/.md: https://www.stern.nyu.edu/business-partnerships/employment-reports and /year-over-year-data
- stern_2025_2yr_employment.pdf, stern_2024_employment.pdf: public Google Drive files linked from those pages (drive.google.com, no login)
- stern_classprofile.html, rendered_stern_classprofile.html: class profile page (Class of 2028 now)
- stern_news_class2027.html, stern_news_2025.html: school news items
Tuck
- tuck_employment.html: https://tuck.dartmouth.edu/mba/career-services/employment-statistics
- tuck_news_class2027.html: https://tuck.dartmouth.edu/news/articles/an-ambitious-and-inspired-first-year-class-is-off-to-the-races-at-tuck
- tuck_classprofile.html, rendered_tuck_classprofile.html: class profile (Class of 2028 now); tuck_news_2025.html, tuck_class_news.html: other school news items
Berkeley Haas
- haas_classprofile.html, rendered_haas_classprofile.html: https://mba.haas.berkeley.edu/admissions/class-profile (figures are in image alt text)
- haas_2025_tables.pdf: .../Haas%20FTMBA%202025%20Employment%20Report%20Tables%20FINAL-s.pdf on mba.haas.berkeley.edu
- haas_2024_detailed.pdf: https://haas.berkeley.edu/wp-content/uploads/Full-time-MBA-Detailed-Employment-Report-2024.pdf
- haas_employment.html, haas_recruiters_report.html: summary pages

## Gaps
Class of 2027 profiles for Wharton, MIT Sloan and NYU Stern are not in pages read (live pages now show Class of 2028). Columbia read by no document except the 2024 PDF (403). HBS employment data behind a challenge. Tuck and Booth Class of 2024 employment figures only partly collected. Prior-class (fall 2024) profile rows collected for Booth and MIT Sloan only.

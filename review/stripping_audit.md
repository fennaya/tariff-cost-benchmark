# Stripping audit (Round 2, Part 1, Check 5)

For each of 20 random wrong answers: the cleaned description actually sent to the model, the original ruling's full description section (everything before the classification discussion, undstripped), the true code, and the predicted code. **Judgment** (filled in by hand, not automated): could a competent human reach at least the true 6-digit code from the CLEANED description alone (material, function, composition, dimensions, use all present)?

## Verdict: 2/20 (10%) lack the needed facts -- below the 5/20 (25%) threshold for "the stripper is too aggressive"

No stripper rerun is triggered by this gate. That said, both failing cases have a clear,
specific, identified root cause (not vague over-stripping) worth fixing opportunistically
in a later pass:

1. **#1 (N360873, testosterone gel):** a missing-space PDF artifact in the source text
   ("...ruling.Testosterone Gel is...") fused the real opening sentence onto the
   preceding boilerplate clause, so the boilerplate filter discarded both together. Same
   artifact class as Round 1's "FACTS:"/anchor bugs -- affects the START anchor this
   time rather than the END cut.
2. **#17 (N358854, DIY crochet shoe kit):** the source states each kit component's
   material inline with its own parenthetical HTS chapter citation (e.g. "a PVC outer
   sole (Chapter 64, HTSUS)"). The cutter correctly avoids leaking "Chapter 64" but, with
   no way to strip only the parenthetical, discards the whole sentence -- including the
   material fact sitting right outside the parentheses.

The other 18/20 wrong answers had fully sufficient descriptions -- most strikingly,
several (#5, #7, #19) show the model matching the true code through all 8 digits and
missing only the final 2-digit statistical suffix, and several others (#8, #9, #12,
#15, #18) show the model contradicting an explicitly stated fact (material, composition,
intended use) outright. This is direct evidence that most of Headline A's errors are
genuine model failures, not artifacts of an overly aggressive stripper.


## 1. N360873 (model: allam-2-7b)

**True code:** 3004390055  |  **Predicted:** 29229090


**Cleaned description (sent to model):**

> Each pumpactuation delivers 20.25 mg of testosterone in 1.25 g of gel.


<details><summary>Original raw ruling text</summary>

```
N360873 May 15, 2026CLA-2-30:OT:RR:NC:N3:138
 CATEGORY: Classification
 TARIFF NO.: 3004.39.0055
 Ciara HorganNorthstar Healthcare UC3300 Cork Airport Business ParkCork T12XN72IrelandRE:  The tariff classification of Testosterone Gel in dosage form, from ChinaDear Ms. Horgan:In your letter dated 
 April 21, 2026
 , you requested a tariff classification ruling.Testosterone Gel is a steroid hormone for topical use only and available as a metered-dose pump. Each pumpactuation delivers 20.25 mg of testosterone in 1.25 g of gel. It is indicated for replacement therapy in malesfor conditions associated with a deficiency or absence of endogenous testosterone such as primaryhypogonadism (congenital or acquired) and hypogonadotropic hypogonadism (congenital or acquired).The applicable subheading for the Testosterone Gel in dosage form will be 3004.39.0055, Harmonized TariffSchedule of the United States (HTSUS), which provides for “Medicaments … consisting of mixed orunmixed products for therapeutic or prophylactic uses, put up in measured doses … or in forms or packingsfor retail sale: Other, containing hormones or other products of heading 2937: Other: Other: Other.”  Thegeneral rate of duty will be free.The duties cited above are current as of this ruling’s issuance. Duty rates are provided for your convenience and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are providedat https://hts.usitc.gov/.This merchandise may be subject to the Federal Food, Drug, and Cosmetic Act and/or The Public HealthSecurity and Bioterrorism Preparedness and Response Act of 2002 (The Bioterrorism Act), which areadministered by the U.S. Food and Drug Administration (FDA). Information on the Federal Food, Drug, andCosmetic Act, as well as The Bioterrorism Act, can be obtained by calling the FDA at 1-888-463-6332, or byvisiting their website at www.fda.gov.
 This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or othercharges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and otherduties as provided for in Subchapter III to Chapter 99, HTSUS.Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with eitherthe Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisionscovering exceptions to such tariffs.For further information to assist with the importation process, please refer to the frequently updated CargoSystems Messaging Service (CSMS) messages at https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at https://www.cbp.gov/trade/programs-administration/trade-remedies.The holding set forth above applies only to the specific factual situation and merchandise description asidentified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations(CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of theinformation furnished in the ruling letter, whether directly, by reference, or by implication, is accurate andcomplete in every material respect.  In the event that the facts are modified in any way, or if the goods do notconform to these facts at time of importation, you should bring this to the attention of U.S. Customs andBorder Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2. Additionally, we note that the material facts described in the foregoing ruling may be subject to periodicverification by CBP.This ruling is being issued under the provisions of Part 177 of the Customs and Border ProtectionRegulations (19 C.F.R. 177).A copy of the ruling or the control number indicated above should be provided with the entry documentsfiled at the time this merchandise is imported. If you have any questions regarding the ruling, please contactNational Import Specialist Judy Lee at judy.h.lee@cbp.dhs.gov.
 Sincerely,
 (for)James P. ForkanDirectorNational Commodity Specialist Division
 
```
</details>


**Judgment:** NO -- insufficient. Cleaned text is just one isolated sentence ("Each pump actuation delivers 20.25 mg of testosterone in 1.25 g of gel.") with no product name, dosage FORM, or therapeutic/topical-use context. Root cause: a missing-space PDF artifact in the source ("...classification ruling.Testosterone Gel is a steroid hormone..." -- no space after the first period) fused the real opening sentence onto the preceding boilerplate clause, so the boilerplate-detector correctly-but-unluckily skipped the whole fused unit, including the real content inside it. Same artifact class documented in Round 1 DECISIONS.md, here hitting the START anchor instead of the END cut.


## 2. N360329 (model: openai/gpt-oss-20b)

**True code:** 9503000073  |  **Predicted:** 9503000020


**Cleaned description (sent to model):**

> A sample of the “Disney Princess Style Collection Glam Jewelry Tower” was submitted with your inquiry. The “Disney Princess Style Collection Glam Jewelry Tower,” item number 291294, consists of a pink and white 4 tiered hinged plastic container measuring approximately 7.5” x 3.5” x 3.5” with a mirror affixed to the top serving as the lid. The lid is decorated with the image of 3 Disney princesses. The tower comes with various toy items: 3 plastic rings, 2 plastic hair clips, and a fake plastic watch. These components are all packaged together and contribute to the imitative role-play activity of dressing-up like a Disney Princess. The “Disney Princess Style Collection Glam Jewelry Tower” is principally designed for the amusement of children ages 3 years and older.


<details><summary>Original raw ruling text</summary>

```
N360329  

April 29, 2026

  CLA-2-95:OT:RR:NC:N4:424  

CATEGORY: Classification  

TARIFF NO.: 9503.00.0073

  Cathy Yu  Jakks Pacific Inc.  21749 Baker Pkwy  Walnut, CA 91789  RE:  The tariff classification of the “Disney Princess Style Collection Glam Jewelry Tower,” children’s toy   from China  Dear Ms. Yu:  In your letter dated April 2, 2026, you requested a tariff classification ruling.  A sample of the “Disney Princess Style Collection Glam Jewelry Tower” was submitted with your inquiry.  The “Disney Princess Style Collection Glam Jewelry Tower,” item number 291294, consists of a pink and  white 4 tiered hinged plastic container measuring approximately 7.5” x 3.5” x 3.5” with a mirror affixed to  the top serving as the lid.  The lid is decorated with the image of 3 Disney princesses.  The tower comes with  various toy items: 3 plastic rings, 2 plastic hair clips, and a fake plastic watch.  These components are all  packaged together and contribute to the imitative role-play activity of dressing-up like a Disney Princess.    The “Disney Princess Style Collection Glam Jewelry Tower” is principally designed for the amusement of  children ages 3 years and older.   You suggest classification of the subject merchandise as a toy under 9503.00.0073, Harmonized Tariff  Schedule of the United States (HTSUS).  We agree.  The applicable subheading for the “Disney Princess Style Collection Glam Jewelry Tower,” item number  291294, will be 9503.00.0073, HTSUS, which provides for “Tricycles, scooters, pedal cars, and similar  wheeled toys…dolls, other toys…puzzles of all kinds; parts and accessories thereof… ‘Children’s products’  as defined in 15 U.S.C. § 2052: Other: Labeled or determined by importer as intended for use by persons: 3  to 12 years of age.”  The rate of duty will be Free.  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/. 



This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at   https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Irene Tsiavos at Irene.Tsiavos@cbp.dhs.gov.  

Sincerely,

  (for)  James P. Forkan  Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- sufficient for 6-digit (950300) and even 8-digit (95030000, which the model got exactly right). Rich description: materials, dimensions, contents, intended age. The miss is only the final 2-digit statistical age-bracket suffix (73 vs 20), an administrative bucket not fully inferable without the schedule's exact age-range table -- not an input gap.


## 3. N360218 (model: allam-2-7b)

**True code:** 3004909263  |  **Predicted:** 29221900


**Cleaned description (sent to model):**

> Bumetanide, imported in 0.5 mg, 1 mg, and 2 mg tablets, belongs to a class of medications called loop diuretics. It is indicated for the treatment of edema associated with congestive heart failure, hepatic and renal diseases, including nephrotic syndrome. In your letter you stated the country of origin is Spain and exported out of India.


<details><summary>Original raw ruling text</summary>

```
N360218  

April 28, 2026

  CLA-2-30:OT:RR:NC:N3:138  

CATEGORY: Classification  

TARIFF NO.: 3004.90.9263

  Trish O’ Mahoney  Northstar Healthcare Limited  3300 Cork Airport Business Park  Kinsale Road, Cork T12 XN72  Ireland  RE:  The tariff classification of Bumetanide Tablets in dosage form, from Spain  Dear Ms. O’ Mahoney:  In your letter dated March 31, 2026, you requested a tariff classification ruling.  Bumetanide, imported in 0.5 mg, 1 mg, and 2 mg tablets, belongs to a class of medications called loop  diuretics. It is indicated for the treatment of edema associated with congestive heart failure, hepatic and renal  diseases, including nephrotic syndrome. In your letter you stated the country of origin is Spain and exported  out of India.  The applicable subheading for the Bumetanide Tablets in dosage form will be 3004.90.9263, Harmonized  Tariff Schedule of the United States (HTSUS), which provides for “Medicaments … consisting of mixed or  unmixed products for therapeutic or prophylactic uses, put up in measured doses … or in forms or packings  for retail use: Other: Other: Other: Preparations primarily affecting the electrolytic, caloric or water balance:  Diuretics: Other.” The general rate of duty will be free.  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This merchandise may be subject to the Federal Food, Drug, and Cosmetic Act and/or The Public Health  Security and Bioterrorism Preparedness and Response Act of 2002 (The Bioterrorism Act), which are  administered by the U.S. Food and Drug Administration (FDA). Information on the Federal Food, Drug, and  Cosmetic Act, as well as The Bioterrorism Act, can be obtained by calling the FDA at 1-888-463-6332, or by  visiting their website at www.fda.gov. 



This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at   https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Judy Lee at judy.h.lee@cbp.dhs.gov.  

Sincerely,

  (for)  James P. Forkan  Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- sufficient. Explicitly states dosage form ("tablets") and "medications", which is exactly the fact that should route this to Chapter 30 (dosage-form medicaments) rather than Chapter 29 (bulk organic chemicals). The model's miss (chapter 29) ignores an explicit, stated fact -- a model error, not an input gap.


## 4. N356635 (model: openai/gpt-oss-20b)

**True code:** 6802990090  |  **Predicted:** 6801909000


**Cleaned description (sent to model):**

> The merchandise under consideration is referred to as Piracema White stone. A sample was submitted with your ruling request and was forwarded to the Customs and Border Protection Laboratory for analysis. This analysis has been completed. Piracema White is a light gray stone mottled with dark gray and black streaks and banding. From the information you provided, it will measure between 115 to 122 inches in length, between 65 to 75 inches in width, and either 0.75 inches or 1.5 inches in thickness. After importation, it will be cut to size and shape for such applications as kitchen countertops, bathroom surfaces, and surfaces for office furniture. Laboratory analysis has determined that Piracema White is made of gneiss. The top of the stone has been polished and the sides are simply cut or sawn.


<details><summary>Original raw ruling text</summary>

```
N356635  

June 25, 2026

  CLA-2-68:OT:RR:NC:N1:128  

CATEGORY: Classification  

TARIFF NO.: 6802.99.0090

  Ms. Natalia Teixeira  OHM International Inc.  195 Prospect Plains Road  Monroe Township, NJ 08831  RE:  The tariff classification of Piracema White stone from Brazil.  Dear Ms. Teixeira:  In your letter dated December 2, 2025, you requested a tariff classification ruling.  The merchandise under consideration is referred to as Piracema White stone.  A sample was submitted with  your ruling request and was forwarded to the Customs and Border Protection Laboratory for analysis.  This  analysis has been completed.  Piracema White is a light gray stone mottled with dark gray and black streaks and banding.  From the  information you provided, it will measure between 115 to 122 inches in length, between 65 to 75 inches in  width, and either 0.75 inches or 1.5 inches in thickness.  After importation, it will be cut to size and shape for  such applications as kitchen countertops, bathroom surfaces, and surfaces for office furniture.   Laboratory analysis has determined that Piracema White is made of gneiss.  The top of the stone has been  polished and the sides are simply cut or sawn.    The applicable subheading for the Piracema White stone will be 6802.99.0090, HTSUS, which provides for  “Worked monumental or building stone (except slate) and articles thereof, other than goods of heading  6801…:  Other:  Other stone:  Other:  Other.”  The general rate of duty will be 6.5 percent ad valorem.   The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the 



classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at   https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.  Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported.  If you have any questions regarding the ruling, please contact  National Import Specialist Nicole Sullivan at nicole.d.sullivan@cbp.dhs.gov.  

Sincerely,

  (for)  James P. Forkan  Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- sufficient. Material (gneiss), finish (polished top, cut sides), dimensions, and application (countertops) are all explicit. Distinguishing heading 6802 (worked/polished building stone) from 6801 (setts/curbstones, typically unpolished paving stone) is a genuine, explainable model confusion between adjacent headings, not a missing fact.


## 5. N359428 (model: openai/gpt-oss-120b)

**True code:** 3004909206  |  **Predicted:** 30049090


**Cleaned description (sent to model):**

> Valacyclovir Hydrochloride, imported in 1000 mg tablets, is an anti-viral medication. It is indicated for the treatment of herpes zoster (shingles), genital herpes, and cold sores.


<details><summary>Original raw ruling text</summary>

```
N359428  

April 1, 2026

  CLA-2-30:OT:RR:NC:N3:138  

CATEGORY: Classification  

TARIFF NO.: 3004.90.9206

  Ciara Horgan  Northstar Healthcare UC  3300 Cork Airport Business Park  Cork T12XN72  Ireland  RE:  The tariff classification of Valacyclovir Hydrochloride Tablets in dosage form, from India  Dear Ms. Horgan:  In your letter dated March 4, 2026, you requested a tariff classification ruling.  Valacyclovir Hydrochloride, imported in 1000 mg tablets, is an anti-viral medication.  It is indicated for the  treatment of herpes zoster (shingles), genital herpes, and cold sores.  The applicable subheading for the Valacyclovir Hydrochloride Tablets in dosage form will be 3004.90.9206,  Harmonized Tariff Schedule of the United States (HTSUS), which provides for “Medicaments … consisting  of mixed or unmixed products for therapeutic or prophylactic uses, put up in measured doses … or in forms  or packings for retail sale: Other: Other: Other: Anti-infective medicaments: Antivirals: Other.” The general  rate of duty will be free.  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This merchandise may be subject to the Federal Food, Drug, and Cosmetic Act and/or The Public Health  Security and Bioterrorism Preparedness and Response Act of 2002 (The Bioterrorism Act), which are  administered by the U.S. Food and Drug Administration (FDA). Information on the Federal Food, Drug, and  Cosmetic Act, as well as The Bioterrorism Act, can be obtained by calling the FDA at 1-888-463-6332, or by  visiting their website at www.fda.gov.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the 



classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at   https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Judy Lee at judy.h.lee@cbp.dhs.gov.  

Sincerely,

  (for)  James Forkan  Designated Official Performing the Duties of the Division Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- more than sufficient; the model's prediction (30049090) is exactly the correct 8-digit prefix of the true code, just missing the final 2-digit statistical suffix entirely. Drug name, dosage form, and indication are all given. Not an input problem -- if anything, proof the input was enough to reach the duty-relevant level.


## 6. N360185 (model: openai/gpt-oss-120b)

**True code:** 9603908050  |  **Predicted:** 9603900000


**Cleaned description (sent to model):**

> Images were provided in lieu of a sample. The product under consideration is described as the “Sparta Spectrum 30-inch Broiler/Grill Cleaning Brush with Scraper,” item number 4029000. It is intended to scrub away food buildup and carbon deposits on grilling and broiling surfaces. This brush includes stiff stainless steel bristles on one side of the rectangular wooden head and semi-stiff stainless steel bristles on the other. Also featured on the head is a metal scraper. The handle for this brush is 30 inches in length.


<details><summary>Original raw ruling text</summary>

```
N360185  

April 21, 2026

  CLA-2-96:OT:RR:NC:N4:415  

CATEGORY: Classification  

TARIFF NO.: 9603.90.8050

  Scott Hoffman  Trans American Customhouse Brokers, LLC  300 Airborne Parkway, Suite 212  Buffalo, NY 14225  RE:      The tariff classification of a cleaning brush from China.  Dear Mr. Hoffman:  In your letter dated March 30, 2026, you requested a tariff classification ruling on behalf of your client,  Foodware, LLC.  Images were provided in lieu of a sample.  The product under consideration is described as the “Sparta Spectrum 30-inch Broiler/Grill Cleaning Brush  with Scraper,” item number 4029000.  It is intended to scrub away food buildup and carbon deposits on  grilling and broiling surfaces.  This brush includes stiff stainless steel bristles on one side of the rectangular  wooden head and semi-stiff stainless steel bristles on the other.  Also featured on the head is a metal scraper.   The handle for this brush is 30 inches in length.  The applicable subheading for the  “Sparta Spectrum 30-inch Broiler/Grill Cleaning Brush with Scraper,”  item number 4029000, will be 9603.90.8050, Harmonized Tariff Schedule of the United States (HTSUS),  which provides for “[b]rooms, brushes (including brushes constituting parts of machines, appliances or  vehicles), hand-operated mechanical floor sweepers, not motorized, mops and feather dusters; prepared knots  and tufts for broom or brush making; paint pads and rollers; squeegees (other than roller squeegees): [o]ther:  [o]ther: [o]ther.”  The column one, general rate of duty is 2.8% ad valorem.  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change.  The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the 



classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at  https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at  https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the CBP Regulations (19 CFR 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported.  If you have any questions regarding the ruling, please contact  National Import Specialist Kristopher Burton at kristopher.burton@cbp.dhs.gov.  

Sincerely,

  (for)  James P. Forkan  Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- sufficient for 6-digit (960390, achieved). Detailed physical description (materials, bristle types, scraper, handle length). The remaining precision (8/10-digit) requires specific HTS brush-subcategory knowledge not inferable from physical facts alone.


## 7. N361030 (model: openai/gpt-oss-20b)

**True code:** 8517620090  |  **Predicted:** 8517620000


**Cleaned description (sent to model):**

> The items concerned are referred to as the Vivi 200 Series boxes, Models VWP-205-16 and VWP-210-16. These devices are receiver units which connect computers and other mobile devices allowing for information to be shared within a system. They are dedicated for use in a larger system of devices including laptops, tablets, personal computers, and flat panel televisions and projectors. The Vivi 200 Series boxes are being imported separately and do not include the additional devices which make up a complete system. The complete system is intended for use in educational settings allowing multiple users to link and share information from multiple devices. Students and teachers can access the system using the Vivi receiver from their own devices while the teacher keeps control of the system. The Vivi 200 Series boxes contain a processor, 2 GB of memory and 16 GB of data storage. Connectivity is provided by an HDMI port, a LAN (RJ-45) port and four USB ports. The units possess an audio line out. The receivers, which have two external antennas and contain a power unit, can also connect to the system wirelessly via a temporary access point. The dimensions of the receivers are 124 x 76m x 26mm (excluding the antenna) and are housed in an anodized metal enclosure.


<details><summary>Original raw ruling text</summary>

```
N361030  

May 7, 2026

  CLA-2-85:OT:RR:NC:N2:209  

CATEGORY: Classification  

TARIFF NO.: 8517.62.0090

  Sam McClure  CV International Inc  3735 Glen Lakes Dr., Ste 100C   Charlotte, NC 28208  RE:  The tariff classification of presentation receivers from Australia  Dear Mr. McClure:  In your letter dated April 27, 2026, you requested a tariff classification ruling on behalf of your client, Vivi  LLC.  The items concerned are referred to as the Vivi 200 Series boxes, Models VWP-205-16 and VWP-210-16.  These devices are receiver units which connect computers and other mobile devices allowing for information  to be shared within a system. They are dedicated for use in a larger system of devices including laptops,  tablets, personal computers, and flat panel televisions and projectors.  The Vivi 200 Series boxes are being imported separately and do not include the additional devices which  make up a complete system. The complete system is intended for use in educational settings allowing  multiple users to link and share information from multiple devices. Students and teachers can access the  system using the Vivi receiver from their own devices while the teacher keeps control of the system.  The Vivi 200 Series boxes contain a processor, 2 GB of memory and 16 GB of data storage. Connectivity is  provided by an HDMI port, a LAN (RJ-45) port and four USB ports. The units possess an audio line out. The  receivers, which have two external antennas and contain a power unit, can also connect to the system  wirelessly via a temporary access point. The dimensions of the receivers are 124 x 76m x 26mm (excluding  the antenna) and are housed in an anodized metal enclosure.  The applicable subheading for the Vivi 200 Series boxes, Models VWP-205-16 and VWP-210-16 will be  8517.62.0090, Harmonized Tariff Schedule of the United States (HTSUS), which provides for “Telephone  sets, including smartphones and other telephones for cellular networks or for other wireless networks; other  apparatus for the transmission or reception of voice, images or other data, including apparatus for  communication in a wired or wireless network (such as a local or wide area network)…: Other apparatus for  transmission or reception of voice, images or other data, including apparatus for communication in a wired or 



wireless network (such as a local or wide area network): Machines for the reception, conversion and  transmission or regeneration of voice, images or other data, including switching and routing apparatus:  Other.” The general rate of duty will be Free.  The duties cited above are current as of this ruling’s issuance. Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein. This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS. Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at   https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request. This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1). This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect. In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.  Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Steven Pollichino at steven.pollichino@cbp.dhs.gov.  

Sincerely,

  (for)  James P. Forkan  Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- more than sufficient; model matched the true code through all 8 digits (85176200), missing only the final statistical suffix (90 vs 00). Thorough technical description given.


## 8. N359074 (model: openai/gpt-oss-120b)

**True code:** 8518908100  |  **Predicted:** 85269190


**Cleaned description (sent to model):**

> The items under consideration are referred to as Cup, Left (Part number: 303-00014-000.B2) and Cup, Right (Part number: 303-00017-000.B2). Both components are ear cup assemblies for Lightspeed’s Sierra aviation headset. The left and right ear cups are composed of a dome shaped plastic housing, which is a blend of polycarbonate and acrylonitrile butadiene styrene resin. This design allows for passive noise reduction by creating a physical barrier to isolate and block external noise, facilitate a snug fit between the cup and the ear, and enable the active noise cancellation function of the headset.


<details><summary>Original raw ruling text</summary>

```
N359074  

March 6, 2026

  CLA-2-85:OT:RR:NC:N2:209  

CATEGORY: Classification  

TARIFF NO.: 8518.90.8100

  Madison Ratto  Lightspeed Aviation  6135 Jean Road  Lake Oswego, OR 97035  RE:  The tariff classification of parts for aviation headsets from the Philippines  Dear Ms. Ratto:  In your letter dated February 23, 2026, you requested a tariff classification ruling.  The items under consideration are referred to as Cup, Left (Part number: 303-00014-000.B2) and Cup, Right  (Part number: 303-00017-000.B2). Both components are ear cup assemblies for Lightspeed’s Sierra aviation  headset. The left and right ear cups are composed of a dome shaped plastic housing, which is a blend of  polycarbonate and acrylonitrile butadiene styrene resin. This design allows for passive noise reduction by  creating a physical barrier to isolate and block external noise, facilitate a snug fit between the cup and the ear,  and enable the active noise cancellation function of the headset.  The applicable subheading for the Cup, Left (Part number: 303-00014-000.B2) and Cup, Right (Part number:  303-00017-000.B2) will be 8518.90.8100, Harmonized Tariff Schedule of the United States (HTSUS), which  provides for “Microphones and stands therefor; loudspeakers, whether or not mounted in their enclosures;  headphones and earphones, whether or not combined with a microphone, and sets consisting of a microphone  and one or more loudspeakers; audio-frequency electric amplifiers; electric sound amplifier sets; parts  thereof: Parts: Other: Other.” The general rate of duty will be free.  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the 



classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at   https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Steven Pollichino at steven.pollichino@cbp.dhs.gov.  

Sincerely,

  (for)  James Forkan  Designated Official Performing the Duties of the Division Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- sufficient and then some. Explicitly "ear cup assemblies for Lightspeed's Sierra aviation headset", with acoustic/fit function described. Predicting radar/navigation apparatus (8526) is a severe, inexplicable model error unrelated to any information gap.


## 9. N359188 (model: allam-2-7b)

**True code:** 4421999880  |  **Predicted:** 7605200000


**Cleaned description (sent to model):**

> The request was returned to you for additional information, which was received by this office on February 25, 2026. Product information and diagrams were submitted for our review. The products under consideration are wood hood canopy tops and wood hood canopy bases, which together form range hood covers. The covers are non-functional. They are custom made and may vary in size and materials. You state that they are constructed of “standard wood species (except exotic woods)”, medium density fiberboard (MDF), particle board, and melamine. The range hood covers merely obscure a range hood or fan. The canopy tops and bases range from simple to more complex and are generally secured to the ceiling during installation.


<details><summary>Original raw ruling text</summary>

```
N359188  

March 12, 2026

  CLA-2-44:OT:RR:NC:N5:130  

CATEGORY: Classification  

TARIFF NO.: 4421.99.9880

  Ms. Chantal Fortin  Groupe Cabico  677 Rue Akhurst  Coaticook, QC J1A 0B4  Canada  RE:      The tariff classification of two-piece range hood covers from Canada  Dear Ms. Fortin:  In your letter, dated January 12, 2026, you requested a binding tariff classification ruling range hood covers.    The request was returned to you for additional information, which was received by this office on February  25, 2026.  Product information and diagrams were submitted for our review.  The products under consideration are wood hood canopy tops and wood hood canopy bases, which together  form range hood covers.  The covers are non-functional.  They are custom made and may vary in size and  materials.  You state that they are constructed of “standard wood species (except exotic woods)”, medium  density fiberboard (MDF), particle board, and melamine.  The range hood covers merely obscure a range  hood or fan.  The canopy tops and bases range from simple to more complex and are generally secured to the  ceiling during installation.  You suggest in your letter that the two-piece range hood covers are classifiable under subheading  4420.19.0000, Harmonized Tariff Schedule of the United States (HTSUS) which provides for statuettes and  ornaments of wood.  We disagree.  While the range hood covers have a decorative aspect to them, they are  not “ornaments” as intended by heading 4420.  They provide continuity to cabinetry, while not being  functionally cabinetry.  The covers, however, do not meet the definitions of furniture or builders’ joinery.   Note 3 to Chapter 44, HTSUS, indicates that “Headings 4414 to 4421 apply to articles of the respective  descriptions of particle board or similar board, fiberboard, laminated wood or densified wood as they apply to  such articles of wood.”  Therefore, the fact that the range hood covers are constructed of MDF and particle  board does not exclude them from Chapter 44.  They are classifiable as other articles.  The applicable subheading for the non-functional range hood covers will be 4421.99.9880, HTSUS, which  provides for Other articles of wood: Other: Other: Other: Other: Other.  The general rate of duty will be 3.3  percent ad valorem. 



The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and Frequently Asked Questions on  the Trade Remedy/IEEPA page at   https://www.cbp.gov/trade/programs-administration/trade-remedies/IEEPA-FAQ.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request. This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1). This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect. In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.  Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Laurel Duvall at laurel.duvall@cbp.dhs.gov.  

Sincerely,

  (for)  James Forkan  Designated Official Performing the Duties of the Division Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- sufficient. Material (standard wood species, MDF, particle board, melamine) stated explicitly and repeatedly. Predicting "aluminum wire" (chapter 76) directly contradicts the stated material -- a clear model hallucination, not a stripper problem.


## 10. N359753 (model: openai/gpt-oss-20b)

**True code:** 9406900130  |  **Predicted:** 7308909000


**Cleaned description (sent to model):**

> The request was returned to you for additional information, which was received by this office on March 16, 2026. Product information and diagrams were submitted for our review. The product under consideration is a prefabricated building structure for residential construction. The structure is constructed of cold-formed steel structural members including wall studs, tracks, floor joists, and roof trusses. The wall panels are constructed of cold-formed steel studs and tracks with magnesium oxide sheathing boards and various types of insulation. The floor structure is constructed of cold-formed steel joists. You state that “the prefabricated wall panels incorporate exterior sheathing, insulation systems, and mechanical, electrical, and plumbing rough-in components prior to shipment. Exterior wall panels are configured to receive exterior cladding on site, while interior finishes are completed after installation and final utility connections.” You state that “(e)lectrical conduit and wiring, plumbing piping, and HVAC pathways may be installed within the cold formed steel wall cavities during panel fabrication.” You also state that interior finishes are installed after the structural building has been erected in the U.S. The structures are not imported with furniture or appliances. The components are entered together ready to assemble into a prefabricated building structure. The materials are not adapted to general use. The units are not modular units that are assembled together to form a larger structure.


<details><summary>Original raw ruling text</summary>

```
N359753  

April 7, 2026

  CLA-2-94:OT:RR:NC:N5:130  

CATEGORY: Classification  

TARIFF NO.: 9406.90.0130

  Mr. LeVaughn Kaopio  Novus Universal, Inc.  500 Alakawa Street, #105  Honolulu, HI  96817  RE:      The tariff classification, country of origin, and trade program status of a prefabricated building  structure  Dear Mr. Kaopio:  In your letter, dated February 24, 2026, you requested a binding tariff classification, country of origin, and  applicability of trade programs ruling on a prefabricated building structure.  The request was returned to you  for additional information, which was received by this office on March 16, 2026.  Product information and  diagrams were submitted for our review.   The product under consideration is a prefabricated building structure for residential construction.  The  structure is constructed of cold-formed steel structural members including wall studs, tracks, floor joists, and  roof trusses.  The wall panels are constructed of cold-formed steel studs and tracks with magnesium oxide  sheathing boards and various types of insulation.  The floor structure is constructed of cold-formed steel  joists.  You state that “the prefabricated wall panels incorporate exterior sheathing, insulation systems, and  mechanical, electrical, and plumbing rough-in components prior to shipment. Exterior wall panels are  configured to receive exterior cladding on site, while interior finishes are completed after installation and  final utility connections.”  You state that “(e)lectrical conduit and wiring, plumbing piping, and HVAC  pathways may be installed within the cold formed steel wall cavities during panel fabrication.”  You also  state that interior finishes are installed after the structural building has been erected in the U.S.  The  structures are not imported with furniture or appliances.  The components are entered together ready to  assemble into a prefabricated building structure.  The materials are not adapted to general use.  The units are  not modular units that are assembled together to form a larger structure.  Note 4 to Chapter 94, Harmonized Tariff Schedule of the United States (HTSUS) defines “prefabricated  buildings”: 



For the purposes of heading 9406, the expression "prefabricated buildings" means buildings which are  finished in the factory or put up as elements, entered together, to be assembled on site, such as  housing or worksite accommodation, offices, schools, shops, sheds, garages or similar buildings.  The Explanatory Notes to the Harmonized System for Chapter 94 set for that prefabricated buildings are in  the form of  -    complete buildings, fully assembled, ready for use;  -    complete buildings, unassembled;  -    incomplete buildings, whether or not assembled, having the essential character of prefabricated  buildings.  In the case of buildings presented unassembled, the necessary elements may be presented partially  assembled (for example, walls, trusses) or cut to size (beams, joists, in particular) or, in some cases, in  indeterminate or random lengths for cutting on the site (sills, insulation, etc.).  The instant units are finished in the factory and entered together to be assembled onsite into housing units.    They include trusses, wall panels (with steel framing), and joists.  While the finishing is completed in the  United States, the imported goods have the essential character of prefabricated buildings.  The applicable subheading for the prefabricated building structures will be 9406.90.0130, HTSUS, which  provides for Prefabricated buildings: Other: Of metal: Other.  The general rate of duty will be 2.9 percent ad  valorem.   While you request a country of origin and trade program status ruling, you have provided insufficient  information for those determinations.  We must know each manufacturing operation and the country in which  each operation takes place.  Purchase of materials in a particular country does not confer country of origin.  I  n accordance with Title 19, Code of Federal Regulations, Section 177.7, “Moreover, no ruling letter will be  issued with regard to transactions or questions which are essentially hypothetical in nature or in any instance  in which it appears contrary to the sound administration of the Customs and related laws to do so.”  We  cannot provide a determination on possible countries of origin.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at   https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request. This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1). This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect. In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.  Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP. 



This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Laurel Duvall at laurel.duvall@cbp.dhs.gov.  

Sincerely,

  (for)  James P. Forkan  Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- sufficient, arguably generous: the description literally uses the phrase "prefabricated building structure", which is close to verbatim heading 9406's title ("Prefabricated buildings"). The model's miss (generic chapter 73 steel structures) overlooks text that almost names the correct heading.


## 11. N362830 (model: openai/gpt-oss-120b)

**True code:** 8708220000  |  **Predicted:** 87089990


**Cleaned description (sent to model):**

> The articles under consideration are framed sunroof glass assemblies that are installed in the roof of a motor vehicle and function as moveable or fixed roof windows. Part number 916047JA0A (Product Name GLASS ASSY-SUNROOF, RR) consists of a glass, frame, bracket, and weatherstrip. Part numbers 916046CT1B (Product Name GLASS ASSY-SUNROOF, RR) and 916026CT1B (Product Name GLASS ASSY-SUNROOF, FR) consists of a glass, frame, and weatherstrip. Part number 912057JA0A (Product Name SUNROOF COMPL-SLIDE) is a complete sunroof, which consists of a glass, frame, rail, weatherstrip, and motor. The glass panel is permanently fitted within a frame that provides structural support and facilitates installation, sealing, and integration with the vehicle’s sunroof mechanism. When installed, the assembly forms the transparent roof panel of the sunroof system and may be raised, tilted, or retracted, depending on the vehicle design.


<details><summary>Original raw ruling text</summary>

```
N362830  

July 21, 2026

  CLA-2-87:OT:RR:NC:N2:206  

CATEGORY: Classification  

TARIFF NO.: 8708.22.0000

  Jason Ricketts  Nissan North America  1 Nissan Way  Franklin, TN 37067  RE:  The tariff classification of framed sunroof glass assemblies from Japan  Dear Mr. Ricketts:  In your letter dated July 2, 2026, you requested a tariff classification ruling.  The articles under consideration are framed sunroof glass assemblies that are installed in the roof of a motor  vehicle and function as moveable or fixed roof windows.  Part number 916047JA0A (Product Name GLASS ASSY-SUNROOF, RR) consists of a glass, frame,  bracket, and weatherstrip. Part numbers 916046CT1B (Product Name GLASS ASSY-SUNROOF, RR) and  916026CT1B (Product Name GLASS ASSY-SUNROOF, FR) consists of a glass, frame, and weatherstrip.  Part number 912057JA0A (Product Name SUNROOF COMPL-SLIDE) is a complete sunroof, which  consists of a glass, frame, rail, weatherstrip, and motor.  The glass panel is permanently fitted within a frame that provides structural support and facilitates  installation, sealing, and integration with the vehicle’s sunroof mechanism. When installed, the assembly  forms the transparent roof panel of the sunroof system and may be raised, tilted, or retracted, depending on  the vehicle design.  You suggest classification of the sunroof assemblies in subheading 8708.22, Harmonized Tariff Schedule of  the United States (HTSUS), which provides for front windscreens (windshields) and other framed windows.  You also claim that there are published rulings, e.g., HQ H112616, dated November 1, 2010, classifying  similar assemblies in subheading 8708.29, HTSUS, which provides for other parts of vehicle bodies and  request this office to revoke these rulings. Please be advised that subheading 8708.22 was added to the  nomenclature on January 26, 2022, when the relevant HTSUS subheading notes were amended. This  statutory change and the interpretative changes that followed now preclude such articles from being classified 



in subheading 8708.29, HTSUS. Thus, HQ ruling H112616, as well as any other rulings published prior to  January 26, 2022, for similar merchandise, are revoked by operation of law and are no longer controlling. See  HQ H331958, dated April 8, 2026.  The applicable subheading for the framed sunroof glass assemblies will be 8708.22.0000, HTSUS, which  provides for parts and accessories of the motor vehicles of headings 8701 to 8705: Front windscreens  (windshields), rear windows and other windows specified in subheading note 1 to this chapter. The general  rate of duty will be 2.5 percent ad valorem.  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at   https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Liana Alvarez at liana.alvarez@cbp.dhs.gov.  

Sincerely,

  (for)  James P. Forkan  Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES, with a caveat. All physical facts (glass, frame, movable/fixed window function) are present, and the description explicitly says "windows", which maps to subheading 8708.22's own legal text ("other windows"). Flagged as borderline: the ruling text itself notes 8708.22 is a subheading recently added (Jan 2022) specifically to pull these articles out of a formerly-used "other parts" subheading (8708.29) -- a regulatory-history nuance a generalist, not just a reader of the facts, would need to know. Judged YES because the key discriminating word ("windows") is present in the input, but this is the most defensible borderline case in the sample.


## 12. N357936 (model: openai/gpt-oss-120b)

**True code:** 2827410000  |  **Predicted:** 26022000


**Cleaned description (sent to model):**

> the subject product is identified as Tribasic Copper Chloride, an inorganic compound. You state that this is a salt consisting of copper, oxygen, hydrogen, and chlorine. The chemical formula is Cu2 (OH)3CI and the Chemical Abstract (“CAS”) number is 1332-65-6. This chemical compound is used in a variety of applications; primarily as an agricultural fungicide, an animal feed additive for copper supplementation, and a blue-green coloring agent for pyrotechnics. It is also used in other industrial applications as a catalyst in organic synthesis and for manufacturing components like pigments for glass and ceramics. In the instant case, the Tribasic Copper Chloride will be labelled and sold as Basic Copper Chloride, a source of copper for further manufacture of feed for livestock.


<details><summary>Original raw ruling text</summary>

```
N357936  

January 28, 2026

  CLA-2-28:OT:RR:NC::N3:136  

CATEGORY: Classification  

TARIFF NO.: 2827.41.0000

  Michael Roll  Roll & Harris LLP  2121 Avenue of the Stars, Suite 800  Los Angeles, CA 90067  RE:  The tariff classification of Tribasic Copper Chloride from Thailand  Dear Mr. Roll:  In your letter dated January 19, 2026, on behalf of your client, Brova Inc., you requested a tariff classification  ruling on Tribasic Copper Chloride.  In your submission, the subject product is identified as Tribasic Copper Chloride, an inorganic compound.   You state that this is a salt consisting of copper, oxygen, hydrogen, and chlorine.  The chemical formula is  Cu2 (OH)3CI and the Chemical Abstract (“CAS”) number is 1332-65-6. This chemical compound is used in  a variety of applications; primarily as an agricultural fungicide, an animal feed additive for copper  supplementation, and a blue-green coloring agent for pyrotechnics. It is also used in other industrial  applications as a catalyst in organic synthesis and for manufacturing components like pigments for glass and  ceramics. In the instant case, the Tribasic Copper Chloride will be labelled and sold as Basic Copper  Chloride, a source of copper for further manufacture of feed for livestock.  The applicable subheading for the Tribasic Copper Chloride will be 2827.41.0000, Harmonized Tariff  Schedule of the United States (HTSUS), which provides for Chlorides, chloride oxides and chloride  hydroxides; bromides and bromide oxides; iodides and iodide oxides: Chloride oxides and chloride  hydroxides: Of copper.  The general rate of duty will be 3.9 percent ad valorum.  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either 



the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and Frequently Asked Questions on  the Trade Remedy/IEEPA page at   https://www.cbp.gov/trade/programs-administration/trade-remedies/IEEPA-FAQ.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported.  If you have any questions regarding the ruling, please contact  National Import Specialist Nuccio Fera at nuccio.fera@cbp.dhs.gov.  

Sincerely,

  (for)  Denise Faingar  Designated Official Performing the Duties of the Division Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- more than sufficient. Exact chemical formula (Cu2(OH)3Cl) and CAS number are given, explicitly described as a "salt". Predicting copper ORE/concentrate (heading 2602, raw mined material) rather than a refined inorganic chemical salt (chapter 28) is a severe, inexplicable model error.


## 13. N355375 (model: openai/gpt-oss-120b)

**True code:** 6802990090  |  **Predicted:** 68022000


**Cleaned description (sent to model):**

> The merchandise under consideration is referred to as Silver Grey stone.A sample was submitted with your ruling request and was forwarded to the Customs and Border Protection Laboratory for analysis.This analysis has been completed. Silver Grey is a black and white stone with a salt-and-pepper appearance, featuring white streaks. From theinformation you provided, it will measure between 115 to 122 inches in length, between 65 to 75 inches inwidth, and either 0.75 inches or 1.5 inches in thickness. After importation, it will be cut to size and shape for pplications such as kitchen countertops, bathroom surfaces, and surfaces for office furniture. aLaboratory analysis has determined that Silver Grey is an other metamorphic stone. The sides of the stonehave been simply cut or sawn.


<details><summary>Original raw ruling text</summary>

```
N355375 May 21, 2026CLA-2-68:OT:RR:NC:N1:128
 CATEGORY: Classification
 TARIFF NO.: 6802.99.0090
 Ms. Natalia TeixeiraOHM International Inc.195 Prospect Plains RoadMonroe Township, NJ 08831RE:  The tariff classification of Silver Grey stone from Brazil. Dear Ms. Teixeira:In your letter dated 
 October 28, 2025
 , you requested a tariff classification ruling.The merchandise under consideration is referred to as Silver Grey stone.A sample was submitted with your  ruling request and was forwarded to the Customs and Border Protection Laboratory for analysis.This  analysis has been completed. Silver Grey is a black and white stone with a salt-and-pepper appearance, featuring white streaks. From theinformation you provided, it will measure between 115 to 122 inches in length, between 65 to 75 inches inwidth, and either 0.75 inches or 1.5 inches in thickness.  After importation, it will be cut to size and shape for pplications such as kitchen countertops, bathroom surfaces, and surfaces for office furniture.  aLaboratory analysis has determined that Silver Grey is an other metamorphic stone.  The sides of the stonehave been simply cut or sawn.  The top face of the stone has been honed, and the bottom face has beencoated.The applicable subheading for the Silver Grey stone will be 6802.99.0090, Harmonized Tariff Schedule ofthe United States (HTSUS), which provides for “Worked monumental or building stone (except slate) andarticles thereof, other than goods of heading 6801…: Other: Other stone: Other: Other.”  The general rate ofduty will be 6.5 percent ad valorem. The duties cited above are current as of this ruling’s issuance. Duty rates are provided for your convenience and are subject to change.The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.
 This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or othercharges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and otherduties as provided for in Subchapter III to Chapter 99, HTSUS.Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with eitherthe Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisionscovering exceptions to such tariffs.For further information to assist with the importation process, please refer to the frequently updated CargoSystems Messaging Service (CSMS) messages at https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at https://www.cbp.gov/trade/programs-administration/trade-remedies.The holding set forth above applies only to the specific factual situation and merchandise description asidentified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations(CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of theinformation furnished in the ruling letter, whether directly, by reference, or by implication, is accurate andcomplete in every material respect.  In the event that the facts are modified in any way, or if the goods do notconform to these facts at time of importation, you should bring this to the attention of U.S. Customs andBorder Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.Additionally, we note that the material facts described in the foregoing ruling may be subject to periodicverification by CBP.This ruling is being issued under the provisions of Part 177 of the Customs and Border ProtectionRegulations (19 C.F.R. 177).A copy of the ruling or the control number indicated above should be provided with the entry documentsfiled at the time this merchandise is imported.  If you have any questions regarding the ruling, please contactNational Import Specialist Nicole Sullivan at nicole.d.sullivan@cbp.dhs.gov.
 Sincerely,
 (for)James P. ForkanDirectorNational Commodity Specialist Division
 
```
</details>


**Judgment:** YES -- sufficient. Explicitly states "other metamorphic stone" (not marble/travertine/alabaster), which is the fact needed to route to subheading 6802.9x rather than 6802.2x (the marble-family group). A schedule-structure nuance, but the distinguishing fact is present in the text.


## 14. N362193 (model: openai/gpt-oss-120b)

**True code:** 3307410000  |  **Predicted:** 33074900


**Cleaned description (sent to model):**

> The merchandise under consideration consists of 14 Palo Santo (Bursera Graveolens) sticks, a copper clip, and a textile drawstring bag, packaged for retail sale under the brand name AuraSerenity. You state that the sticks are gathered from naturally fallen trees in Peruvian forests and are aged for several years, during which they are exposed to natural sun and rain conditions, allowing them to develop aromatic resins. The incense sticks are intended for use in aromatic rituals, releasing their scent when burned. The clip is used to hold the stick during burning.


<details><summary>Original raw ruling text</summary>

```
N362193  

July 8, 2026

  CLA-2-33:OT:RR:NC:N3:140  

CATEGORY: Classification  

TARIFF NO.: 3307.41.0000

  Christian Bustamante  Prologix  7890 Peters Rd. STE G107  Plantation, FL 33324-4028  RE:  The tariff classification of “Palo Santo” (Bursera Graveolens) sticks from Peru  Dear Mr. Bustamante:  In your letter dated June 9, 2026, you requested a tariff classification ruling on behalf of your client, Magusa  Global Cargo.  The merchandise under consideration consists of 14 Palo Santo (Bursera Graveolens) sticks, a copper clip,  and a textile drawstring bag, packaged for retail sale under the brand name AuraSerenity. You state that the  sticks are gathered from naturally fallen trees in Peruvian forests and are aged for several years, during which  they are exposed to natural sun and rain conditions, allowing them to develop aromatic resins. The incense  sticks are intended for use in aromatic rituals, releasing their scent when burned. The clip is used to hold the  stick during burning.  The Explanatory Notes of the Harmonized Tariff System provide guidance in the interpretation of the  Harmonized Commodity Description and Coding System at the international level. Explanatory Note X to  GRI 3(b) provides that the term "goods put up in sets for retail sale" means goods that: (a) consist of at least  two different articles which are prima facie, classifiable in different headings: (b) consist of articles put up  together to meet a particular need or carry out a specific activity; and (c) are put up in a manner suitable for  sale directly to users without repacking. Goods classifiable under GRI 3(b) are classified as if they consisted  of the material or component which gives them their essential character.  The product at issue will be classified as a set for tariff classification purposes in accordance with GRI 3(b),  with the essential character imparted by the incense sticks.  The applicable subheading for the Palo Santo sticks will be 3307.41.0000, Harmonized Tariff Schedule of the  United States (HTSUS), which provides for “Preparations for perfuming or deodorizing rooms, including  odoriferous preparations used during religious rites: ‘Agarbatti’ and other odoriferous preparations which  operate by burning.” The general rate of duty will be 2.4 percent ad valorem. 



The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at Cargo Systems Messaging Service and the Trade Remedies  page at https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Merari Ortiz at merari.ortiz@cbp.dhs.gov  

Sincerely,

  (for)  James P. Forkan  Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- sufficient, arguably generous. Description explicitly says the sticks "release their scent when burned" for "aromatic rituals" -- near-verbatim match to subheading 3307.41's own legal text ("odoriferous preparations which operate by burning"). The model's choice of the generic "other" subheading (3307.49) misses text that almost quotes the correct subheading.


## 15. N358769 (model: openai/gpt-oss-20b)

**True code:** 7616995190  |  **Predicted:** 39249099


**Cleaned description (sent to model):**

> The item under consideration is a Lipstick Container, Model # LMMR210. The container is a storage cartridge used to apply, carry, and protect lipstick products. This container does not contain lipstick molds when imported. According to the information provided, the container is in the shape of an elliptical cylinder 21.3 millimeters wide and 73.3 millimeters in height. It weighs 26.3 grams and 73.02% of its components are made of aluminum while the remaining components are made of plastic or other metals. At the top there is an empty cylindrical cap that can be removed and reattached to the container. When attached, the cap encapsulates a sleeve that would hold a lipstick mold, which rests on another cylinder of comparable width identified as a draw ring. The draw ring contains a rotational mechanism that raises and lowers a lipstick mold within the sleeve, allowing the user to apply lipstick. We note that the container is composed of various materials.


<details><summary>Original raw ruling text</summary>

```
N358769  

February 27, 2026

  CLA-2-76:OT:RR:NC:N1:113  

CATEGORY: Classification  

TARIFF NO.: 7616.99.5190

  Kyung-Jin Moon  JINSOL Customs Consulting & Logistic Service  129, Gaetbeol-Ro  Yeonsu-Gu, Incheon 21999  South Korea  RE:  The tariff classification of a Lipstick Container from South Korea  Dear Kyung-Jin Moon:  In your letter dated February 11, 2026, you requested a tariff classification ruling on behalf of your client,  Jeong-Hun Cosmetic Packaging.  Descriptions, technical information, and photographs were submitted with  your request.  The item under consideration is a Lipstick Container, Model # LMMR210. The container is a storage  cartridge used to apply, carry, and protect lipstick products. This container does not contain lipstick molds  when imported.   According to the information provided, the container is in the shape of an elliptical cylinder 21.3 millimeters  wide and 73.3 millimeters in height.  It weighs 26.3 grams and 73.02% of its components are made of  aluminum while the remaining components are made of plastic or other metals.   At the top there is an empty  cylindrical cap that can be removed and reattached to the container.  When attached, the cap encapsulates a  sleeve that would hold a lipstick mold, which rests on another cylinder of comparable width identified as a  draw ring.  The draw ring contains a rotational mechanism that raises and lowers a lipstick mold within the  sleeve, allowing the user to apply lipstick.   We note that the container is composed of various materials.  The classification of merchandise under the  Harmonized Tariff Schedule of the United States (HTSUS) is in accordance with the General Rules of  Interpretation (GRI), taken in order.  GRI 3(b) provides that mixtures, composite goods consisting of  different materials or made up of different components, and goods put up in sets for retail sale shall be  classified as if they consisted of the material or component which gives them their essential character.    Explanatory Note (EN) VIII to GRI 3(b) explains that “the factor which determines essential character will  vary as between different kinds of goods. It may, for example, be determined by the nature of the material or  component, its bulk, quantity, weight or the use of the goods.”  Since the container is composed of different 



materials and aluminum is the predominant material used, the container fits the description of a composite  good with the aluminum components imparting the essential character.   The Explanatory Notes (ENs) to Section XV, Note 7 of the HTSUS, states that “except where the headings  otherwise require, articles of base metal (including articles of mixed materials treated as articles of base metal  under the General Interpretative Rules) containing two or more base metals are to be treated as articles of the  base metal.”  The predominant metal in the Lipstick Container is aluminum. Therefore, this container will be  classified under heading 7616, HTSUS, which provides for other articles of aluminum.   Heading 7616, HTSUS, is a residual or basket provision which covers a wide range of aluminum articles that  are not more specifically provided for elsewhere in the HTSUS. The ENs to heading 7616 state that “This  heading covers all articles of aluminum other than those covered by the preceding headings of this Chapter,  or by Note 1 to Section XV, or articles specified or included in Chapter 82 or 83, or more specifically  covered elsewhere in the Nomenclature.” An article of aluminum can be classified in heading 7616 if it is  determined that the item is not more specifically provided for in any other heading of the tariff.  The Lipstick  Container is not specifically covered elsewhere in the tariff. Accordingly, it is classifiable in heading 7616,  HTSUS.  The applicable subheading for the Lipstick Container will be 7616.99.5190, HTSUS, which provides for  “Other articles of aluminum: Other: Other: Other.” The general rate of duty will be 2.5 percent ad valorem.  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at   https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177). 



A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Matthew Gay at matthew.gay@cbp.dhs.gov.  

Sincerely,

  (for)  James Forkan  Designated Official Performing the Duties of the Division Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- more than sufficient. Material composition is explicitly quantified ("73.02% of its components are made of aluminum"). Predicting a plastics classification (chapter 39) directly contradicts this explicit, numeric fact.


## 16. N361892 (model: openai/gpt-oss-20b)

**True code:** 6402999005  |  **Predicted:** 6403191000


**Cleaned description (sent to model):**

> Style # 6018774A-BR UA Pulse Storm is a below-the-ankle, unisex, athletic shoe. This style has a unique upper in that there are two forms of functional closures; an elastic lace over a separate tongue, and a slide fastener closure over the lace closure. The external surface area of the upper (esau) is made up of textile with 3D printed rubber/plastic overlays and dots. The rubber/plastic on either side of the slide fastener and the wide rubber/plastic overlays, together with the connected rubber/plastic dots, makes up the majority of the esau. The widely spaced small dots are considered accessories or reinforcements and not included in the esau calculation. The rubber/plastic traction outer sole is molded over the upper material by ¼ inches for the majority of the perimeter and is considered a foxing-like band. This style is valued at more than $12 per pair. Style # 6011642A-BR UA Pulse is a man’s below-the-ankle athletic shoe with a lace-up closure. The esau consists of rubber/plastics and textile. The majority of the esau is made up of 3D printed rubber/plastic eye stays, overlays and fine lines. The rubber/plastics traction outer sole covers the upper material by ¼ inches for the majority of the perimeter and is considered a foxing-like band. This style is valued at more than $12 per pair.


<details><summary>Original raw ruling text</summary>

```
N361892  

June 29, 2026

  CLA-2-64:OT:RR:NC:N2 247  

CATEGORY: Classification  

TARIFF NO.: 6402.99.9005

  Andrea Loftus  Under Armour, Inc.  2601 Port Covington Dr.  Baltimore, MD  21230  RE:  The tariff classification of athletic footwear from Vietnam  Dear Ms. Loftus:  In your letter dated May 29, 2026, you requested a tariff classification ruling.  Two styles of athletic footwear  submitted with your request were examined and will be returned as requested.  Style # 6018774A-BR UA Pulse Storm is a below-the-ankle, unisex, athletic shoe. This style has a unique  upper in that there are two forms of functional closures; an elastic lace over a separate tongue, and a slide  fastener closure over the lace closure. The external surface area of the upper (esau) is made up of textile with  3D printed rubber/plastic overlays and dots.  The rubber/plastic on either side of the slide fastener and the  wide rubber/plastic overlays, together with the connected rubber/plastic dots, makes up the majority of the  esau.  The widely spaced small dots are considered accessories or reinforcements and not included in the esau  calculation.  The rubber/plastic traction outer sole is molded over the upper material by ¼ inches for the  majority of the perimeter and is considered a foxing-like band.  This style is valued at more than $12 per pair.  Style # 6011642A-BR UA Pulse is a man’s below-the-ankle athletic shoe with a lace-up closure.  The esau  consists of rubber/plastics and textile.  The majority of the esau is made up of 3D printed rubber/plastic eye  stays, overlays and fine lines.  The rubber/plastics traction outer sole covers the upper material by ¼ inches  for the majority of the perimeter and is considered a foxing-like band.  This style is valued at more than $12  per pair.  You suggested Style # 6011642A-BR UA Pulse, the man’s athletic shoe is classified under subheading  6404.11.9020, Harmonized Tariff Schedule of the United States, (HTSUS), the provision for footwear with  uppers of textile.  The exposed textile areas between the crossed rubber/plastic lines that are smaller than a  collar button are considered “filled-in” and counted as rubber/plastics for esau calculations. Therefore, this  style will be classified elsewhere. 



The applicable subheading for Style # 6018774A-BR UA Pulse Storm and Style # 6011642A-BR UA Pulse  will be 6402.99.9005, HTSUS, which provides for Other footwear with outer soles and uppers of  rubber/plastics: Other footwear: Other: Other: Other: Other: Valued over $12/pair: Tennis shoes, basketball  shoes, gym shoes, training shoes and the like.  The rate of duty will be 20 percent ad valorem.  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at   https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.  Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Stacey Kalkines at stacey.kalkines@cbp.dhs.gov.  

Sincerely,

  (for)  James P. Forkan  Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- sufficient for the 4-digit heading level (6402, rubber/plastics footwear) at least: upper material is explicitly described as "textile with 3D printed rubber/plastic overlays" with a rubber/plastic outer sole, and leather is never mentioned. Predicting a LEATHER-upper heading (6403) contradicts the explicit stated materials. The exact 10-digit ESAU (external-surface-area-of-upper) calculation is a specialized footwear-classification methodology not fully derivable without the schedule's own rules, but the material facts needed to avoid the leather-heading error are present.


## 17. N358854 (model: openai/gpt-oss-20b)

**True code:** 6406200000  |  **Predicted:** 6403909000


**Cleaned description (sent to model):**

> The subject kit of ruling N355798, dated December 17, 2025, contained a ball of cotton yarn and other identical components. You submitted a description and several photographs of the “DIY Crochet Shoe Kit.” The kit provides the consumer the opportunity to handcraft an upper and to assemble the components into a pair of wearable shoes after purchase.


<details><summary>Original raw ruling text</summary>

```
N358854  

February 27, 2026

  OT:RR:NC:N2:247  

CATEGORY: Classification; Origin; Marking; Trade Program  

TARIFF NO.: 6406.20.0000

  Jae Hee Park    O2Wide Co., Ltd.  Cocoro Building,  308 Dongnam-ro, Songpa-gu  Seoul 05835  Republic of South Korea  RE:  The classification, country of origin, marking, and trade program eligibility of a DIY Crochet Shoe Kit  Dear Mr. Park:  In your letter dated February 13, 2026, you requested a ruling on the classification, country of origin,  marking, and trade program eligibility of a “DIY Crochet Shoe Kit” containing a ball of folded paper strip.   The subject kit of ruling N355798, dated December 17, 2025, contained a ball of cotton yarn and other  identical components.  You submitted a description and several photographs of the “DIY Crochet Shoe Kit.”  The kit provides the  consumer the opportunity to handcraft an upper and to assemble the components into a pair of wearable shoes  after purchase.  The kit contains a PVC outer sole (Chapter 64 of the Harmonized Tariff Schedule of the  United States, HTSUS) manufactured in Turkey, an EVA insole (Chapter 64, HTSUS) manufactured in  South Korea, a printed pattern sheet (Chapter 49, HTSUS) manufactured in South Korea, and a ball/cake of  folded paper strips (Chapter 48, HTSUS) manufactured in Taiwan.  The kit is assembled, packaged in South  Korea, and exported to the United States for retail sale.  The Explanatory Notes to GRI 3(b) indicate, in pertinent part, that "goods put up in sets for retail sale" means  goods which:  (a) consist of at least two different articles which are prima facie classifiable in different  headings; (b) consist of products or articles put up together to meet a particular need or carry out a specific  activity; and (c) are put up in a manner suitable for sale directly to users without repacking.  Each of the  components of the kit is classified under different subheadings and considered a set for tariff purposes.  Since  no one subheading in the tariff schedule covers all the components, GRI 3(b) provides that goods put up in  sets for retail sale, shall be classified as the component which gives them their essential character.  In general,  "essential character" has been construed to mean the attribute which strongly marks or serves to distinguish  an article.  It may be determined by the nature of the material, its bulk, quantity, weight, value, or by the role  of the constituent material in relation to the use of the goods.  The outer sole dominates by weight and 



dictates the size, shape, and type of the completed shoe.  Therefore, this office determined that the rubber or  plastic outer sole from Turkey imparts the essential character of the set and determines the classification.  The applicable subheading for the “DIY Crochet Shoe Kit” will be 6406.20.0000, Harmonized Tariff  Schedule of the United States (HTSUS), which provides for Parts of footwear (including uppers whether or  not attached to soles other than outer soles): Outer soles and heels of rubber or plastics. The general rate of  duty will be 2.7 percent ad valorem.  When determining the country of origin for purposes of applying current trade remedies under Section 301  and additional duties, the substantial transformation analysis is applicable. See, e.g., Headquarters Ruling  Letter H301619, dated November 6, 2018. The test for determining whether a substantial transformation will  occur is whether an article emerges from a process with a new name, character, or use different from that  possessed by the article prior to processing. See Texas Instruments Inc. v. United States, 681 F.2d 778  (C.C.P.A. 1982). This determination is based on the totality of the evidence. See National Hand Tool Corp. v.  United States, 16 C.I.T. 308 (1992), aff’d, 989 F.2d 1201 (Fed. Cir. 1993).  Additionally, Section 304 of the Tariff Act of 1930, as amended (19 U.S.C. 1304), provides that unless  excepted, every article of foreign origin imported into the United States shall be marked in a conspicuous  place as legibly, indelibly, and permanently as the nature of the article (or its container) will permit, in such a  manner as to indicate to the ultimate purchaser in the United States, the English name of the country of origin  of the article. Congressional intent in enacting 19 U.S.C. 1304 was “that the ultimate purchaser should be  able to know by an inspection of the marking on the imported goods the country of which the goods is the  product. The evident purpose is to mark the goods so that at the time of purchase the ultimate purchaser may,  by knowing where the goods were produced, be able to buy or refuse to buy them, if such marking should  influence his will.” See United States v. Friedlander & Co., 27 C.C.P.A. 297, 302 (1940).  Part 134 of the U.S. Customs and Border Protection (“CBP”) Regulations (19 CFR 134) implements the  country of origin marking requirements and exceptions of 19 U.S.C. 1304. Section 134.1(b), CBP  Regulations (19 CFR 134.1(b)), defines “country of origin” as the country of manufacture, production, or  growth of any article of foreign origin entering the United States. Further work or material added to an article  in another country must effect a substantial transformation in order to render such other country the “country  of origin” within the meaning of the marking laws and regulations.  The essential character for goods classified as a set, or where no single manufacturing process provides a  clear "substantial transformation," is determined by the origin based on the single component that imparts the  essential character to the finished product.  Given that the outer sole determines the essential character of this  set, its origin dictates the origin of the entire set. The inner sole and yarn, while necessary components, are  considered secondary to the fundamental nature of the good, which is defined by the outer sole. Therefore, as  the outer sole is from Turkey, the country of origin for the set is Turkey.  General Note 33, HTSUS, sets forth the criteria for determining whether a good is originating under the  UKFTA. General Note 33(b), HTSUS, states, in pertinent part, as follows:  For the purposes of this note, subject to the provisions of subdivisions (c), (d), (n) and (o) thereof, a good  imported into the customs territory of the United States is eligible for treatment as an originating good of a  UKFTA country under the terms of this note if- (i) the good is wholly obtained or produced entirely in the  territory of Korea or of the United States, or both;  (ii) the good is produced entirely in the territory of Korea  or of the United States, or both, and-- (A) each of the non-originating materials used in the production of the  good undergoes an applicable change in tariff classification specified in subdivision (o) of this note; or (B)  the good otherwise satisfies any applicable regional value-content or other requirements set forth in such  subdivision (o); and satisfies all other applicable requirements of this note and of applicable regulations; or  (iii) the good is produced entirely in the territory of Korea or of the United States, or both, exclusively from  materials described in subdivisions (i) or (ii), above. 



For the purposes of this note, the term “UKFTA country” refers only to Korea or to the United States.   Because not all components of the “DIY Crochet Shoe Kit” were wholly obtained or produced entirely in the  territory of Korea or the United States, other requirements of General Note 33(b), HTSUS, are not applicable.   The “DIY Crochet Shoe Kit” will not be eligible for preferential tariff treatment under the UKFTA.    You have also inquired about the country of origin marking.    Please note pursuant to the marking statute, Section 304, Tariff Act of 1930, as amended (19 U.S.C. 1304)  unless excepted, every article of foreign origin (or its container) imported into the U.S. shall be marked in a  conspicuous place as legibly, indelibly and permanently as the nature of the article (or its container) will  permit, in such a manner as to indicate to the ultimate purchaser in the U.S. the English name of the country  of origin of the article.  Part 134, Customs Regulations (19 CFR Part 134), implements the country of origin  marking requirements and exceptions of 19 U.S.C. 1304.  Section 134.41(b), Customs Regulations (19 CFR  134.41(b)), mandates that the ultimate purchaser in the U.S. must be able to find the marking easily and read  it without strain.  Section 134.1(d), defines the ultimate purchaser as generally the last person in the U.S. who  will receive the article in the form in which it was imported.  If an imported article is to be sold at retail in its  imported form, the purchaser at retail is the ultimate purchaser.  As to the marking of this kit, we look to the Treasury Decision (T.D.) 91-7, published in Volume 25,  Customs Bulletin and Decisions, (January 16, 1991), which addressed, among other things, the application of  country of origin marking requirements to sets.  It was stated therein:  … in most cases, the mere inclusion of an item in a collection will not substantially transform it into an  article with a new name, character or use and, therefore, each item must be separately marked with its own  country of origin. (Where the marking of the container will reasonably indicate the country of origin to the  ultimate purchaser, the container may be marked instead of the individual articles.  See 19 U.S.C.  1304(a)(3)(D) and 19 CFR 134.32(d)). This result is consistent with the purpose of the marking statute since  the ultimate purchaser’s decision as to whether to buy the set might be influenced by the country of origin of  any of the items in the set, whether or not an item gives the set its essential character.  As the kit contains products sourced from Turkey and South Korea that have not been substantially  transformed in either country, you will need to mark the retail packaging box to indicate the proper country  of origin for each item in the kit.  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and the Trade Remedies page at   https://www.cbp.gov/trade/programs-administration/trade-remedies.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request. This position is clearly set forth in Title 19, Code of Federal Regulations 



(CFR), Section 177.9(b)(1). This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect. In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.  Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Stacey Kalkines at stacey.kalkines@cbp.dhs.gov.  

Sincerely,

  (for)  James Forkan  Designated Official Performing the Duties of the Division Director  National Commodity Specialist Division 




```
</details>


**Judgment:** NO -- insufficient. The cleaned description omits what the kit's components actually ARE (PVC outer sole, EVA insole, printed pattern sheet, paper strip ball) -- exactly the facts needed to apply GRI 3(b) essential-character reasoning and reach heading 6406 (parts of footwear). Root cause: the source ruling states each component's material inline with its own parenthetical HTS chapter citation ("a PVC outer sole (Chapter 64, HTSUS)..."), so the keyword-based cutter correctly avoided leaking "Chapter 64" but, lacking a way to strip only the parenthetical, discarded the whole sentence -- including the material fact outside the parentheses. A real, identified stripper limitation (see DECISIONS.md), though only 1 of 20 cases here.


## 18. N362770 (model: openai/gpt-oss-20b)

**True code:** 8509905500  |  **Predicted:** 73089090


**Cleaned description (sent to model):**

> The merchandise under consideration is identified as a ring made of a die-cast zinc alloy. The images in your submission illustrate that the zinc alloy ring is a C-shaped, circular ring with a distinct raised flange running along the outer circumference and features cutouts/notches. You state that the zinc alloy ring is a purely mechanical metal component designed for use solely with the electric toothbrush. It is imported as a standalone mechanical component, without any electronic elements.


<details><summary>Original raw ruling text</summary>

```
N362770  

July 20, 2026

  CLA-2-85:OT:RR:NC:N4:410  

CATEGORY: Classification  

TARIFF NO.: 8509.90.5500

  Robert Leo  Meeks, Sheppard, Leo & Pillsbury LLP  570 Lexington Avenue, Suite 2405  New York, NY 10022  RE:  The tariff classification of a zinc alloy ring from the Netherlands  Dear Mr. Leo:  In your letter dated June 30, 2026, you requested a tariff classification ruling on behalf of Discus Dental  LLC.  The merchandise under consideration is identified as a ring made of a die-cast zinc alloy. The images in your  submission illustrate that the zinc alloy ring is a C-shaped, circular ring with a distinct raised flange running  along the outer circumference and features cutouts/notches.  You state that the zinc alloy ring is a purely mechanical metal component designed for use solely with the  electric toothbrush. It is imported as a standalone mechanical component, without any electronic elements.  In your submission, you suggest that the zinc alloy ring should be correctly classified in subheading  8509.90.5500, Harmonized Tariff Schedule of the United States (HTSUS), as a toothbrush part.  We agree.  The applicable subheading for the zinc alloy ring will be 8509.90.5500, HTSUS, which provides for  “Electromechanical domestic appliances, with self-contained electric motor, other than vacuum cleaners of  heading 8508; parts thereof: Parts: Other: Other: Other”. The rate of duty will be 4.2 percent ad valorem.  The duties cited above are current as of this ruling’s issuance. Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations 



(CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Michael Chen at michael.w.chen@cbp.dhs.gov.  

Sincerely,

  (for)  James P. Forkan  Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- more than sufficient. Material is explicit ("die-cast zinc alloy"), as is the intended use ("designed for use solely with the electric toothbrush"). Predicting an iron/steel structural classification (chapter 73) contradicts both the stated material and the stated use -- a severe model error.


## 19. N352171 (model: openai/gpt-oss-120b)

**True code:** 6802990090  |  **Predicted:** 6802990010


**Cleaned description (sent to model):**

> The merchandise under consideration is referred to as “Negresco (Black Mist).” A sample was submitted with your ruling request and was forwarded to the Customs and Border Protection laboratory for analysis. This analysis has been completed. Negresco is a surface-worked black stone mottled with gray streaks and white specks. From the information you provided, its measurements upon importation are approximately 317.5 centimeters long by 198 centimeters wide by 2 or 3 centimeters thick. It is designed for use in such applications as countertops, backsplashes, and flooring. Laboratory analysis has determined that the Negresco is an other igneous stone.


<details><summary>Original raw ruling text</summary>

```
N352171  

January 29, 2026

  CLA-2-68:OT:RR:NC:N1:128  

CATEGORY: Classification  

TARIFF NO.: 6802.99.0090

  Mr. Leonardo Bermudes  Bramagran  Rodovia Fued Nemer  Castelo 29360000  Brazil  RE:  The tariff classification of Negresco stone from Brazil.  Dear Mr. Bermudes:  In your letter dated August 8, 2025, you requested a tariff classification ruling.  The merchandise under consideration is referred to as “Negresco (Black Mist).”  A sample was submitted  with your ruling request and was forwarded to the Customs and Border Protection laboratory for analysis.   This analysis has been completed.   Negresco is a surface-worked black stone mottled with gray streaks and white specks.  From the information  you provided, its measurements upon importation are approximately 317.5 centimeters long by 198  centimeters wide by 2 or 3 centimeters thick.  It is designed for use in such applications as countertops,  backsplashes, and flooring.  Laboratory analysis has determined that the Negresco is an other igneous stone.  The applicable subheading for the Negresco (Black Mist) stone will be 6802.99.0090, Harmonized Tariff  Schedule of the United States (HTSUS), which provides for “Worked monumental or building stone (except  slate) and articles thereof, other than goods of heading 6801…:  Other: Other stone: Other:  Other.”  The  general rate of duty will be 6.5 percent ad valorem  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/.  This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other 



duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and Frequently Asked Questions on  the Trade Remedy/IEEPA page at   https://www.cbp.gov/trade/programs-administration/trade-remedies/IEEPA-FAQ.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported.  If you have any questions regarding the ruling, please contact  National Import Specialist Nicole Sullivan at nicole.d.sullivan@cbp.dhs.gov.  

Sincerely,

  (for)  Denise Faingar  Designated Official Performing the Duties of the Division Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- more than sufficient; model matched the true code through all 8 digits, missing only the final 2-digit statistical suffix (10 vs 90), both generic "Other" buckets. Full physical description given.


## 20. N356923 (model: allam-2-7b)

**True code:** 8544493080  |  **Predicted:** 8544400000


**Cleaned description (sent to model):**

> The merchandise under consideration is described as a Local Area Network (LAN) Cable and is identified by model number UTP CAT5e PLUS CMR Riser 4-pair Solid LAN Cable. You state that the subject cable is a communications cable used for Ethernet and related network applications for data transmission in various industries and installations. The cables are constructed of four twisted pairs of 24 AWG copper wire, each insulated with polyethylene and jacketed using Polyvinyl Chloride (PVC). It is noted that the cables are not fitted with connectors and rated at 300 volts. The cables will be imported on reels in boxes of 1,000 ft.


<details><summary>Original raw ruling text</summary>

```
N356923  

January 5, 2026

  CLA-2:OT:RR:NC:N2:212  

CATEGORY: Classification  

TARIFF NO.: 8544.49.3080

  Donghee Jeong  Passwin Customs Service Inc.  11 Beobwon-ro 11-gil  Songpa-gu, Seoul 05836  South Korea  RE:  The tariff classification of LAN Cables from South Korea  Dear Mr. Jeong:  In your letter dated December 10, 2025, you requested a tariff classification ruling on behalf of your client,  Dong-Il Electric Wire Co. LTD.  The merchandise under consideration is described as a Local Area Network (LAN) Cable and is identified by  model number UTP CAT5e PLUS CMR Riser 4-pair Solid LAN Cable. You state that the subject cable is a  communications cable used for Ethernet and related network applications for data transmission in various  industries and installations. The cables are constructed of four twisted pairs of 24 AWG copper wire, each  insulated with polyethylene and jacketed using Polyvinyl Chloride (PVC). It is noted that the cables are not  fitted with connectors and rated at 300 volts. The cables will be imported on reels in boxes of 1,000 ft.  In your request, you suggest that the correct classification for the subject cables are under subheading  8544.49.3080, Harmonized Tariff Schedule of the United States (HTSUS). We agree.  The applicable subheading for the LAN Cables, model number UTP CAT5e PLUS CMR Riser 4-pair Solid  LAN Cable will be 8544.49.3080, HTSUS, which provides for “ Insulated (including enameled or anodized)  wire, cable (including coaxial cable) and other insulated electric conductors, whether or not fitted with  connectors; Optical fiber cables, made up of individually sheathed fibers, whether or not assembled with  electric conductors or fitted with connectors: Other electrical conductors, for a voltage not exceeding 1,000V:  Other: Of copper: Other.” The general rate of duty will be 5.3% ad valorem.  The duties cited above are current as of this ruling’s issuance.  Duty rates are provided for your convenience  and are subject to change. The text of the most recent HTSUS and the accompanying duty rates are provided  at https://hts.usitc.gov/. 



This ruling does not address the applicability of any additional duties, taxes, fees, exactions and/or other  charges, which may apply to the goods discussed herein.  This includes, but is not limited to, tariffs and other  duties as provided for in Subchapter III to Chapter 99, HTSUS.  Thus, for example, in addition to the  classification stated above, the merchandise covered by this ruling may also need to be reported with either  the Chapter 99 provision under which an additional tariff applies or one of the Chapter 99 provisions  covering exceptions to such tariffs.  For further information to assist with the importation process, please refer to the frequently updated Cargo  Systems Messaging Service (CSMS) messages at   https://www.cbp.gov/trade/automated/cargo-systems-messaging-service and Frequently Asked Questions on  the Trade Remedy/IEEPA page at   https://www.cbp.gov/trade/programs-administration/trade-remedies/IEEPA-FAQ.  The holding set forth above applies only to the specific factual situation and merchandise description as  identified in the ruling request.  This position is clearly set forth in Title 19, Code of Federal Regulations  (CFR), Section 177.9(b)(1).  This section states that a ruling letter is issued on the assumption that all of the  information furnished in the ruling letter, whether directly, by reference, or by implication, is accurate and  complete in every material respect.  In the event that the facts are modified in any way, or if the goods do not  conform to these facts at time of importation, you should bring this to the attention of U.S. Customs and  Border Protection (CBP) and submit a request for a new ruling in accordance with 19 CFR 177.2.   Additionally, we note that the material facts described in the foregoing ruling may be subject to periodic  verification by CBP.  This ruling is being issued under the provisions of Part 177 of the Customs and Border Protection  Regulations (19 C.F.R. 177).  A copy of the ruling or the control number indicated above should be provided with the entry documents  filed at the time this merchandise is imported. If you have any questions regarding the ruling, please contact  National Import Specialist Luke LePage at luke.lepage@cbp.dhs.gov.  

Sincerely,

  (for)  Evan Conceicao  Designated Official Performing the Duties of the Division Director  National Commodity Specialist Division 




```
</details>


**Judgment:** YES -- sufficient. Material (copper wire, specific gauge, insulation/jacket materials), voltage rating, and explicit "not fitted with connectors" status are all given -- these are exactly the facts the relevant subheadings turn on. The model's miss at the 6-digit subheading level is a classification-nuance error, not an input gap.

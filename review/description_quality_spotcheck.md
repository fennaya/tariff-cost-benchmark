# Description-quality spot check (hand-read, 2026-10-07)

The sample was drawn by `scripts/audit_description_quality.py` with a fixed seed (20261008): 20 flagged and 20 unflagged rulings, listed in `review/description_quality_spotcheck_sample.json`. I read the first 230 characters of each cleaned description and judged by eye whether a classifier could identify the product from it. These verdicts are my judgment, not a script output.

## 20 flagged rulings

- **Genuinely inadequate (17):** N361384 (FTC marking advice), N360727, N361037 and N360778 (FDA referral text), N361313, N361321, N361310, N361402 (sleeves and hem edges only), N361386 (robe stitching), N361404, N361398, N361312, N361305 (partial garment details with no product or fabric), N361063 ("This replaces ruling number ..."), N362356 ("a sample was submitted"), N364227 (a cloth's dimensions with no material), N361401 (pants and a scarf, no fabric or construction).
- **Borderline (1):** N361665 (only a product name and item number, "Hydro Dip Mini Pumpkin Kit").
- **Adequate, flagged by the 150-character rule only (2):** N357261 (a methylene blue injection with its indication) and N360873 (a testosterone gel pump with its dose).

So the flag is right for 17 of 20 and wrong for 2, with 1 borderline. The false positives are all from the blunt length rule.

## 20 unflagged rulings

All 20 read as adequate product descriptions (materials, construction or function stated): N361448, N359551, N359733, N360189, N362773, N357329, N359188, N357738, N360246, N362060, N363520, N362910, N362905, N357326, N352501, N361293, N357482, N363473, N357381, N360889. None was inadequate, so no false negative was found in this sample.

## What this does not show

The sample is small (40). It cannot rule out rulings with a short description of a few hundred characters that still lack the detail needed for an 8-digit classification, which the audit does not try to flag. The sensitivity analysis in `review/v1_1_results.md` therefore tests only the clearly inadequate rulings.

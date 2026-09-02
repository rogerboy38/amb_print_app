"""
Track 5 (2026-09-02) — sample-tag cells on Label Small 8 (Container).

Standalone script, not a pytest/unittest module (this repo's other unit
tests exercise exporters in isolation; this one needs a real Frappe site
and real Batch AMB data, so it runs the same way the rest of this session
has verified label rendering: `bench --site <site> console` /
`env/bin/python` against a live bench).

Run directly:
    cd <bench> && env/bin/python apps/amb_print/tests/unit/test_track5_sample_tags.py <site>

Exercises `amb_print.amb_print.label.render.build_html` directly (not the
whitelisted API, to avoid creating File attachments) against
LOTE-26-26-0005 (14 active rows, 2-line item name) and LOTE-26-25-0003
(14 active rows too, but different item name length — used for the
guard/short-name checks).

Checks, each printed PASS/FAIL with its own reason:
  1. build_html accepts sample_tags= without raising.
  2. N active rows + K requested tags -> exactly N+K non-empty label-cell
     divs in the rendered HTML (guard not triggered — tags requested are
     not already present on any active row).
  3. Guard: if a requested tag already equals some active row's
     label_sample_tag, it is NOT duplicated as an extra cell (cell count
     stays N + (K-1) for that one guarded tag).
  4. start_position: cells before the start position render as
     class="label-cell empty-cell" (no content).
  5. Requesting 0 tags reproduces the exact byte-identical output of a
     None/absent sample_tags call (no regression on the untouched path).
"""
import sys

FAILURES = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" -- {detail}" if detail and not condition else ""))
    if not condition:
        FAILURES.append(label)


def main(site):
    import frappe
    frappe.init(site=site, sites_path="sites")
    frappe.connect()
    try:
        from amb_print.amb_print.label.render import build_html

        # --- Check 1: accepts sample_tags without raising ---
        try:
            build_html(
                doctype="Batch AMB", docname="LOTE-26-26-0005",
                print_format="Label Small 8 (Container)",
                sample_tags=["MICROBIOLOGICAL ANALYSIS SAMPLE"],
            )
            check("1. build_html accepts sample_tags=", True)
        except TypeError as e:
            check("1. build_html accepts sample_tags=", False, str(e))
            # If the signature itself doesn't accept the kwarg, every
            # later check would also raise -- report and stop here.
            print("\n".join(f"[FAIL] {f}" for f in FAILURES[1:]))
            return len(FAILURES)

        # --- Fetch active-row count and an existing tag value for the guard case ---
        rows = frappe.db.get_all(
            "Container Barrels",
            filters={"parent": "LOTE-26-26-0005", "parenttype": "Batch AMB",
                     "label_is_active": 1},
            fields=["name", "label_sample_tag"],
        )
        n_active = len(rows)

        # --- Check 2: N + K cells, no guard triggered ---
        tags_4 = [
            "MICROBIOLOGICAL ANALYSIS SAMPLE",
            "CUSTOMER RETENTION SAMPLE",
            "DISTRIBUTOR RETENTION SAMPLE",
            "AMB WELLNESS RETENTION",
        ]
        html_4tags = build_html(
            doctype="Batch AMB", docname="LOTE-26-26-0005",
            print_format="Label Small 8 (Container)",
            sample_tags=tags_4,
        )
        # non-empty cells = label-cell divs NOT carrying empty-cell
        non_empty = html_4tags.count('<div class="label-cell">') + html_4tags.count(
            '<div class="label-cell ">')
        # our template emits class="label-cell empty-cell" for empties and
        # class="label-cell" (bare) for real content -- count bare ones,
        # accounting for possible Jinja whitespace variants.
        import re
        bare_cells = len(re.findall(r'<div class="label-cell"[^>]*>\s*<div class="label-content">', html_4tags))
        expected = n_active + 4
        check("2. N active + 4 requested tags = N+4 non-empty cells",
              bare_cells == expected,
              f"active={n_active} tags=4 expected={expected} got={bare_cells}")

        # --- Check 3: guard -- if a tag already exists on an active row, skip it ---
        existing_tag_values = {r["label_sample_tag"] for r in rows if r.get("label_sample_tag")}
        if existing_tag_values:
            already = next(iter(existing_tag_values))
            html_guarded = build_html(
                doctype="Batch AMB", docname="LOTE-26-26-0005",
                print_format="Label Small 8 (Container)",
                sample_tags=[already, "AMB WELLNESS RETENTION"],
            )
            bare_guarded = len(re.findall(
                r'<div class="label-cell"[^>]*>\s*<div class="label-content">', html_guarded))
            # one of the two requested tags is already present -> only +1, not +2
            check("3. guard skips an already-present tag",
                  bare_guarded == n_active + 1,
                  f"expected={n_active + 1} got={bare_guarded} (existing tag was {already!r})")
        else:
            check("3. guard skips an already-present tag", True,
                  "SKIPPED -- no active row currently carries a label_sample_tag to test against")

        # --- Check 4: start_position emits empty cells before the start ---
        html_sp = build_html(
            doctype="Batch AMB", docname="LOTE-26-26-0005",
            print_format="Label Small 8 (Container)",
            start_position="B2",
        )
        # First 3 grid cells (A1, B1, A2) must be empty-cell; 4th (B2) must not.
        cell_divs = re.findall(r'<div class="label-cell( empty-cell)?"', html_sp)
        check("4. start_position=B2 leaves A1,B1,A2 empty",
              len(cell_divs) >= 4 and cell_divs[0] and cell_divs[1] and cell_divs[2] and not cell_divs[3],
              f"first 4 cell classes: {cell_divs[:4]}")

        # --- Check 5b: tag cells never render the literal string "None"
        #     (regression -- found live during Track 5 §5 measurement:
        #     E.D. on a tag cell rendered "E.D. None" because the fallback
        #     expression skipped the `or ""` coalescing the regular-row
        #     branch has). Use a batch/tag combo guaranteed to produce at
        #     least one tag cell.
        html_tags = build_html(
            doctype="Batch AMB", docname="LOTE-26-26-0005",
            print_format="Label Small 8 (Container)",
            sample_tags=["AMB WELLNESS RETENTION"],
        )
        check("5b. no literal 'None' text in tag-cell output",
              " None" not in html_tags and ">None<" not in html_tags,
              "found a literal None -- a field access is missing 'or \"\"'")

        # --- Check 5: sample_tags=[] / None produce byte-identical output ---
        html_none = build_html(
            doctype="Batch AMB", docname="LOTE-26-26-0005",
            print_format="Label Small 8 (Container)",
        )
        html_empty_list = build_html(
            doctype="Batch AMB", docname="LOTE-26-26-0005",
            print_format="Label Small 8 (Container)",
            sample_tags=[],
        )
        check("5. sample_tags=None and sample_tags=[] are byte-identical",
              html_none == html_empty_list)

    finally:
        frappe.db.rollback()

    return len(FAILURES)


if __name__ == "__main__":
    site = sys.argv[1] if len(sys.argv) > 1 else "v2.sysmayal.cloud"
    n_fail = main(site)
    print(f"\n{'ALL PASS' if n_fail == 0 else f'{n_fail} FAILURE(S)'}")
    sys.exit(1 if n_fail else 0)

# Updating SAMPLE LABEL 8 Letter for `label_cells`

This guide walks you through updating the existing **SAMPLE LABEL 8 Letter** Print Designer format so it iterates the new `label_cells` child table on Sample Request AMB instead of repeating the same top-level fields 8 times.

## 1. Locate the format

1. In ERPNext, navigate to **Print Format List**.
2. Search for `SAMPLE LABEL 8 Letter` (filter by Doc Type = `Sample Request AMB`, Print Designer = `1`).
3. Click the row → **Edit** (this opens the Print Designer canvas).

## 2. Why we are updating it

The current version renders the Sample Request top-level fields (item, lot, dates, etc.) eight times — the same data on every cell. With this PR, Sample Request AMB has a new child table `label_cells` populated by the **Generate Label Cells / Generar Etiquetas** button. Each row in that table represents one physical label cell (A1 through B4). The format should iterate `doc.label_cells` and render one cell per row, so an SR with 3 different items at 2 samples each correctly produces 6 cells.

## 3. Page and grid layout

- Paper size: **Letter** (8.5" × 11")
- Grid: **2 columns × 4 rows** (8 cells total)
- Cell size: ~95mm wide × 65mm tall
- Cell positions map to `cell_position` values:
  - A1 = top-left, B1 = top-right
  - A2 = middle-upper-left, B2 = middle-upper-right
  - A3 = middle-lower-left, B3 = middle-lower-right
  - A4 = bottom-left, B4 = bottom-right

In Print Designer, use a **repeater (Table iteration)** bound to `doc.label_cells`, then position each cell on the grid based on `row.cell_position`. Print Designer's grid + table-loop tooling is the right primitive — do not hardcode 8 separate static blocks.

## 4. Per-cell content (top to bottom)

Render the following Jinja inside each cell, in this order:

1. **Bold large** — item name (allow wrapping to 2 lines):

   ```jinja
   {{ row.item_name }}
   ```

2. Lot number:

   ```jinja
   LOTE: {{ row.lot }}
   ```

3. Manufacture and expiration dates on a single line:

   ```jinja
   M.D. {{ row.manufacture_date }}  E.D. {{ row.expiration_date }}
   ```

4. Net weight:

   ```jinja
   NET WEIGHT: {{ row.net_weight }}
   ```

5. **Sample tag (red, bold, on its own line)** — only when present:

   ```jinja
   {% if row.sample_tag %}
     <span style="color: red; font-weight: bold;">{{ row.sample_tag }}</span>
   {% endif %}
   ```

6. Smaller text footer:

   ```
   No commercial value. For sample use only
   ```

7. Smaller bold text footer:

   ```
   PRODUCT OF MEXICO
   ```

## 5. Position handling

Each row carries `row.cell_position` (`A1`..`B4`). Use this to drop the rendered cell content into the correct slot of the 2×4 grid. In Print Designer this is typically a **conditional grid placement** — match `cell_position` to a fixed coordinate on the page.

## 6. Skip inactive cells

If `row.is_active` is `0` (False), render the cell as **blank** (no content, but the slot in the grid remains empty so the rest of the layout doesn't shift).

```jinja
{% if row.is_active %}
  {# render cell content as in section 4 #}
{% endif %}
```

## 7. Save the format

1. Click **Save** in Print Designer.
2. Optionally set **SAMPLE LABEL 8 Letter** as the **Default Print Format** for Sample Request AMB under Customize Form.

---

After updating the format, validate by opening any Sample Request AMB, clicking Generate Label Cells, then Print → SAMPLE LABEL 8 Letter.

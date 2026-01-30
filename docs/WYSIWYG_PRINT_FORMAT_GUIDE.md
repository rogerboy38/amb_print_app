# WYSIWYG Print Format Development Guide

## Vision: "What You See Is What You Get"

This guide establishes a workflow for creating ERPNext print formats where the **design process matches the final PDF output** - eliminating surprises and iterations.

---

## The Problem We Solved

### Before (Pain Points)
1. Design in browser → PDF looks different
2. Hardcoded page numbers → Don't match actual pages
3. Empty fields → Unclear if code bug or missing data
4. Multiple test cycles → Waste time

### After (WYSIWYG Approach)
1. Understand PDF engine limitations first
2. Use dynamic CSS counters for page numbers
3. Verify source data before blaming code
4. Test PDF output, not just browser preview

---

## The WYSIWYG Workflow

### Step 1: Analyze Your Target PDF
Before writing any code, study your example PDF:
- [ ] Page layout and margins
- [ ] Header/footer content
- [ ] Table structures
- [ ] Page break positions
- [ ] Font sizes and families

### Step 2: Know Your PDF Engine

**On Frappe Cloud = wkhtmltopdf**

| Works | Doesn't Work |
|-------|--------------|
| `display: flex` | `display: grid` |
| `@page` counters | CSS Grid layout |
| `page-break-*` | `position: sticky` |
| Basic transforms | Complex animations |

### Step 3: Build Structure First
```html
<style>
@page {
    size: Letter;
    margin: 10mm;
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
    }
}
</style>

<div class="document-container">
    <div class="page-1-content">...</div>
    <div class="page-2-content" style="page-break-before: always;">...</div>
</div>
```

### Step 4: Test with Real Data
1. Create a test document with ALL fields populated
2. Generate PDF (not just preview)
3. Compare PDF to design requirements

### Step 5: Document Field Mappings
```jinja
{# Document this for future reference #}
{{ doc.name }}              {# SO-00754-Calipso s.r.l #}
{{ doc.customer_name }}     {# Calipso s.r.l #}
{{ doc.transaction_date }}  {# 2024-01-15 #}
```

---

## AMB Print Format Templates

### Sales Order (PEDIDO_VENTAS_AMB)
**DocType**: Sales Order
**Pages**: 3 (dynamic based on content)
**Key Features**:
- Dynamic page numbering via CSS
- Multi-section layout
- Automatic page breaks

### Quotation (Normal/Escalated)
**DocType**: Quotation
**Variants**: Canada-style, Woongjin
**Key Features**:
- Customer-specific branding
- Conditional sections

### TDS Product Specification
**DocType**: TDS Product Specification
**Key Features**:
- Technical data tables
- Product specifications grid

---

## Code Templates

### Basic Print Format Structure
```html
<style>
@page {
    @bottom-center {
        content: "Página " counter(page) " de " counter(pages);
        font-size: 9pt;
    }
}
.section { page-break-inside: avoid; }
.new-page { page-break-before: always; }
</style>

<div class="print-container">
    <!-- Header -->
    <div class="header">
        <img src="/files/logo.png" height="60">
        <div class="company-info">{{ doc.company }}</div>
    </div>
    
    <!-- Content -->
    <div class="content">
        <table>
            {% for item in doc.items %}
            <tr>
                <td>{{ item.item_code }}</td>
                <td>{{ item.qty }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    
    <!-- Footer handled by @page CSS -->
</div>
```

### Multi-Page Template
```html
<!-- Page 1: Main Info -->
<div class="page-1">
    <div class="main-title">DOCUMENT TITLE</div>
    <!-- Page 1 content -->
</div>

<!-- Page 2: Details (force new page) -->
<div class="page-2 new-page">
    <div class="main-title">DOCUMENT TITLE</div>
    <!-- Page 2 content -->
</div>
```

---

## Debugging Checklist

### Empty Field?
- [ ] Check field name spelling in Jinja
- [ ] Verify field exists in DocType
- [ ] Check if source document has data
- [ ] Use `{{ field or "N/A" }}` for defaults

### PDF Looks Wrong?
- [ ] Hard refresh browser (Ctrl+Shift+R)
- [ ] Generate actual PDF, not preview
- [ ] Check CSS compatibility with wkhtmltopdf
- [ ] Verify page-break CSS

### Page Numbers Wrong?
- [ ] Remove hardcoded page numbers from HTML
- [ ] Use CSS @page counters only
- [ ] Check PDF generator setting

---

## Version Control Strategy

### Export Print Format
```bash
# Via bench console
bench --site your-site export-fixtures \
    --doctype "Print Format" \
    --filters '{"name": "PEDIDO_VENTAS_AMB"}'
```

### File Structure in amb_print_app
```
amb_print/
├── print_format/
│   ├── pedido_ventas_amb/
│   │   ├── pedido_ventas_amb.json
│   │   └── pedido_ventas_amb.html
│   └── quotation_canada/
│       └── ...
└── fixtures/
    └── print_format.json
```

---

*Part of amb_print_app - AMB Wellness Print Format System*
*Last Updated: January 30, 2026*

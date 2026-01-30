# Lessons Learned: ERPNext Print Format Development

## Overview

This document captures lessons learned from developing print formats for AMB Wellness on Frappe Cloud, including:
- **Quotation Print Formats** (Canada-style, Woongjin/Escalated)
- **Sales Order Print Format** (PEDIDO_VENTAS_AMB)
- **TDS Product Specification**

---

## 1. PDF Engine Compatibility

### Frappe Cloud Limitation
**Critical**: Frappe Cloud does NOT support Chromium PDF backend (as of January 2026).

| Feature | wkhtmltopdf (Frappe Cloud) | Chromium (Self-hosted v16+) |
|---------|---------------------------|----------------------------|
| CSS3 Support | Limited | Full (grid, flexbox) |
| Speed | Slower | 2-3x Faster |
| @page counters | Works | Different syntax |
| Availability | Default | Not on Frappe Cloud |

### Recommendation
Always design for **wkhtmltopdf** first when targeting Frappe Cloud.

---

## 2. Page Numbering Best Practices

### DON'T: Hardcode Page Numbers
```html
<!-- BAD - Page numbers won't match actual PDF pages -->
<div class="main-title">PEDIDO DE VENTAS - Página 2</div>
```

### DO: Use CSS @page Counters
```css
@page {
    @bottom-center {
        content: "Página " counter(page) " de " counter(pages);
        font-size: 9pt;
    }
}
```

---

## 3. Empty Fields Investigation

### Problem
Fields appear empty in print preview (e.g., Contacto, Domicilio)

### Root Cause
1. Check the print format code - Is the field reference correct?
2. Check the source document - Does the document have data?

### Common Field Mappings (Sales Order)
```jinja
{{ doc.contact_display }}     {# Contact name #}
{{ doc.contact_phone }}       {# Phone number #}
{{ doc.shipping_address }}    {# Shipping address #}
{{ doc.transaction_date }}    {# Order date #}
```

### Lesson
Empty fields are often **data issues**, not code issues.

---

## 4. Page Break Control

```css
/* Force new page */
.page-2-section { page-break-before: always; }

/* Prevent splitting */
.section-wrapper { page-break-inside: avoid; }

/* Keep header with content */
.section-header { page-break-after: avoid; }
```

---

## 5. Testing Workflow

1. **Edit** in Print Format UI (use Ctrl+H for Find/Replace)
2. **Preview** with Ctrl+Shift+R to clear cache
3. **Generate PDF** - Click "Get PDF" (browser preview ≠ PDF output)

**The PDF is the final truth**

---

## 6. CSS for wkhtmltopdf

### Supported
```css
display: flex;
border: 1px solid #000;
background: linear-gradient(...);
```

### Problematic
```css
display: grid;        /* Limited */
position: sticky;     /* Not supported */
```

---

## Quick Reference

### Jinja Field Access
```jinja
{{ doc.name }}
{{ doc.customer_name }}
{{ frappe.format_date(doc.transaction_date, "dd/MM/yy") }}
{{ frappe.format_currency(doc.grand_total, doc.currency) }}
{{ value or "" }}
```

---

*Last Updated: January 30, 2026*

# Designing the Base Layout

## Desired Layout
+-----------------------------------------------------------+
|                     Top Navigation                         |
|-----------------------------------------------------------|
| Left Sidebar |               Main Section                 |
|              |                                           |
|              |                                           |
|              |                                           |
|              |                                           |
|              |-------------------------------------------|
|              |          Bottom Navigation                |
+-----------------------------------------------------------+


## Template Inheritance
```text
base.html
├── base_auth.html              (login, register)
└── base_layout.html             (four-region skeleton)
    ├── admin/base_admin.html     (admin nav)
    ├── staff/base_staff.html     (staff nav)
    └── trekker/base_trekker.html (trekker nav)
```
- `base.html`: root template, `<head>` tags, CDN links only.
- `base_auth.html`: simple centered card, for login/register only.
- `base_layout.html`: the four-region skeleton, no role content.
- `base_admin.html` / `base_staff.html` / `base_trekker.html`: fills 
  in that role's sidebar and top-nav links. Every page for a role 
  extends this, not `base_layout.html` directly.
- Individual pages: extend their role's base file, supply only page 
  title and main content.

## The Four Regions
```text
#screen (column flex, 100vh)
├── #top-navigation (fixed height)
└── #main-body (row flex, flex: 1)
    ├── #left-navigation (fixed width)
    └── #right-section (column flex, flex: 1)
        ├── #main-section (flex: 1, overflow-y: auto)
        └── #bottom-navigation (fixed height)
```
Only `#main-section` scrolls.

## Decisions

### Plain flexbox, not Bootstrap grid, for the skeleton
- Bootstrap's row/col grid fights fixed-region + single-scroll 
  layouts.
- Bootstrap grid IS used elsewhere (e.g. dashboard stat cards), since 
  equal-width responsive cards is what it's actually built for.

### `flex: 1`, not `height: 100%`
- `height: 100%` needs the parent's height to be directly resolvable; 
  breaks when the parent's height came from flex math instead.
- `flex: 1` is flexbox's native mechanism and composes reliably.

### `min-height: 0` on every nested flex container
- Flex items default to `min-height: auto` (never shrink below 
  content). This silently overrides `flex: 1` and `overflow-y: auto` 
  once content is large enough.
- Bug only appeared once a page had enough content to expose it — 
  worked fine on the dashboard's small preview table, broke on the 
  full treks list.

### `html, body { height: 100%; overflow: hidden; }`
- Without it, `<body>` can grow past the viewport and the browser's 
  own scrollbar appears, regardless of how correct the inner flex 
  chain is.

### `.list-page-wrapper` / `.list-table-wrapper`
- Reusable pair for full list pages: heading takes natural size, 
  table takes `flex: 1` + its own scroll.
- Not used on detail pages (multiple sections, no single dominant 
  table) or the dashboard's preview table (deliberately capped, not 
  "fill remaining space").

## Avoided
- Bootstrap's `navbar`/`nav-pills` for sidebar/top-nav — hand-written 
  CSS instead, so every rule is fully understood, not just applied.
- Inline CSS — centralized in `base_layout.html`'s `<style>` block, 
  with a few pragmatic one-off exceptions (`style="display:inline;"` 
  on single-button forms).

## Process
Plain-English structure first, then built one flex property at a 
time, testing visually after each step. Bugs diagnosed with temporary 
colored borders on invisible boxes, and by swapping subtle colors for 
loud ones to confirm a rule was actually applying.
# CLAUDE.md

## What this repo is

Hugo extended static site for **Casaway** (casaway.it) — Federico Maggi's short-term rental property business. Bilingual (EN default, IT). Builds and deploys to GitHub Pages on push to `main`.

## Lodgings

Three top-level entries under `content/lodgings/`. The Vimercate one is a **branch bundle** with two child leaf bundles; the other two are leaf bundles.

```
content/lodgings/
├── studio-apartments-vimercate-city-center/        ← branch bundle (_index.*.md)
│   ├── guide/house-guide-vimercate.pdf
│   ├── large-studio-apartment-vimercate-city-center/   alias: /apt703
│   └── studio-apartment-vimercate-city-center/         (no alias)
├── san-francesco-apartment-oreno-vimercate/        ← leaf bundle, alias: /apt2
│   └── guide/house-guide-oreno.pdf
└── langhe-vacation-house/                          ← leaf bundle, alias: /nocciolina
    └── guide/nocciolina-house-guide{,-hr}.pdf
```

Booking targets: Vimercate + Oreno → Airbnb. Langhe house → `nocciolina.net`.

## How the homepage renders

`layouts/_default/home.html` iterates `Pages` under `lodgings` and handles two cases:

- **Section page** (e.g. Vimercate studios): aggregates images and booking buttons from each child leaf bundle. The section's location/subtitle/copy comes from `_index.*.md`; each child contributes its own "Book now" button via `linkTitle` + `airbnb`.
- **Single page**: renders that page's images and booking button directly.

The **hero carousel** pulls the first 3 images from every lodging (or child of a section). The **per-property gallery grid** indexes images 1–5 from the section's aggregated set. Practical minimum: ≥6 images per leaf bundle (or per child, for sectioned lodgings).

## Tech stack

| Concern | Tool |
|---------|------|
| SSG | Hugo extended — CI pins **v0.147.1** (`.github/workflows/hugo.yml`) |
| CSS framework | Bootstrap 5.3 (CDN) |
| Icons | Font Awesome 6.4, Bootstrap Icons 1.10 |
| Fonts | Google Fonts: Lato + Spinnaker |
| Gallery | Fancybox 5 (CDN) |
| Slider | Slick Carousel 1.9 (CDN) — testimonials |
| Custom CSS | `static/css/style.css`, `static/css/responsive.css` (prefix `thmv-`) |
| CI/CD | GitHub Actions → GitHub Pages |
| Local CI | `act` |

`/public/` and `/resources/_gen/` are gitignored. Never commit build output.

## Common commands

```bash
hugo server                       # local dev (live reload, port 1313)
hugo --gc --minify                # production build to ./public
hugo --printI18nWarnings          # find missing translations
act                               # run the GH Actions workflow locally
```

If local Hugo is newer than the pinned CI version, behavior on prod may differ — match the CI version (`HUGO_VERSION` in `.github/workflows/hugo.yml`) before debugging anything build-related.

## Project layout

```
hugo.yaml               # site config: languages, menus (main + footer_lodgings), params
archetypes/             # `hugo new` templates
content/
  _index.{en,it}.md     # homepage copy + pricing section
  lodgings/_index.*.md  # section landing (mostly title)
  lodgings/<slug>/      # leaf or branch bundle (see above)
i18n/{en,it}.yaml       # T-strings (book_now, contact_us, modern_stays, ...)
data/{en,it}/
  amenities.yaml        # services list + amenities icon grid
  reviews.yaml          # testimonials
layouts/
  _default/
    baseof.html
    home.html           # the bulk of the homepage logic
    single.html         # trivial — just renders .Content
    list.html, page.html
  partials/             # header, footer, gmap, amenities, review, service, top-nav, meta, ...
static/                 # css/, img/, favicons, site.webmanifest
assets/images/          # Hugo Pipes inputs
scripts/                # one-off helpers (e.g. fix-image-name.sh)
.github/workflows/hugo.yml
```

## Front matter (property pages)

```yaml
title:        # full page title; also the section heading for sectioned lodgings
linkTitle:    # short label used in booking buttons
name:         # used as urlized anchor ID (homepage section)
location:     # pill badge text
subtitle:     # large heading above the property copy
weight:       # ordering
gmap:         # full Google Maps embed src URL
airbnb:       # booking URL (may point to Airbnb OR an external site like nocciolina.net)
aliases:      # Hugo aliases for short URLs (e.g. /apt2, /apt703, /nocciolina)
```

`CIR` registration numbers (Italian short-let licensing) are rendered as **bold inline text in the body**, not front matter.

## Content conventions

- Bilingual: every content file exists as `*.en.md` AND `*.it.md`. The IT version is mandatory — the build prints placeholders for missing translations (`enableMissingTranslationPlaceholders: true`).
- Page-bundle assets:
  - `images/` — auto-processed by Hugo to WebP via `Fill` / `Resize`
  - `guide/` — PDF house guides, shipped as-is via page bundle
- Adding a new property:
  1. Decide leaf vs. branch bundle (branch only if there are sub-units sharing a location).
  2. Drop ≥6 images into `images/`, even-named (the gallery indexes 0–5).
  3. Set `title`, `linkTitle`, `name`, `location`, `subtitle`, `gmap`, `airbnb`, optional `aliases`.
  4. Mirror the file in `.it.md`.
  5. Add the property to both `languages.en.menu` and `languages.it.menu` in `hugo.yaml` (both `main` and `footer_lodgings`).
- Data-driven blocks: add amenities/reviews to BOTH `data/en/` and `data/it/`.
- i18n: add new `{{ T "key" }}` strings to BOTH `i18n/en.yaml` and `i18n/it.yaml`.

## Deployment

Push to `main` → GH Actions installs Hugo extended + Dart Sass → `hugo --gc --minify --cacheDir <tmp>` → uploads `./public` → deploys to GitHub Pages. `baseURL` is `https://casaway.it/` (set in `hugo.yaml`).

## Site params (in `hugo.yaml`)

- Email: `info@casaway.it`
- Phone (WhatsApp only): `https://wa.me/message/R2AKZF4C64OZL1` → +39 039 6360500
- Airbnb profile: `https://www.airbnb.com/users/show/181969055`
- Default content language: `en`. Italian lives at `/it/`.

Each language has its own `params` block (name, motto, subtitle, logo, description, disclaimer, phone, email, airbnb).

## Editing guidelines

- Never commit `/public/` or `/resources/_gen/`.
- Don't reorder/rename `thmv-` CSS classes — they're tightly coupled to `style.css` and the partials.
- Keep `hugo.yaml` menus in sync between `en` and `it`.
- When adding new front matter fields to a property, update `layouts/_default/home.html` if the template needs to consume them (single.html is a no-op pass-through).
- Aliases produce HTML redirect stubs — handy for legacy short URLs (`/apt2`, `/nocciolina`); add new ones the same way.
- `linkTitle` is what guests see on the booking buttons — keep it brand-consistent.

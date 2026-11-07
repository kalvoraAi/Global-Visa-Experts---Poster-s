# Global Visa Experts — Brand Kit

Only use the real details below on posters. Never add a guessed phone number,
website or email: a wrong number sends real customers nowhere.

## Logo

| File | Use on |
|---|---|
| [`logo/gve-logo.png`](logo/gve-logo.png) | White / light backgrounds (navy + orange, transparent) |
| [`logo/gve-logo-white.png`](logo/gve-logo-white.png) | Dark / colour backgrounds (white + orange, transparent) |
| [`logo/gve-logo-original.webp`](logo/gve-logo-original.webp) | Original file as supplied |

- Tagline: **Where Dreams Take Flight.**
- Logo colours: navy `#0A2547`, orange `#F77123`

## Contact details

| Item | Value |
|---|---|
| Company name | Global Visa Experts (GVE) |
| Phone | +91 93424 93425 |
| Phone | +91 95819 93949 |
| Email | TODO |
| Website | TODO |
| Instagram / socials | TODO |

## Office locations

| City | Address |
|---|---|
| Vijayawada | Above Reflections Store, MG Road |
| Guntur | Opp HDFC Bank, Lakshmipuram Main Road |

## Colours

| Scheme | Background | Accent | Text |
|---|---|---|---|
| Royal blue | `#1E3FA8` → `#0F2370` | Yellow `#FFC727` | White |
| Crimson | `#B3123A` → `#6E0B2A` | Yellow `#FFC727` | White |
| Teal | `#0E9AA7` → `#0B5E73` | Yellow / white | White |
| Clean white | `#FFFFFF` + `#EAF2FF` shapes | Royal blue `#1E3FA8` | Navy `#0B1F4D` |

Defined as CSS variables in [brand.css](brand.css). Use class `royal`, `crimson`,
`teal` or `white` on `.canvas`.

## Fonts — always use only these

Matched from the approved "Study in UK" poster. Files are in `brand/fonts/`
(free Google Fonts, OFL licence) and load automatically via `brand.css`.

| Font | CSS | Use for | Weights |
|---|---|---|---|
| **Montserrat** | `var(--font-brand)` | "GLOBAL VISA EXPERTS" header, phone numbers, "Apply Now" button | 700–800 |
| **Poppins** | `var(--font-display)` | Big headline ("UK"), course names ("Artificial Intelligence") | 700–900 |
| **Poppins** | `var(--font-body)` | Bullets, addresses, "Bachelor's • Master's", spaced labels ("AVAILABLE COURSES", "WHY UK") | 400–600 |
| **Kaushan Script** | `var(--font-script)` / `.script` | Brush script line ("Study In") | 400 |
| **Playfair Display Italic** | `var(--font-serif)` / `.serif` | Gold accent words ("MSc", "Jan") | 500–700 |

Spaced labels: Poppins 600, uppercase, letter-spacing ~6px, gold `#E8C26A`
(class `.label`).

## Copy rules

- Never promise "100% visa" or "guaranteed approval". Embassies decide.
- OK: "expert guidance", "high success rate", "free consultation".
- Client photos ("visa approved" posts) need the client's written permission.

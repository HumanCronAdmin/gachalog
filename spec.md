# GachaLog - Notion Template Spec

## Overview
Japanese toy collection tracker template for Notion.
Target: gashapon, figures, ichiban kuji, blind boxes, shokugan.

## Database Structure

### DB1: Series
| Property | Type | Description |
|---|---|---|
| Series Name | Title | e.g. "Animal Kitchen" |
| Maker | Select | Bandai, Takara Tomy, Epoch, etc. |
| Category | Select | Gashapon / Figure / Ichiban Kuji / Blind Box / Shokugan / Other |
| Total Items | Number | Total pieces in series |
| Owned Count | Rollup | Count from Items DB |
| Completion | Formula | Owned / Total as % |
| Release Date | Date | |
| Status | Formula | Complete / In Progress / Wishlist |
| Notes | Text | |

### DB2: Items
| Property | Type | Description |
|---|---|---|
| Item Name | Title | e.g. "Shiba Inu Chef" |
| Series | Relation | -> Series DB |
| Photo | Files | User uploads |
| Status | Select | Owned / Wanted / Trading / Sold |
| Rarity | Select | Normal / Secret / Limited |
| Acquired Date | Date | |
| Acquired From | Select | Store / Online / Trade / Gift |
| Price | Number | JPY or USD |
| Condition | Select | Mint / Good / Fair |
| Duplicate | Checkbox | |
| Notes | Text | |

### DB3: Wishlist (filtered view of Items where Status = Wanted)

## Views (Items DB)
1. **Gallery** - Photo gallery catalog view
2. **By Series** - Grouped by series relation
3. **Wishlist** - Filter: Status = Wanted
4. **Trade Board** - Filter: Status = Trading OR Duplicate = true
5. **Timeline** - By acquired date

## Views (Series DB)
1. **All Series** - Table with completion bars
2. **By Category** - Board grouped by category
3. **Complete** - Filter: Completion = 100%

## Dashboard (top page)
- Inline: Series DB (completion view)
- Inline: Items DB (gallery view, last 8 added)
- Callout: Quick stats summary
- Callout: "Recently Added" highlight

## Design
- Color scheme: Match LP palette (pastels, warm)
- Cover image: Provided separately
- Icons: Capsule emoji for series, star for items
- Language: English (all property names)

## Deliverable
- Notion page with template duplicate enabled
- Public link for Gumroad delivery

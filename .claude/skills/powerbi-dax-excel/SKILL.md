---
name: powerbi-dax-excel
description: Use whenever the task involves Power BI, DAX measures/calculated columns, Excel Power Pivot data modeling, pivot tables, or building a business-facing report/dashboard from a data model. Trigger on "measure," "DAX," "Power BI," "pivot table," "date table," "YoY," "budget vs actual," or any request to turn a dataset into a report a non-technical stakeholder will read — even if the user just says "can you build me a dashboard" without naming the tool. For the visual/chart design itself (color, layout, what chart type to use) pair this with the dataviz skill; this skill covers the data-model and DAX side.
---

# Power BI, DAX & Excel

BI-layer knowledge: how to model data for reporting and write DAX that holds up, not just
one-off formulas. Pair with **dataviz** for the visual design of the report itself.

## The data model comes first — DAX is only as good as the model underneath it

A Power BI/Power Pivot report needs a proper **star schema**, not a single flat table:
- One or more **fact tables** (the transactional data — sales, finance actuals) with
  foreign keys to dimensions and numeric measures.
- **Dimension/lookup tables** (Accounts, Products, Geography, and always a **Date table**)
  with unique keys, joined to the fact table by relationship.
- Fewer columns in each table = faster calculations — don't import every column "just in
  case"; import what the report actually needs (see `sql-data-engineering`'s star-schema
  section for the same idea from the database side).

**Every model needs a dedicated Date table** for time-intelligence DAX functions
(`TOTALYTD`, `DATEADD`, `SAMEPERIODLASTYEAR`) to work. Build it once, mark it as the
official Date table (Modeling → Mark as Date Table, on a column with unique contiguous
dates), and reuse it across every report:

```dax
Fiscal Year = "FY" & RIGHT(INT((MONTH([Date])-1)/[FYE]) + YEAR([Date]), 4)
Fiscal Quarter = [Fiscal Year] & "-Q" & FORMAT(INT((MOD(MONTH([Date])+[FYE]-1,12)+3)/3), "0")
Month Name = FORMAT([Date], "MMM")
```
(`FYE` = the month your fiscal year ends on, as a measure/parameter — adjust the formulas
above if the fiscal year doesn't start in January.)

## Measures vs. calculated columns — pick correctly, it matters for performance

- **Calculated column**: computed once per row, at refresh time, stored in the table.
  Use for something that needs to be a *row-level* attribute you can filter/group by
  (e.g., a Fiscal Year label on the Date table).
- **Measure**: computed on the fly, per query, in the current filter context. Use for
  anything aggregated (sums, ratios, YoY comparisons) — this is almost everything in a
  report. Measures are lighter on model size and correctly respond to slicers/filters;
  calculated columns don't recompute per-view.

Default to a measure unless you specifically need the value as a filterable row attribute.

## DAX patterns that cover most real reports

```dax
-- Base aggregation measure — build these first, everything else composes from them
Actual Sum := SUM('Finance Data'[Actual])
Budget Sum := SUM('Finance Data'[Budget])

-- Prior period comparison — CALCULATE + DATEADD shifts the filter context in time
Prior Year Actual := CALCULATE([Actual Sum], DATEADD('Date'[Date], -1, YEAR))
Prior Quarter Actual := CALCULATE([Actual Sum], DATEADD('Date'[Date], -1, QUARTER))

-- Year-over-year change and its percentage
YoY := [Actual Sum] - [Prior Year Actual]
YoY % := IF([Prior Year Actual], [YoY] / ABS([Prior Year Actual]), BLANK())
-- Watch sign convention: for revenue accounts a rise vs. prior year should read
-- positive; for expense accounts it usually should read negative (spending more is
-- bad) — decide the sign convention explicitly per account type, don't assume.

-- Variance to budget
VTB Sum := [Budget Sum] - [Actual Sum]
VTB % := IF([Budget Sum], [VTB Sum] / ABS([Budget Sum]), BLANK())

-- Year-to-date / quarter-to-date
YTD Actual := TOTALYTD([Actual Sum], 'Date'[Date])
QTD Actual := TOTALQTD([Actual Sum], 'Date'[Date])

-- Always guard division with IF/DIVIDE to avoid a blank report from a divide-by-zero
Attainment % := DIVIDE([Actual Sum], [Budget Sum])   -- DIVIDE returns BLANK() on /0, cleaner than IF
```

Build measures in layers: base sums → prior-period versions → variance/YoY versions that
reference the earlier measures, rather than writing one giant nested formula each time.
It's easier to debug and every report ends up needing the same base measures anyway.

## Common gotchas

- **CALCULATE is the one function that changes filter context** — almost every
  time-intelligence or "ignore a filter" pattern (`ALL()`, `ALLEXCEPT()`) runs through it.
  If a measure isn't responding to a slicer the way you expect, look for a missing or
  misplaced `CALCULATE`.
- **Implicit vs explicit measures**: dragging a raw column into a visual creates an
  implicit `SUM`/`COUNT` you can't reuse or debug well — always create named, explicit
  measures instead, even for a simple sum.
- **BLANK() vs 0**: a measure that returns `BLANK()` for a row with no data is usually
  right (it won't show as a spurious zero on a chart); explicitly guard divisions so they
  return `BLANK()` on `/0` rather than erroring the whole visual.

## Excel Power Pivot specifics

Power Pivot is the same DAX engine embedded in Excel — everything above applies. To get
data in: **Power Pivot → Get External Data → From Database/From Other Sources**, choose
only the tables/columns actually needed, and set each column's data type explicitly
(Power Pivot requires one consistent type per column). Pivot Tables built on the model
read both raw columns and defined measures from the **PivotTable Fields** list — build
the measures in Power Pivot first, then drag them into pivots, not the other way around.

## Where this hands off

- Chart type, color, and layout for the finished report → **dataviz** skill — load it
  before finalizing visuals, not after.
- Where the data comes from (the query/pipeline feeding the model) →
  **sql-data-engineering** skill.
- Framing what the report should actually answer for the business → **data-business-strategy**.

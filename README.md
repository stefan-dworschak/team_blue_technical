# Design Thinking

## Setup & Run

This project uses [`uv`](https://docs.astral.sh/uv/) as the package manager and runner. Only the
Python standard library is used for application code — `uv` handles the dev environment.

### Prerequisites

- Python 3.12+
- `uv` installed (see [installation guide](https://docs.astral.sh/uv/getting-started/installation/))

### Install dependencies

```bash
uv sync
```

### Run the tests

```bash
uv run pytest
```

### Exercise 1 — Generate the IP traffic report

Place the input log at `logfiles/requests.log`, then run:

```bash
uv run python report_generator.py
```

The report is written to `reports/ipaddress.csv`. The output format is inferred from the file
extension, so passing a `.json` filename will produce JSON output instead.

### Exercise 2 — Array-based multiplication

`array_multiplier.py` exposes the `ArrayNumber` and `ArrayMultiplier` classes. The CLI provides
two subcommands:

```bash
# Compute n!
uv run python array_multiplier.py factorial 100

# Multiply two non-negative integers
uv run python array_multiplier.py multiply 123 456
```

---

## Exercise 1 — IP Address Traffic Report

### Problem Analysis

The task requires reading a semicolon-delimited log file, filtering records, aggregating by IP, and
producing a sorted report in CSV or JSON format.

### Architecture

I split the solution into two classes with distinct responsibilities:

- **`LogParser`** — handles file I/O and parsing. Each line is split by `;`, validated for the
  correct number of fields, and filtered by status, in a single linear pass over the input.
  The status filter is configurable via the constructor, defaulting to `"OK"`.

- **`ReportGenerator`** — handles aggregation and output formatting. The `aggregate()` method
  builds a `dict[str, IPTrafficSummary]` mapping IP addresses to their running totals in a single
  linear pass. Totals for requests and bytes are tracked inline to avoid a second pass. Percentages
  are computed once after aggregation, then the result is sorted by request count descending.

### Key Decisions

- **`IPTrafficSummary` dataclass** — aggregation writes directly into `IPTrafficSummary` instances stored in
  the dict. This avoids an intermediate `list[int]` representation and a separate construction
  step, keeping the code cleaner and the data self-documenting.

- **Separation of concerns in formatting** — `to_csv()` and `to_json()` receive fully computed
  `IPTrafficSummary` objects and only handle serialisation. No business logic lives in the formatters,
  so adding a new output format requires only a new formatting method.

- **No csv/io modules** — CSV output uses simple string concatenation with f-strings. For this
  use case the data contains no commas or special characters that would need escaping, so the
  stdlib `csv` module adds overhead without benefit.

## Exercise 2 — Array-Based Multiplication

### Problem Analysis

Multiply integers using only single-digit addition, with digits stored in arrays. Must handle
100! which is 158 digits long.

### Architecture

- **`ArrayNumber`** — wraps a `list[int]` of digits in big-endian order (most significant first).
  Supports `from_int()` for construction, `__add__` for addition, `__str__` for display, and
  `__eq__` for comparison. Addition reverses both digit lists, walks them with a carry, and
  reverses the result.

- **`ArrayMultiplier`** — implements long multiplication using only addition. For each digit `d`
  at position `p` in the multiplier, the multiplicand is shifted left by `p` positions (appending
  zeros) and added `d` times to the running result. This mirrors pencil-and-paper multiplication.

### Key Decisions

- **Big-endian storage** — digits are stored most-significant-first for natural display. Addition
  internally reverses to work from least-significant, which is standard for carry propagation.

- **No Python `*` operator** — the constraint says "using addition only". The `*` operator is not
  used anywhere in the multiplication logic. Division/modulo (`//`, `%`) are used only for
  carry propagation within single-digit addition (splitting a two-digit sum into digit + carry),
  which is a necessary primitive.

- **Shift via zero-padding** — instead of tracking position offsets, shifting is done by appending
  zeros to the digit list. This keeps the implementation simple.

### Why not Karatsuba or FFT?

The exercise specifically asks to use addition for multiplication. Karatsuba and FFT-based
approaches optimise the multiplication step but don't satisfy the "addition only" constraint.
The long-multiplication-via-addition approach is the natural fit and handles 100! comfortably.

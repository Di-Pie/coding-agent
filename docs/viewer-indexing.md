# Viewer Indexing

## Core Rule

> Pick one coordinate system for calculations. Convert only at input and
> output boundaries.

The viewer accepts human-facing, 1-based line numbers, but performs all
internal calculations with Python's zero-based, half-open intervals:

```text
[start_index, stop_index)
```

`start_index` is included; `stop_index` is excluded. This matches Python list
slicing exactly:

```python
visible_lines = lines[start_index:stop_index]
```

## Coordinate Systems

```text
Human line:    1  2  3  4  5
Python index:  0  1  2  3  4
```

Convert between them only at the system boundary:

```python
index = line_number - 1
line_number = index + 1
```

Use names that make the coordinate system explicit:

```python
target_line_number  # 1-based, external
target_index        # 0-based, internal
start_index         # 0-based and included
stop_index          # 0-based and excluded
```

Avoid `end_index`, because it does not reveal whether the end is included or
excluded.

## Understanding One Slice

Suppose a ten-line file must display human lines 4 through 7:

```text
Human line:    1  2  3  4  5  6  7  8  9 10
Python index:  0  1  2  3  4  5  6  7  8  9
```

The first displayed line has index:

```python
start_index = 4 - 1  # 3
```

Human line 7 has index 6, but the slice must stop one position after the last
included index:

```python
stop_index = 6 + 1  # 7
```

Therefore, `lines[3:7]` selects indices `3, 4, 5, 6`, corresponding to human
lines `4, 5, 6, 7`. The number of selected elements is always:

```python
visible_count = stop_index - start_index
```

## SWE-agent Target Placement

Following the SWE-agent implementation, the desired number of displayed lines
before the requested line is:

```python
lines_before_target = ceil(window_size / 6)
```

For a positive integer window size, ceiling division can be written without
floating-point arithmetic:

```python
lines_before_target = (window_size + 5) // 6
```

For `window_size = 100`, this produces 17. Therefore, when neither file
boundary affects the window, 17 lines precede the target and the target is the
18th displayed line. The offset means "lines before the target," not "the
target's 1-based display position."

This location is an ACI design choice rather than a mathematical necessity. We
use it to reproduce SWE-agent's behavior.

## Calculating and Clamping a Window

First convert the requested line and calculate the desired start:

```python
target_index = line_number - 1
lines_before_target = (window_size + 5) // 6
desired_start = target_index - lines_before_target
```

The window cannot start before index 0. Its last possible full-window start is
`total_lines - window_size`. If the file is shorter than the window, that
value is negative, so clamp it to zero:

```python
max_start = max(0, total_lines - window_size)
start_index = min(max(desired_start, 0), max_start)
```

Finally, calculate the exclusive stop without passing the end of the file:

```python
stop_index = min(start_index + window_size, total_lines)
visible_lines = lines[start_index:stop_index]
```

The full calculation is:

```python
target_index = line_number - 1
lines_before_target = (window_size + 5) // 6

desired_start = target_index - lines_before_target
max_start = max(0, total_lines - window_size)

start_index = min(max(desired_start, 0), max_start)
stop_index = min(start_index + window_size, total_lines)

visible_lines = lines[start_index:stop_index]
```

### Concrete Viewer Example

Assume:

```text
total_lines = 250
window_size = 100
line_number = 50
```

Then:

```python
target_index = 50 - 1                         # 49
lines_before_target = (100 + 5) // 6          # 17
desired_start = 49 - 17                       # 32
max_start = max(0, 250 - 100)                 # 150
start_index = min(max(32, 0), 150)            # 32
stop_index = min(32 + 100, 250)               # 132
```

The slice `lines[32:132]` contains indices 32 through 131, which correspond to
human lines 33 through 132. Human line 50 is the 18th displayed line.

Near the beginning or end of the file, clamping changes the target's displayed
position. A target near the beginning cannot have 17 real lines before it, and
the final file line appears at the bottom of the last complete window.

## Lines Above and Below

Think of the complete file as three adjacent half-open intervals:

```text
0                                  total_lines
|-------------------------------------------|
|      above     |    visible    |   below  |
|----------------|---------------|----------|
0          start_index      stop_index      N

above   = [0, start_index)
visible = [start_index, stop_index)
below   = [stop_index, total_lines)
```

Their lengths follow directly from interval subtraction:

```python
lines_above = start_index
visible_count = stop_index - start_index
lines_below = total_lines - stop_index
```

`start_index` is included in the visible window. It also equals the number of
elements before the window because the preceding indices are
`0 .. start_index - 1`.

`stop_index` is not included in the visible window. It is the first index in
the region below the window, so `total_lines - stop_index` is the number of
remaining lines.

A potentially confusing numerical coincidence is that `stop_index` equals the
1-based line number of the last displayed line. For example, human line 10 has
index 9 and a slice that includes it stops at index 10. Index 10 itself is not
displayed.

## Correctness Invariants

Do not rely only on mental simulation. Check properties that must always hold:

```python
assert 0 <= start_index <= stop_index <= total_lines
assert len(visible_lines) == stop_index - start_index
assert lines_above == start_index
assert lines_below == total_lines - stop_index
assert lines_above + len(visible_lines) + lines_below == total_lines
```

When the file is at least as large as the window:

```python
if total_lines >= window_size:
    assert len(visible_lines) == window_size
```

When a valid target was supplied:

```python
assert start_index <= target_index < stop_index
```

Test at least these cases:

- An empty file.
- A file shorter than the window.
- A file exactly as long as the window.
- A file longer than the window.
- A target at the first line.
- A target in the middle.
- A target at the last line.
- Invalid targets before and after the valid range.

## Repeatable Problem-Solving Process

When facing similar indexing problems:

1. Write down the external coordinate system.
2. Convert external values to zero-based indices immediately.
3. Represent ranges as `[start, stop)`.
4. Calculate the desired range without considering boundaries.
5. Clamp the range to valid boundaries as a separate step.
6. Derive counts from interval lengths instead of converting back to line
   numbers.
7. Convert indices back to human-facing numbers only for display.
8. Verify the result with a small numbered example and invariants.

Using a concrete example is not a workaround; it is the correct debugging
technique. The goal is not to mentally remember every `+1` and `-1`. The goal
is to use one internal representation so those conversions occur only at
explicit boundaries.

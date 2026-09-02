# Viewer Indexing

## A Systematic Indexing Method

The key rule is:

> Pick one coordinate system for calculations. Convert only at input and
> output boundaries.

For Python, use zero-based, half-open intervals internally because that is
exactly how lists and slices work.

## 1. Name the Two Coordinate Systems

Human-facing line numbers:

```text
1, 2, 3, 4, 5
```

Python indices:

```text
0, 1, 2, 3, 4
```

Their relationship is always:

```python
index = line_number - 1
line_number = index + 1
```

Use variable names that expose the coordinate system:

```python
target_line_number  # 1-based
target_index        # 0-based
start_index         # 0-based, included
stop_index          # 0-based, excluded
```

Avoid ambiguous names such as `end_index`: does "end" mean included or
excluded?

## 2. Understand One Concrete Slice

Suppose a real file has ten lines:

```text
Human line:    1  2  3  4  5  6  7  8  9 10
Python index:  0  1  2  3  4  5  6  7  8  9
```

We want human lines 4-7.

Convert line 4 to its index:

```python
start_index = 4 - 1  # 3
```

Line 7 has index 6, but Python's slice stop must point one position after the
last wanted element:

```python
stop_index = 7
```

Therefore:

```python
lines[3:7]
```

selects indices:

```text
3, 4, 5, 6
```

which correspond to human lines:

```text
4, 5, 6, 7
```

The number selected is always:

```python
stop_index - start_index  # 7 - 3 = 4
```

## 3. Apply It to the Viewer

Assume:

```text
total lines N = 12
window size W = 4
requested line = 8
offset = 1
```

Convert the requested line immediately:

```python
target_index = 8 - 1  # 7
```

Calculate where we want the window to start:

```python
desired_start = target_index - offset  # 6
```

The last possible start of a four-line window is:

```python
max_start = N - W  # 12 - 4 = 8
```

Clamp the desired start:

```python
start_index = min(max(desired_start, 0), max_start)
# min(max(6, 0), 8) = 6
```

Calculate the exclusive stop:

```python
stop_index = min(start_index + W, N)
# min(6 + 4, 12) = 10
```

The slice is:

```python
lines[6:10]
```

That selects indices 6-9, corresponding to human lines 7-10:

```text
7: ...
8: ...  <- requested line
9: ...
10: ...
```

The surrounding counts follow directly:

```python
lines_above = start_index          # 6
lines_below = N - stop_index       # 2
```

Check the accounting:

```text
6 above + 4 visible + 2 below = 12 total
```

## 4. Use Invariants Instead of Intuition

After calculating a window, these must always be true:

```python
assert 0 <= start_index <= stop_index <= total_lines
assert stop_index - start_index <= window_size
assert lines_above + len(lines_content) + lines_below == total_lines
```

If the file is at least as large as the window:

```python
if total_lines >= window_size:
    assert len(lines_content) == window_size
```

If a target line was supplied:

```python
target_index = line_number - 1
assert start_index <= target_index < stop_index
```

These assertions catch the exact mistakes encountered while implementing the
viewer.

## If the Current 1-Based Implementation Is Retained

The current conversion is correct:

```python
start_index = start_line - 1
end_index = end_line
lines[start_index:end_index]
```

Why is there no `-1` for `end_line`?

`end_line` is a 1-based inclusive line number, while Python needs a 0-based
exclusive stop:

```text
inclusive line 7
-> zero-based index 6
-> exclusive stop 7
```

The two conversions cancel:

```text
stop_index = (end_line - 1) + 1
           = end_line
```

This is correct, but it is cognitively difficult. Using zero-based
`start_index` and `stop_index` throughout makes the reasoning easier.

Using a real file or numbered example is the right debugging method. Draw the
two rows, calculate one slice manually, and then enforce the general properties
with tests. Do not rely on mentally juggling `+1` and `-1`.

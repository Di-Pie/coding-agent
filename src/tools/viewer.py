"""Stateful file-viewer tools."""

from agent_protocol import Observation

from .context import ToolContext, ToolPathError


def _failed_open(error: Exception | str) -> Observation:
    """Return an expected open failure in the tool-result format."""
    return Observation(
        output="",
        success=False,
        truncated=False,
        terminal=False,
        error=f"open: {error}",
    )


def open_file(
    context: ToolContext,
    path: str,
    line_number: int | None = None,
) -> Observation:
    """Open a file and display a configured window around an optional line."""

    try:
        resolved_path = context.resolve_path(path)
        if not resolved_path.exists():
            raise ToolPathError(f"file does not exist: {resolved_path}")
        if not resolved_path.is_file():
            raise ToolPathError(f"path is not a regular file: {resolved_path}")

        content = resolved_path.read_text(encoding="utf-8")
    except (ToolPathError, OSError, UnicodeError) as error:
        return _failed_open(error)

    lines = content.splitlines()
    total_lines = len(lines)

    if line_number is not None and not 1 <= line_number <= total_lines:
        return _failed_open(
            f"line_number must be between 1 and {total_lines}: {line_number}"
        )

    start_index = 0
    if line_number is not None:
        target_index = line_number - 1
        offset = (context.window_size + 5) // 6
        desired_start = target_index - offset
        max_start = max(0, total_lines - context.window_size)
        start_index = min(max(desired_start, 0), max_start)

    stop_index = min(start_index + context.window_size, total_lines)
    visible_lines = lines[start_index:stop_index]
    lines_above = start_index
    lines_below = total_lines - stop_index

    output_lines = [f"[File: {resolved_path} ({total_lines} lines total)]"]

    if lines_above > 0:
        output_lines.append(f"({lines_above} more lines above)")

    # Keep line numbers padded so the file contents align vertically.
    line_number_width = len(str(stop_index))
    output_lines.extend(
        f"{number:{line_number_width}d}:{line}"
        for number, line in enumerate(visible_lines, start=start_index + 1)
    )

    if lines_below > 0:
        output_lines.append(f"({lines_below} more lines below)")

    output_text = "\n".join(output_lines)

    context.open_file = resolved_path
    context.window_start = start_index + 1

    truncated = len(output_text) > context.max_output_chars
    if truncated:
        output_text = output_text[:context.max_output_chars]

    return Observation(
        output=output_text,
        success=True,
        truncated=truncated,
        terminal=False,
    )


def goto(context: ToolContext, line_number: int) -> Observation:
    """Move the current file window to include a line number."""
    raise NotImplementedError


def scroll_down(context: ToolContext) -> Observation:
    """Move the current file view down by one configured window."""
    raise NotImplementedError


def scroll_up(context: ToolContext) -> Observation:
    """Move the current file view up by one configured window."""
    raise NotImplementedError

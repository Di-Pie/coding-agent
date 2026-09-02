"""Stateful file-viewer tools."""

from pathlib import Path

from agent_protocol import Observation

from .context import ToolContext, ToolPathError


def _failed_view(tool_name: str, error: Exception | str) -> Observation:
    """Return an expected viewer failure in the tool-result format."""
    return Observation(
        output="",
        success=False,
        truncated=False,
        terminal=False,
        error=f"{tool_name}: {error}",
    )


def _read_lines(path: Path) -> list[str]:
    """Read the current UTF-8 file contents as lines without newline markers."""
    return path.read_text(encoding="utf-8").splitlines()


def _read_current_file(context: ToolContext) -> tuple[Path, list[str]]:
    """Return the current file and freshly read contents, or raise if absent."""
    if context.open_file is None:
        raise ToolPathError("no file is currently open")
    return context.open_file, _read_lines(context.open_file)


def _desired_start_for_line(line_number: int, window_size: int) -> int:
    """Place a 1-based target after about one-sixth of the window."""
    target_index = line_number - 1
    lines_before_target = (window_size + 5) // 6
    return target_index - lines_before_target


def _clamp_start_index(
    desired_start: int,
    total_lines: int,
    window_size: int,
) -> int:
    """Clamp a desired zero-based window start to the valid file range."""
    max_start = max(0, total_lines - window_size)
    return min(max(desired_start, 0), max_start)


def _render_window(
    context: ToolContext,
    path: Path,
    lines: list[str],
    desired_start: int,
) -> Observation:
    """Render a clamped file window, update its state, and return its result."""
    total_lines = len(lines)
    start_index = _clamp_start_index(
        desired_start,
        total_lines,
        context.window_size,
    )
    stop_index = min(start_index + context.window_size, total_lines)
    visible_lines = lines[start_index:stop_index]

    output_lines = [f"[File: {path} ({total_lines} lines total)]"]

    lines_above = start_index
    if lines_above > 0:
        output_lines.append(f"({lines_above} more lines above)")

    # Keep line numbers padded so the file contents align vertically.
    line_number_width = len(str(stop_index))
    output_lines.extend(
        f"{number:{line_number_width}d}:{line}"
        for number, line in enumerate(visible_lines, start=start_index + 1)
    )

    lines_below = total_lines - stop_index
    if lines_below > 0:
        output_lines.append(f"({lines_below} more lines below)")

    output_text = "\n".join(output_lines)

    context.open_file = path
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

        lines = _read_lines(resolved_path)
    except (ToolPathError, OSError, UnicodeError) as error:
        return _failed_view("open", error)

    total_lines = len(lines)

    if line_number is not None and not 1 <= line_number <= total_lines:
        return _failed_view(
            "open",
            f"line_number must be between 1 and {total_lines}: {line_number}"
        )

    desired_start = 0
    if line_number is not None:
        desired_start = _desired_start_for_line(line_number, context.window_size)

    return _render_window(context, resolved_path, lines, desired_start)


def goto(context: ToolContext, line_number: int) -> Observation:
    """Move the current file window to include a line number."""
    try:
        file_path, lines = _read_current_file(context)
    except (ToolPathError, OSError, UnicodeError) as error:
        return _failed_view("goto", error)

    total_lines = len(lines)

    if not 1 <= line_number <= total_lines:
        return _failed_view(
            "goto",
            f"line_number must be between 1 and {total_lines}: {line_number}"
        )

    desired_start = _desired_start_for_line(line_number, context.window_size)

    return _render_window(context, file_path, lines, desired_start)


def scroll_down(context: ToolContext) -> Observation:
    """Move the current file view down by one configured window."""
    try:
        file_path, lines = _read_current_file(context)
    except (ToolPathError, OSError, UnicodeError) as error:
        return _failed_view("scroll_down", error)

    scroll_distance = context.window_size - context.window_overlap
    current_start = context.window_start - 1
    desired_start = current_start + scroll_distance

    return _render_window(context, file_path, lines, desired_start)


def scroll_up(context: ToolContext) -> Observation:
    """Move the current file view up by one configured window."""
    try:
        file_path, lines = _read_current_file(context)
    except (ToolPathError, OSError, UnicodeError) as error:
        return _failed_view("scroll_up", error)

    scroll_distance = context.window_size - context.window_overlap
    current_start = context.window_start - 1
    desired_start = current_start - scroll_distance

    return _render_window(context, file_path, lines, desired_start)

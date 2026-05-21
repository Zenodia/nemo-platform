# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Data structures for cell processing in notebook conversion.

This module defines immutable dataclasses that represent the flow of data
through the cell processing pipeline. Each dataclass is self-documenting
with clear examples.

Design Philosophy:
- Immutable data structures (frozen=True)
- Clear separation of concerns
- Easy to test in isolation
- Explicit data flow (no hidden state)
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from .markers import MarkerCommand


@dataclass
class Cell:
    """Represents a notebook cell."""

    cell_type: str  # 'markdown' or 'code'
    source: List[str]
    metadata: Dict = field(default_factory=dict)
    outputs: List = field(default_factory=list)
    execution_count: Optional[int] = None

    def get_comment_char(self) -> str:
        """Get the appropriate comment character for the cell's language."""
        language = self.metadata.get("language", "python")

        if language in ["python", "bash", "sh", "shell", "ruby", "perl"]:
            return "#"
        elif language in ["javascript", "typescript", "java", "c", "cpp", "go", "rust", "jsonc"]:
            return "//"
        else:
            return "#"

    @classmethod
    def from_dict(cls, data: Dict) -> "Cell":
        """Create a Cell from a dictionary."""
        source = data.get("source", [])
        # normalize source to list of strings
        if isinstance(source, str):
            source = source.splitlines(keepends=True)
        elif isinstance(source, list):
            # ensure trailing newlines if they are missing?
            # nbformat says lines should have \n except maybe the last one.
            # But let's trust the input for now or just pass it through.
            pass

        return cls(
            cell_type=data["cell_type"],
            source=source,
            metadata=data.get("metadata", {}),
            outputs=data.get("outputs", []),
            execution_count=data.get("execution_count"),
        )

    def to_dict(self) -> Dict:
        """Convert Cell to a dictionary."""
        cell_dict = {
            "cell_type": self.cell_type,
            "metadata": self.metadata,
            "source": self.source,
        }
        if self.cell_type == "code":
            cell_dict["outputs"] = self.outputs
            cell_dict["execution_count"] = self.execution_count
        return cell_dict


@dataclass(frozen=True)
class CellMetadata:
    """Cell metadata for language detection and visibility control.

    Represents the metadata dictionary from a Jupyter notebook cell,
    providing convenient access to language settings and hide flags.
    Most features now use marker-based commands (see markers.py),
    but metadata is still used for basic language detection.

    Attributes:
        metadata: The raw metadata dictionary from the notebook cell.
                  Contains keys like 'language', 'vscode', 'tags', 'nemo_nb'.

        nemo_config: Nested configuration under metadata.nemo_nb.
                     Used for hide flags: {'hide': True}

        tags: List of cell tags from metadata.tags.
              Used for hide-cell tag: ['hide-cell', 'other-tag']

    Example - From notebook cell metadata to CellMetadata:
        Notebook cell JSON:
        ```json
        {
          "cell_type": "code",
          "metadata": {
            "language": "python",
            "vscode": {"languageId": "python"},
            "tags": ["hide-cell"],
            "nemo_nb": {"hide": false}
          },
          "source": ["print('hello')"]
        }
        ```

        Creating CellMetadata from this cell:
        >>> cell_dict = {
        ...     "cell_type": "code",
        ...     "metadata": {
        ...         "language": "python",
        ...         "vscode": {"languageId": "python"},
        ...         "tags": ["hide-cell"],
        ...         "nemo_nb": {"hide": False}
        ...     },
        ...     "source": ["print('hello')"]
        ... }
        >>> meta = CellMetadata(cell_dict)
        >>> meta.get_language()
        'python'
        >>> meta.should_hide()
        True

        Minimal metadata (defaults):
        >>> minimal_cell = {"cell_type": "code", "metadata": {}, "source": ["code"]}
        >>> meta = CellMetadata(minimal_cell)
        >>> meta.get_language()
        'python'
        >>> meta.should_hide()
        False
    """

    cell: Dict

    @property
    def metadata(self) -> Dict:
        """Get the metadata dictionary from the cell."""
        return self.cell.get("metadata", {})

    @property
    def nemo_config(self) -> Dict:
        """Get nemo_nb configuration from metadata."""
        return self.metadata.get("nemo_nb", {})

    @property
    def tags(self) -> List[str]:
        """Get tags list from metadata."""
        return self.metadata.get("tags", [])

    def should_hide(self) -> bool:
        """Check if cell should be hidden.

        Supports:
        - metadata.nemo_nb.hide = true
        - metadata.tags includes "hide-cell"

        Returns:
            True if cell should be omitted from output
        """
        return self.nemo_config.get("hide", False) or "hide-cell" in self.tags

    def get_language(self) -> str:
        """Get code cell language for syntax highlighting.

        Default: python

        Supports:
        - metadata.language: Direct language specification
        - metadata.vscode.languageId: VSCode language identifier
        - Converts "shellscript" and "bash" to "sh" for proper rendering

        Returns:
            Language identifier for code fence (e.g., "python", "sh")
        """
        # Check for direct language specification
        if lang := self.metadata.get("language"):
            return lang

        # Check for VSCode language identifier
        vscode_meta = self.metadata.get("vscode", {})
        if lang_id := vscode_meta.get("languageId"):
            # Convert VSCode language IDs to standard code fence languages
            if lang_id == "shellscript":
                return "sh"
            return lang_id

        # Default to Python
        return "python"


@dataclass(frozen=True)
class CellInput:
    """Input data for processing a single notebook cell.

    Represents a cell after marker parsing has been performed, containing
    the cleaned content (with marker lines removed) and the extracted marker
    commands that control cell transformation.

    Attributes:
        content: Cell content with marker lines removed.
                 For code cells: the actual code without comment markers.
                 For markdown cells: the markdown text without HTML comment markers.

        commands: Parsed marker commands extracted from the cell.
                  Each command controls how the cell should be transformed
                  (e.g., hide, wrap-cell-start, indent-space).

        cell_type: Type of notebook cell.
                   Either "code" or "markdown".

        meta: Cell metadata containing language info and visibility settings.
              Only present for code cells. Contains information like
              language="python" or hide flags.

    Example - From notebook cell to CellInput:
        Notebook cell (raw JSON):
        ```json
        {
          "cell_type": "code",
          "metadata": {"language": "python"},
          "source": [
            "# @nemo-nb: wrap-cell-start :::{note} Important\\n",
            "# @nemo-nb: wrap-cell-end ::::\\n",
            "print('hello world')\\n",
            "result = 42"
          ]
        }
        ```

        After marker parsing, creates this CellInput:
        >>> from nemo_nb.markers import MarkerCommand
        >>> cell = CellInput(
        ...     content="print('hello world')\\nresult = 42",
        ...     commands=[
        ...         MarkerCommand(
        ...             command="wrap-cell-start",
        ...             args=[":::{note} Important"],
        ...             line="# @nemo-nb: wrap-cell-start :::{note} Important",
        ...             position=-1,
        ...             is_at_cell_start=True
        ...         ),
        ...         MarkerCommand(
        ...             command="wrap-cell-end",
        ...             args=[":::"],
        ...             line="# @nemo-nb: wrap-cell-end :::",
        ...             position=-1,
        ...             is_at_cell_start=True
        ...         )
        ...     ],
        ...     cell_type="code",
        ...     meta=CellMetadata({"cell_type": "code", "metadata": {"language": "python"}})
        ... )

        Markdown cell example:
        ```json
        {
          "cell_type": "markdown",
          "metadata": {},
          "source": [
            "<!-- @nemo-nb: indent-space 4 -->\\n",
            "# Introduction\\n",
            "\\n",
            "This is content."
          ]
        }
        ```

        After marker parsing:
        >>> cell = CellInput(
        ...     content="# Introduction\\n\\nThis is content.",
        ...     commands=[
        ...         MarkerCommand(
        ...             command="indent-space",
        ...             args=["4"],
        ...             line="<!-- @nemo-nb: indent-space 4 -->",
        ...             position=-1,
        ...             is_at_cell_start=True
        ...         )
        ...     ],
        ...     cell_type="markdown",
        ...     meta=None
        ... )
    """

    content: str
    commands: List["MarkerCommand"]
    cell_type: str
    meta: Optional["CellMetadata"] = None


@dataclass(frozen=True)
class GroupMarkers:
    """Information about multi-cell group markers detected in a cell.

    Multi-cell groups allow indenting multiple consecutive cells together,
    which is essential for MyST directives like tab-sets where several cells
    need to be indented as children of a parent directive.

    A group is started with multi-cell-indent-{space|tab}-start and ended
    with multi-cell-indent-{space|tab}-end. These markers can appear at the
    start of a cell or in the middle (causing cell content splitting).

    Attributes:
        end_info: Information about a group end marker if detected.
                  Dict with keys:
                  - 'type': Either 'space' or 'tab' indentation
                  - 'id': Group identifier (e.g., 'indent-a') to match start/end
                  None if no end marker present.

        end_at_start: Whether the end marker appears at the very start of the cell.
                      True: Cell starts with end marker (close group, then process content)
                      False: End marker is in middle (process pre-marker content in group,
                             then close group, then process post-marker content)

        start_info: Information about a group start marker if detected.
                    Dict with keys:
                    - 'type': Either 'space' or 'tab' indentation
                    - 'id': Group identifier (e.g., 'indent-b')
                    - 'spaces' or 'tabs': Number of spaces/tabs to indent
                    None if no start marker present.

        start_at_start: Whether the start marker appears at the very start of the cell.
                        True: Cell starts with marker (begin group immediately)
                        False: Marker is in middle (process pre-marker content normally,
                               then start group for post-marker content)

    Example - From notebook cells with multi-cell markers to GroupMarkers:
        Notebook sequence for a tab-set:

        Cell 1 (markdown):
        ```
        <!-- @nemo-nb: multi-cell-indent-space-start tabset-1 4 -->
        ::::{tab-set}
        ```
        ? Creates GroupMarkers:
        >>> markers = GroupMarkers(
        ...     end_info=None,
        ...     end_at_start=False,
        ...     start_info={'type': 'space', 'id': 'tabset-1', 'spaces': 4},
        ...     start_at_start=True
        ... )
        # This starts a new group that will accumulate subsequent cells

        Cell 2 (markdown) - inside the group:
        ```
        :::{tab-item} Python
        ```
        ? Creates GroupMarkers:
        >>> markers = GroupMarkers(
        ...     end_info=None,
        ...     end_at_start=False,
        ...     start_info=None,
        ...     start_at_start=False
        ... )
        # No markers, so this cell gets accumulated into the active group

        Cell 3 (code) - inside the group:
        ```python
        print('hello')
        ```
        ? Creates GroupMarkers (no markers):
        >>> markers = GroupMarkers()
        # This cell is also accumulated into the group

        Cell 4 (markdown) - ends the group:
        ```
        <!-- @nemo-nb: multi-cell-indent-space-end tabset-1 -->
        ::::
        ```
        ? Creates GroupMarkers:
        >>> markers = GroupMarkers(
        ...     end_info={'type': 'space', 'id': 'tabset-1'},
        ...     end_at_start=True,
        ...     start_info=None,
        ...     start_at_start=False
        ... )
        # This closes the 'tabset-1' group and outputs all accumulated cells with indentation
    """

    end_info: Optional[Dict] = None
    end_at_start: bool = False
    start_info: Optional[Dict] = None
    start_at_start: bool = False


@dataclass
class ProcessingState:
    """Mutable state that tracks context during multi-cell processing.

    As we process cells sequentially, we need to maintain state about:
    1. Whether we're inside a multi-cell group (for indentation)
    2. Which cells belong to the current group
    3. The nesting level of MyST directives (for proper indentation)

    This state is mutated and returned as we process each cell, creating
    an explicit data flow through the processing pipeline.

    Attributes:
        active_group: Information about the currently active multi-cell group.
                      None if we're not inside a group.
                      Dict with keys when active:
                      - 'type': Either 'space' or 'tab'
                      - 'id': Group identifier (e.g., 'indent-a')
                      - 'spaces' or 'tabs': Indentation amount

                      Groups are used for tab-sets and other nested structures:
                      ::::{tab-set}              <- start group
                      :::{tab-item} Python       <- inside group
                      ```python                  <- inside group
                      code here
                      ```
                      :::                        <- inside group
                      ::::                       <- end group

        group_cells: Accumulated cell content strings for the active group.
                     Empty list when no group is active.
                     When a group ends, these cells are joined with proper
                     indentation and added to the result list.

                     Example: [':::{tab-item} Python', '```python\ncode\n```']

        directive_stack: Stack tracking nested MyST directives for indentation.
                         Each tuple is (directive_type, indent_level).
                         Used to properly indent code fences that appear
                         inside directives.

                         Example: [('note', 0), ('tab-set', 4)]
                         Means we're inside a note at column 0, which contains
                         a tab-set at column 4.

    Example - How ProcessingState evolves while processing notebook cells:
        Initial state (no cells processed yet):
        >>> state = ProcessingState()
        >>> assert state.active_group is None
        >>> assert state.group_cells == []
        >>> assert state.directive_stack == []

        After processing Cell 1 (starts multi-cell group with tab-set):
        Notebook cell:
        ```
        <!-- @nemo-nb: multi-cell-indent-space-start tabs-1 4 -->
        ::::{tab-set}
        ```

        State after processing:
        >>> state = ProcessingState(
        ...     active_group={'type': 'space', 'id': 'tabs-1', 'spaces': 4},
        ...     group_cells=['::::{tab-set}'],
        ...     directive_stack=[('tab-set', 0)]
        ... )
        # Group started, first cell accumulated, directive tracked

        After processing Cell 2 (inside the group):
        Notebook cell:
        ```
        :::{tab-item} Python
        ```

        State after processing:
        >>> state = ProcessingState(
        ...     active_group={'type': 'space', 'id': 'tabs-1', 'spaces': 4},
        ...     group_cells=['::::{tab-set}', ':::{tab-item} Python'],
        ...     directive_stack=[('tab-set', 0), ('tab-item', 4)]
        ... )
        # Second cell accumulated, nested directive tracked

        After processing Cell 3 (code inside the group):
        Notebook cell:
        ```python
        print('hello')
        ```

        State after processing:
        >>> state = ProcessingState(
        ...     active_group={'type': 'space', 'id': 'tabs-1', 'spaces': 4},
        ...     group_cells=[
        ...         '::::{tab-set}',
        ...         ':::{tab-item} Python',
        ...         '```python\\nprint(\\'hello\\')\\n```'
        ...     ],
        ...     directive_stack=[('tab-set', 0)]
        ... )
        # Code cell accumulated, tab-item directive popped from stack

        After processing Cell 4 (ends the group):
        Notebook cell:
        ```
        <!-- @nemo-nb: multi-cell-indent-space-end tabs-1 -->
        ::::
        ```

        State after processing (group flushed):
        >>> state = ProcessingState()
        # Group closed, all cells output with indentation, state reset

        Functional updates using copy():
        >>> original = ProcessingState(group_cells=['cell1'])
        >>> updated = original.copy()
        >>> updated.group_cells.append('cell2')
        >>> len(original.group_cells)  # Original unchanged
        1
        >>> len(updated.group_cells)   # New state modified
        2
    """

    active_group: Optional[Dict] = None
    group_cells: List[str] = field(default_factory=list)
    directive_stack: List[Tuple] = field(default_factory=list)

    def copy(self) -> "ProcessingState":
        """Create a copy with same values but new list instances.

        This enables functional-style updates where we create a new state
        rather than mutating the existing one, making data flow explicit.

        Returns:
            New ProcessingState with copied lists.

        Example:
            >>> original = ProcessingState(group_cells=['cell1'])
            >>> updated = original.copy()
            >>> updated.group_cells.append('cell2')
            >>> len(original.group_cells)  # Original unchanged
            1
            >>> len(updated.group_cells)   # New state modified
            2
        """
        return ProcessingState(
            active_group=self.active_group,
            group_cells=self.group_cells.copy(),
            directive_stack=self.directive_stack.copy(),
        )


@dataclass(frozen=True)
class ProcessingResult:
    """Result of processing a single cell.

    Encapsulates the updated state after processing a cell, along with
    any output that should be added to the final result list.

    Using an immutable result object makes the data flow explicit:
    cell_input + current_state -> ProcessingResult(new_state, output)

    Attributes:
        state: Updated processing state after handling this cell.
               Contains updated active_group, group_cells, and directive_stack.

        output: List of markdown strings to append to the result.
                Usually 0-1 items, but can be multiple if cell was split
                at a marker boundary.
                Empty list if cell is being accumulated in a group.

    Example - ProcessingResult for different scenarios:
        Scenario 1: Normal markdown cell (not in a group)
        Input notebook cell:
        ```
        # Introduction

        This is the content.
        ```

        Processing result:
        >>> result = ProcessingResult(
        ...     state=ProcessingState(),  # No active group
        ...     output=['# Introduction\\n\\nThis is the content.']
        ... )
        # Cell is immediately added to output

        Scenario 2: Cell that starts a multi-cell group
        Input notebook cell:
        ```
        <!-- @nemo-nb: multi-cell-indent-space-start grp-1 4 -->
        ::::{tab-set}
        ```

        Processing result:
        >>> result = ProcessingResult(
        ...     state=ProcessingState(
        ...         active_group={'type': 'space', 'id': 'grp-1', 'spaces': 4},
        ...         group_cells=['::::{tab-set}'],
        ...         directive_stack=[('tab-set', 0)]
        ...     ),
        ...     output=[]  # Nothing in output yet, cell accumulated
        ... )
        # State updated to track the group, no output yet

        Scenario 3: Cell inside an active group
        Input notebook cell (while group 'grp-1' is active):
        ```python
        print('hello')
        ```

        Processing result:
        >>> result = ProcessingResult(
        ...     state=ProcessingState(
        ...         active_group={'type': 'space', 'id': 'grp-1', 'spaces': 4},
        ...         group_cells=['::::{tab-set}', '```python\\nprint(\\'hello\\')\\n```']
        ...     ),
        ...     output=[]  # Still accumulating
        ... )
        # Cell added to group_cells, still no output

        Scenario 4: Cell that ends the group
        Input notebook cell:
        ```
        <!-- @nemo-nb: multi-cell-indent-space-end grp-1 -->
        ::::
        ```

        Processing result:
        >>> result = ProcessingResult(
        ...     state=ProcessingState(),  # Group closed, state reset
        ...     output=[
        ...         '    ::::{tab-set}\\n'
        ...         '    ```python\\n'
        ...         '    print(\\'hello\\')\\n'
        ...         '    ```\\n'
        ...         '    ::::'
        ...     ]
        ... )
        # Group flushed with 4-space indentation, output contains all accumulated cells
    """

    state: ProcessingState
    output: List[str] = field(default_factory=list)

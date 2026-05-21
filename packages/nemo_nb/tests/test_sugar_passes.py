# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for the pass-based sugar pipeline."""

import pytest
from nemo_nb.structures import Cell
from nemo_nb.sugar import (
    BasePass,
    DropdownPass,
    LabelInsertPass,
    PassOptions,
    SugarPass,
    SugarPipeline,
    TabItemPass,
    TabSetPass,
)


class TestPassProtocol:
    """Test the SugarPass protocol."""

    def test_base_pass_is_abstract(self):
        """BasePass cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BasePass()

    def test_passes_implement_protocol(self):
        """All pass classes implement the SugarPass protocol."""
        passes = [TabSetPass(), TabItemPass(), DropdownPass(), LabelInsertPass()]
        for p in passes:
            assert isinstance(p, SugarPass)
            assert hasattr(p, "name")
            assert hasattr(p, "apply")

    def test_pass_names_are_unique(self):
        """Each pass has a unique name."""
        passes = SugarPipeline.default_passes()
        names = [p.name for p in passes]
        assert len(names) == len(set(names))


class TestPassOptions:
    """Test PassOptions dataclass."""

    def test_default_options(self):
        """Default options have sensible values."""
        opts = PassOptions()
        assert opts.fence_conversion_disabled is False
        assert opts.verbose is False

    def test_custom_options(self):
        """Custom options can be set."""
        opts = PassOptions(fence_conversion_disabled=True, verbose=True)
        assert opts.fence_conversion_disabled is True
        assert opts.verbose is True


class TestSugarPipeline:
    """Test the SugarPipeline class."""

    def test_default_passes(self):
        """Default pipeline has expected passes."""
        pipeline = SugarPipeline()
        names = [p.name for p in pipeline.passes]
        assert "TabSet" in names
        assert "TabItem" in names
        assert "Dropdown" in names
        assert "LabelInsert" in names

    def test_custom_passes(self):
        """Pipeline can be initialized with custom passes."""
        custom_passes = [LabelInsertPass()]
        pipeline = SugarPipeline(passes=custom_passes)
        assert len(pipeline.passes) == 1
        assert pipeline.passes[0].name == "LabelInsert"

    def test_empty_cells(self):
        """Pipeline handles empty cell list."""
        pipeline = SugarPipeline()
        result = pipeline.run([])
        assert result == []

    def test_pass_order(self):
        """Passes run in the order specified."""
        # Create cells that need multiple passes
        cells = [Cell(cell_type="markdown", source=["(my-label)=\n", "# Title\n"])]
        pipeline = SugarPipeline()
        result = pipeline.run(cells)
        # LabelInsertPass should have added an insert marker
        content = "".join(result[0].source)
        assert "<!-- @nemo-nb: insert (my-label)= -->" in content


class TestLabelInsertPass:
    """Test the LabelInsertPass."""

    def test_detects_myst_label(self):
        """Detects MyST label at start of first cell."""
        cells = [Cell(cell_type="markdown", source=["(my-label)=\n", "# Title\n", "Content\n"])]
        p = LabelInsertPass()
        result = p.apply(cells, PassOptions())

        content = "".join(result[0].source)
        assert "<!-- @nemo-nb: insert (my-label)= -->" in content
        # Original label line should be removed
        assert "(my-label)=\n" not in result[0].source[0]

    def test_no_label(self):
        """Cells without labels are unchanged."""
        cells = [Cell(cell_type="markdown", source=["# Title\n", "Content\n"])]
        p = LabelInsertPass()
        result = p.apply(cells, PassOptions())

        assert result[0].source == ["# Title\n", "Content\n"]

    def test_code_cell_first(self):
        """Code cell as first cell is unchanged."""
        cells = [Cell(cell_type="code", source=["print('hello')\n"])]
        p = LabelInsertPass()
        result = p.apply(cells, PassOptions())

        assert result[0].source == ["print('hello')\n"]

    def test_label_with_frontmatter(self):
        """Label is inserted after frontmatter."""
        cells = [
            Cell(
                cell_type="markdown",
                source=[
                    "(my-label)=\n",
                    "---\n",
                    "title: Test\n",
                    "---\n",
                    "# Title\n",
                ],
            )
        ]
        p = LabelInsertPass()
        result = p.apply(cells, PassOptions())

        lines = result[0].source
        # Insert marker should come after frontmatter
        frontmatter_end = lines.index("---\n", 1) if "---\n" in lines else -1
        insert_idx = next(i for i, line in enumerate(lines) if "insert (my-label)=" in line)
        assert insert_idx > frontmatter_end


class TestTabSetPass:
    """Test the TabSetPass."""

    def test_detects_tab_set(self):
        """Detects ::::{tab-set} and adds markers."""
        cells = [
            Cell(
                cell_type="markdown",
                source=["::::{tab-set}\n", ":::{tab-item} Python\n", ":::\n", "::::\n"],
            )
        ]
        p = TabSetPass()
        result = p.apply(cells, PassOptions())

        content = "".join(result[0].source)
        assert "multi-cell-indent-space-start" in content
        assert "insert ::::{tab-set}" in content

    def test_fence_conversion_disabled_skips(self):
        """With fence_conversion_disabled, pass does nothing."""
        cells = [Cell(cell_type="markdown", source=["::::{tab-set}\n", "::::\n"])]
        p = TabSetPass()
        opts = PassOptions(fence_conversion_disabled=True)
        result = p.apply(cells, opts)

        content = "".join(result[0].source)
        assert "multi-cell-indent-space-start" not in content

    def test_no_tab_set(self):
        """Cells without tab-set are unchanged."""
        cells = [Cell(cell_type="markdown", source=["# Title\n", "Content\n"])]
        p = TabSetPass()
        result = p.apply(cells, PassOptions())

        assert result[0].source == ["# Title\n", "Content\n"]

    def test_indentation_detection(self):
        """Detects indentation level of tab-set."""
        cells = [
            Cell(
                cell_type="markdown",
                source=["    ::::{tab-set}\n", "    ::::\n"],
            )
        ]
        p = TabSetPass()
        result = p.apply(cells, PassOptions())

        content = "".join(result[0].source)
        # Should detect 4 spaces of indentation
        assert "indent-space-start indent-a 4" in content


class TestTabItemPass:
    """Test the TabItemPass."""

    def test_wraps_code_cell(self):
        """Wraps code cell following tab-item."""
        cells = [
            Cell(
                cell_type="markdown",
                source=[":::{tab-item} Python\n", ":sync: python\n"],
            ),
            Cell(cell_type="code", source=["print('hello')\n"]),
        ]
        p = TabItemPass()
        result = p.apply(cells, PassOptions())

        # Code cell should have wrap markers
        code_content = "".join(result[-1].source)
        assert "wrap-cell-start" in code_content
        assert "tab-item" in code_content
        assert "wrap-cell-end" in code_content

    def test_preserves_sync(self):
        """Preserves :sync: directive in markers."""
        cells = [
            Cell(
                cell_type="markdown",
                source=[":::{tab-item} Python\n", ":sync: python\n"],
            ),
            Cell(cell_type="code", source=["print('hello')\n"]),
        ]
        p = TabItemPass()
        result = p.apply(cells, PassOptions())

        code_content = "".join(result[-1].source)
        assert ":sync: python" in code_content

    def test_fence_conversion_disabled_skips(self):
        """With fence_conversion_disabled, pass does nothing."""
        cells = [
            Cell(cell_type="markdown", source=[":::{tab-item} Python\n"]),
            Cell(cell_type="code", source=["print('hello')\n"]),
        ]
        p = TabItemPass()
        opts = PassOptions(fence_conversion_disabled=True)
        result = p.apply(cells, opts)

        code_content = "".join(result[-1].source)
        assert "wrap-cell-start" not in code_content


class TestDropdownPass:
    """Test the DropdownPass."""

    def test_wraps_code_cell(self):
        """Wraps code cell following dropdown."""
        cells = [
            Cell(
                cell_type="markdown",
                source=[":::{dropdown} Click to expand\n", ":open:\n"],
            ),
            Cell(cell_type="code", source=["print('hello')\n"]),
        ]
        p = DropdownPass()
        result = p.apply(cells, PassOptions())

        code_content = "".join(result[-1].source)
        assert "wrap-cell-start" in code_content
        assert "dropdown" in code_content
        assert "Click to expand" in code_content

    def test_preserves_options(self):
        """Preserves dropdown options like :icon: and :open:."""
        cells = [
            Cell(
                cell_type="markdown",
                source=[
                    ":::{dropdown} Click to expand\n",
                    ":icon: code\n",
                    ":open:\n",
                ],
            ),
            Cell(cell_type="code", source=["print('hello')\n"]),
        ]
        p = DropdownPass()
        result = p.apply(cells, PassOptions())

        code_content = "".join(result[-1].source)
        assert ":icon: code" in code_content
        assert ":open:" in code_content

    def test_inline_dropdown_unchanged(self):
        """Dropdown that closes in same cell is unchanged."""
        cells = [
            Cell(
                cell_type="markdown",
                source=[
                    ":::{dropdown} Inline\n",
                    "Content inside\n",
                    ":::\n",
                ],
            ),
        ]
        p = DropdownPass()
        result = p.apply(cells, PassOptions())

        # Should be unchanged since it closes in same cell
        assert ":::{dropdown} Inline\n" in result[0].source

    def test_fence_conversion_disabled_skips(self):
        """With fence_conversion_disabled, pass does nothing."""
        cells = [
            Cell(cell_type="markdown", source=[":::{dropdown} Test\n"]),
            Cell(cell_type="code", source=["print('hello')\n"]),
        ]
        p = DropdownPass()
        opts = PassOptions(fence_conversion_disabled=True)
        result = p.apply(cells, opts)

        code_content = "".join(result[-1].source)
        assert "wrap-cell-start" not in code_content


class TestPipelineIntegration:
    """Integration tests for the full pipeline."""

    def test_complex_document(self):
        """Pipeline handles complex document with multiple patterns."""
        cells = [
            Cell(
                cell_type="markdown",
                source=["(my-doc)=\n", "# My Document\n", "\n"],
            ),
            Cell(
                cell_type="markdown",
                source=["::::{tab-set}\n"],
            ),
            Cell(
                cell_type="markdown",
                source=[":::{tab-item} Python\n", ":sync: python\n"],
            ),
            Cell(cell_type="code", source=["print('hello')\n"]),
            Cell(
                cell_type="markdown",
                source=[":::\n", "::::\n"],
            ),
        ]

        pipeline = SugarPipeline()
        result = pipeline.run(cells)

        # Should have label marker
        first_content = "".join(result[0].source)
        assert "insert (my-doc)=" in first_content

        # Should have tab-set markers somewhere
        all_content = "".join("".join(c.source) for c in result)
        assert "multi-cell-indent-space-start" in all_content
        assert "tab-item" in all_content

    def test_idempotent(self):
        """Running pipeline twice produces same result."""
        cells = [
            Cell(cell_type="markdown", source=["(label)=\n", "# Title\n"]),
        ]

        pipeline = SugarPipeline()
        result1 = pipeline.run(cells)
        # Deep copy for second run
        cells2 = [Cell(cell_type=c.cell_type, source=list(c.source)) for c in result1]
        result2 = pipeline.run(cells2)

        # Results should be the same
        assert len(result1) == len(result2)
        for c1, c2 in zip(result1, result2):
            assert c1.source == c2.source

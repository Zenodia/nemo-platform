# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""add deletion_stage to workspaces

Revision ID: 54a9f4ccf8b1
Revises: a870a05e48ca
Create Date: 2026-02-19 15:53:55.446702

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "54a9f4ccf8b1"
down_revision: Union[str, Sequence[str], None] = "a870a05e48ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("workspaces", sa.Column("deletion_stage", sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("workspaces", "deletion_stage")

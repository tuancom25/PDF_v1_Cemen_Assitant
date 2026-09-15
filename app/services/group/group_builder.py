from typing import List
from ..ingestion.models import ContentBlock
from .group import Group
class GroupBuilder:

    def __init__(
        self,
        vertical_gap: float = 80.0,
        horizontal_tolerance: float = 100.0,
    ):
        self.vertical_gap = vertical_gap
        self.horizontal_tolerance = horizontal_tolerance

    # ---------------------------------------------------------
    # Geometry
    # ---------------------------------------------------------

    @staticmethod
    def _vertical_gap(
        a: ContentBlock,
        b: ContentBlock,
    ) -> float:

        _, ay1, _, ay2 = a.bbox
        _, by1, _, by2 = b.bbox

        if by1 >= ay2:
            return by1 - ay2

        if ay1 >= by2:
            return ay1 - by2

        return 0.0

    @staticmethod
    def _horizontal_distance(
        a: ContentBlock,
        b: ContentBlock,
    ) -> float:

        ax1, _, ax2, _ = a.bbox
        bx1, _, bx2, _ = b.bbox

        if bx1 >= ax2:
            return bx1 - ax2

        if ax1 >= bx2:
            return ax1 - bx2

        return 0.0

    # ---------------------------------------------------------
    # Structural relation
    # ---------------------------------------------------------

    def _should_join(
        self,
        previous: ContentBlock,
        current: ContentBlock,
    ) -> bool:

        if previous.page != current.page:
            return False

        vertical_gap = self._vertical_gap(
            previous,
            current,
        )

        if vertical_gap > self.vertical_gap:
            return False

        horizontal_distance = self._horizontal_distance(
            previous,
            current,
        )

        if horizontal_distance > self.horizontal_tolerance:
            return False

        return True

    # ---------------------------------------------------------
    # Build
    # ---------------------------------------------------------

    def build(
        self,
        blocks: List[ContentBlock],
    ) -> List[Group]:

        if not blocks:
            return []
        '''
        # đoạn này là code cũ, sử dụng page, y, x để sắp xếp các block
        # đoạn sau là thay thế: dùng page, order, y, x để sắp xếp các block
        blocks = sorted(
            blocks,
            key=lambda b: (
                b.page,
                b.bbox[1],
                b.bbox[0],
            ),
        )
        '''
        blocks = sorted(
            blocks,
            key=lambda b: (
                b.page,
                b.reading_order if b.reading_order is not None else 999999,
                b.bbox[1],
                b.bbox[0],
                ),
            )

        groups: List[Group] = []

        current_group = None

        for block in blocks:

            if current_group is None:

                current_group = Group(
                    group_id=len(groups),
                    page=block.page,
                )

                current_group.add_block(block)

                continue

            previous_block = (
                current_group.content_blocks[-1]
            )

            if self._should_join(
                previous_block,
                block,
            ):

                current_group.add_block(block)

            else:

                current_group.calculate_bbox()

                groups.append(
                    current_group
                )

                current_group = Group(
                    group_id=len(groups),
                    page=block.page,
                )

                current_group.add_block(block)

        # flush
        if current_group is not None:

            current_group.calculate_bbox()

            groups.append(
                current_group
            )

        # previous / next
        for i, group in enumerate(groups):

            if i > 0:
                group.previous_group_id = (
                    groups[i - 1].group_id
                )

            if i < len(groups) - 1:
                group.next_group_id = (
                    groups[i + 1].group_id
                )

        return groups
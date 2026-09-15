from app.services.group.unassigned_group_old import group_blocks


def main():
    blocks = [
        {"role": "heading", "text": "Introduction"},
        {"role": "paragraph", "text": "Paragraph 1"},
        {"role": "paragraph", "text": "Paragraph 2"},
        {"role": "paragraph", "text": "Paragraph 3"},

        {"role": "figure", "text": ""},
        {"role": "caption", "text": "Figure 1. Cement process"},

        {"role": "paragraph", "text": "Paragraph after figure"},

        {"role": "heading", "text": "Calcination"},
        {"role": "paragraph", "text": "Calcination paragraph"},
    ]

    groups = group_blocks(blocks)

    print("=" * 70)
    print("TEST UNASSIGNED GROUP")
    print("=" * 70)

    for group_id, block_indices in enumerate(groups):

        print(f"\nGroup {group_id}")

        for index in block_indices:
            block = blocks[index]

            print(
                f"  [{index}] "
                f"{block.get('role'):10s} "
                f"{block.get('text', '')[:60]}"
            )


if __name__ == "__main__":
    main()
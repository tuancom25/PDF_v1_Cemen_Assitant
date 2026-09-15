import json
from pathlib import Path


class CheckpointManager:

    def __init__(self, path):

        self.path = Path(path)

        self.data = {
            "schema_version": "1.0",
            "documents": {},
        }

        self.load()

    # -------------------------------------------------
    # LOAD
    # -------------------------------------------------

    def load(self):

        if not self.path.exists():
            return

        self.data = json.loads(
            self.path.read_text(
                encoding="utf-8"
            )
        )

    # -------------------------------------------------
    # SAVE
    # -------------------------------------------------

    def save(self):

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        tmp = self.path.with_suffix(
            ".tmp"
        )

        tmp.write_text(
            json.dumps(
                self.data,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        tmp.replace(self.path)

    # -------------------------------------------------
    # START DOCUMENT
    # -------------------------------------------------

    def start_document_old(
        self,
        document_id,
        total_pages,
        ):

        existing = self.data["documents"].get(
            document_id
        )

        # Document đã có checkpoint
        if existing:

            existing["total_pages"] = total_pages

            # Nếu trước đó completed thì
            # không reset last_completed_page
            if existing.get("status") != "completed":
                existing["status"] = "running"

        else:

            self.data["documents"][document_id] = {
                "status": "running",
                "total_pages": total_pages,
                "last_completed_page": 0,
            }

        self.save()
    def start_document(
        self,
        document_id,
        total_pages,
    ):
        if document_id not in self.data["documents"]:

            self.data["documents"][document_id] = {
                "status": "running",
                "total_pages": total_pages,
                "last_completed_page": 0,
            }
        else:

            record = self.data["documents"][document_id]

            record["total_pages"] = total_pages
            record["status"] = "running"

        self.save()

    # -------------------------------------------------
    # PAGE CHECKPOINT
    # -------------------------------------------------

    def update_page(
        self,
        document_id,
        page_number,
    ):

        record = self.data[
            "documents"
        ][document_id]

        record[
            "last_completed_page"
        ] = page_number

        self.save()

    # -------------------------------------------------
    # COMPLETE
    # -------------------------------------------------

    def complete_document(
        self,
        document_id,
    ):

        record = self.data[
            "documents"
        ][document_id]

        record["status"] = "completed"

        record[
            "last_completed_page"
        ] = record["total_pages"]

        self.save()

    # -------------------------------------------------
    # FAILED
    # -------------------------------------------------

    def fail_document(
        self,
        document_id,
        error,
    ):

        record = self.data[
            "documents"
        ][document_id]

        record["status"] = "failed"
        record["error"] = str(error)

        self.save()

    # -------------------------------------------------
    # QUERY
    # -------------------------------------------------

    def is_completed(
        self,
        document_id,
    ):

        record = self.data[
            "documents"
        ].get(document_id)

        return (
            record is not None
            and record["status"]
            == "completed"
        )

    def last_completed_page(
        self,
        document_id,
    ):

        record = self.data[
            "documents"
        ].get(document_id)

        if record is None:
            return 0

        return record.get(
            "last_completed_page",
            0,
        )
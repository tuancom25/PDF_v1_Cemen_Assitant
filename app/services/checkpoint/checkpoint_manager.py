import json
from pathlib import Path


class CheckpointManager :
    def __init__(self, checkpoint_root: Path):
        self.checkpoint_root = checkpoint_root
        self.checkpoint_root.mkdir(
            parents=True,
            exist_ok=True
        )
    def load_document_checkpoint(self, document_id: str) -> dict:
        checkpoint_file = self.checkpoint_root / f"{document_id}.json"

        if checkpoint_file.exists():
            with checkpoint_file.open("r", encoding="utf-8") as f:
                return json.load(f)

        return {}
    def mark_document_complete( self, 
                   document_id: str,     
            ) :
        checkpoint_file = self.checkpoint_root / f"{document_id}.json"
        checkpoint_data = { }
        with checkpoint_file.open("w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=4)
        
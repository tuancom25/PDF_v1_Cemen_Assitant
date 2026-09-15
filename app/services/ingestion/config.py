from dataclasses import dataclass
from pathlib import Path

# # Load layout model
# model = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config', extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5])
@dataclass
class AnalyzerConfig:
    output_root: Path = Path("data/processed/documents")
    catalog_root: Path = Path("data/catalog")
    checkpoint_file: Path = Path("data/catalog/checkpoint.json" )
    render_dpi: int = 200
    text_chars_threshold: int = 80
    scan_image_ratio_threshold: float = 0.55
    enable_ocr: bool = False
    enable_layout: bool = False
    layout_model_config: str = (
        "lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config"
    )
    layout_score_threshold: float = 0.5

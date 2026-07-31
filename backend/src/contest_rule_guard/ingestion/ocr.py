import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR  # type: ignore[import-untyped]

from contest_rule_guard.ingestion.ports import OcrEngine, OcrToken


class RapidOcrEngine(OcrEngine):
    def __init__(self) -> None:
        self._engine = RapidOCR()

    def recognize(self, image: Image.Image) -> list[OcrToken]:
        raw_result, _ = self._engine(np.asarray(image.convert("RGB")))
        if raw_result is None:
            return []
        return [
            OcrToken(
                text=str(item[1]).strip(),
                confidence=float(item[2]),
                polygon=[(float(point[0]), float(point[1])) for point in item[0]],
            )
            for item in raw_result
            if str(item[1]).strip()
        ]

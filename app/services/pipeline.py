from detectors.combined_detector import CombinedDetector
from vault.token_manager import generate_token
from logger.audit_logger import log_token_creation


class RedactionPipeline:
    def __init__(self):
        self.detector = CombinedDetector()

    def process(self, text: str):
        detections = self.detector.detect(text)

        redacted_text = text

        # Replace from end to beginning so indexes stay valid
        for d in sorted(detections, key=lambda x: x.start, reverse=True):

            token = generate_token(d.entity_type)

            log_token_creation(d.entity_type, token)

            redacted_text = (
                redacted_text[:d.start]
                + token
                + redacted_text[d.end:]
            )

        return {
            "redacted_text": redacted_text,
            "detections": [
                {
                    "entity_type": d.entity_type,
                    "text": d.text,
                    "start": d.start,
                    "end": d.end,
                    "source": d.source,
                }
                for d in detections
            ],
        }
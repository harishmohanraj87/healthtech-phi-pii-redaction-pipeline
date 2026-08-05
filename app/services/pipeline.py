import re

from detectors.combined_detector import CombinedDetector
from vault.token_vault import TokenVault
from logger.audit_logger import log_token_creation


class RedactionPipeline:
    """
    End-to-end PHI/PII redaction pipeline.

    Workflow:
    1. Detect PHI/PII entities.
    2. Store/retrieve secure tokens from the Redis Token Vault.
    3. Replace original values with secure tokens.
    4. Restore original values when required.
    """

    def __init__(self):
        self.detector = CombinedDetector()
        self.vault = TokenVault()

    def process(self, text: str):
        """
        Detect PHI/PII and replace each entity with a secure token.
        """

        detections = self.detector.detect(text)
        redacted_text = text

        # Replace from end to beginning so indexes remain valid
        for d in sorted(detections, key=lambda x: x.start, reverse=True):

            token = self.vault.get_or_create_token(
                d.entity_type,
                d.text
            )

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

    def restore(self, text: str):
        """
        Restore secure tokens back to their original PHI values
        using the Redis Token Vault.
        """

        pattern = r"\[[A-Z]+_[A-Za-z0-9]+\]"

        restored_text = text

        tokens = re.findall(pattern, text)

        for token in tokens:
            original_value = self.vault.restore_token(token)

            if original_value:
                restored_text = restored_text.replace(
                    token,
                    original_value
                )

        return restored_text
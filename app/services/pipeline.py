import re
import time

from detectors.combined_detector import CombinedDetector
from vault.token_vault import TokenVault
from logger.audit_logger import log_token_creation


class RedactionPipeline:
    """
    End-to-end PHI/PII Redaction Pipeline.

    Workflow
    --------
    1. Detect PHI/PII entities.
    2. Store or retrieve secure tokens from Redis.
    3. Replace original values with secure tokens.
    4. Restore original values when required.
    """

    def __init__(self):
        self.detector = CombinedDetector()
        self.vault = TokenVault()

    def process(self, text: str, return_metrics: bool = False):
        """
        Detect PHI/PII and replace each entity with a secure token.

        Parameters
        ----------
        text : str
            Clinical text to redact.

        return_metrics : bool
            If True, performance metrics are included in the response.
        """

        overall_start = time.perf_counter()

        # -----------------------------
        # Detection Stage
        # -----------------------------
        detection_start = time.perf_counter()

        detections = self.detector.detect(text)

        detection_time = (
            time.perf_counter() - detection_start
        ) * 1000

        redacted_text = text

        # Store generated token information
        detection_results = []

        # -----------------------------
        # Token Vault Stage
        # -----------------------------
        vault_time = 0.0

        # Replace from end to beginning
        # so character indexes remain valid.
        for d in sorted(
            detections,
            key=lambda x: x.start,
            reverse=True
        ):

            vault_start = time.perf_counter()

            token = self.vault.get_or_create_token(
                d.entity_type,
                d.text
            )

            vault_time += (
                time.perf_counter() - vault_start
            ) * 1000

            log_token_creation(
                d.entity_type,
                token
            )

            # Store detection information
            # including the generated token.
            detection_results.append(
                {
                    "entity_type": d.entity_type,
                    "text": d.text,
                    "start": d.start,
                    "end": d.end,
                    "source": d.source,
                    "token": token,
                }
            )

            # Replace original PHI/PII with token
            redacted_text = (
                redacted_text[:d.start]
                + token
                + redacted_text[d.end:]
            )

        # -----------------------------
        # Performance Metrics
        # -----------------------------
        total_time = (
            time.perf_counter() - overall_start
        ) * 1000

        # Restore original document order
        detection_results.sort(
            key=lambda x: x["start"]
        )

        # -----------------------------
        # API Response
        # -----------------------------
        result = {
            "redacted_text": redacted_text,
            "detections": detection_results,
        }

        if return_metrics:
            result["metrics"] = {
                "detection_ms": round(
                    detection_time,
                    2
                ),
                "vault_ms": round(
                    vault_time,
                    2
                ),
                "total_ms": round(
                    total_time,
                    2
                ),
                "entities_detected": len(
                    detections
                ),
            }

        return result

    def restore(self, text: str):
        """
        Restore secure tokens back to their
        original PHI values using Redis.
        """

        pattern = r"\[[A-Z]+_[A-Za-z0-9]+\]"

        restored_text = text

        tokens = re.findall(
            pattern,
            text
        )

        for token in tokens:

            original_value = (
                self.vault.restore_token(token)
            )

            if original_value:
                restored_text = (
                    restored_text.replace(
                        token,
                        original_value
                    )
                )

        return restored_text
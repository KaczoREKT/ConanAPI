import re

from Levenshtein import distance
from jiwer import wer

class Evaluation:
    def __init__(self):
        self.evaluation_dict = {
            'CER': self.cer_accuracy,
            'WER': self.wer_accuracy
        }
        self.current_evaluation = self.evaluation_dict['CER']

    def _normalize(self, s: str) -> str:
        s = s.lower().strip()
        s = re.sub(r"\s+", " ", s)
        return s

    def cer_accuracy(self, original_text:str, ocr_result:str) -> float:
        ref_n = self._normalize(original_text)
        hyp_n = self._normalize(ocr_result)
        if len(ref_n) == 0:
            return 100.0 if len(hyp_n) == 0 else 0.0
        cer = distance(ref_n, hyp_n) / len(ref_n)
        acc = max(0.0, 1.0 - cer) * 100.0
        return acc

    def wer_accuracy(self, original_text: str, ocr_result: str) -> float:
        w = wer(original_text, ocr_result)
        return max(0.0, 1.0 - w) * 100.0
    
    def full_evaluation(self, original_text, ocr_result):
        cer = self.cer_accuracy(original_text, ocr_result)
        wer = self.wer_accuracy(original_text, ocr_result)
        return f"CER: {cer:.2f}%, WER: {wer:.2f}%"

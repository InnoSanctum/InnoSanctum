from typing import Dict, List
from dataclasses import dataclass

class TransSegment:
    segment_number: int
    segment_text: str ## utf-8 stextring
    aligned_segment: int ## number of the aligned segment, if any
    #align_scores: List[int] ## list of segment numbers and scores; {number_of_eng_segment: alignment_score}

    def __init__(self, *, segment_number: int = -1, segment_text: str = '', aligned_segment: int = -1 , align_scores: List[int] = []):
        self.segment_number = segment_number
        self.segment_text = segment_text
        self.aligned_segment = aligned_segment
        #self.align_scores = align_scores

    def prn(self):
        print(f"{self.segment_number} : {self.segment_text} <==> {self.aligned_segment}")
    

@dataclass
class Segment:
    segment_number: int
    segment_text: str
    aligned_segment : int
    max_score: int
    source: bool

@dataclass
class dic_article:
    id: int
    eng_word: str
    ukr_word: str

@dataclass
class UsedItem:
    source_seg_no: int
    target_seg_no: int
    scr: int


def main():
    pass

if __name__ == '__main__':
    main()
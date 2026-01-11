import os
import re

import numpy as np
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


import json
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
import pandas as pd
from PIL import Image
import glob


def csv_yolo_to_coco(csv_path, images_dir):
    """Konwertuj YOLO CSV → COCO GT"""
    df = pd.read_csv(csv_path)
    df['area'] = (df.xmax - df.xmin) * (df.ymax - df.ymin)
    df['category_id'] = 1
    df['bbox'] = df[['xmin', 'ymin', 'xmax-xmin', 'ymax-ymin']].values.tolist()
    df['id'] = range(1, len(df) + 1)
    df['iscrowd'] = 0

    images = []
    img_id_map = {}
    img_id = 1
    for img_name in df.image_name.unique():
        img_path = os.path.join(images_dir, img_name)
        w, h = Image.open(img_path).size
        images.append({'id': img_id, 'file_name': img_name, 'width': w, 'height': h})
        img_id_map[img_name] = img_id
        img_id += 1
    df['image_id'] = df.image_name.map(img_id_map)

    coco_gt = {
        'images': images,
        'annotations': df[['id', 'image_id', 'category_id', 'bbox', 'area']].to_dict('records'),
        'categories': [{'id': 1, 'name': 'text_line'}]
    }
    return coco_gt, img_id_map

def merge_line(boxes_list):
    """Zwraca Python list, nie numpy"""
    boxes = np.array(boxes_list)
    return [
        float(boxes[:, 0].min()),
        float(boxes[:, 1].min()),
        float(boxes[:, 2].max()),
        float(boxes[:, 3].max())
    ]
def group_words_to_lines(keypoints, overlap_th=0.3):
    """keypoints [{'x':10,'y':20,'w':100,'h':30}, ...] → line bbox [[x1,y1,x2,y2]]"""
    if not keypoints:
        return []

    # Konwertuj na boxes [x1,y1,x2,y2]
    boxes = []
    for k in keypoints:
        boxes.append([k['x'], k['y'], k['x'] + k['w'], k['y'] + k['h']])
    boxes = np.array(boxes)

    # Sort po Y
    order = np.argsort(boxes[:, 1])
    boxes = boxes[order]

    lines = []
    for box in boxes:
        merged = False
        for i in range(len(lines)):
            line_boxes = lines[i]  # lista boxów w linii
            if y_overlap(line_boxes[-1], box) > overlap_th * (box[3] - box[1]):
                line_boxes.append(box)
                lines[i] = line_boxes  # update lista
                merged = True
                break
        if not merged:
            lines.append([box])

    # Konwertuj linie na pojedyncze bbox
    line_bboxes = []
    for line_boxes in lines:
        line_bboxes.append(merge_line(line_boxes))
    return line_bboxes


def y_overlap(b1, b2):
    return max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))


def merge_bbox(boxes):
    return [boxes[:, 0].min(), boxes[:, 1].min(), boxes[:, 2].max(), boxes[:, 3].max()]


def predictions_to_coco(keypoints, img_id):
    """Zwraca LISTĘ annotations dla JEDNEGO image_id"""
    lines = group_words_to_lines(keypoints)
    anns = []
    for line in lines:
        x1, y1, x2, y2 = line
        bbox = [x1, y1, x2-x1, y2-y1]
        anns.append({
            'image_id': img_id,
            'category_id': 1,
            'bbox': bbox,
            'score': 1.0,  # dummy confidence
            'area': bbox[2]*bbox[3],
            'iscrowd': 0,
        })
    return anns  # <- TYLKO lista dicts!



def yolo_txt_to_coco(labels_dir, images_dir, class_names=['text_line']):
    """labels_dir: /path/to/labels/*.txt, images_dir: /path/to/images/*.jpg"""
    images = []
    annotations = []
    img_id = 0
    ann_id = 0

    img_files = glob.glob(os.path.join(images_dir, '*.jpg')) + glob.glob(os.path.join(images_dir, '*.png'))

    for img_path in sorted(img_files):
        img_name = os.path.basename(img_path)
        label_path = os.path.join(labels_dir, img_name.replace('.jpg', '.txt').replace('.png', '.txt'))

        # Image info
        w, h = Image.open(img_path).size
        img_id += 1
        images.append({'id': img_id, 'file_name': img_name, 'width': w, 'height': h})

        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    cls, xc, yc, bw, bh = map(float, line.strip().split())
                    x = (xc - bw / 2) * w
                    y = (yc - bh / 2) * h
                    ww = bw * w
                    hh = bh * h
                    ann_id += 1
                    annotations.append({
                        'id': ann_id,
                        'image_id': img_id,
                        'category_id': int(cls) + 1,
                        'bbox': [x, y, ww, hh],
                        'area': ww * hh,
                        'iscrowd': 0
                    })

    coco = {
        'images': images,
        'annotations': annotations,
        'categories': [{'id': i + 1, 'name': name} for i, name in enumerate(class_names)]
    }
    return coco

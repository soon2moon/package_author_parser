def f1_score(result, reference):
    gt_set = set(result)
    pred_set = set(reference)

    tp = len(gt_set & pred_set)
    fp = len(pred_set - gt_set)
    fn = len(gt_set - pred_set)

    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1_score = (2 * precision * recall) / max(precision + recall, 1)

    return { "f1_score": f1_score, "precision": precision, "recall": recall }
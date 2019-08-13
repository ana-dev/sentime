def get_confusion_matrix(true_tags, predicted_tags):
    tags = set(true_tags + predicted_tags)
    confusion_matrix = {true_tag: {pred_tag: 0 for pred_tag in tags} for true_tag in tags }
    for true_tag, pred_tag in zip(true_tags, predicted_tags):
        confusion_matrix[true_tag][pred_tag] += 1
    return confusion_matrix


def get_class_recalls(confusion_matrix):
    class_recalls = {}
    for true_tag, predictions in confusion_matrix.items():
        class_recalls[true_tag] = predictions[true_tag] / sum(predictions.values())
    return class_recalls


def get_class_precisions(confusion_matrix):
    class_sum = {tag: 0 for tag, predictions in confusion_matrix.items()}
    for true_tag, predictions in confusion_matrix.items():
        for pred_tag, count in predictions.items():
            class_sum[pred_tag] += count
    class_precisions = {}
    for tag, count in class_sum.items():
        class_precisions[tag] = confusion_matrix[tag][tag] / count
    return class_precisions


def get_average_recall(confusion_matrix):
    recalls = get_class_recalls(confusion_matrix)
    return sum(recalls.values()) / len(recalls)


def get_average_precision(confusion_matrix):
    precisions = get_class_precisions(confusion_matrix)
    return sum(precisions.values()) / len(precisions)

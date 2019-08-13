from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

from sqlalchemy import case

import logic.file as file_logic
import logic.net as net_logic

from models import EmbeddingModel, db, File, NetModule, Net, NetStatus
from netword_metrics.confusion_matrix import get_class_precisions, get_class_recalls, get_average_precision, \
    get_average_recall

net_bp = Blueprint('net', __name__)


def to_datetime(queryDateString):
    return datetime.strptime(queryDateString, "%d.%m.%Y")


def to_net_status(status):
    for index, value in enumerate(NetStatus):
        if status == value.name:
            return value
    return None


def to_int(int_str):
    return int(int_str)


@net_bp.route("/net-modules", methods=["GET"])
def get_all_net_modules():
    modules = db.session.query(NetModule).all()
    return jsonify([module.to_dict(_hide=[]) for module in modules])


@net_bp.route("/trained", methods=["GET"])
def get_trained_only():
    nets = db.session.query(Net).filter(Net.status == NetStatus.trained)
    return jsonify([net.to_dict(_hide=[]) for net in nets])


@net_bp.route("/", methods=["GET"])
def get_all():
    from_index = request.args.get('from', 0, type=int)
    to_index = request.args.get('to', 9, type=int)
    if from_index > to_index:
        tmp_index = from_index
        from_index = to_index
        to_index = tmp_index
    if to_index - from_index > 50:
        raise ValueError('Can not return more than 50 net records')

    direction = request.args.get('sort_direction', 'asc')
    if direction != 'asc' and direction != 'desc':
        raise ValueError('Direction {} is not allowed'.format(direction))

    sort_field_name = request.args.get('sort_field', 'updated_time')
    if sort_field_name not in ('updated_time', 'name', 'status', 'net_module_name', 'embedding_model_name'):
        raise ValueError('Sort field {} is not allowed'.format(sort_field_name))

    default_from_updated_time = datetime.today() - timedelta(days=7)
    from_updated_time = request.args.get('from_updated_time', default=default_from_updated_time, type=to_datetime)

    default_to_updated_time = datetime.today()
    to_updated_time = request.args.get('to_updated_time', default=default_to_updated_time, type=to_datetime) + timedelta(days=1)

    name = request.args.get('name', default=None)

    status = request.args.get('status', default=None, type=to_net_status)

    net_module_id = request.args.get('net_module_id', default=None, type=int)

    embedding_model_name = request.args.get('embedding_model_name', default=None)

    embedding_method_id = request.args.get('embedding_method_id', default=None, type=int)

    nets = db.session.query(Net)
    nets = nets.filter(Net.updated_time.between(from_updated_time, to_updated_time))
    if name is not None and name:
        nets = nets.filter(Net.name.contains(name))
    if status is not None:
        nets = nets.filter(Net.status == status)
    if net_module_id is not None:
        nets = nets.filter(Net.net_module_id == net_module_id)
    if embedding_model_name is not None and embedding_model_name:
        nets = nets.filter(Net.embedding_model.name.contains(embedding_model_name))
    if embedding_method_id is not None:
        nets = nets.filter(Net.embedding_model.embedding_method_id == embedding_method_id)

    status_indexes = {status: index for index, status in enumerate(NetStatus)}
    status_sort_logic = case(value=Net.status, whens=status_indexes).label("status")
    nets = {
        ('updated_time', 'desc'): nets.order_by(Net.updated_time.desc()),
        ('updated_time', 'asc'): nets.order_by(Net.updated_time.asc()),
        ('name', 'desc'): nets.order_by(Net.name.desc()),
        ('name', 'asc'): nets.order_by(Net.name.asc()),
        ('status', 'desc'): nets.order_by(status_sort_logic),
        ('status', 'asc'): nets.order_by(status_sort_logic),
        ('net_module_name', 'desc'): nets.join(NetModule, Net.net_module).order_by(NetModule.name.desc()),
        ('net_module_name', 'asc'): nets.join(NetModule, Net.net_module).order_by(NetModule.name.asc()),
        ('embedding_model_name', 'desc'): nets.join(EmbeddingModel, Net.embedding_model).order_by(EmbeddingModel.name.desc()),
        ('embedding_model_name', 'asc'): nets.join(EmbeddingModel, Net.embedding_model).order_by(EmbeddingModel.name.asc()),
    }[(sort_field_name, direction)]
    all_count = nets.count()
    nets = nets.limit(to_index-from_index).offset(from_index)
    return jsonify({'count': all_count, 'nets': [net.to_dict(_hide=[]) for net in nets]})


@net_bp.route('/<net_id>', methods=["GET"])
def get(net_id):
    net_id = int(net_id)
    net = net_logic.get(net_id)
    net_info = net.to_dict(_hide=["epochs.epoch_confusion_matrix"])
    for epoch in net.epochs:
        epoch_info = next(epoch_info for epoch_info in net_info["epochs"] if epoch_info["id"] == epoch.id)
        epoch_info["confusion_matrix"] = net_logic.get_confusion_matrix(epoch.id)
        epoch_info["class_precisions"] = get_class_precisions(epoch_info["confusion_matrix"])
        epoch_info["class_recalls"] = get_class_recalls(epoch_info["confusion_matrix"])
        epoch_info["average_precision"] = get_average_precision(epoch_info["confusion_matrix"])
        epoch_info["average_recall"] = get_average_recall(epoch_info["confusion_matrix"])
    return jsonify(net_info)


@net_bp.route('/<net_id>', methods=["DELETE"])
def delete(net_id):
    net_id = int(net_id)
    try:
        net = net_logic.delete(net_id)
    except:
        return jsonify({'success': False})
    return jsonify({'success': True})


@net_bp.route("/", methods=["PUT"])
def create():
    net = Net()
    net.from_dict(**request.json)
    db.session.add(net)
    db.session.commit()
    return jsonify(net.to_dict(_hide=[]))


@net_bp.route("/train", methods=["POST"])
def train():
    net_id = int(request.form["net_id"])
    net = net_logic.get(net_id)  # type: Net

    separator = request.form["separator"]
    text_column = int(request.form["text_column"])
    tag_column = int(request.form["tag_column"])
    positive_tag = request.form["positive_tag"]
    negative_tag = request.form["negative_tag"]
    uploaded_files = []
    for filename, file_stream in request.files.items():
        file = File()
        file.separator = separator
        file.text_column = text_column
        file.tag_column = tag_column
        file.positive_tag = positive_tag
        file.negative_tag = negative_tag
        uploaded_files.append(file_logic.save(file, file_stream))

    extend_vocabulary = True if request.form["extend_vocabulary"] == "true" else False

    net = net_logic.init_training(net.id, [file.id for file in uploaded_files], extend_vocabulary)

    net_info = net.to_dict(_hide=[])
    return jsonify(net_info)


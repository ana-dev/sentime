from flask import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.event import listens_for
from sqlalchemy.orm.attributes import QueryableAttribute
from datetime import datetime
from sqlalchemy.exc import IntegrityError, OperationalError
from enum import Enum
from datetime import time

from sqlalchemy.orm.base import NO_VALUE, NEVER_SET

from validation.errorinfo import FieldError, ObjectError

db = SQLAlchemy()


def validatable(cls):
    cls.register_validators()
    return cls


class BaseModel(db.Model):
    __abstract__ = True

    @classmethod
    def register_validators(cls):
        raise NotImplementedError()

    @staticmethod
    def __register_col_validators__(col, validators):
        @listens_for(col, 'set', retval=True)
        def validate(instance, value, oldvalue, initiator):
            errors = []
            new_value = value
            for validator in validators:
                validator_errors, validator_value = validator.validate(value)
                errors.extend(validator_errors)
                new_value = validator_value
            if errors:
                raise FieldError(initiator.key, errors)
            return new_value

    def to_dict(self, show=None, _hide=[], _path=None):
        """Return a dictionary representation of this model."""

        show = show or []

        hidden = self._hidden_fields if hasattr(self, "_hidden_fields") else []
        default = self._default_fields if hasattr(self, "_default_fields") else []
        default.extend(['id', 'modified_at', 'created_at'])

        if not _path:
            _path = self.__tablename__.lower()

            def prepend_path(item):
                item = item.lower()
                if item.split(".", 1)[0] == _path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != ".":
                    item = ".%s" % item
                item = "%s%s" % (_path, item)
                return item

            _hide[:] = [prepend_path(x) for x in _hide]
            show[:] = [prepend_path(x) for x in show]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        ret_data = {}

        for key in columns:
            if key.startswith("_"):
                continue
            check = "%s.%s" % (_path, key)
            if check in _hide or key in hidden:
                continue
            if check in show or key in default:
                column_type = self.__table__.columns[key].type.python_type
                attr_val = getattr(self, key)
                if issubclass(column_type, Enum):
                    attr_val = attr_val.name
                elif column_type is time and attr_val is not None:
                    attr_val = attr_val.strftime("%d.%m.%Y %H:%M:%S")
                elif column_type is datetime and attr_val is not None:
                    attr_val = attr_val.strftime("%d.%m.%Y %H:%M:%S")
                ret_data[key] = attr_val

        for key in relationships:
            if key.startswith("_"):
                continue
            check = "%s.%s" % (_path, key)
            if check in _hide or key in hidden:
                continue
            if check in show or key in default:
                _hide.append(check)
                is_list = self.__mapper__.relationships[key].uselist
                if is_list:
                    items = getattr(self, key)
                    if self.__mapper__.relationships[key].query_class is not None:
                        if hasattr(items, "all"):
                            items = items.all()
                    ret_data[key] = []
                    for item in items:
                        ret_data[key].append(
                            item.to_dict(
                                show=list(show),
                                _hide=list(_hide),
                                _path=("%s.%s" % (_path, key.lower())),
                            )
                        )
                else:
                    if (
                        self.__mapper__.relationships[key].query_class is not None
                        or self.__mapper__.relationships[key].instrument_class
                        is not None
                    ):
                        item = getattr(self, key)
                        if item is not None:
                            ret_data[key] = item.to_dict(
                                show=list(show),
                                _hide=list(_hide),
                                _path=("%s.%s" % (_path, key.lower())),
                            )
                        else:
                            ret_data[key] = None
                    else:
                        ret_data[key] = getattr(self, key)

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith("_"):
                continue
            if not hasattr(self.__class__, key):
                continue
            attr = getattr(self.__class__, key)
            if not (isinstance(attr, property) or isinstance(attr, QueryableAttribute)):
                continue
            check = "%s.%s" % (_path, key)
            if check in _hide or key in hidden:
                continue
            if check in show or key in default:
                val = getattr(self, key)
                if hasattr(val, "to_dict"):
                    ret_data[key] = val.to_dict(
                        show=list(show),
                        _hide=list(_hide),
                        _path=('%s.%s' % (_path, key.lower())),
                    )
                else:
                    try:
                        ret_data[key] = json.loads(json.dumps(val))
                    except:
                        pass

        return ret_data

    def from_dict(self, **kwargs):
        """Update this model with a dictionary."""

        _force = kwargs.pop("_force", False)

        readonly = self._readonly_fields if hasattr(self, "_readonly_fields") else []
        if hasattr(self, "_hidden_fields"):
            readonly += self._hidden_fields

        readonly += ["id", "created_at", "modified_at"]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        changes = {}
        errors = []

        for key in columns:
            if key.startswith("_"):
                continue
            allowed = True if _force or key not in readonly else False
            exists = True if key in kwargs else False
            if allowed and exists:
                val = getattr(self, key)
                if val != kwargs[key]:
                    try:
                        column_type = self.__table__.columns[key].type.python_type
                    except Exception:
                        continue
                    if issubclass(column_type, Enum):
                        attr_val = column_type[kwargs[key]]
                    elif column_type is time:
                        attr_val = datetime.strptime(kwargs[key], "%d.%m.%Y %H:%M:%S")
                    elif column_type is datetime:
                        attr_val = datetime.strptime(kwargs[key], "%d.%m.%Y %H:%M:%S")
                    else:
                        attr_val = kwargs[key]
                    changes[key] = {"old": val, "new": attr_val}
                    try:
                        setattr(self, key, attr_val)
                    except FieldError as e:
                        errors.append(e)

        for rel in relationships:
            if rel.startswith("_"):
                continue
            allowed = True if _force or rel not in readonly else False
            exists = True if rel in kwargs else False
            if allowed and exists:
                is_list = self.__mapper__.relationships[rel].uselist
                if is_list:
                    valid_ids = []
                    rel_list = getattr(self, rel)
                    # query = getattr(self, rel)
                    cls = self.__mapper__.relationships[rel].argument()
                    for item in kwargs[rel]:
                        if (
                                "id" in item
                                and any(x for x in rel_list if x.id == item["id"])
                                # and query.filter_by(id=item["id"]).limit(1).count() == 1
                        ):
                            obj = cls.query.filter_by(id=item["id"]).first()
                            col_changes = obj.from_dict(**item)
                            if col_changes:
                                col_changes["id"] = str(item["id"])
                                if rel in changes:
                                    changes[rel].append(col_changes)
                                else:
                                    changes.update({rel: [col_changes]})
                            valid_ids.append(str(item["id"]))
                        else:
                            col = cls()
                            col_changes = col.from_dict(**item)
                            rel_list.append(col)
                            # query.append(col)
                            db.session.flush()
                            if col_changes:
                                col_changes["id"] = str(col.id)
                                if rel in changes:
                                    changes[rel].append(col_changes)
                                else:
                                    changes.update({rel: [col_changes]})
                            if col.id is not None:
                                valid_ids.append(str(col.id))

                    # delete rows from relationship that were not in kwargs[rel]
                    for item in [x for x in rel_list if x.id is not None and x.id not in valid_ids]:
                    # for item in query.filter(not_(cls.id.in_(valid_ids))).all():
                        col_changes = {"id": str(item.id), "deleted": True}
                        if rel in changes:
                            changes[rel].append(col_changes)
                        else:
                            changes.update({rel: [col_changes]})
                        db.session.delete(item)

                else:
                    val = getattr(self, rel)
                    if self.__mapper__.relationships[rel].query_class is not None:
                        if val is not None:
                            col_changes = val.from_dict(**kwargs[rel])
                            if col_changes:
                                changes.update({rel: col_changes})
                    else:
                        if val != kwargs[rel]:
                            setattr(self, rel, kwargs[rel])
                            changes[rel] = {"old": val, "new": kwargs[rel]}

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith("_"):
                continue
            allowed = True if _force or key not in readonly else False
            exists = True if key in kwargs else False
            if allowed and exists and getattr(self.__class__, key).fset is not None:
                val = getattr(self, key)
                if hasattr(val, "to_dict"):
                    val = val.to_dict()
                changes[key] = {"old": val, "new": kwargs[key]}
                setattr(self, key, kwargs[key])
        if errors:
            raise ObjectError(type(self).__name__, errors)
        return changes

    @classmethod
    def _get_or_create(
            cls,
            _session=None,
            _filters=None,
            _defaults={},
            _retry_count=0,
            _max_retries=3,
            **kwargs
    ):
        if not _session:
            _session = db.session
        query = _session.query(cls)
        if _filters is not None:
            query = query.filter(*_filters)
        if len(kwargs) > 0:
            query = query.filter_by(**kwargs)

        instance = query.first()
        if instance is not None:
            return instance, False

        _session.begin_nested()
        try:
            kwargs.update(_defaults)
            instance = cls(**kwargs)
            _session.add(instance)
            _session.commit()
            return instance, True

        except IntegrityError:
            _session.rollback()
            instance = query.first()
            if instance is None:
                raise
            return instance, False

        except OperationalError:
            _session.rollback()
            instance = query.first()
            if instance is None:
                if _retry_count < _max_retries:
                    return cls._get_or_create(
                        _filters=_filters,
                        _defaults=_defaults,
                        _retry_count=_retry_count + 1,
                        _max_retries=_max_retries,
                        **kwargs
                    )
                raise
            return instance, False

    @classmethod
    def get_or_create(cls, **kwargs):
        return cls._get_or_create(**kwargs)[0]

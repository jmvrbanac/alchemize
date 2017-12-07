"""
Copyright 2014 John Vrbanac

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class Attr(object):
    """ Attribute Definition

    :param name: Python attribute name
    :param type: Attribute type (e.g str, int, dict, etc)
    :param serialize: Determines if the attribute can be serialized
    :param required: Forces attribute to be defined
    :param coerce: Forces attribute to be coerced to its type (primitive types)
    """
    def __init__(self, attr_name, attr_type, serialize=True, required=False,
                 coerce=None):
        self.name = attr_name
        self.type = attr_type
        self.serialize = serialize
        self.required = required
        self.coerce = coerce


class ExpandedType(object):
    """Custom Expanded Type Definition (Unstable Feature)"""
    cls = None

    @classmethod
    def check_type(cls, inst):
        if issubclass(type(inst), type):
            return issubclass(inst, cls.cls)
        else:
            return isinstance(inst, cls.cls)

    @classmethod
    def serialize(cls, value):
        """Serialization implementation for the type."""
        pass

    @classmethod
    def deserialize(cls, attr_type, value):
        """Deserialization implementation for the type."""
        pass


class BaseMappedModel(object):
    __wrapped_attr_name__ = None
    __mapping__ = {}

    @classmethod
    def __get_full_mapping__(cls):
        full_mapping = {}
        sub_classes = [sub_class for sub_class in cls.mro()
                       if issubclass(sub_class, BaseMappedModel)]

        # Invert so we are updating layering mappings from the bottom up
        sub_classes.reverse()

        for sub_class in sub_classes:
            full_mapping.update(sub_class.__mapping__)

        return full_mapping


class JsonMappedModel(BaseMappedModel):
    """Creates an explicit mapping for de/serialization by the JsonTransmuter


    **Map Structure**::

        'json_attr_name': Attr('python_attr_name', StorageType)

    **Mapping Types**::

        __mapping__ = {
            'name': Attr('name', str),
            'number': Attr('number', int),
            'dict': Attr('sample_dict', dict),
            'list': Attr('sample_list', list),
            'child': Attr('child', ChildModel),
            'children': Attr('children', [ChildModel])
        }

    """
    pass


def get_normalized_map(model):
    """Normalizes mapping data to support backward compatibility."""
    key_map = {}

    for key, map_obj in model.__get_full_mapping__().items():
        if not isinstance(map_obj, Attr):
            key_map[key] = Attr(map_obj[0], map_obj[1])
        else:
            key_map[key] = map_obj

    return key_map


def is_mapped_model(obj):
    return isinstance(obj, type) and issubclass(obj, BaseMappedModel)


def get_key_paths(model, sep='/', prefix=''):
    """Walks a model class and returns a list of all key paths

    :param model: Mapped Model instance or class
    :param sep: Separator used to join the keys together
    :param prefix: Prefix to add to all keys

    :return: List of key paths
    """
    key_list = []

    for key, attr in get_normalized_map(model).items():
        full_key_name = '{pre}{sep}{key}'.format(
            pre=prefix,
            sep=sep,
            key=key
        )

        if is_mapped_model(attr.type):
            key_list.extend(
                get_key_paths(
                    attr.type,
                    sep=sep,
                    prefix=full_key_name
                )
            )

        elif (isinstance(attr.type, list)
                and len(attr.type) == 1
                and is_mapped_model(attr.type[0])):
            key_list.extend(
                get_key_paths(
                    attr.type[0],
                    sep=sep,
                    prefix=full_key_name
                )
            )

        else:
            key_list.append(full_key_name)

    return key_list

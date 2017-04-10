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
    """
    def __init__(self, attr_name, attr_type, serialize=True):

        self.name = attr_name
        self.type = attr_type
        self.serialize = serialize


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

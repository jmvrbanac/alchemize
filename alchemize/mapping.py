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


class BaseMappedModel(object):
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

        'json_attr_name': ['python_attr_name', StorageType]

    **Mapping Types**::

        __mapping__ = {
            'name': ['name', str],
            'number': ['number', int],
            'dict': ['sample_dict', dict],
            'list': ['sample_list', list],
            'child': ['child', ChildModel],
            'children': ['children', [ChildModel]]
        }

    """
    pass

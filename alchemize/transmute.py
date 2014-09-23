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
import json
import types
from abc import ABCMeta, abstractmethod

from alchemize.mapping import JsonMappedModel


NON_CONVERSION_TYPES = [
    types.BooleanType,
    types.DictType,
    types.DictionaryType,
    types.FloatType,
    types.IntType,
    types.ListType,
    types.LongType,
    types.NoneType,
    types.StringType,
    types.UnicodeType
]


class UnsupportedMappedModelError(Exception):
    """Exception that is raised when attempting to transmute a model that
    is not supported by the specified transmuter.
    """
    pass


class AbstractBaseTransmuter(object):
    """The abtract base class from which all Transmuters are built."""
    __metaclass__ = ABCMeta
    __supported_base_mappings__ = []

    @classmethod
    def _check_supported_mapping(cls, mapped_model, ignore_failure=False):
        """Checks the passed mapped model type if it's compatible with the
            specified support base mappings.
        """
        if not isinstance(mapped_model, type):
            return False

        results = [issubclass(mapped_model, map_type)
                   for map_type in cls.__supported_base_mappings__]

        if not ignore_failure and False in results:
            raise UnsupportedMappedModelError()

        return False not in results

    @classmethod
    @abstractmethod
    def transmute_to(cls, mapped_model):
        """Generic Abstract Base Method to convert to serialized form

        :param mapped_model: An instance of a class based from BaseMappedModel.
        :returns: A serialized or serializable form of your mapped model.
        """
        cls._check_supported_mapping(mapped_model)

    @classmethod
    @abstractmethod
    def transmute_from(cls, data, mapped_model_type):
        """Generic Abstract Base Method to deserialize into a Python object

        :param mapped_model_type: A type that extends BaseMappedModel.
        :returns: The an instance of the passed in mapped model type
            containing the deserialized data.
        """
        cls._check_supported_mapping(mapped_model_type)


class JsonTransmuter(AbstractBaseTransmuter):
    __supported_base_mappings__ = [JsonMappedModel]

    @classmethod
    def is_list_of_mapping_types(cls, attr_type):
        if isinstance(attr_type, types.ListType) and len(attr_type) == 1:
            if cls._check_supported_mapping(attr_type[0]):
                return True
        return False

    @classmethod
    def transmute_to(cls, mapped_model, to_string=True):
        """Converts a model based off of a JsonMappedModel into JSON.

        :param mapped_model: An instance of a subclass of JsonMappedModel.
        :param to_string: Boolean value to disable the return of a string
            and return a dictionary instead.
        :returns: A string or dictionary containing the JSON form of your
            mapped model.
        """
        super(JsonTransmuter, cls).transmute_to(mapped_model)
        result = {}

        for json_key, map_list in mapped_model.__get_full_mapping__().items():
            attr_name, attr_type = map_list[0], map_list[1]

            if hasattr(mapped_model, attr_name):
                current_value = getattr(mapped_model, attr_name)
                # Convert a single mapped object
                if cls._check_supported_mapping(attr_type, True):
                    attr_value = cls.transmute_to(current_value, False)

                # Converts lists of mapped objects
                elif (cls.is_list_of_mapping_types(attr_type)
                      and isinstance(current_value, types.ListType)):
                    attr_value = [cls.transmute_to(child, False)
                                  for child in current_value]

                # Converts all other objects (if possible)
                elif attr_type in NON_CONVERSION_TYPES:
                    attr_value = current_value

                result[json_key] = attr_value

        return json.dumps(result) if to_string else result

    @classmethod
    def transmute_from(cls, data, mapped_model_type):
        """Converts a JSON string or dict into a corresponding Mapping Object.

        :param data: JSON data in string or dictionary form.
        :param mapped_model_type: A type that extends the JsonMappedModel base.
        :returns: An instance of your mapped model type.
        """
        super(JsonTransmuter, cls).transmute_from(data, mapped_model_type)

        json_dict = data
        if isinstance(data, types.StringType):
            json_dict = json.loads(data)

        mapped_obj = mapped_model_type()
        for key, val in json_dict.items():
            map_list = mapped_model_type.__get_full_mapping__().get(key)
            if map_list and len(map_list) == 2:
                attr_name, attr_type = map_list[0], map_list[1]

                attr_value = None

                # Convert a single mapped object
                if cls._check_supported_mapping(attr_type, True):
                    attr_value = cls.transmute_from(val, attr_type)

                # Converts lists of mapped objects
                elif (cls.is_list_of_mapping_types(attr_type)
                      and isinstance(val, types.ListType)):
                    attr_value = [cls.transmute_from(child, attr_type[0])
                                  for child in val]

                # Converts all other objects (if possible)
                elif attr_type in NON_CONVERSION_TYPES:
                    attr_value = val

                # Add mapped value to the new mapped_obj is possible
                setattr(mapped_obj, attr_name, attr_value)

        return mapped_obj

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
import six
from abc import ABCMeta, abstractmethod

from alchemize.mapping import JsonMappedModel, Attr


NON_CONVERSION_TYPES = [
    bool,
    dict,
    float,
    int,
    list,
    type(None),
    str,
    six.integer_types,
    six.string_types
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

    @classmethod
    def is_list_of_mapping_types(cls, attr_type):
        if isinstance(attr_type, list) and len(attr_type) == 1:
            if cls._check_supported_mapping(attr_type[0]):
                return True
        return False


class JsonTransmuter(AbstractBaseTransmuter):
    __supported_base_mappings__ = [JsonMappedModel]

    @classmethod
    def transmute_to(cls, mapped_model, to_string=True, assign_all=False,
                     coerce_values=True, serialize_all=False):
        """Converts a model based off of a JsonMappedModel into JSON.

        :param mapped_model: An instance of a subclass of JsonMappedModel.
        :param to_string: Boolean value to disable the return of a string
            and return a dictionary instead.
        :param assign_all: Boolean value to force assignment of all values,
            including null values.
        :param coerce_values: Boolean value to allow for values with python
            types to be coerced with their mapped type.
        :param serialize_all: Boolean value that allows for you to force
            serialization of values regardless of the attribute settings.
        :returns: A string or dictionary containing the JSON form of your
            mapped model.
        """
        super(JsonTransmuter, cls).transmute_to(mapped_model)
        result = {}

        for json_key, map_obj in mapped_model.__get_full_mapping__().items():

            # For backwards compatibility
            if not isinstance(map_obj, Attr):
                map_obj = Attr(map_obj[0], map_obj[1])

            # Make we ignore values that shouldn't be serialized
            if not serialize_all and not map_obj.serialize:
                continue

            attr_name, attr_type = map_obj.name, map_obj.type
            attr_value = None

            if hasattr(mapped_model, attr_name):
                current_value = getattr(mapped_model, attr_name)
                # Convert a single mapped object
                if cls._check_supported_mapping(attr_type, True):
                    attr_value = cls.transmute_to(current_value, False)

                # Converts lists of mapped objects
                elif (cls.is_list_of_mapping_types(attr_type)
                      and isinstance(current_value, list)):
                    attr_value = [cls.transmute_to(child, False)
                                  for child in current_value]

                # Converts all other objects (if possible)
                elif attr_type in NON_CONVERSION_TYPES:
                    attr_value = current_value

                    if coerce_values:
                        attr_value = attr_type(attr_value)

                if assign_all or attr_value is not None:
                    result[json_key] = attr_value

        # Support Attribute Wrapping
        if mapped_model.__wrapped_attr_name__:
            result = {mapped_model.__wrapped_attr_name__: result}

        return json.dumps(result) if to_string else result

    @classmethod
    def transmute_from(cls, data, mapped_model_type, coerce_values=False):
        """Converts a JSON string or dict into a corresponding Mapping Object.

        :param data: JSON data in string or dictionary form.
        :param mapped_model_type: A type that extends the JsonMappedModel base.
        :param coerce_values: Boolean value to allow for values with python
            types to be coerced with their mapped type.
        :returns: An instance of your mapped model type.
        """
        super(JsonTransmuter, cls).transmute_from(data, mapped_model_type)

        json_dict = data
        if isinstance(data, six.string_types):
            json_dict = json.loads(data)

        mapped_obj = mapped_model_type()

        # Support Attribute Wrapping
        if mapped_obj.__wrapped_attr_name__:
            json_dict = json_dict.get(mapped_obj.__wrapped_attr_name__)

        for key, val in json_dict.items():
            map_obj = mapped_model_type.__get_full_mapping__().get(key)
            if map_obj:
                # For backwards compatibility
                if not isinstance(map_obj, Attr):
                    map_obj = Attr(map_obj[0], map_obj[1])

                attr_name, attr_type = map_obj.name, map_obj.type
                attr_value = None

                # Convert a single mapped object
                if cls._check_supported_mapping(attr_type, True):
                    attr_value = cls.transmute_from(
                        val,
                        attr_type,
                        coerce_values
                    )

                # Converts lists of mapped objects
                elif (cls.is_list_of_mapping_types(attr_type)
                      and isinstance(val, list)):
                    attr_value = [
                        cls.transmute_from(child, attr_type[0], coerce_values)
                        for child in val
                    ]

                # Converts all other objects (if possible)
                elif attr_type in NON_CONVERSION_TYPES:
                    attr_value = val

                    if coerce_values:
                        attr_value = attr_type(attr_value)

                # Add mapped value to the new mapped_obj is possible
                setattr(mapped_obj, attr_name, attr_value)

        return mapped_obj

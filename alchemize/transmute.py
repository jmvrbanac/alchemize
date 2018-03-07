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

from alchemize.mapping import ExpandedType, JsonMappedModel, get_normalized_map


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

EXPANDED_TYPES = []


def register_type(custom_type):
    """Adds a custom expanded type (unstable feature)."""
    EXPANDED_TYPES.append(custom_type)


def remove_type(custom_type):
    """Removes a custom expanded type (unstable feature)."""
    EXPANDED_TYPES.remove(custom_type)


try:
    import enum

    class EnumType(ExpandedType):
        cls = enum.Enum

        @classmethod
        def serialize(cls, value):
            return value.value

        @classmethod
        def deserialize(cls, attr_type, value):
            return attr_type(value)

    register_type(EnumType)
except ImportError:  # pragma: no cover
    pass


class AlchemizeError(Exception):
    """Base Exception for all Alchemize errors."""
    pass


class UnsupportedMappedModelError(AlchemizeError):
    """Exception that is raised when attempting to transmute a model that
    is not supported by the specified transmuter.
    """
    pass


class RequiredAttributeError(AlchemizeError):
    """Exception that is raised when attempting to retrieve/apply an
    attribute that isn't available.
    """
    def __init__(self, attribute_name):
        super(RequiredAttributeError, self).__init__(
            'Attribute "{}" is required'.format(attribute_name)
        )


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
                     coerce_values=True, serialize_all=False, encoder=None,
                     encoder_kwargs=None):
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
        :param encoder: module that implements dumps(...).
        :param encoder_kwargs: A dictionary containing kwargs to be used
            with the encoder.
        :returns: A string or dictionary containing the JSON form of your
            mapped model.
        """
        super(JsonTransmuter, cls).transmute_to(mapped_model)
        result = {}
        encoder = encoder or json
        encoder_kwargs = encoder_kwargs or {}

        for name, attr in get_normalized_map(mapped_model).items():
            attr_value = None

            # Make we ignore values that shouldn't be serialized
            if not serialize_all and not attr.serialize:
                continue

            if hasattr(mapped_model, attr.name):
                current_value = getattr(mapped_model, attr.name)
                # Convert a single mapped object
                if cls._check_supported_mapping(attr.type, True):
                    attr_value = cls.transmute_to(
                        mapped_model=current_value,
                        to_string=False,
                        assign_all=assign_all,
                        coerce_values=coerce_values,
                        serialize_all=serialize_all
                    )

                # Converts lists of mapped objects
                elif (cls.is_list_of_mapping_types(attr.type)
                      and isinstance(current_value, list)):
                    attr_value = [
                        cls.transmute_to(
                            mapped_model=child,
                            to_string=False,
                            assign_all=assign_all,
                            coerce_values=coerce_values,
                            serialize_all=serialize_all
                        )
                        for child in current_value
                    ]

                # Converts all other objects (if possible)
                elif attr.type in NON_CONVERSION_TYPES:
                    attr_value = current_value
                    should_coerce = coerce_values

                    if attr.coerce is not None:
                        should_coerce = attr.coerce

                    if should_coerce:
                        # If someone attempts to coerce a None to a dict type
                        if attr.type == dict and not attr_value:
                            attr_value = {}

                        attr_value = attr.type(attr_value)

                # Support Expanded Types
                else:
                    find_exp_type = (
                        item
                        for item in EXPANDED_TYPES
                        if item.check_type(current_value)
                    )

                    item = next(find_exp_type, None)

                    if item:
                        attr_value = item.serialize(current_value)

                if assign_all or attr_value is not None:
                    result[name] = attr_value

            elif attr.required:
                raise RequiredAttributeError(attr.name)

        # Support Attribute Wrapping
        if mapped_model.__wrapped_attr_name__:
            result = {mapped_model.__wrapped_attr_name__: result}

        return encoder.dumps(result, **encoder_kwargs) if to_string else result

    @classmethod
    def transmute_from(cls, data, mapped_model_type, coerce_values=False,
                       decoder=None, decoder_kwargs=None):
        """Converts a JSON string or dict into a corresponding Mapping Object.

        :param data: JSON data in string or dictionary form.
        :param mapped_model_type: A type that extends the JsonMappedModel base.
        :param coerce_values: Boolean value to allow for values with python
            types to be coerced with their mapped type.
        :param decoder: A module that implements loads(...).
        :param decoder_kwargs: A dictionary containing kwargs to use
            with the decoder.
        :returns: An instance of your mapped model type.
        """
        super(JsonTransmuter, cls).transmute_from(data, mapped_model_type)
        decoder = decoder or json
        decoder_kwargs = decoder_kwargs or {}

        json_dict = data
        if isinstance(data, six.string_types):
            json_dict = decoder.loads(data, **decoder_kwargs)

        mapped_obj = mapped_model_type()

        # Support Attribute Wrapping
        if mapped_obj.__wrapped_attr_name__:
            json_dict = json_dict.get(mapped_obj.__wrapped_attr_name__)

        for name, attr in get_normalized_map(mapped_model_type).items():
            val = json_dict.get(name)
            attr_value = None

            if attr.required and val is None:
                raise RequiredAttributeError(name)

            # PERF: If the value isn't there, lets just skip-on forward
            elif val is None:
                continue

            # Convert a single mapped object
            if cls._check_supported_mapping(attr.type, True):
                attr_value = cls.transmute_from(val, attr.type, coerce_values)

            # Converts lists of mapped objects
            elif (cls.is_list_of_mapping_types(attr.type)
                  and isinstance(val, list)):
                attr_value = [
                    cls.transmute_from(child, attr.type[0], coerce_values)
                    for child in val
                ]

            # Converts all other objects (if possible)
            elif attr.type in NON_CONVERSION_TYPES:
                attr_value = val
                should_coerce = coerce_values

                if attr.coerce is not None:
                    should_coerce = attr.coerce

                if should_coerce:
                    attr_value = attr.type(attr_value)

            # Support Expanded Types
            else:
                find_exp_type = (
                    item
                    for item in EXPANDED_TYPES
                    if item.check_type(attr.type)
                )

                item = next(find_exp_type, None)

                if item:
                    attr_value = item.deserialize(attr.type, val)

            # Add mapped value to the new mapped_obj is possible
            setattr(mapped_obj, attr.name, attr_value)

        return mapped_obj

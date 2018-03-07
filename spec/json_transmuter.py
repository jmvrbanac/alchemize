import json
import six

from specter import Spec, DataSpec, expect, require

import alchemize
from alchemize import ExpandedType, JsonTransmuter, JsonMappedModel, Attr
from alchemize.transmute import RequiredAttributeError


class TestWrappedModel(JsonMappedModel):
    __wrapped_attr_name__ = '#item'
    __mapping__ = {
        'test': Attr('test', str)
    }


class TestMappedModel(JsonMappedModel):
    __mapping__ = {
        'test': Attr('test', str)
    }


class TestChildMapping(JsonMappedModel):
    __mapping__ = {
        'child': Attr('child', TestMappedModel),
    }


class TestListChildMapping(JsonMappedModel):
    __mapping__ = {
        'children': Attr('children', [TestMappedModel])
    }


class TestExtendedModel(TestMappedModel):
    __mapping__ = {
        'second': Attr('second', str)
    }


class TestDifferentAttrNaming(TestMappedModel):
    __mapping__ = {
        'my-thing': Attr('my_thing', str)
    }


class TestRequiredMappedModel(JsonMappedModel):
    __mapping__ = {
        'test': Attr('test', int),
        'other': Attr('other', int, required=True),
    }


TRANSMUTE_COMMON_TYPES_DATASET = {
    'bool': {
        'attr_type': bool,
        'attr_data': 'true', 'attr_result': True
    },
    'str': {
        'attr_type': str,
        'attr_data': '"data"', 'attr_result': 'data'
    },
    'int': {
        'attr_type': int,
        'attr_data': '1', 'attr_result': 1
    },
    'list': {
        'attr_type': list,
        'attr_data': '[1, 2]', 'attr_result': [1, 2]
    },
    'dict': {
        'attr_type': dict,
        'attr_data': '{"a": "b"}', 'attr_result': {'a': 'b'}
    },

    # ---------------- Default Type Values
    'int_zero': {
        'attr_type': int,
        'attr_data': '0', 'attr_result': 0
    },
    'str_empty': {
        'attr_type': str,
        'attr_data': '""', 'attr_result': ''
    },
}


class TransmutingJsonContent(Spec):

    class TransmuteFromJsonAttributeTypes(DataSpec):
        DATASET = TRANSMUTE_COMMON_TYPES_DATASET

        def transmute_attribute_with_type(self, attr_type, attr_data,
                                          attr_result):
            class FlexMapping(JsonMappedModel):
                __mapping__ = {
                    'test': Attr('test', attr_type)
                }

            data = '{{"test": {0} }}'.format(attr_data)
            result = JsonTransmuter.transmute_from(data, FlexMapping)
            expect(result.test).to.equal(attr_result)

    class TransmuteToJsonAttributeTypes(DataSpec):
        DATASET = TRANSMUTE_COMMON_TYPES_DATASET

        def transmute_attribute_with_type(self, attr_type, attr_data,
                                          attr_result):
            class FlexMapping(JsonMappedModel):
                __mapping__ = {
                    'test': ['test', attr_type]
                }

            mapping = FlexMapping()
            mapping.test = attr_result

            result = JsonTransmuter.transmute_to(mapping)
            expected_result = '{{"test": {0}}}'.format(attr_data)
            expect(result).to.equal(expected_result)

    def transmute_from_with_child_mapping(self):
        data = '{"other": "sample", "child": {"test": "sample stuff"}}'

        result = JsonTransmuter.transmute_from(data, TestChildMapping)

        require(result.child).not_to.be_none()
        expect(result.child.test).to.equal('sample stuff')

    def transmute_from_with_list_of_child_mappings(self):
        data = '{"children": [{"test": "sample1"}, {"test": "sample2"}]}'

        result = JsonTransmuter.transmute_from(data, TestListChildMapping)

        require(result.children).not_to.be_none()
        expect(len(result.children)).to.equal(2)
        expect(result.children[0].test).to.equal('sample1')
        expect(result.children[1].test).to.equal('sample2')

    def transmute_from_with_inherited_mapping(self):
        data = '{"test": "sample", "second": "other"}'

        result = JsonTransmuter.transmute_from(data, TestExtendedModel)

        expect(result.test).to.equal('sample')
        expect(result.second).to.equal('other')

    def transmute_to_with_child_mapping(self):
        child_mapping = TestMappedModel()
        child_mapping.test = 'sample stuff'

        mapping = TestChildMapping()
        mapping.child = child_mapping

        expected_result = '{"child": {"test": "sample stuff"}}'

        result = JsonTransmuter.transmute_to(mapping)
        expect(result).to.equal(expected_result)

    def transmute_to_with_null_value(self):
        mapping = TestMappedModel()
        mapping.test = None

        expected_result = '{"test": null}'

        result = JsonTransmuter.transmute_to(
            mapping,
            assign_all=True,
            coerce_values=False
        )
        expect(result).to.equal(expected_result)

    def transmute_to_with_zero_int_value(self):
        class IntMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', int)
            }

        mapping = IntMappedModel()
        mapping.test = 0

        expected_result = '{"test": 0}'

        result = JsonTransmuter.transmute_to(mapping)
        expect(result).to.equal(expected_result)

    def transmute_to_with_list_of_child_mappings(self):
        child_mapping = TestMappedModel()
        child_mapping.test = 'sample stuff'

        mapping = TestListChildMapping()
        mapping.children = [child_mapping]

        expected_result = '{"children": [{"test": "sample stuff"}]}'

        result = JsonTransmuter.transmute_to(mapping)
        expect(result).to.equal(expected_result)

    def transmute_to_with_inherited_mapping(self):
        model = TestExtendedModel()
        model.test = 'sample'
        model.second = 'other'

        expected_result = json.loads('{"test": "sample", "second": "other"}')

        result = JsonTransmuter.transmute_to(model)
        result_dict = json.loads(result)
        expect(result_dict['test']).to.equal(expected_result['test'])
        expect(result_dict['second']).to.equal(expected_result['second'])

    if six.PY3:
        def transmute_to_coerce_decimal_to_int(self):
            import decimal

            class IntMappedModel(JsonMappedModel):
                __mapping__ = {
                    'test': Attr('test', int)
                }

            mapping = IntMappedModel()
            mapping.test = decimal.Decimal(10)

            expected_result = '{"test": 10}'

            result = JsonTransmuter.transmute_to(mapping)
            expect(result).to.equal(expected_result)

    def transmute_to_coercion_can_be_overriden_per_attr(self):
        class IntMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', int, coerce=True)
            }

        mapping = IntMappedModel()
        mapping.test = '1'

        expected_result = '{"test": 1}'

        result = JsonTransmuter.transmute_to(mapping, coerce_values=False)
        expect(result).to.equal(expected_result)

    def transmute_to_with_old_attr_style(self):
        class OldStyleMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': ['test', int]
            }

        mapping = OldStyleMappedModel()
        mapping.test = 0

        expected_result = '{"test": 0}'

        result = JsonTransmuter.transmute_to(mapping)
        expect(result).to.equal(expected_result)

        result = JsonTransmuter.transmute_from(
            {'test': 1},
            OldStyleMappedModel
        )
        expect(result.test).to.equal(1)

    if six.PY3:
        def transmute_to_and_from_supports_enums(self):
            import enum

            class TestEnum(enum.Enum):
                RED = 1
                GREEN = 2
                BLUE = 3

            class OtherEnum(enum.Enum):
                BLUE = 1
                GREEN = 2
                RED = 3

            class EnumMappedModel(JsonMappedModel):
                __mapping__ = {
                    'test': Attr('test', TestEnum),
                    'other': Attr('other', OtherEnum),
                }

            mapping = EnumMappedModel()
            mapping.test = TestEnum.RED
            mapping.other = OtherEnum.RED

            serialized = '{"test": 1, "other": 3}'

            result = JsonTransmuter.transmute_to(mapping)

            res_dict = json.loads(result)
            expect(res_dict.get('test')).to.equal(1)
            expect(res_dict.get('other')).to.equal(3)

            result = JsonTransmuter.transmute_from(serialized, EnumMappedModel)
            expect(result.test).to.equal(TestEnum.RED)
            expect(result.other).to.equal(OtherEnum.RED)

    def transmute_to_and_from_with_expanded_type(self):
        class CustomType(object):
            def __init__(self, something):
                self.something = something

        class CustomDefinition(ExpandedType):
            cls = CustomType

            @classmethod
            def serialize(self, value):
                return {
                    'something': value.something
                }

            @classmethod
            def deserialize(self, attr_type, value):
                return attr_type(**value)

        class TestMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', CustomType),
            }

        model = TestMappedModel()
        model.test = CustomType('thing')

        serialized = '{"test": {"something": "thing"}}'

        alchemize.register_type(CustomDefinition)

        result = JsonTransmuter.transmute_to(model)
        expect(result).to.equal(serialized)

        result = JsonTransmuter.transmute_from(serialized, TestMappedModel)
        expect(result.test.something).to.equal('thing')

        alchemize.remove_type(CustomDefinition)

    def transmute_to_and_from_with_unknown_type(self):
        class CustomType(object):
            def __init__(self, something):
                self.something = something

        class TestMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', CustomType),
            }

        model = TestMappedModel()
        model.test = CustomType('thing')

        serialized = '{}'

        result = JsonTransmuter.transmute_to(model)
        expect(result).to.equal(serialized)

        result = JsonTransmuter.transmute_from(
            '{"test": {"something": "thing"}}',
            TestMappedModel
        )

        attr = getattr(result, 'test', None)
        expect(attr).to.be_none()

    def transmute_to_and_from_with_wrapped_attr_name(self):
        mapping = TestWrappedModel()
        mapping.test = "bam"

        json_str = '{"#item": {"test": "bam"}}'

        result = JsonTransmuter.transmute_to(
            mapping,
            assign_all=True,
            coerce_values=False
        )
        expect(result).to.equal(json_str)

        result = JsonTransmuter.transmute_from(json_str, TestWrappedModel)
        expect(result.test).to.equal("bam")

    def transmute_to_and_from_with_excluded_items(self):
        class MixedMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', int),
                'another': Attr('another', int, serialize=False)
            }

        mapping = MixedMappedModel()
        mapping.test = 1
        mapping.another = 2

        without_result = '{"test": 1}'
        result_without = JsonTransmuter.transmute_to(mapping)
        expect(result_without).to.equal(without_result)

        # Make sure we can override the serialization preferences
        result_with = JsonTransmuter.transmute_to(
            mapping,
            to_string=False,
            serialize_all=True
        )
        expect(result_with.get('test')).to.equal(1)
        expect(result_with.get('another')).to.equal(2)

        result = JsonTransmuter.transmute_from(
            {'test': 100, 'another': 200},
            MixedMappedModel
        )
        expect(result.test).to.equal(100)
        expect(result.another).to.equal(200)

    def transmute_to_and_from_with_custom_serializer(self):
        mapping = TestWrappedModel()
        mapping.test = "bam"

        json_str = '{"#item": {"test": "bam"}}'

        class Custom(object):
            @classmethod
            def dumps(cls, value):
                value['#item']['test'] = 'allthethings'
                return json.dumps(value)

            @classmethod
            def loads(cls, value):
                loaded = json.loads(json_str)
                loaded['#item']['test'] = 'magic'
                return loaded

        result = JsonTransmuter.transmute_to(
            mapping,
            encoder=Custom
        )
        expect(result).to.equal('{"#item": {"test": "allthethings"}}')

        result = JsonTransmuter.transmute_from(
            json_str,
            TestWrappedModel,
            decoder=Custom
        )
        expect(result.test).to.equal('magic')

    def transmute_from_can_coerce_types(self):
        class TestMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', int),
            }

        test_json = '{"test": "1"}'
        result = JsonTransmuter.transmute_from(
            test_json,
            TestMappedModel,
            coerce_values=True
        )

        expect(result.test).to.equal(1)
        expect(result.test).to.be_an_instance_of(int)

    def transmute_from_coercion_can_be_overriden_per_attr(self):
        class TestMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', int, coerce=False),
            }

        test_json = '{"test": "1"}'
        result = JsonTransmuter.transmute_from(
            test_json,
            TestMappedModel,
            coerce_values=True
        )

        expect(result.test).to.equal('1')

    def transmute_from_can_coerce_nested(self):
        class SubMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', int),
            }

        class TestMappedModel(JsonMappedModel):
            __mapping__ = {
                'nope': Attr('nope', SubMappedModel),
            }

        test_json = '{"nope": {"test": "1"}}'
        result = JsonTransmuter.transmute_from(
            test_json,
            TestMappedModel,
            coerce_values=True
        )

        expect(result.nope.test).to.equal(1)
        expect(result.nope.test).to.be_an_instance_of(int)

    def transmute_from_can_disable_nested_coerce(self):
        class SubMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', int),
            }

        class TestMappedModel(JsonMappedModel):
            __mapping__ = {
                'nope': Attr('nope', SubMappedModel),
            }

        test_json = '{"nope": {"test": "1"}}'
        result = JsonTransmuter.transmute_from(
            test_json,
            TestMappedModel,
            coerce_values=False
        )

        expect(result.nope.test).to.equal('1')
        expect(result.nope.test).not_to.be_an_instance_of(int)

    def transmute_to_can_disable_nested_coerce(self):
        class SubMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', int),
            }

        class TestMappedModel(JsonMappedModel):
            __mapping__ = {
                'nope': Attr('nope', SubMappedModel),
            }

        model = TestMappedModel()
        model.nope = SubMappedModel()
        model.nope.test = '1'

        expected_result = '{"nope": {"test": "1"}}'

        result = JsonTransmuter.transmute_to(model, coerce_values=False)
        expect(result).to.equal(expected_result)

    def transmute_to_can_coerce_a_null_dict_value(self):
        class IntMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', dict)
            }

        mapping = IntMappedModel()
        mapping.test = None

        expected_result = '{"test": {}}'

        result = JsonTransmuter.transmute_to(mapping)
        expect(result).to.equal(expected_result)

    def transmute_from_with_missing_required_attr_raises(self):
        expect(
            JsonTransmuter.transmute_from,
            [
                '{"test": 1}',
                TestRequiredMappedModel
            ]
        ).to.raise_a(RequiredAttributeError)

    def transmute_from_with_all_required_attrs(self):
        result = JsonTransmuter.transmute_from(
            '{"test": 1, "other": 2}',
            TestRequiredMappedModel,
        )

        expect(result.test).to.equal(1)
        expect(result.other).to.equal(2)

    def transmute_to_missing_required_attr_raises(self):
        model = TestRequiredMappedModel()
        model.test = 1

        expect(
            JsonTransmuter.transmute_to,
            [model]
        ).to.raise_a(RequiredAttributeError)

    def transmute_to_with_all_required_attrs(self):
        model = TestRequiredMappedModel()
        model.test = 1
        model.other = 2

        result = JsonTransmuter.transmute_to(model, to_string=False)

        expect(result['test']).to.equal(1)
        expect(result['other']).to.equal(2)

    def transmute_from_with_different_attr_naming(self):
        test_json = '{"my-thing": "something"}'

        result = JsonTransmuter.transmute_from(
            test_json,
            TestDifferentAttrNaming
        )

        expect(result.my_thing).to.equal('something')

    def transmute_to_with_different_attr_naming(self):
        model = TestDifferentAttrNaming()
        model.my_thing = 'something'

        result = JsonTransmuter.transmute_to(model, to_string=False)

        expect(result['my-thing']).to.equal('something')

    def transmute_from_leaves_default_if_not_there(self):
        class TestMappedModel(JsonMappedModel):
            __mapping__ = {
                'test': Attr('test', str),
            }
            test = ''

        test_json = '{"not-in-here": "1"}'
        result = JsonTransmuter.transmute_from(test_json, TestMappedModel)

        expect(result.test).to.equal('')

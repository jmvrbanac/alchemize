import json
import six

from specter import Spec, DataSpec, expect, require
from alchemize.transmute import JsonTransmuter
from alchemize.mapping import JsonMappedModel, Attr


class TestMappedModel(JsonMappedModel):
    __mapping__ = {
        'test': Attr('test', str)
    }


class TestChildMapping(JsonMappedModel):
    __mapping__ = {
        'child': Attr('child', TestMappedModel)
    }


class TestListChildMapping(JsonMappedModel):
    __mapping__ = {
        'children': Attr('children', [TestMappedModel])
    }


class TestExtendedModel(TestMappedModel):
    __mapping__ = {
        'second': Attr('second', str)
    }

TRANSMUTE_COMMON_TYPES_DATASET = {
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

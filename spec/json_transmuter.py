from specter import Spec, DataSpec, expect, require
from alchemize.transmute import JsonTransmuter
from alchemize.mapping import JsonMappedModel


class TestMappedModel(JsonMappedModel):
    __mapping__ = {
        'test': ['test', str]
    }


class TestChildMapping(JsonMappedModel):
    __mapping__ = {
        'child': ['child', TestMappedModel]
    }


class TestListChildMapping(JsonMappedModel):
    __mapping__ = {
        'children': ['children', [TestMappedModel]]
    }


class TransmutingJsonContent(Spec):

    class TransmuteFromJsonAttributeTypes(DataSpec):
        DATASET = {
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
                'attr_data': '[1,2]', 'attr_result': [1, 2]
            },
            'dict': {
                'attr_type': dict,
                'attr_data': '{"a": "b"}', 'attr_result': {'a': 'b'}
            }
        }

        def transmute_attribute_with_type(self, attr_type, attr_data,
                                          attr_result):
            class FlexMapping(JsonMappedModel):
                __mapping__ = {
                    'test': ['test', attr_type]
                }

            data = '{{"test": {0} }}'.format(attr_data)
            result = JsonTransmuter.transmute_from(data, FlexMapping)
            expect(result.test).to.equal(attr_result)

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

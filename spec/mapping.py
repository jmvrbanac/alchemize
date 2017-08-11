from specter import Spec, expect
from alchemize import Attr, JsonMappedModel
from alchemize.mapping import get_key_paths


class TestModel(JsonMappedModel):
    __mapping__ = {
        'thing': Attr('thing', str),
        'old_style': ['thing', str],
    }


class SampleMapping(JsonMappedModel):
    __mapping__ = {
        'top_lvl': Attr('top_lvl', str),
        'model': Attr('model', TestModel),
        'model_list': Attr('model_list', [TestModel]),
    }


class TestMapping(Spec):
    def can_get_key_paths(self):
        key_list = get_key_paths(SampleMapping)

        expect('/top_lvl').to.be_in(key_list)
        expect('/model/thing').to.be_in(key_list)
        expect('/model/old_style').to.be_in(key_list)
        expect('/model_list/thing').to.be_in(key_list)

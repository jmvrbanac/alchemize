import json
import six

from specter import Spec, expect

from alchemize import Attr, JsonModel, JsonListModel


class TestModel(JsonModel):
    __mapping__ = {
        'thing': Attr('thing', str),
    }


class TestListModel(JsonListModel):
    __mapping__ = {
        'items': Attr('collection', [TestModel]),
    }


class TestJsonHelperModel(Spec):
    def can_create_from_dict(self):
        model = TestModel.from_dict({'thing': 'bam'})
        expect(model.thing).to.equal('bam')

    def can_create_from_json(self):
        model = TestModel.from_json(
            json.dumps({'thing': 'bam'})
        )
        expect(model.thing).to.equal('bam')

    def can_convert_to_dict(self):
        model = TestModel()
        model.thing = 'bam'

        obj = model.as_dict()
        expect(obj['thing']).to.equal('bam')

    def can_convert_to_json(self):
        model = TestModel()
        model.thing = 'bam'

        json_str = model.as_json()
        expect(json_str).to.equal('{"thing": "bam"}')

    def can_update(self):
        model = TestModel()
        model.thing = 'bam'

        model.update(thing='other')

        expect(model.thing).to.equal('other')

    def can_set_attrs_in_constructor(self):
        model = TestModel(thing='bam')
        expect(model.thing).to.equal('bam')


class TestJsonHelperListModel(Spec):
    if six.PY3:
        def can_iterate(self):
            child = TestModel()
            child.thing = 'bam'

            model = TestListModel()
            model.collection = [child]

            item = next(model)
            expect(item.thing).to.equal('bam')

        def iter_empty_works(self):
            model = TestListModel()
            model.collection = []

            obj = next(model, None)
            expect(obj).to.be_none()

    def casting_empty_works(self):
        model = TestListModel()
        model.collection = []

        flattened = list(model)
        expect(flattened).to.equal([])

    def can_get_length(self):
        model = TestListModel()
        model.collection = [TestModel(), TestModel()]

        expect(len(model)).to.equal(2)

    def can_get(self):
        child = TestModel()
        child.thing = 'bam'

        model = TestListModel()
        model.collection = [child]

        expect(model[0]).to.equal(child)

    def can_set(self):
        child = TestModel()
        child.thing = 'bam'

        model = TestListModel()
        model.append(TestModel)

        model[0] = child

        expect(model[0]).to.equal(child)

    def can_delete(self):
        child = TestModel()
        child.thing = 'bam'

        model = TestListModel()
        model.collection = [child]

        del model[0]

        expect(len(model)).to.equal(0)

    def can_append(self):
        child = TestModel()
        child.thing = 'bam'

        model = TestListModel()
        model.append(child)

        expect(model[0]).to.equal(child)

    def can_extend(self):
        child = TestModel()
        child.thing = 'bam'

        model = TestListModel()
        model.extend([child])

        expect(model[0]).to.equal(child)

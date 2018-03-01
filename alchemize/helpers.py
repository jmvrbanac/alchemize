from alchemize import JsonMappedModel, JsonTransmuter


class JsonModel(JsonMappedModel):
    """Model helper that is designed to provide common usage methods."""

    @classmethod
    def transmute_from(cls, data, **options):
        return JsonTransmuter.transmute_from(data, cls, **options)

    def transmute_to(self, to_string=False, serialize_all=False,
                     coerce_values=False):
        return JsonTransmuter.transmute_to(
            self,
            to_string=to_string,
            coerce_values=coerce_values,
            serialize_all=serialize_all,
        )

    def as_json(self, serialize_all=False):
        """Converts the model into a JSON string."""
        return self.transmute_to(to_string=True, serialize_all=serialize_all)

    def as_dict(self, serialize_all=False):
        """Converts the model into a dictionary."""
        return self.transmute_to(serialize_all=serialize_all)

    @classmethod
    def from_json(cls, data, **transmute_options):
        """Creates a new instance of the model from a JSON string."""
        return cls.transmute_from(data, **transmute_options)

    @classmethod
    def from_dict(cls, data, **transmute_options):
        """Creates a new instance of the model from a dictionary."""
        return cls.transmute_from(data, **transmute_options)

    def update(self, **attrs):
        """Updates object attributes with specified kwarg values."""
        for key, val in attrs.items():
            setattr(self, key, val)


class JsonListModel(JsonModel):
    """The list model helper is designed to be a top-level container for
    more complex list structures.

    While you can map any number of attributes to this model, it expects a
    special mapping to the 'collection' attribute that it'll alias normal
    iterable operations to.

    **Mapping Usage**::

        'my-items': Attr('collection', [ChildModel])

    .. note::

        The child items should be mapped into the 'collection' attribute to
        properly use this helper.

    """

    def __init__(self):
        self.collection = []

    def __iter__(self):
        """Iterates the collection."""
        for item in self.collection:
            yield item

    def __next__(self):
        for item in self:
            return item

        raise StopIteration()

    def __getitem__(self, idx):
        """Returns an item from the collection."""
        return self.collection[idx]

    def __delitem__(self, idx):
        """Deletes an item from the collection."""
        del self.collection[idx]

    def __setitem__(self, idx, val):
        """Sets an item from the collection."""
        self.collection[idx] = val

    def __len__(self):
        """Returns the length of the collection."""
        return len(self.collection)

    def append(self, item):
        """Appends an item to the collection."""
        return self.collection.append(item)

    def extend(self, items):
        """Appends multiple items to the collection."""
        return self.collection.extend(items)

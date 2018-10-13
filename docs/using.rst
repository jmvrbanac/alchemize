Using Alchemize
==================

Alchemize relies on a explicit mapping structure that is defined on your
model class. The mapping combined with the appropriate class mix-in will
enable your object to serialize and deserialize to a supported format by
Alchemize.

Simple Example
---------------

In the following example, we'll be taking a portion of the sample response from the GitHub's
API to retrieve data on a single user.

**Input JSON**

.. code-block:: javascript

    {
        "login": "octocat",
        "id": 1,
        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
        "gravatar_id": "",
        "url": "https://api.github.com/users/octocat",
        "html_url": "https://github.com/octocat",
        "type": "User",
        "site_admin": false,
        "name": "monalisa octocat",
        "company": "GitHub",
        "blog": "https://github.com/blog",
        "location": "San Francisco",
        "email": "octocat@github.com",
        "hireable": false,
        "bio": "There once was...",
        "public_repos": 2,
        "public_gists": 1,
        "followers": 20,
        "following": 0,
        "created_at": "2008-01-14T04:33:35Z",
        "updated_at": "2008-01-14T04:33:35Z"
    }

**Example Mapping**

.. code-block:: python

    from alchemize import JsonMappedModel, Attr

    class ExampleClass(JsonMappedModel):
        __mapping__ = {
            'id': Attr('user_id', int),
            'login': Attr('login', str),
            "email": Attr('email', str),
            "name": Attr('name' , str)
        }
        ...

Now that we have some sample JSON and a mapping on a class, we can put
this information through the JsonTransmuter to get two-way conversion of
our data.

**Example Transmutation**

.. code-block:: python

    from alchemize import JsonTransmuter

    # From JSON to our Python Mapped Model
    result_model = JsonTransmuter.transmute_from(json_str, ExampleClass)

    # From our Python Mapped Model back to JSON
    result_json = JsonTransmuter.transmute_to(result_model)


If you look at the resulting model and JSON string, you might notice that
the only information that is carried over is what has been explicitly mapped.


Nested Mapped Models
----------------------

Alchemize supports the ability to de/serialize child mapped models as well.
This allows for you to explicitly map your data into nested Python objects
and let Alchemize handle the serialization and deserialization of the entire
data structure at once.

**Example:**

We want to convert the following JSON into appropriate Python objects.

.. code-block:: javascript

    {
        "id": 12345,
        "users": [
            {
                "name": "Foster Person",
                "email": "foster.person@example.com"
            },
            {
                "name": "Other Person",
                "email": "other.person@example.com"
            }
        ]
    }

.. code-block:: python

    from alchemize import JsonMappedModel, Attr

    class User(JsonMappedModel):
        __mapping__ = {
            'name': Attr('name', str),
            'email': Attr('email', str)
        }

    class Project(JsonMappedModel):
        __mapping__ = {
            'id': Attr('project_id', int),
            'users': Attr('users', [User])
        }


We can now deserialize the data into our models using the JsonTransmuter

.. code-block:: python

    from alchemize import JsonTransmuter

    result_model = JsonTransmuter.transmute_from(json_str, Project)

    result_model.users[0].name # 'Foster Person'
    result_model.users[1].name # 'Other Person'

We have successfully converted our JSON structure into a easily usable
Python object structure.

For more information on how to define your mappings, take a look at the
:doc:`api`


Excluding Attributes for Serialization
--------------------------------------

For specific data models there are instances where you don't want to serialize
certain attributes. For example, you're pulling user information from a database
but you don't want to serialize the password hash or some other internal value.
This is done by setting the ``serialize=False`` argument on your ``Attr``.

.. code-block:: python

    from alchemize import JsonMappedModel, Attr

    class User(JsonMappedModel):
        __mapping__ = {
            'name': Attr('name', str),
            'email': Attr('email', str),
            'password': Attr('password', str, serialize=False),
        }

.. note::

    The ``serialize`` setting can be overridden by the transmuter if
    explicited set during the ``transmute_to(...)`` call.


Wrapped Objects
---------------

Some API responses can wrap the information you're interested in inside a
container object. There are many reasons for this, but often from a model
interface perspective, you just want to represent the data itself and not
the container. To handle this use-case, Alchemize provides the
``__wrapped_attr_name__`` option.

This option allows for parsing this JSON into the following single model

.. code-block:: javascript

    {
        "#item": {
            "name": "John Doe",
            "email": "rando@doe.com",
        }
    }

.. code-block:: python

    from alchemize import JsonMappedModel, Attr

    class User(JsonMappedModel):
        __wrapped_attr_name__ = '#item'
        __mapping__ = {
            'name': Attr('name', str),
            'email': Attr('email', str),
        }

Simple Helper Usage
-------------------

If you don't really care about a custom serialization implementation or hook-in
you can use the basic helper models which handle will transmute to/from on
their own.


.. code-block:: python

    from alchemize import JsonModel, Attr


    class User(JsonModel):
        __mapping__ = {
            'name': Attr('name', str),
            'email': Attr('email', str),
            'password': Attr('password', str, serialize=False),
        }


    model = User.from_dict({
        'name': 'thing',
        'email': 'thing@thing.corp',
        'password': 'my-password',
    })

    json_dict = model.as_dict()

    # You can also set attributes on instance creation
    model = User(name='thing', email='thing@thing.corp')

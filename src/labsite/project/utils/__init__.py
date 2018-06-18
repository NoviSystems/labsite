class choices(tuple):
    """
    Tuple subclass intended to be used with Django model choices/states. The
    'key' of each choice is made dot-accessible as its uppercased value on
    the main tuple. Using attributes is more durable to code changes than
    string literals.
    Notes:
    - Integer keys are made available as an underscore-prefixed attribute.
    - Empty strings are made available as an ``__EMPTY__`` attribute.
    - Whitespace and dashes are replaced with underscores
    ex::
        class Example(models.Model):
            states = choices((
                ('new', 'New'),
                ('draft', 'Draft'),
                ('published', 'published'),
            ))
            state = models.CharField(choices=states, default=states.NEW, max_length=8)
            ...
        # accessible as:
        Example.states.NEW
    """

    def __init__(self, *args, **kwargs):
        for key, _ in self:
            # Use explicit type check, as boolean literals are ints
            if type(key) == int:
                attr = '_%d' % key
            elif key == '':
                attr = '__EMPTY__'
            else:
                attr = str(key) \
                    .replace('-', '_') \
                    .upper()
                attr = '_'.join(attr.split())

            setattr(self, attr, key)

    def keys(self):
        return [key for key, _ in self]

    def values(self):
        return [value for _, value in self]

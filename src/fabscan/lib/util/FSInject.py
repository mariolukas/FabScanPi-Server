# The following code is borrowed from https://raw.githubusercontent.com/soulrebel/diy/master/diy.py

"""
Do It yourself Dependency Injection
***********************************

A minimal, but feature complete, dependency injection library that works
transparently, leveraging metaclasses.

Usage
+++++

Define an interface and an implementation as usual:

>>> class Interface(object):
...     def imethod(self):
...         raise NotImplementedError()

>>> class Implementation(Interface):
...     def __init__(self):
...         self.value = 'Implementation'
...     def imethod(self):
...         return self.value

Make Implementation the provider of Interface objects, by registering on the
*injector*:

>>> injector.provide(Interface, Implementation)

In a dependent class request injection of an object implementing Interface
for the **keyword** parameter named 'interface':

>>> @inject(interface=Interface)
... class Dependent(object):
...     def __init__(self, interface):
...         self.interface = interface

Instantiate object omitting the parameter 'interface':

>>> Dependent().interface.imethod()
'Implementation'

If you need to use the object with a custom parameter you can do it manually
using a **keyword** parameter:

>>> Dependent(interface='parameter').interface
'parameter'

It is also possible to set up multiple *named* implementations and/or use
custom singleton instances for an interface:

>>> injector.provide_instance(str, 'http://localhost:1234/', name='endpoint')

Just request them using named() in the decorator:

>>> @inject(endpoint=named('endpoint', str))
... class NamedDependent(object):
...     def __init__(self, endpoint):
...         self.endpoint = endpoint

>>> NamedDependent().endpoint
'http://localhost:1234/'

But you can also turn classes into singletons:

>>> @singleton(interface=Interface)
... class SomeSingleton(Dependent):
...     pass

>>> SomeSingleton() is SomeSingleton()
True

And of course you ca n also inject classes, without the need for defining and
interface and registering an implementation:

>>> @inject(singleton=SomeSingleton)
... class SingletonDependent(object):
...     def __init__(self, singleton):
...         self.singleton = singleton

>>> SingletonDependent().singleton is SomeSingleton()
True

Other tests
+++++++++++

Class with custom metaclasses are supported:

>>> class Meta(type):
...     pass
>>> @inject(interface=Interface)
... class MetaDependent(object):
...     __metaclass__ = Meta
...     def __init__(self, interface):
...         self.interface = interface

>>> MetaDependent().interface.imethod()
'Implementation'

Derived classes get inject as well, but remember to call super!:

>>> class Derived(Dependent):
...     def __init__(self, extra, interface):
...         super(Derived, self).__init__(interface)
...         self.extra = extra

>>> Derived('extra').interface.imethod()
'Implementation'

No duplicate classes are built

>>> type(Dependent) is Injectable
True
>>> type(Derived) is type(Dependent)
True
>>> named('name', Interface) is named('name', Interface)
True
"""


class Injector(object):
    """
    The injector provides instances implementing interfaces using classes,
    factories or live objects
    """

    def __init__(self):
        self._providers = {None: {}}

    def provide(self, iface, cls, name=None):
        "Bind an interface to a class"
        assert issubclass(cls, iface)
        self.provide_factory(iface, cls, name)

    def provide_instance(self, iface, obj, name=None):
        "Bind an interface to an object"
        assert isinstance(obj, iface)
        self.provide_factory(iface, lambda: obj, name)

    def provide_factory(self, iface, method, name=None):
        "Bind an interface to a factory method, called with no parameters"
        assert callable(method)
        self._providers.setdefault(name, {})[iface] = method

    def get_instance(self, iface_or_cls, name=None):
        "Get an object implementing an interface"
        provider = self._providers[name].get(iface_or_cls, iface_or_cls)
        return provider()

    def __repr__(self):
        return '<injector>'

injector = Injector()
"Import this and provide your implementations"


class Injectable(type):
    "Metaclass to implements dependency injection"

    def __call__(cls, *args, **kwargs):
        for k, c in cls.__dependencies__.items():
            if not k in kwargs:
                kwargs[k] = injector.get_instance(c)
        r = super(Injectable, type(cls)).__call__(cls, *args, **kwargs)
        return r


class Singleton(Injectable):
    "Metaclass to implement instance reuse"

    def __call__(cls, *args, **kwargs):
        r = getattr(cls, '__instance__', None)
        if r is None:
            r = super(Singleton, type(cls)).__call__(cls, *args, **kwargs)
            setattr(cls, '__instance__', r)
        return r


def _with_meta(new_meta, cls):
    meta = type(cls)
    if not issubclass(meta, new_meta):
        if new_meta.__mro__[1:] != meta.__mro__:
            # class has a custom metaclass, we extend it on the fly
            name = new_meta.__name__ + meta.__name__
            new_meta = type(name, (new_meta,) + meta.__bases__, {})
        # rebuild the class
        return new_meta(cls.__name__, cls.__bases__, dict(cls.__dict__))
    else:
        # class has alredy the correct metaclass due to inheritance
        return cls


def _inject(_injectable_type, **dependencies):
    def annotate(cls):
        cls = _with_meta(_injectable_type, cls)
        setattr(cls, '__dependencies__', dependencies)
        return cls
    return annotate


def inject(**dependencies):
    "Bind constructor arguments to implementations"
    return _inject(Injectable, **dependencies)


def singleton(**dependencies):
    "Make the class a singleton, accepts the same parameters as inject()"
    return _inject(Singleton, **dependencies)


class Named(type):
    "Metaclass to implement named lookup of dependencies"

    _names = {}

    def __new__(metacls, name, bases, attrs):
        name = attrs['name']
        iface = attrs['iface']
        cls = metacls._names.setdefault(name, {}).get(iface)
        if cls is None:
            cls = super(Named, metacls).__new__(metacls, name, bases, attrs)
            metacls._names[name][iface] = cls
        return cls

    def __call__(cls):
        return injector.get_instance(cls.iface, name=cls.name)


def named(name, iface):
    "Request a named implementation of a dependency"
    return Named('%s<%s>' % (iface.__name__, name), (object,),
                 {'iface': iface, 'name': name})

__all__ = ['injector', 'inject', 'singleton', 'named']
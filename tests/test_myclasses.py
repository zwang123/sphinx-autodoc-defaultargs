from collections import abc

import pytest
from myclasses import MyCallable, MyIterable
from myclasses import __MyFunctor as MyFunctor


@pytest.mark.parametrize('args', [(), ([],), ((1,),), ((0, 1),), (range(1),)])
@pytest.mark.parametrize('kwargs', [{}])
def test_my_iterable(args, kwargs):
    print(MyIterable, args, kwargs)
    assert issubclass(MyIterable, abc.Iterable)
    assert not issubclass(MyIterable, abc.Container)
    assert not issubclass(MyIterable, abc.Hashable)
    assert not issubclass(MyIterable, abc.Iterator)
    assert not issubclass(MyIterable, abc.Sized)
    assert not issubclass(MyIterable, abc.Callable)
    assert not issubclass(MyIterable, abc.Sequence)
    assert not issubclass(MyIterable, abc.Set)
    assert not issubclass(MyIterable, abc.Mapping)
    try:
        assert not issubclass(MyIterable, abc.Collection)
    except AttributeError:
        pass  # Python 3.5 Compatibility
    my_iterable = MyIterable(*args, **kwargs)
    print(my_iterable.contents)
    assert isinstance(my_iterable, abc.Iterable)
    for _ in my_iterable:
        pass
    [x for x in my_iterable]

    assert my_iterable.contents == MyIterable.Type(*args, **kwargs)
    assert not my_iterable == MyIterable.Type(*args, **kwargs)
    assert my_iterable == MyIterable(*args, **kwargs)

    assert MyIterable() + [0] == MyIterable([0])
    assert MyIterable() + (0, 1) == MyIterable((0, 1))


@pytest.mark.parametrize('func, args, kwargs', [
    (MyCallable(lambda: None), (), {}),
    (MyFunctor(), (5,), {}),
])
def test_my_callable(func, args, kwargs):
    assert issubclass(MyCallable, abc.Callable)
    assert not issubclass(MyCallable, abc.Container)
    assert not issubclass(MyCallable, abc.Hashable)
    assert not issubclass(MyCallable, abc.Iterable)
    assert not issubclass(MyCallable, abc.Iterator)
    assert not issubclass(MyCallable, abc.Sized)
    assert not issubclass(MyCallable, abc.Sequence)
    assert not issubclass(MyCallable, abc.Set)
    assert not issubclass(MyCallable, abc.Mapping)
    try:
        assert not issubclass(MyCallable, abc.Collection)
    except AttributeError:
        pass  # Python 3.5 Compatibility
    my_callable = MyCallable(func)
    assert isinstance(my_callable, abc.Callable)
    try:
        func = getattr(my_callable.func, 'deepcopy', my_callable.func.copy)()
    except AttributeError:
        func = my_callable.func

    print(func)
    print(type(func))
    assert func(*args, **kwargs) == my_callable(*args, **kwargs)
    assert not my_callable.func == my_callable
    assert MyCallable(my_callable.func) == my_callable


@pytest.mark.parametrize('args, kwargs', [
    ((5,), {'y_': 3}),
])
def test_my_functor(args, kwargs):
    assert issubclass(MyFunctor, abc.Callable)
    assert not issubclass(MyFunctor, abc.Container)
    assert not issubclass(MyFunctor, abc.Hashable)
    assert not issubclass(MyFunctor, abc.Iterable)
    assert not issubclass(MyFunctor, abc.Iterator)
    assert not issubclass(MyFunctor, abc.Sized)
    assert not issubclass(MyFunctor, abc.Sequence)
    assert not issubclass(MyFunctor, abc.Set)
    assert not issubclass(MyFunctor, abc.Mapping)
    try:
        assert not issubclass(MyFunctor, abc.Collection)
    except AttributeError:
        pass  # Python 3.5 Compatibility
    my_func = MyFunctor()
    assert isinstance(my_func, abc.Callable)
    assert my_func == MyFunctor()
    assert not my_func == (lambda: None)

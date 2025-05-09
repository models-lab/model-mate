"""Definition of meta model 'yakindumm'."""
from functools import partial
import pyecore.ecore as Ecore
from pyecore.ecore import *


name = 'yakindumm'
nsURI = 'hu.bme.mit.inf.yakindumm'
nsPrefix = 'hu.bme.mit.inf.yakindumm'

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)


@abstract
class Vertex(EObject, metaclass=MetaEClass):

    kind = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    specification = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    incomingTransitions = EReference(ordered=False, unique=True,
                                     containment=False, derived=False, upper=-1)
    outgoingTransitions = EReference(ordered=False, unique=True,
                                     containment=True, derived=False, upper=-1)

    def __init__(self, *, kind=None, name=None, specification=None, incomingTransitions=None, outgoingTransitions=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if kind is not None:
            self.kind = kind

        if name is not None:
            self.name = name

        if specification is not None:
            self.specification = specification

        if incomingTransitions:
            self.incomingTransitions.extend(incomingTransitions)

        if outgoingTransitions:
            self.outgoingTransitions.extend(outgoingTransitions)


class Region(EObject, metaclass=MetaEClass):

    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    vertices = EReference(ordered=False, unique=True, containment=True, derived=False, upper=-1)

    def __init__(self, *, name=None, vertices=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if name is not None:
            self.name = name

        if vertices:
            self.vertices.extend(vertices)


class Transition(EObject, metaclass=MetaEClass):

    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    specification = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    target = EReference(ordered=False, unique=True, containment=False, derived=False)
    source = EReference(ordered=False, unique=True, containment=False, derived=False)

    def __init__(self, *, name=None, specification=None, target=None, source=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if name is not None:
            self.name = name

        if specification is not None:
            self.specification = specification

        if target is not None:
            self.target = target

        if source is not None:
            self.source = source


@abstract
class CompositeElement(EObject, metaclass=MetaEClass):

    documentation = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    name = EAttribute(eType=EString, unique=True, derived=False, changeable=True)
    regions = EReference(ordered=True, unique=True, containment=True, derived=False, upper=-1)

    def __init__(self, *, documentation=None, name=None, regions=None):
        # if kwargs:
        #    raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        if documentation is not None:
            self.documentation = documentation

        if name is not None:
            self.name = name

        if regions:
            self.regions.extend(regions)


@abstract
class Pseudostate(Vertex):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class Statechart(CompositeElement):

    specification = EAttribute(eType=EString, unique=True, derived=False, changeable=True)

    def __init__(self, *, specification=None, **kwargs):

        super().__init__(**kwargs)

        if specification is not None:
            self.specification = specification


@abstract
class RegularState(Vertex):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class Entry(Pseudostate):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class Synchronization(Pseudostate):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class Choice(Pseudostate):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class Exit(Pseudostate):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class FinalState(RegularState):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


class State(RegularState, CompositeElement):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 23:23:31 2023

@author: christophercox
"""


# import os

# os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import uuid as uuidlib

import pint

# Use the shared application registry so that quantities created by library
# users with pint.get_application_registry() interoperate with sysml2py.
# (Quantities from different registries cannot be mixed in pint.)
ureg = pint.get_application_registry()

from sysml2py.formatting import classtree

from sysml2py.grammar.classes import (
    Identification,
    DefinitionBody,
    DefinitionBodyItem,
    FeatureSpecializationPart,
)

from sysml2py.grammar.classes import (
    AttributeUsage,
    AttributeDefinition,
    ValuePart,
    PartUsage,
    PartDefinition,
    ItemUsage,
    ItemDefinition,
    PortUsage,
    PortDefinition,
    DefaultReferenceUsage,
    RefPrefix,
)

from sysml2py.grammar.classes import (
    UseCaseDefinition,
    UseCaseUsage,
    IncludeUseCaseUsage,
    ActorMember,
    ActorUsage,
    CaseBodyItem,
)


class Usage:
    def __init__(self):
        self.name = str(uuidlib.uuid4())
        self.children = []
        self.typedby = None
        return self

    def _ensure_body(self, subgrammar="usage"):
        # Add children
        body = []
        for abc in self.children:
            body.append(
                DefinitionBodyItem(
                    abc._get_definition(child="DefinitionBody")
                ).get_definition()
            )

        if len(body) > 0:
            new_body = DefinitionBody(
                {"name": "DefinitionBody", "ownedRelatedElement": body}
            )
            if subgrammar == "usage":
                self.grammar.usage.completion.body.body = new_body
            else:
                # Definition-shaped grammar objects (e.g. PartDefinition's
                # `.definition`) hold their body directly - there is no
                # `.completion` wrapper, unlike the usage shape.
                self.grammar.definition.body = new_body
        return self

    def usage_dump(self, child):
        # This is a usage.

        self._ensure_body("usage")

        # Add packaging
        package = {
            "name": "StructureUsageElement",
            "ownedRelatedElement": self.grammar.get_definition(),
        }
        package = {"name": "OccurrenceUsageElement", "ownedRelatedElement": package}

        if child == "DefinitionBody":
            package = {
                "name": "OccurrenceUsageMember",
                "prefix": None,
                "ownedRelatedElement": [package],
            }

            package = {"name": "DefinitionBodyItem", "ownedRelationship": [package]}
        elif "PackageBody":
            package = {"name": "UsageElement", "ownedRelatedElement": package}
            package = {
                "name": "PackageMember",
                "ownedRelatedElement": package,
                "prefix": None,
            }

        return package

    def definition_dump(self, child):
        # This is a definition.

        self._ensure_body("definition")

        package = {
            "name": "DefinitionElement",
            "ownedRelatedElement": self.grammar.get_definition(),
        }

        if child == "DefinitionBody":
            package = {
                "name": "DefinitionMember",
                "prefix": None,
                "ownedRelatedElement": [package],
            }

            package = {"name": "DefinitionBodyItem", "ownedRelationship": [package]}

        elif child == "PackageBody" or child == None:
            # Add these packets to make this dump without parents

            package = {
                "name": "PackageMember",
                "ownedRelatedElement": package,
                "prefix": None,
            }

        return package

    def _get_definition(self, child=None):
        if "usage" in self.grammar.__dict__:
            package = self.usage_dump(child)
        else:
            package = self.definition_dump(child)

        if child is None:
            package = {
                "name": "PackageBodyElement",
                "ownedRelationship": [package],
                "prefix": None,
            }

        # Add the typed by definition to the package output
        if self.typedby is not None:
            if child is None:
                package["ownedRelationship"].insert(
                    0, self.typedby._get_definition(child="PackageBody")
                )
            elif child == "PackageBody":
                package = [self.typedby._get_definition(child="PackageBody"), package]
            else:
                package["ownedRelationship"].insert(
                    0, self.typedby._get_definition(child=child)["ownedRelationship"][0]
                )

        return package

    def dump(self, child=None):
        return classtree(self._get_definition(child)).dump()

    def _set_name(self, name, short=False):
        if hasattr(self.grammar, "usage"):
            path = self.grammar.usage.declaration.declaration
        elif hasattr(self.grammar, "definition"):
            path = self.grammar.definition.declaration
        else:
            if hasattr(self.grammar.declaration, "declaration"):
                path = self.grammar.declaration.declaration
            else:
                path = self.grammar.declaration

        if path.identification is None:
            path.identification = Identification()

        if short:
            path.identification.declaredShortName = "<" + name + ">"
        else:
            self.name = name
            path.identification.declaredName = name

        return self

    def _get_name(self):
        return self.grammar.usage.declaration.declaration.identification.declaredName

    def _set_child(self, child):
        self.children.append(child)
        return self

    def _get_child(self, featurechain):
        # 'x.y.z'
        if isinstance(featurechain, str):
            fc = featurechain.split(".")
        else:
            raise TypeError

        if fc[0] == self.name:
            # This first one must match self name, otherwise pass it all
            featurechain = ".".join(fc[1:])

        for child in self.children:
            fcs = featurechain.split(".")
            if child.name == fcs[0]:
                if len(fcs) == 1:
                    return child
                else:
                    return child._get_child(featurechain)

    def _set_typed_by(self, typed):
        # Only set if the pointed object is a definition
        if "definition" in typed.grammar.__dict__:
            self.typedby = typed
            if "definition" in self.grammar.__dict__:
                raise ValueError("A definition element cannot be defined.")
            else:
                if self.grammar.usage.declaration.declaration.specialization is None:
                    package = {
                        "name": "QualifiedName",
                        "names": [typed.name],
                    }
                    package = {
                        "name": "FeatureType",
                        "type": package,
                        "ownedRelatedElement": [],
                    }
                    package = {"name": "OwnedFeatureTyping", "type": package}
                    package = {"name": "FeatureTyping", "ownedRelationship": package}
                    package = {"name": "TypedBy", "ownedRelationship": [package]}
                    package = {
                        "name": "Typings",
                        "typedby": package,
                        "ownedRelationship": [],
                    }
                    package = {
                        "name": "FeatureSpecialization",
                        "ownedRelationship": package,
                    }
                    package = {
                        "name": "FeatureSpecializationPart",
                        "specialization": [package],
                        "multiplicity": None,
                        "specialization2": [],
                        "multiplicity2": None,
                    }
                    self.grammar.usage.declaration.declaration.specialization = (
                        FeatureSpecializationPart(package)
                    )
        else:
            raise ValueError("Typed by element was not a definition.")
        return self

    def _get_grammar(self):
        self._ensure_body()
        return self.grammar

    def load_from_grammar(self, grammar):
        #!TODO Typed By
        self.__init__()
        self.grammar = grammar
        children = []
        if "usage" in self.grammar.__dict__:
            # This is a usage
            u_name = grammar.usage.declaration.declaration.identification.declaredName
            a_children = grammar.usage.completion.body.body.children

            for child in a_children:
                children.append(child.children[0].children[0])
        else:
            # This is a definition
            u_name = grammar.definition.declaration.identification.declaredName
            # grammar.definition.body.children is a list of DefinitionBodyItem
            # objects, each wrapping exactly one OccurrenceUsageMember /
            # NonOccurrenceUsageMember / DefinitionMember (`.children[0]`),
            # which in turn wraps exactly one OccurrenceUsageElement /
            # NonOccurrenceUsageElement / DefinitionElement (`.children[0]`
            # again) - unwrap to that so the shared loop below (which
            # expects one more `.children` hop to reach the actual
            # AttributeUsage/StructureUsageElement/nested-definition object,
            # matching what the usage branch above already produces) works
            # the same way for both usages and definitions.
            children = [
                item.children[0].children[0] for item in grammar.definition.body.children
            ]

        if u_name is not None:
            self.name = u_name

        for child in children:
            sc = child.children
            if isinstance(sc, list):
                if len(sc) == 1:
                    sc = sc[0]

            if sc.__class__.__name__ == "AttributeUsage":
                self.children.append(Attribute().load_from_grammar(sc))
            elif sc.__class__.__name__ == "ItemDefinition":
                self.children.append(Item().load_from_grammar(sc))
            elif sc.__class__.__name__ == "PartDefinition":
                self.children.append(Part(definition=True).load_from_grammar(sc))
            elif sc.__class__.__name__ == "PortDefinition":
                self.children.append(Port(definition=True).load_from_grammar(sc))
            elif sc.__class__.__name__ == "AttributeDefinition":
                self.children.append(Attribute(definition=True).load_from_grammar(sc))
            elif sc.__class__.__name__ == "UseCaseDefinition":
                self.children.append(UseCase().load_from_grammar(sc))
            elif sc.__class__.__name__ == "StructureUsageElement":
                if sc.children.__class__.__name__ == "PartUsage":
                    self.children.append(Part().load_from_grammar(sc.children))
                elif sc.children.__class__.__name__ == "ItemUsage":
                    self.children.append(Item().load_from_grammar(sc.children))
                elif sc.children.__class__.__name__ == "PortUsage":
                    self.children.append(Port().load_from_grammar(sc.children))
                else:
                    print(child.children.children.__class__.__name__)
                    raise NotImplementedError
            else:
                print(sc.__class__.__name__)
                raise NotImplementedError

        return self

    def add_directed_feature(self, direction, name=str(uuidlib.uuid4())):
        self._set_child(DefaultReference()._set_name(name).set_direction(direction))
        return self

    # def modify_directed_feature(self, direction, name):
    #     child = self._get_child(name)
    #     if child is not None:
    #         pass
    #     else:
    #         raise AttributeError("Invalid Feature Name or Chain")


class Attribute(Usage):
    def __init__(self, definition=False, name=None):
        Usage.__init__(self)

        if definition:
            self.grammar = AttributeDefinition()
        else:
            self.grammar = AttributeUsage()

    def usage_dump(self, child):
        # Override - base output

        # Add children
        body = []
        for abc in self.children:
            body.append(DefinitionBodyItem(abc.dump(child=True)).get_definition())
        if len(body) > 0:
            self.grammar.usage.completion.body.body = DefinitionBody(
                {"name": "DefinitionBody", "ownedRelatedElement": body}
            )

        # Add packaging
        package = {
            "name": "NonOccurrenceUsageElement",
            "ownedRelatedElement": self.grammar.get_definition(),
        }

        if child:
            package = {
                "name": "NonOccurrenceUsageMember",
                "prefix": None,
                "ownedRelatedElement": [package],
            }
            package = {"name": "DefinitionBodyItem", "ownedRelationship": [package]}
        else:
            # Add these packets to make this dump without parents
            package = {"name": "UsageElement", "ownedRelatedElement": package}
            package = {
                "name": "PackageMember",
                "ownedRelatedElement": package,
                "prefix": None,
            }
        return package

    def set_value(self, value):
        if not isinstance(value, pint.Quantity):
            value = ureg.Quantity(value)
        if isinstance(value, pint.Quantity):
            # "~" formats units in their short form ("kg", "N", "m / s"),
            # matching the strings astropy's str(unit) used to produce.
            # For dimensionless quantities it yields "", so the original
            # emptiness check is preserved.
            unit_str = f"{value.units:~}"
            if unit_str != "":
                package_units = {
                    "name": "QualifiedName",
                    "names": [unit_str],
                }
                package_units = {
                    "name": "FeatureReferenceMember",
                    "memberElement": package_units,
                }
                package_units = {
                    "name": "FeatureReferenceExpression",
                    "ownedRelationship": [package_units],
                }
                package_units = {
                    "name": "BaseExpression",
                    "ownedRelationship": package_units,
                }
                package_units = {
                    "name": "PrimaryExpression",
                    "operand": [],
                    "base": package_units,
                    "operator": [],
                    "ownedRelationship1": [],
                    "ownedRelationship2": [],
                }
                package_units = {
                    "name": "ExtentExpression",
                    "operator": "",
                    "ownedRelationship": [],
                    "primary": package_units,
                }
                package_units = {
                    "name": "UnaryExpression",
                    "operand": [],
                    "operator": None,
                    "extent": package_units,
                }
                package_units = {
                    "name": "ExponentiationExpression",
                    "operand": [],
                    "operator": [],
                    "unary": package_units,
                }
                package_units = {
                    "name": "MultiplicativeExpression",
                    "operation": [],
                    "exponential": package_units,
                }
                package_units = {
                    "name": "AdditiveExpression",
                    "operation": [],
                    "multiplicitive": package_units,
                }
                package_units = {
                    "name": "RangeExpression",
                    "operand": None,
                    "additive": package_units,
                }
                package_units = {
                    "name": "RelationalExpression",
                    "operation": [],
                    "range": package_units,
                }
                package_units = {
                    "name": "ClassificationExpression",
                    "operand": [],
                    "operator": None,
                    "ownedRelationship": [],
                    "relational": package_units,
                }
                package_units = {
                    "name": "EqualityExpression",
                    "operation": [],
                    "classification": package_units,
                }
                package_units = {
                    "name": "AndExpression",
                    "operation": [],
                    "equality": package_units,
                }
                package_units = {
                    "name": "XorExpression",
                    "operand": [],
                    "operator": [],
                    "and": package_units,
                }
                package_units = {
                    "name": "OrExpression",
                    "xor": package_units,
                    "operand": [],
                    "operator": [],
                }
                package_units = {
                    "name": "ImpliesExpression",
                    "operand": [],
                    "operator": [],
                    "or": package_units,
                }
                package_units = {
                    "name": "NullCoalescingExpression",
                    "implies": package_units,
                    "operator": [],
                    "operand": [],
                }
                package_units = {
                    "name": "ConditionalExpression",
                    "operator": None,
                    "operand": [package_units],
                }
                package_units = {"name": "OwnedExpression", "expression": package_units}
                package_units = {
                    "name": "SequenceExpression",
                    "operation": [],
                    "ownedRelationship": package_units,
                }
                package_units = [package_units]
                operator = ["["]
            else:
                package_units = []
                operator = []

            package = {
                "name": "BaseExpression",
                "ownedRelationship": {
                    "name": "LiteralInteger",
                    "value": str(float(value.magnitude)),
                },
            }
            package = {
                "name": "PrimaryExpression",
                "operand": package_units,
                "base": package,
                "operator": operator,
                "ownedRelationship1": [],
                "ownedRelationship2": [],
            }
            package = {
                "name": "ExtentExpression",
                "operator": "",
                "ownedRelationship": [],
                "primary": package,
            }
            package = {
                "name": "UnaryExpression",
                "operand": [],
                "operator": None,
                "extent": package,
            }
            package = {
                "name": "ExponentiationExpression",
                "operand": [],
                "operator": [],
                "unary": package,
            }
            package = {
                "name": "MultiplicativeExpression",
                "operation": [],
                "exponential": package,
            }
            package = {
                "name": "AdditiveExpression",
                "operation": [],
                "multiplicitive": package,
            }
            package = {
                "name": "RangeExpression",
                "operand": None,
                "additive": package,
            }
            package = {
                "name": "RelationalExpression",
                "operation": [],
                "range": package,
            }
            package = {
                "name": "ClassificationExpression",
                "operand": [],
                "operator": None,
                "ownedRelationship": [],
                "relational": package,
            }
            package = {
                "name": "EqualityExpression",
                "operation": [],
                "classification": package,
            }
            package = {
                "name": "AndExpression",
                "operation": [],
                "equality": package,
            }
            package = {
                "name": "XorExpression",
                "operand": [],
                "operator": [],
                "and": package,
            }
            package = {
                "name": "OrExpression",
                "xor": package,
                "operand": [],
                "operator": [],
            }
            package = {
                "name": "ImpliesExpression",
                "operand": [],
                "operator": [],
                "or": package,
            }
            package = {
                "name": "NullCoalescingExpression",
                "implies": package,
                "operator": [],
                "operand": [],
            }
            package = {
                "name": "ConditionalExpression",
                "operator": None,
                "operand": [package],
            }
            package = {"name": "OwnedExpression", "expression": package}
            package = {
                "name": "FeatureValue",
                "isDefault": False,
                "isEqual": False,
                "isInitial": False,
                "ownedRelatedElement": package,
            }
            package = {"name": "ValuePart", "ownedRelationship": [package]}
            self.grammar.usage.completion.valuepart = ValuePart(package)
            # value.unit

        return self

    def get_value(self):
        realpart = (
            self.grammar.usage.completion.valuepart.relationships[0]
            .element.expression.operands[0]
            .implies.orexpression.xor.andexpression.equality.classification.relational.range.additive.left_hand.exponential.unary.extent.primary
        )
        real = float(realpart.base.relationship.dump())
        unit = (
            realpart.operand[0]
            .relationship.expression.operands[0]
            .implies.orexpression.xor.andexpression.equality.classification.relational.range.additive.left_hand.exponential.unary.extent.primary.base.relationship.children[
                0
            ]
            .memberElement.dump()
        )
        return ureg.Quantity(real, unit)


class Part(Usage):
    def __init__(self, definition=False, name=None):
        Usage.__init__(self)
        if definition:
            self.grammar = PartDefinition()
        else:
            self.grammar = PartUsage()


class Item(Usage):
    def __init__(self, definition=False, name=None):
        Usage.__init__(self)
        if definition:
            self.grammar = ItemDefinition()
        else:
            self.grammar = ItemUsage()


class Port(Usage):
    def __init__(self, definition=False, name=None):
        Usage.__init__(self)
        if definition:
            self.grammar = PortDefinition()
        else:
            self.grammar = PortUsage()


class Actor:
    """A SysML `actor` member of a use case.

    Actors have no independent top-level existence in the SysML v2 grammar
    (they only appear nested inside a use case's body), so unlike
    Part/Item/Attribute this is a plain name holder, not a Usage subclass.
    """

    def __init__(self, name=None):
        self.name = name if name is not None else str(uuidlib.uuid4())

    def __repr__(self):
        return f"Actor({self.name!r})"


class UseCase:
    def __init__(self, definition=False, name=None):
        self.name = str(uuidlib.uuid4())
        self.actors = []
        # Names of use cases referenced via `include <name>;` in this use
        # case's body. Populated by load_from_grammar; there is currently
        # no add_include() to construct these fresh from Python, since
        # that would additionally require default-construction and
        # get_definition() support for CalculationBodyItem/ActionBodyItem
        # (the generic wrapper types `include` is nested under inside a
        # CaseBody) - out of scope for this pass.
        self.includes = []
        if definition:
            self.grammar = UseCaseDefinition()
        else:
            self.grammar = UseCaseUsage()
        if name is not None:
            self._set_name(name)

    def _is_definition(self):
        return isinstance(self.grammar, UseCaseDefinition)

    def _set_name(self, name):
        if self._is_definition():
            if self.grammar.declaration.identification is None:
                self.grammar.declaration.identification = Identification()
            self.grammar.declaration.identification.declaredName = name
        else:
            feature_declaration = self.grammar.declaration.declaration.declaration
            if feature_declaration.identification is None:
                feature_declaration.identification = Identification()
            feature_declaration.identification.declaredName = name
        self.name = name
        return self

    def _get_name(self):
        return self.name

    def add_actor(self, name):
        actor_usage = ActorUsage()
        actor_usage.set_name(name)
        # Mirror the parser: consecutive `actor X;` statements are one
        # ActorMember with multiple children (textX's `+=` is one-or-more
        # repetition, see grammar/classes.py's ActorMember), not separate
        # CaseBodyItems - so append to a trailing ActorMember if present
        # instead of always creating a new one.
        items = self.grammar.body.items
        if items and items[-1].child.__class__.__name__ == "ActorMember":
            items[-1].child.add_actor(actor_usage)
        else:
            actor_member = ActorMember()
            actor_member.add_actor(actor_usage)
            self.grammar.body.add_item(CaseBodyItem(child=actor_member))
        self.actors.append(Actor(name))
        return self

    def _get_definition(self, child=None):
        if self._is_definition():
            package = {
                "name": "DefinitionElement",
                "ownedRelatedElement": self.grammar.get_definition(),
            }
            if child == "DefinitionBody":
                package = {
                    "name": "DefinitionMember",
                    "prefix": None,
                    "ownedRelatedElement": [package],
                }
                package = {"name": "DefinitionBodyItem", "ownedRelationship": [package]}
            elif child == "PackageBody" or child is None:
                package = {
                    "name": "PackageMember",
                    "ownedRelatedElement": package,
                    "prefix": None,
                }
        else:
            package = {
                "name": "BehaviorUsageElement",
                "ownedRelationship": self.grammar.get_definition(),
            }
            package = {"name": "OccurrenceUsageElement", "ownedRelatedElement": package}
            if child == "DefinitionBody":
                package = {
                    "name": "OccurrenceUsageMember",
                    "prefix": None,
                    "ownedRelatedElement": [package],
                }
                package = {"name": "DefinitionBodyItem", "ownedRelationship": [package]}
            elif child == "PackageBody" or child is None:
                package = {"name": "UsageElement", "ownedRelatedElement": package}
                package = {
                    "name": "PackageMember",
                    "ownedRelatedElement": package,
                    "prefix": None,
                }

        if child is None:
            package = {
                "name": "PackageBodyElement",
                "ownedRelationship": [package],
                "prefix": None,
            }
        return package

    def dump(self, child=None):
        return classtree(self._get_definition(child)).dump()

    def load_from_grammar(self, grammar):
        self.__init__(definition=isinstance(grammar, UseCaseDefinition))
        self.grammar = grammar

        if self._is_definition():
            identification = grammar.declaration.identification
        else:
            identification = grammar.declaration.declaration.declaration.identification

        if identification is not None and identification.declaredName is not None:
            self.name = identification.declaredName

        for item in grammar.body.items:
            child = item.child
            if child.__class__.__name__ == "ActorMember":
                for actor_usage in child.children:
                    actor_name = (
                        actor_usage.child.declaration.declaration.identification.declaredName
                    )
                    self.actors.append(Actor(actor_name))
            elif child.__class__.__name__ == "CalculationBodyItem":
                for nested in child.children:
                    if nested.__class__.__name__ != "ActionBodyItem":
                        continue
                    for target in nested.children:
                        if target.__class__.__name__ != "ActionBodyItemTarget":
                            continue
                        member = target.children
                        if member.__class__.__name__ != "BehaviorUsageMember":
                            continue
                        for behavior_element in member.children:
                            behavior = behavior_element.children
                            if behavior.__class__.__name__ == "IncludeUseCaseUsage":
                                name = self._reference_name(behavior.ors)
                                if name is not None:
                                    self.includes.append(name)
            # SubjectMember/ObjectiveMember are parsed at the grammar level
            # (dump()/get_definition() work) but are not yet surfaced as
            # friendly attributes here.

        return self

    @staticmethod
    def _reference_name(ors):
        # Resolve the use case name referenced by `include <name>;`.
        # textX's PEG parser fills either `referencedFeature` (a single
        # QualifiedName) or `elements` (a list of OwnedFeatureChain,
        # segment-by-segment) depending on how the reference was written -
        # both are seen in practice, so both are handled here.
        if ors is None:
            return None
        if ors.referencedFeature is not None:
            return "::".join(ors.referencedFeature.names)
        parts = []
        for chain in ors.elements:
            for chaining in chain.feature.children:
                parts.extend(chaining.chainingFeature.names)
        return ".".join(parts) if parts else None


class DefaultReference(Usage):
    def __init__(self):
        Usage.__init__(self)
        self.grammar = DefaultReferenceUsage()

    def set_direction(self, direction):
        r = RefPrefix()
        if direction == "in":
            r.direction.isIn = True
        elif direction == "out":
            r.direction.isOut = True
        elif direction == "inout":
            r.direction.isInOut = True
        else:
            raise ValueError
        self.grammar.prefix = r
        return self

    def usage_dump(self, child):
        # This is a usage.

        self._ensure_body("definition")

        # Add packaging
        package = {
            "name": "NonOccurrenceUsageElement",
            "ownedRelatedElement": self.grammar.get_definition(),
        }

        if child == "DefinitionBody":
            package = {
                "name": "NonOccurrenceUsageMember",
                "prefix": None,
                "ownedRelatedElement": [package],
            }

            package = {"name": "DefinitionBodyItem", "ownedRelationship": [package]}
        elif "PackageBody":
            package = {"name": "UsageElement", "ownedRelatedElement": package}
            package = {
                "name": "PackageMember",
                "ownedRelatedElement": package,
                "prefix": None,
            }

        return package

    def _get_definition(self, child=None):
        package = self.usage_dump(child)

        if child is None:
            package = {
                "name": "PackageBodyElement",
                "ownedRelationship": [package],
                "prefix": None,
            }

        # Add the typed by definition to the package output
        if self.typedby is not None:
            if child is None:
                package["ownedRelationship"].insert(
                    0, self.typedby._get_definition(child="PackageBody")
                )
            elif child == "PackageBody":
                package = [self.typedby._get_definition(child="PackageBody"), package]
            else:
                package["ownedRelationship"].insert(
                    0, self.typedby._get_definition(child=child)["ownedRelationship"][0]
                )

        return package

    # def dump(self, child=None):
    #     package = self.usage_dump(child)

    #     if child is None:
    #         package = {
    #             "name": "PackageBodyElement",
    #             "ownedRelationship": [package],
    #             "prefix": None,
    #         }

    #     # Add the typed by definition to the package output
    #     if self.typedby is not None:
    #         if child is None:
    #             package["ownedRelationship"].insert(
    #                 0, self.typedby.dump(child="PackageBody")
    #             )
    #         elif child == "PackageBody":
    #             package = [self.typedby.dump(child="PackageBody"), package]
    #         else:
    #             package["ownedRelationship"].insert(
    #                 0, self.typedby.dump(child=child)["ownedRelationship"][0]
    #             )

    #     return package

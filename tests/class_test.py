#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 16:46:28 2023

@author: christophercox
"""

import pytest

from sysml2py.formatting import classtree
from sysml2py import Package, Item, Model, Attribute, Part, Port, UseCase, Actor, Action
from sysml2py import load_grammar as loads
from sysml2py.grammar.classes import UseCaseDefinition, UseCaseUsage


def test_package():
    p = classtree(Package()._get_definition()).dump()

    text = """package ;"""
    q = classtree(loads(text)).dump()

    assert p == q


def test_package_name():
    name = "Rocket"
    p = classtree(Package()._set_name(name)._get_definition()).dump()

    text = "package " + name + ";"
    q = classtree(loads(text)).dump()

    assert p == q


def test_package_shortname():
    name = "'3.1'"
    p = classtree(Package()._set_name(name, short=True)._get_definition()).dump()

    text = "package <" + name + ">;"
    q = classtree(loads(text)).dump()

    assert p == q


def test_package_setbothnames():
    name = "Rocket"
    shortname = "'3.1'"
    p = classtree(
        Package()._set_name(name)._set_name(shortname, short=True)._get_definition()
    ).dump()

    text = "package <" + shortname + "> " + name + ";"
    q = classtree(loads(text)).dump()

    assert p == q


def test_package_getname():
    name = "Rocket"
    p = Package()._set_name(name)
    assert p._get_name() == name


def test_package_addchild():
    p1 = Package()._set_name("Rocket")
    p2 = Package()._set_name("Engine")
    p1._set_child(p2)
    p = classtree(p1._get_definition()).dump()

    text = """package Rocket {
       package Engine;
    }"""

    q = classtree(loads(text)).dump()

    assert p == q


def test_package_get_child():
    p1 = Package()._set_name("Rocket")
    p2 = Package()._set_name("Engine")
    p1._set_child(p2)
    p = classtree(p1._get_child("Rocket.Engine")._get_definition()).dump()

    text = """package Engine;"""

    q = classtree(loads(text)).dump()

    assert p == q


def test_package_get_child_method2():
    p1 = Package()._set_name("Rocket")
    p2 = Package()._set_name("Engine")
    p1._set_child(p2)
    p = classtree(p1._get_child("Engine")._get_definition()).dump()

    text = """package Engine;"""

    q = classtree(loads(text)).dump()

    assert p == q


def test_package_typed_child():
    p1 = Package()._set_name("Rocket")
    i1 = Item(definition=True)._set_name("Fuel")
    i2 = Item()._set_name("Hydrogen")
    p1._set_child(i2)
    i2._set_typed_by(i1)
    p = classtree(p1._get_definition()).dump()

    text = """package Rocket {
       item def Fuel ;
       item Hydrogen : Fuel;
    }"""

    q = classtree(loads(text)).dump()

    assert p == q


def test_package_load_grammar():
    p = Package()

    text = """package Rocket {
       item def Fuel ;
       item Hydrogen : Fuel;
    }"""
    q = Model().load(text)
    p.load_from_grammar(q._get_child("Rocket")._get_grammar())

    assert p.dump() == q.dump()


def test_model_cannot_dump_error():
    m = Model()
    with pytest.raises(ValueError, match="Base Model has no elements."):
        m.dump()


def test_model_load_error_not_package_def():
    text = """item def Fuel ;"""
    with pytest.raises(
        ValueError, match="Base Model must be encapsulated by a package."
    ):
        Model().load(text)


def test_model_load_error_not_package_usage():
    text = """item Fuel ;"""
    with pytest.raises(
        ValueError, match="Base Model must be encapsulated by a package."
    ):
        Model().load(text)


def test_model_add_child():
    m = Model()
    p1 = Package()._set_name("Rocket")
    p2 = Package()._set_name("Payload")
    m._set_child(p1)
    m._set_child(p2)

    text = """package Rocket; 
    package Payload;"""
    q = classtree(loads(text))
    assert m.dump() == q.dump()


def test_model_get_child():
    m = Model()
    p1 = Package()._set_name("Rocket")
    p2 = Package()._set_name("Payload")
    m._set_child(p1)
    m._set_child(p2)
    m2 = m._get_child("Rocket")

    text = """package Rocket;"""
    q = classtree(loads(text))
    assert m2.dump() == q.dump()


def test_model_load():
    p1 = Package()._set_name("Rocket")
    i1 = Item(definition=True)._set_name("Fuel")
    i2 = Item()._set_name("Hydrogen")
    p1._set_child(i2)
    i2._set_typed_by(i1)
    p = classtree(p1._get_definition())

    text = """package Rocket {
       item def Fuel ;
       item Hydrogen : Fuel;
    }"""

    q = Model().load(text)

    assert p.dump() == q.dump()


def test_item():
    i1 = Item()
    text = """item;"""
    i2 = classtree(loads(text))

    assert i1.dump() == i2.dump()


def test_item_def():
    i1 = Item(definition=True)
    text = """item def;"""
    i2 = classtree(loads(text))

    assert i1.dump() == i2.dump()


def test_item_name():
    i1 = Item()._set_name("Fuel")
    text = """item Fuel;"""
    i2 = classtree(loads(text))

    assert i1.dump() == i2.dump()


def test_item_shortname():
    i1 = Item()._set_name("'3.1'", short=True)
    text = """item <'3.1'>;"""
    i2 = classtree(loads(text))

    assert i1.dump() == i2.dump()


def test_item_getname():
    name = "Fuel"
    i1 = Item()._set_name(name)

    assert i1._get_name() == name


def test_item_setchild():
    i1 = Item()._set_name("Fuel")
    ic1 = Item()
    i1._set_child(ic1)
    text = """item Fuel {
        item;
    }"""
    i2 = classtree(loads(text))

    assert i1.dump() == i2.dump()


def test_item_getchild():
    i1 = Item()._set_name("Fuel")
    ic1 = Item()._set_name("Fuel_child")
    i1._set_child(ic1)
    text = """item Fuel_child;"""
    i2 = classtree(loads(text))

    assert i1._get_child("Fuel.Fuel_child").dump() == i2.dump()


def test_item_getchild_skipelement():
    i1 = Item()._set_name("Fuel")
    ic1 = Item()._set_name("Fuel_child")
    i1._set_child(ic1)
    text = """item Fuel_child;"""
    i2 = classtree(loads(text))

    assert i1._get_child("Fuel_child").dump() == i2.dump()


def test_item_getchild_threelevel():
    i1 = Item()._set_name("Fuel")
    ic1 = Item()._set_name("child")
    ic2 = Item()._set_name("subchild")
    i1._set_child(ic1)
    ic1._set_child(ic2)
    text = """item subchild;"""
    i2 = classtree(loads(text))

    assert i1._get_child("Fuel.child.subchild").dump() == i2.dump()


def test_item_getchild_error_int():
    i1 = Item()._set_name("Fuel")
    ic1 = Item()._set_name("Fuel_child")
    i1._set_child(ic1)
    with pytest.raises(TypeError):
        i1._get_child(1)


def test_item_getchild_error_str():
    i1 = Item()._set_name("Fuel")
    ic1 = Item()._set_name("Fuel_child")
    i1._set_child(ic1)
    assert i1._get_child("Fuel.error") == None


def test_item_typedby():
    p1 = Package()._set_name("Store")
    i1 = Item()._set_name("apple")
    i2 = Item(definition=True)._set_name("Fruit")
    p1._set_child(i1)
    i1._set_typed_by(i2)

    text = """package Store {
       item def Fruit ;
       item apple : Fruit;
    }"""
    p2 = classtree(loads(text))

    assert p1.dump() == p2.dump()


def test_item_typedby_invalidusage_twousage():
    i1 = Item()._set_name("apple")
    i2 = Item()._set_name("Fruit")
    with pytest.raises(ValueError):
        i1._set_typed_by(i2)


def test_item_typedby_invalidusage_twodef():
    i1 = Item(definition=True)._set_name("apple")
    i2 = Item(definition=True)._set_name("Fruit")
    with pytest.raises(ValueError):
        i1._set_typed_by(i2)


def test_part_load_grammar():
    p = Part()

    text = """package Rocket {
        package EngineAssembly;
        part Tank {
            item def Fuel ;
            item Hydrogen : Fuel;
        }
    }"""
    q = Model().load(text)._get_child("Rocket.Tank")
    p.load_from_grammar(q._get_grammar())

    assert p.dump() == q.dump()


def test_part():
    i1 = Part()
    text = """part;"""
    i2 = classtree(loads(text))

    assert i1.dump() == i2.dump()


def test_part_def():
    i1 = Part(definition=True)
    text = """part def;"""
    i2 = classtree(loads(text))

    assert i1.dump() == i2.dump()


def test_part_name():
    i1 = Part()._set_name("Fuel")
    text = """part Fuel;"""
    i2 = classtree(loads(text))

    assert i1.dump() == i2.dump()


def test_part_shortname():
    i1 = Part()._set_name("'3.1'", short=True)
    text = """part <'3.1'>;"""
    i2 = classtree(loads(text))

    assert i1.dump() == i2.dump()


def test_part_getname():
    name = "Fuel"
    i1 = Part()._set_name(name)

    assert i1._get_name() == name


def test_part_setchild():
    i1 = Part()._set_name("Fuel")
    ic1 = Part()
    i1._set_child(ic1)
    text = """part Fuel {
        part;
    }"""
    i2 = classtree(loads(text))

    assert i1.dump() == i2.dump()


def test_part_getchild():
    i1 = Part()._set_name("Fuel")
    ic1 = Part()._set_name("Fuel_child")
    i1._set_child(ic1)
    text = """part Fuel_child;"""
    i2 = classtree(loads(text))

    assert i1._get_child("Fuel.Fuel_child").dump() == i2.dump()


def test_part_getchild_error_int():
    i1 = Part()._set_name("Fuel")
    ic1 = Part()._set_name("Fuel_child")
    i1._set_child(ic1)
    with pytest.raises(TypeError):
        i1._get_child(1)


def test_part_getchild_error_str():
    i1 = Part()._set_name("Fuel")
    ic1 = Part()._set_name("Fuel_child")
    i1._set_child(ic1)
    assert i1._get_child("Fuel.error") == None


def test_part_typedby():
    p1 = Package()._set_name("Store")
    i1 = Part()._set_name("apple")
    i2 = Part(definition=True)._set_name("Fruit")
    p1._set_child(i1)
    i1._set_typed_by(i2)

    text = """package Store {
       part def Fruit ;
       part apple : Fruit;
    }"""
    p2 = classtree(loads(text))

    assert p1.dump() == p2.dump()


def test_part_typedby_invalidusage_twousage():
    i1 = Part()._set_name("apple")
    i2 = Part()._set_name("Fruit")
    with pytest.raises(ValueError):
        i1._set_typed_by(i2)


def test_part_typedby_invalidusage_twodef():
    i1 = Part(definition=True)._set_name("apple")
    i2 = Part(definition=True)._set_name("Fruit")
    with pytest.raises(ValueError):
        i1._set_typed_by(i2)


def test_port():
    o1 = Port()
    text = """port;"""
    o2 = classtree(loads(text))

    assert o1.dump() == o2.dump()


def test_port_def():
    o1 = Port(definition=True)
    text = """port def;"""
    o2 = classtree(loads(text))

    assert o1.dump() == o2.dump()


def test_port_directed_in():
    o1 = Port()._set_name("FuelHose")
    o1.add_directed_feature("in", "Fuel")
    text = """port FuelHose {
       in Fuel ;
    }"""
    o2 = classtree(loads(text))
    assert o1.dump() == o2.dump()


def test_port_directed_out():
    o1 = Port()._set_name("FuelHose")
    o1.add_directed_feature("out", "Fuel")
    text = """port FuelHose {
       out Fuel ;
    }"""
    o2 = classtree(loads(text))
    assert o1.dump() == o2.dump()


def test_port_directed_inout():
    o1 = Port()._set_name("FuelHose")
    o1.add_directed_feature("inout", "Fuel")
    text = """port FuelHose {
       inout Fuel ;
    }"""
    o2 = classtree(loads(text))
    assert o1.dump() == o2.dump()


def test_port_directed_error():
    o1 = Port()
    with pytest.raises(ValueError):
        o1.add_directed_feature("error", "Fuel")


# This test doesn't work right now
# def test_item_def_subchild():
#     i = Item(definition=True)._set_name("Engine")
#     from sysml2py import ureg

#     a = Attribute()._set_name("mass")
#     a.set_value(100 * ureg.kg)
#     i._set_child(a)

#     text = """item Engine {
#         attribute mass= 100.0 [kg];
#     }"""

#     q = classtree(loads(text))

#     assert i.dump() == q.dump()


def test_attribute_definition():
    from sysml2py import ureg

    a = Attribute(definition=True)._set_name("mass")

    text = """attribute def mass;"""

    q = classtree(loads(text))

    assert a.dump() == q.dump()


def test_attribute_units():
    from sysml2py import ureg

    a = Attribute()._set_name("mass")
    a.set_value(100 * ureg.kg)

    text = """attribute mass= 100.0 [kg];"""

    q = classtree(loads(text))

    assert a.dump() == q.dump()


def test_attribute_getunits():
    from sysml2py import ureg

    value = 100 * ureg.kg

    a = Attribute()._set_name("mass")
    a.set_value(value)

    assert value == a.get_value()


def test_attribute_nounits():
    a = Attribute()._set_name("mass")
    a.set_value(100)

    text = """attribute mass= 100.0;"""

    q = classtree(loads(text))

    assert a.dump() == q.dump()


def test_usecase_definition():
    uc = UseCase(definition=True, name="DriveVehicle")

    text = """use case def DriveVehicle;"""
    q = classtree(loads(text))

    assert uc.dump() == q.dump()


def test_usecase_definition_getname():
    uc = UseCase(definition=True, name="DriveVehicle")
    assert uc._get_name() == "DriveVehicle"


def test_literal_real_with_units_round_trips_through_model_load():
    # Model.load() always rebuilds its grammar via get_definition() (see
    # definition.py Model.load/_ensure_body), so any attribute value that
    # parses to a LiteralReal (a real-number literal with a unit, e.g.
    # "5 [V]") exercises that path. LiteralReal was previously missing
    # get_definition() (unlike its sibling LiteralInteger), which raised
    # AttributeError for any real-valued, unit-carrying attribute nested in
    # a part/item/port definition.
    import sysml2py

    text = """package Demo {
    part def Battery {
        attribute voltage = 5 [V];
    }
}"""
    m = sysml2py.loads(text)
    assert "voltage" in m.dump()
    assert "5[V]" in m.dump().replace(" ", "").replace("\n", "")


def test_directed_port_usage_round_trips_through_model_load():
    # SysML v2 places the FeatureDirection keyword (in/out/inout) BEFORE
    # the usage keyword (e.g. "in port fuelIn : FuelPort;"), not after
    # ("port in fuelIn : ...") - confirmed against the textual-notation
    # syntax reference. Grammar-level support for this already existed
    # (OccurrenceUsagePrefix/RefPrefix/FeatureDirection), but
    # OccurrenceUsagePrefix and BasicUsagePrefix were missing
    # get_definition() (only had dump()), so any directed usage - not
    # port-specific, also affects part/item/attribute - raised
    # AttributeError as soon as Model.load() tried to reconstruct it.
    import sysml2py

    text = """package Demo {
    port def RfOutputPort;
    port def RfInputPort;
    part def Antenna {
        out port rf_out : RfOutputPort;
    }
    part def Amplifier {
        in port rf_in : RfInputPort;
    }
}"""
    m = sysml2py.loads(text)
    dumped = m.dump().replace(" ", "").replace("\n", "")
    assert "outportrf_out:RfOutputPort;" in dumped
    assert "inportrf_in:RfInputPort;" in dumped


def test_usecase_definition_with_actor():
    uc = UseCase(definition=True, name="DriveVehicle")
    uc.add_actor("Driver")

    text = """use case def DriveVehicle {
        actor Driver;
    }"""
    q = classtree(loads(text))

    assert uc.dump() == q.dump()
    assert [a.name for a in uc.actors] == ["Driver"]


def test_usecase_definition_with_multiple_actors():
    uc = UseCase(definition=True, name="ProcessOrder")
    uc.add_actor("Customer")
    uc.add_actor("Clerk")

    text = """use case def ProcessOrder {
        actor Customer;
        actor Clerk;
    }"""
    q = classtree(loads(text))

    assert uc.dump() == q.dump()
    assert [a.name for a in uc.actors] == ["Customer", "Clerk"]


def test_usecase_usage():
    uc = UseCase(name="uc1")

    text = """use case uc1;"""
    q = classtree(loads(text))

    assert uc.dump() == q.dump()


def test_actor_repr():
    assert repr(Actor("Driver")) == "Actor('Driver')"


def test_usecase_load_from_grammar_actors_and_includes():
    text = """use case def Login {
        actor Customer;
        include use case;
        include ValidateCredentials;
    }"""
    parsed = loads(text)
    grammar = UseCaseDefinition(
        parsed["ownedRelationship"][0]["ownedRelatedElement"]["ownedRelatedElement"]
    )

    uc = UseCase().load_from_grammar(grammar)

    assert uc.name == "Login"
    assert [a.name for a in uc.actors] == ["Customer"]
    assert uc.includes == ["ValidateCredentials"]
    assert uc.dump() == classtree(parsed).dump()


def test_usecase_usage_load_from_grammar():
    text = """use case uc1 {
        actor Rider;
    }"""
    parsed = loads(text)
    grammar = UseCaseUsage(
        parsed["ownedRelationship"][0]["ownedRelatedElement"]["ownedRelatedElement"][
            "ownedRelatedElement"
        ]["ownedRelationship"]
    )

    uc = UseCase().load_from_grammar(grammar)

    assert uc.name == "uc1"
    assert [a.name for a in uc.actors] == ["Rider"]
    assert uc.dump() == classtree(parsed).dump()


def test_package_usecase_child():
    p1 = Package()._set_name("Demo")
    uc = UseCase(definition=True, name="DriveVehicle")
    uc.add_actor("Driver")
    p1._set_child(uc)
    p = classtree(p1._get_definition())

    text = """package Demo {
       use case def DriveVehicle {
          actor Driver;
       }
    }"""

    q = Model().load(text)

    assert p.dump() == q.dump()


def test_package_usecase_load_from_grammar():
    text = """package Demo {
       use case def DriveVehicle {
          actor Driver;
       }
    }"""

    q = Model().load(text)
    uc = q._get_child("Demo.DriveVehicle")

    assert uc.name == "DriveVehicle"
    assert [a.name for a in uc.actors] == ["Driver"]


def test_definition_body_consecutive_same_kind_members_all_load():
    # Regression test: textX's `+=` (one-or-more repetition) merges
    # consecutive same-kind body statements (e.g. two `part`s in a row)
    # into a single OccurrenceUsageMember/DefinitionBodyItem rather than
    # one each. An earlier implementation of Usage.load_from_grammar only
    # took the first entry, silently dropping the rest.
    text = """package Demo {
       part def A;
       part def B;
       part def System {
          part a : A;
          part b : B;
          part c : A;
       }
    }"""

    q = Model().load(text)
    system = q._get_child("Demo.System")

    assert [c.name for c in system.children] == ["a", "b", "c"]
    assert q.dump() == classtree(loads(text)).dump()


def test_usage_body_consecutive_same_kind_members_all_load():
    text = """package Demo {
       item def Fuel;
       part def System {
          item f1 : Fuel;
          item f2 : Fuel;
       }
       part sys : System;
    }"""

    q = Model().load(text)
    system = q._get_child("Demo.System")

    assert [c.name for c in system.children] == ["f1", "f2"]


def test_connection_usage_load_and_dump():
    text = """package Demo {
       part def A {
          port p1;
       }
       part def B {
          port p2;
       }
       part def System {
          part a : A;
          part b : B;
          connect a.p1 to b.p2;
       }
    }"""

    q = Model().load(text)
    system = q._get_child("Demo.System")

    connections = [c for c in system.children if c.__class__.__name__ == "Connection"]
    assert len(connections) == 1
    assert connections[0].ends == ["a.p1", "b.p2"]
    assert q.dump() == classtree(loads(text)).dump()


def test_action_definition_successions_load_and_dump():
    text = """package Demo {
       action def DoStuff {
          action step1;
          then action step2;
          then action step3;
       }
    }"""

    q = Model().load(text)
    action = q._get_child("Demo.DoStuff")

    assert action.name == "DoStuff"
    assert action.successions == [("step1", "step2"), ("step2", "step3")]
    assert q.dump() == classtree(loads(text)).dump()


def test_action_usage_nested_in_part_loads_and_dumps():
    text = """package Demo {
       part def Vehicle {
          action step1;
       }
    }"""

    q = Model().load(text)
    vehicle = q._get_child("Demo.Vehicle")
    actions = [c for c in vehicle.children if isinstance(c, Action)]

    assert [a.name for a in actions] == ["step1"]
    assert q.dump() == classtree(loads(text)).dump()

import sys 

sys.path.append('..')

from app import app
from app.models import *

from conftest import test_session


def test_object_insertion_with_multiple_relations(test_session):
    
        o1 = Object(name='CPD')
        o2 = Object(name='robot')
        o3 = Object(name='nuero')
        o4 = Object(name='FEFU')
        o5 = Object(name='rocket')

        print(o5.child_in_relation)
        # res = db.session.add_all([o1, o2, o3, o4, o5])
        res = test_session.add_all([o1, o2, o3])


        test_session.flush()
        r1 = ObjectRelation(parent_object=o1, child_object=o2)
        r2 = ObjectRelation(parent_object=o1, child_object=o3)
        r3 = ObjectRelation(parent_object=o4, child_object=o1)
        # r3 = ObjectRelation(parent_object=o1, child_object=o4)
        # r4 = ObjectRelation(parent_object=o1, child_object=o5)
        # r5 = ObjectRelation(parent_object=o5, child_object=o1)

        # print(r1)

        # db.session.add_all([r1, r2, r3, r4])
        test_session.add_all([r1, r2, r3])

        test_session.flush()
        # print( r3,o4,o1, sep='\n')

        # print(r1, o11.parent_in_relations , o22)


def test_object_types_multiple_objects_with_same_type(test_session):
    
    t1 = ObjectType(type_name='room')
    test_session.add_all([t1])
    test_session.flush()

    o1 = Object(name='CPD', object_type=t1)
    o2 = Object(name='robot', object_type=t1)

    test_session.add_all([t1,o1,o2])

    # print(o1,o2, t1)

    test_session.flush()

    # print(o1,o2, t1)


def test_objects_types_with_attributes(test_session):
    type1 = ObjectType(type_name='room1')
    type2 = ObjectType(type_name='table')

    atr1 = Attribute(attribute_name='length1')
    atr2 = Attribute(attribute_name='width1')
    atr3 = Attribute(attribute_name='heigth1')
    atr4 = Attribute(attribute_name='color1')

    atr_t_1_1 = AttributeType(object_type=type1, attribute=atr1)
    atr_t_1_2 = AttributeType(object_type=type1, attribute=atr2)
    atr_t_1_3 = AttributeType(object_type=type1, attribute=atr3)

    atr_t_2_2 = AttributeType(object_type=type2, attribute=atr2)
    atr_t_2_3 = AttributeType(object_type=type2, attribute=atr3)
    atr_t_2_4 = AttributeType(object_type=type2, attribute=atr4)
    o1 = Object(name='CPD', object_type=type1)

    # print(atr_t_2_4.attribute)
    test_session.add_all([type1, type2, atr_t_1_1, atr_t_1_2, 
                            atr_t_1_3, atr_t_2_2, atr_t_2_3, atr_t_2_4, o1])
    test_session.flush()

    print(type1, type2, o1)

def test_object_with_attributes_with_values(test_session):
    o = Object(name='CPD')

    atr_1 = Attribute(attribute_name='length1')
    atr_2 = Attribute(attribute_name='heigth1')
    atr_3 = Attribute(attribute_name='weigth1')

    atr_val = AttributeValue(value='123', attribute=atr_1, object_=o)
    print(atr_val)

    test_session.add_all([atr_1, atr_2, atr_3, atr_val])
    test_session.flush()
    print(atr_val)

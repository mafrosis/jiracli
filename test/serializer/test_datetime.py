from dataclasses import dataclass
import datetime

from dateutil.tz import gettz, tzlocal, tzoffset
import pytest

from jira_offline.utils.serializer import DataclassSerializer


@dataclass
class Test(DataclassSerializer):
    dt: datetime.datetime


@pytest.mark.parametrize('tz_iso,tz_obj,tz_name', [
    ('', tzlocal(), None),
    ('+00:00', tzlocal(), None),
    ('+10:00', tzlocal(), None),
    ('-06:00', tzlocal(), None),
    ('', gettz('UTC'), 'UTC'),
    ('+00:00', gettz('UTC'), 'UTC'),
    ('+10:00', gettz('Australia/Melbourne'), 'Australia/Melbourne'),
    ('+00:00', gettz('Etc/GMT'), 'Etc/GMT'),
])
def test_datetime_deserialize(tz_iso, tz_obj, tz_name):
    """
    Test datetime deserializes, with a variety of timezones
    """
    obj = Test.deserialize({'dt': f'2018-09-24T08:44:06.333777{tz_iso}'}, tz=tz_name)
    assert isinstance(obj.dt, datetime.datetime)
    assert obj.dt.year == 2018
    assert obj.dt.month == 9
    assert obj.dt.day == 24
    assert obj.dt.hour == 8
    assert obj.dt.minute == 44
    assert obj.dt.second == 6
    assert obj.dt.microsecond == 333777
    assert obj.dt.tzinfo == tz_obj


@pytest.mark.parametrize('tz_iso,tz_name', [
    ('+00:00', None),
    ('+00:00', 'UTC'),
    ('+10:00', 'Australia/Melbourne'),
    ('+00:00', 'Etc/GMT'),
])
def test_datetime_deserialize_roundtrip(tz_iso, tz_name):
    """
    Test datetime deserializes/serializes in a loss-less roundtrip
    """
    json = Test.deserialize({'dt': f'2018-09-24T08:44:06.333777{tz_iso}'}, tz=tz_name).serialize()
    assert json['dt'] == f'2018-09-24T08:44:06.333777{tz_iso}'


@pytest.mark.parametrize('tz_iso,tz_obj', [
    ('+00:00', tzlocal()),
    ('+10:00', tzoffset(None, 36000)),
    ('+10:00', gettz('Australia/Melbourne')),
])
def test_datetime_serialize(tz_iso, tz_obj):
    """
    Test datetime serializes
    """
    json = Test(dt=datetime.datetime(2018, 9, 24, 8, 44, 6, 333777, tzinfo=tz_obj)).serialize()
    assert json['dt'] == f'2018-09-24T08:44:06.333777{tz_iso}'


@pytest.mark.parametrize('tz_obj,tz_name', [
    (tzlocal(), None),
    (gettz('UTC'), 'UTC'),
    (gettz('Australia/Melbourne'), 'Australia/Melbourne'),
    (gettz('Etc/GMT'), 'Etc/GMT'),
])
def test_datetime_serialize_roundtrip(tz_obj, tz_name):
    """
    Test datetime serializes/deserializes in a loss-less roundtrip
    """
    obj = Test.deserialize(
        Test(dt=datetime.datetime(2018, 9, 24, 8, 44, 6, 333777, tzinfo=tz_obj)).serialize(),
        tz=tz_name
    )
    assert obj.dt.year == 2018
    assert obj.dt.month == 9
    assert obj.dt.day == 24
    assert obj.dt.hour == 8
    assert obj.dt.minute == 44
    assert obj.dt.second == 6
    assert obj.dt.microsecond == 333777
    assert obj.dt.tzinfo == tz_obj

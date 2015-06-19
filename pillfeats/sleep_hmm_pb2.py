# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sleep_hmm.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='sleep_hmm.proto',
  package='',
  serialized_pb=_b('\n\x0fsleep_hmm.proto\",\n\x0cPoissonModel\x12\x0c\n\x04mean\x18\x01 \x02(\x01\x12\x0e\n\x06weight\x18\x02 \x01(\x01\">\n\x15\x44iscreteAlphabetModel\x12\x15\n\rprobabilities\x18\x01 \x03(\x01\x12\x0e\n\x06weight\x18\x02 \x01(\x01\":\n\nGammaModel\x12\x0c\n\x04mean\x18\x01 \x02(\x01\x12\x0e\n\x06stddev\x18\x02 \x02(\x01\x12\x0e\n\x06weight\x18\x03 \x01(\x01\"\x98\x03\n\nStateModel\x12\x1e\n\nsleep_mode\x18\x04 \x01(\x0e\x32\n.SleepMode\x12\x1a\n\x08\x62\x65\x64_mode\x18\x05 \x01(\x0e\x32\x08.BedMode\x12 \n\x0bsleep_depth\x18\x06 \x01(\x0e\x32\x0b.SleepDepth\x12\x1a\n\x05light\x18\x0b \x01(\x0b\x32\x0b.GammaModel\x12#\n\x0cmotion_count\x18\x0c \x01(\x0b\x32\r.PoissonModel\x12,\n\x0c\x64isturbances\x18\r \x01(\x0b\x32\x16.DiscreteAlphabetModel\x12$\n\x0flog_sound_count\x18\x0e \x01(\x0b\x32\x0b.GammaModel\x12\x34\n\x14natural_light_filter\x18\x0f \x01(\x0b\x32\x16.DiscreteAlphabetModel\x12+\n\x14partner_motion_count\x18\x10 \x01(\x0b\x32\r.PoissonModel\x12\x34\n\x14partner_disturbances\x18\x11 \x01(\x0b\x32\x16.DiscreteAlphabetModel\"\xca\x04\n\x08SleepHmm\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x0e\n\x06source\x18\x02 \x01(\t\x12\x1b\n\x06states\x18\x03 \x03(\x0b\x32\x0b.StateModel\x12\x12\n\nnum_states\x18\x04 \x01(\x05\x12\x1f\n\x17state_transition_matrix\x18\x05 \x03(\x01\x12#\n\x1binitial_state_probabilities\x18\x06 \x03(\x01\x12&\n\x1e\x61udio_disturbance_threshold_db\x18\x07 \x01(\x01\x12\x30\n(pill_magnitude_disturbance_threshold_lsb\x18\x08 \x01(\x01\x12\'\n\x1fnatural_light_filter_start_hour\x18\t \x01(\x01\x12&\n\x1enatural_light_filter_stop_hour\x18\n \x01(\x01\x12\x18\n\x10num_model_params\x18\x0b \x01(\x05\x12\x12\n\nmodel_name\x18\x0c \x01(\t\x12\"\n\x1anum_minutes_in_meas_period\x18\r \x01(\x05\x12\x1e\n\x16\x65nable_interval_search\x18\x0e \x01(\x08\x12\x1c\n\x14light_pre_multiplier\x18\x0f \x01(\x01\x12\x17\n\x0flight_floor_lux\x18\x10 \x01(\x01\x12\x1f\n\x17use_wave_as_disturbance\x18\x11 \x01(\x08\x12\x31\n)audio_level_above_background_threshold_db\x18\x12 \x01(\x01\"-\n\x10SleepHmmModelSet\x12\x19\n\x06models\x18\x01 \x03(\x0b\x32\t.SleepHmm*7\n\tSleepMode\x12\t\n\x05SLEEP\x10\x00\x12\x08\n\x04WAKE\x10\x01\x12\x15\n\x11\x43ONDITIONAL_SLEEP\x10\x02*7\n\x07\x42\x65\x64Mode\x12\n\n\x06ON_BED\x10\x00\x12\x0b\n\x07OFF_BED\x10\x01\x12\x13\n\x0f\x43ONDITIONAL_BED\x10\x02*G\n\nSleepDepth\x12\x12\n\x0eNOT_APPLICABLE\x10\x00\x12\t\n\x05LIGHT\x10\x01\x12\x0b\n\x07REGULAR\x10\x02\x12\r\n\tDISTURBED\x10\x03\x42\x32\n com.hello.suripu.api.datascienceB\x0eSleepHmmProtos')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_SLEEPMODE = _descriptor.EnumDescriptor(
  name='SleepMode',
  full_name='SleepMode',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SLEEP', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WAKE', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CONDITIONAL_SLEEP', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1236,
  serialized_end=1291,
)
_sym_db.RegisterEnumDescriptor(_SLEEPMODE)

SleepMode = enum_type_wrapper.EnumTypeWrapper(_SLEEPMODE)
_BEDMODE = _descriptor.EnumDescriptor(
  name='BedMode',
  full_name='BedMode',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ON_BED', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='OFF_BED', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CONDITIONAL_BED', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1293,
  serialized_end=1348,
)
_sym_db.RegisterEnumDescriptor(_BEDMODE)

BedMode = enum_type_wrapper.EnumTypeWrapper(_BEDMODE)
_SLEEPDEPTH = _descriptor.EnumDescriptor(
  name='SleepDepth',
  full_name='SleepDepth',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NOT_APPLICABLE', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LIGHT', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='REGULAR', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DISTURBED', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1350,
  serialized_end=1421,
)
_sym_db.RegisterEnumDescriptor(_SLEEPDEPTH)

SleepDepth = enum_type_wrapper.EnumTypeWrapper(_SLEEPDEPTH)
SLEEP = 0
WAKE = 1
CONDITIONAL_SLEEP = 2
ON_BED = 0
OFF_BED = 1
CONDITIONAL_BED = 2
NOT_APPLICABLE = 0
LIGHT = 1
REGULAR = 2
DISTURBED = 3



_POISSONMODEL = _descriptor.Descriptor(
  name='PoissonModel',
  full_name='PoissonModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='mean', full_name='PoissonModel.mean', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='weight', full_name='PoissonModel.weight', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=19,
  serialized_end=63,
)


_DISCRETEALPHABETMODEL = _descriptor.Descriptor(
  name='DiscreteAlphabetModel',
  full_name='DiscreteAlphabetModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='probabilities', full_name='DiscreteAlphabetModel.probabilities', index=0,
      number=1, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='weight', full_name='DiscreteAlphabetModel.weight', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=65,
  serialized_end=127,
)


_GAMMAMODEL = _descriptor.Descriptor(
  name='GammaModel',
  full_name='GammaModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='mean', full_name='GammaModel.mean', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='stddev', full_name='GammaModel.stddev', index=1,
      number=2, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='weight', full_name='GammaModel.weight', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=129,
  serialized_end=187,
)


_STATEMODEL = _descriptor.Descriptor(
  name='StateModel',
  full_name='StateModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sleep_mode', full_name='StateModel.sleep_mode', index=0,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bed_mode', full_name='StateModel.bed_mode', index=1,
      number=5, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sleep_depth', full_name='StateModel.sleep_depth', index=2,
      number=6, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='light', full_name='StateModel.light', index=3,
      number=11, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='motion_count', full_name='StateModel.motion_count', index=4,
      number=12, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='disturbances', full_name='StateModel.disturbances', index=5,
      number=13, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='log_sound_count', full_name='StateModel.log_sound_count', index=6,
      number=14, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='natural_light_filter', full_name='StateModel.natural_light_filter', index=7,
      number=15, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='partner_motion_count', full_name='StateModel.partner_motion_count', index=8,
      number=16, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='partner_disturbances', full_name='StateModel.partner_disturbances', index=9,
      number=17, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=190,
  serialized_end=598,
)


_SLEEPHMM = _descriptor.Descriptor(
  name='SleepHmm',
  full_name='SleepHmm',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='user_id', full_name='SleepHmm.user_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='source', full_name='SleepHmm.source', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='states', full_name='SleepHmm.states', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='num_states', full_name='SleepHmm.num_states', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='state_transition_matrix', full_name='SleepHmm.state_transition_matrix', index=4,
      number=5, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='initial_state_probabilities', full_name='SleepHmm.initial_state_probabilities', index=5,
      number=6, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='audio_disturbance_threshold_db', full_name='SleepHmm.audio_disturbance_threshold_db', index=6,
      number=7, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pill_magnitude_disturbance_threshold_lsb', full_name='SleepHmm.pill_magnitude_disturbance_threshold_lsb', index=7,
      number=8, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='natural_light_filter_start_hour', full_name='SleepHmm.natural_light_filter_start_hour', index=8,
      number=9, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='natural_light_filter_stop_hour', full_name='SleepHmm.natural_light_filter_stop_hour', index=9,
      number=10, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='num_model_params', full_name='SleepHmm.num_model_params', index=10,
      number=11, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='model_name', full_name='SleepHmm.model_name', index=11,
      number=12, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='num_minutes_in_meas_period', full_name='SleepHmm.num_minutes_in_meas_period', index=12,
      number=13, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='enable_interval_search', full_name='SleepHmm.enable_interval_search', index=13,
      number=14, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='light_pre_multiplier', full_name='SleepHmm.light_pre_multiplier', index=14,
      number=15, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='light_floor_lux', full_name='SleepHmm.light_floor_lux', index=15,
      number=16, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='use_wave_as_disturbance', full_name='SleepHmm.use_wave_as_disturbance', index=16,
      number=17, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='audio_level_above_background_threshold_db', full_name='SleepHmm.audio_level_above_background_threshold_db', index=17,
      number=18, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=601,
  serialized_end=1187,
)


_SLEEPHMMMODELSET = _descriptor.Descriptor(
  name='SleepHmmModelSet',
  full_name='SleepHmmModelSet',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='models', full_name='SleepHmmModelSet.models', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1189,
  serialized_end=1234,
)

_STATEMODEL.fields_by_name['sleep_mode'].enum_type = _SLEEPMODE
_STATEMODEL.fields_by_name['bed_mode'].enum_type = _BEDMODE
_STATEMODEL.fields_by_name['sleep_depth'].enum_type = _SLEEPDEPTH
_STATEMODEL.fields_by_name['light'].message_type = _GAMMAMODEL
_STATEMODEL.fields_by_name['motion_count'].message_type = _POISSONMODEL
_STATEMODEL.fields_by_name['disturbances'].message_type = _DISCRETEALPHABETMODEL
_STATEMODEL.fields_by_name['log_sound_count'].message_type = _GAMMAMODEL
_STATEMODEL.fields_by_name['natural_light_filter'].message_type = _DISCRETEALPHABETMODEL
_STATEMODEL.fields_by_name['partner_motion_count'].message_type = _POISSONMODEL
_STATEMODEL.fields_by_name['partner_disturbances'].message_type = _DISCRETEALPHABETMODEL
_SLEEPHMM.fields_by_name['states'].message_type = _STATEMODEL
_SLEEPHMMMODELSET.fields_by_name['models'].message_type = _SLEEPHMM
DESCRIPTOR.message_types_by_name['PoissonModel'] = _POISSONMODEL
DESCRIPTOR.message_types_by_name['DiscreteAlphabetModel'] = _DISCRETEALPHABETMODEL
DESCRIPTOR.message_types_by_name['GammaModel'] = _GAMMAMODEL
DESCRIPTOR.message_types_by_name['StateModel'] = _STATEMODEL
DESCRIPTOR.message_types_by_name['SleepHmm'] = _SLEEPHMM
DESCRIPTOR.message_types_by_name['SleepHmmModelSet'] = _SLEEPHMMMODELSET
DESCRIPTOR.enum_types_by_name['SleepMode'] = _SLEEPMODE
DESCRIPTOR.enum_types_by_name['BedMode'] = _BEDMODE
DESCRIPTOR.enum_types_by_name['SleepDepth'] = _SLEEPDEPTH

PoissonModel = _reflection.GeneratedProtocolMessageType('PoissonModel', (_message.Message,), dict(
  DESCRIPTOR = _POISSONMODEL,
  __module__ = 'sleep_hmm_pb2'
  # @@protoc_insertion_point(class_scope:PoissonModel)
  ))
_sym_db.RegisterMessage(PoissonModel)

DiscreteAlphabetModel = _reflection.GeneratedProtocolMessageType('DiscreteAlphabetModel', (_message.Message,), dict(
  DESCRIPTOR = _DISCRETEALPHABETMODEL,
  __module__ = 'sleep_hmm_pb2'
  # @@protoc_insertion_point(class_scope:DiscreteAlphabetModel)
  ))
_sym_db.RegisterMessage(DiscreteAlphabetModel)

GammaModel = _reflection.GeneratedProtocolMessageType('GammaModel', (_message.Message,), dict(
  DESCRIPTOR = _GAMMAMODEL,
  __module__ = 'sleep_hmm_pb2'
  # @@protoc_insertion_point(class_scope:GammaModel)
  ))
_sym_db.RegisterMessage(GammaModel)

StateModel = _reflection.GeneratedProtocolMessageType('StateModel', (_message.Message,), dict(
  DESCRIPTOR = _STATEMODEL,
  __module__ = 'sleep_hmm_pb2'
  # @@protoc_insertion_point(class_scope:StateModel)
  ))
_sym_db.RegisterMessage(StateModel)

SleepHmm = _reflection.GeneratedProtocolMessageType('SleepHmm', (_message.Message,), dict(
  DESCRIPTOR = _SLEEPHMM,
  __module__ = 'sleep_hmm_pb2'
  # @@protoc_insertion_point(class_scope:SleepHmm)
  ))
_sym_db.RegisterMessage(SleepHmm)

SleepHmmModelSet = _reflection.GeneratedProtocolMessageType('SleepHmmModelSet', (_message.Message,), dict(
  DESCRIPTOR = _SLEEPHMMMODELSET,
  __module__ = 'sleep_hmm_pb2'
  # @@protoc_insertion_point(class_scope:SleepHmmModelSet)
  ))
_sym_db.RegisterMessage(SleepHmmModelSet)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n com.hello.suripu.api.datascienceB\016SleepHmmProtos'))
# @@protoc_insertion_point(module_scope)

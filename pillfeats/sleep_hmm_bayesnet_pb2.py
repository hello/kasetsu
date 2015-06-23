# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sleep_hmm_bayesnet.proto

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
  name='sleep_hmm_bayesnet.proto',
  package='hello',
  serialized_pb=_b('\n\x18sleep_hmm_bayesnet.proto\x12\x05hello\"\x1c\n\x0cPoissonModel\x12\x0c\n\x04mean\x18\x01 \x02(\x01\".\n\x15\x44iscreteAlphabetModel\x12\x15\n\rprobabilities\x18\x01 \x03(\x01\"*\n\nGammaModel\x12\x0c\n\x04mean\x18\x01 \x02(\x01\x12\x0e\n\x06stddev\x18\x02 \x02(\x01\"\x1e\n\x0e\x43hiSquareModel\x12\x0c\n\x04mean\x18\x01 \x02(\x01\";\n\x1bOneDimensionalGaussianModel\x12\x0c\n\x04mean\x18\x01 \x02(\x01\x12\x0e\n\x06stddev\x18\x02 \x02(\x01\"\xc4\x02\n\x08ObsModel\x12\x13\n\x0bstate_index\x18\x01 \x02(\x05\x12\"\n\tmeas_type\x18\x02 \x02(\x0e\x32\x0f.hello.MeasType\x12(\n\tchisquare\x18\x05 \x01(\x0b\x32\x15.hello.ChiSquareModel\x12\x34\n\x08gaussian\x18\x06 \x01(\x0b\x32\".hello.OneDimensionalGaussianModel\x12 \n\x05gamma\x18\x07 \x01(\x0b\x32\x11.hello.GammaModel\x12$\n\x07poisson\x18\x08 \x01(\x0b\x32\x13.hello.PoissonModel\x12.\n\x08\x61lphabet\x18\t \x01(\x0b\x32\x1c.hello.DiscreteAlphabetModel\x12\x0e\n\x06weight\x18\x14 \x01(\x01\x12\x17\n\x0fnum_free_params\x18\x15 \x01(\x05\"+\n\x0c\x42\x65taCondProb\x12\r\n\x05\x61lpha\x18\x01 \x02(\x01\x12\x0c\n\x04\x62\x65ta\x18\x02 \x02(\x01\"T\n\tCondProbs\x12\x10\n\x08model_id\x18\x01 \x02(\t\x12\x11\n\toutput_id\x18\x02 \x02(\t\x12\"\n\x05probs\x18\x03 \x03(\x0b\x32\x13.hello.BetaCondProb\"\x95\x01\n\x11HiddenMarkovModel\x12\n\n\x02id\x18\x01 \x02(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\x12*\n\x11observation_model\x18\x03 \x03(\x0b\x32\x0f.hello.ObsModel\x12\x1f\n\x17state_transition_matrix\x18\x04 \x03(\x01\x12\x12\n\nnum_states\x18\x05 \x02(\x05\"\xaa\x02\n\x11MeasurementParams\x12\"\n\x1anum_minutes_in_meas_period\x18\x01 \x01(\x05\x12\x1e\n\x16\x65nable_interval_search\x18\x02 \x01(\x08\x12\'\n\x1fnatural_light_filter_start_hour\x18\x03 \x01(\x01\x12&\n\x1enatural_light_filter_stop_hour\x18\x04 \x01(\x01\x12\x1c\n\x14light_pre_multiplier\x18\x05 \x01(\x01\x12\x17\n\x0flight_floor_lux\x18\x06 \x01(\x01\x12\"\n\x1ause_waves_for_disturbances\x18\x07 \x01(\x08\x12%\n\x1dmotion_count_for_disturbances\x18\x08 \x01(\x01\"\xb0\x01\n\x0bHmmBayesNet\x12\x38\n\x16measurement_parameters\x18\x01 \x02(\x0b\x32\x18.hello.MeasurementParams\x12\x32\n\x10independent_hmms\x18\x02 \x03(\x0b\x32\x18.hello.HiddenMarkovModel\x12\x33\n\x19\x63onditional_probabilities\x18\x03 \x03(\x0b\x32\x10.hello.CondProbs*p\n\x08MeasType\x12\r\n\tLOG_LIGHT\x10\x00\x12\x13\n\x0fMOTION_DURATION\x10\x01\x12\x1e\n\x1aPILL_MAGNITUDE_DISTURBANCE\x10\x02\x12\x11\n\rNATURAL_LIGHT\x10\x03\x12\r\n\tLOG_SOUND\x10\x04\x42:\n com.hello.suripu.api.datascienceB\x16SleepHmmBayesNetProtos')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_MEASTYPE = _descriptor.EnumDescriptor(
  name='MeasType',
  full_name='hello.MeasType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='LOG_LIGHT', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MOTION_DURATION', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PILL_MAGNITUDE_DISTURBANCE', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NATURAL_LIGHT', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LOG_SOUND', index=4, number=4,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1340,
  serialized_end=1452,
)
_sym_db.RegisterEnumDescriptor(_MEASTYPE)

MeasType = enum_type_wrapper.EnumTypeWrapper(_MEASTYPE)
LOG_LIGHT = 0
MOTION_DURATION = 1
PILL_MAGNITUDE_DISTURBANCE = 2
NATURAL_LIGHT = 3
LOG_SOUND = 4



_POISSONMODEL = _descriptor.Descriptor(
  name='PoissonModel',
  full_name='hello.PoissonModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='mean', full_name='hello.PoissonModel.mean', index=0,
      number=1, type=1, cpp_type=5, label=2,
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
  serialized_start=35,
  serialized_end=63,
)


_DISCRETEALPHABETMODEL = _descriptor.Descriptor(
  name='DiscreteAlphabetModel',
  full_name='hello.DiscreteAlphabetModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='probabilities', full_name='hello.DiscreteAlphabetModel.probabilities', index=0,
      number=1, type=1, cpp_type=5, label=3,
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
  serialized_start=65,
  serialized_end=111,
)


_GAMMAMODEL = _descriptor.Descriptor(
  name='GammaModel',
  full_name='hello.GammaModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='mean', full_name='hello.GammaModel.mean', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='stddev', full_name='hello.GammaModel.stddev', index=1,
      number=2, type=1, cpp_type=5, label=2,
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
  serialized_start=113,
  serialized_end=155,
)


_CHISQUAREMODEL = _descriptor.Descriptor(
  name='ChiSquareModel',
  full_name='hello.ChiSquareModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='mean', full_name='hello.ChiSquareModel.mean', index=0,
      number=1, type=1, cpp_type=5, label=2,
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
  serialized_start=157,
  serialized_end=187,
)


_ONEDIMENSIONALGAUSSIANMODEL = _descriptor.Descriptor(
  name='OneDimensionalGaussianModel',
  full_name='hello.OneDimensionalGaussianModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='mean', full_name='hello.OneDimensionalGaussianModel.mean', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='stddev', full_name='hello.OneDimensionalGaussianModel.stddev', index=1,
      number=2, type=1, cpp_type=5, label=2,
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
  serialized_start=189,
  serialized_end=248,
)


_OBSMODEL = _descriptor.Descriptor(
  name='ObsModel',
  full_name='hello.ObsModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='state_index', full_name='hello.ObsModel.state_index', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='meas_type', full_name='hello.ObsModel.meas_type', index=1,
      number=2, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='chisquare', full_name='hello.ObsModel.chisquare', index=2,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gaussian', full_name='hello.ObsModel.gaussian', index=3,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gamma', full_name='hello.ObsModel.gamma', index=4,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='poisson', full_name='hello.ObsModel.poisson', index=5,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='alphabet', full_name='hello.ObsModel.alphabet', index=6,
      number=9, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='weight', full_name='hello.ObsModel.weight', index=7,
      number=20, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='num_free_params', full_name='hello.ObsModel.num_free_params', index=8,
      number=21, type=5, cpp_type=1, label=1,
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
  serialized_start=251,
  serialized_end=575,
)


_BETACONDPROB = _descriptor.Descriptor(
  name='BetaCondProb',
  full_name='hello.BetaCondProb',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='alpha', full_name='hello.BetaCondProb.alpha', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='beta', full_name='hello.BetaCondProb.beta', index=1,
      number=2, type=1, cpp_type=5, label=2,
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
  serialized_start=577,
  serialized_end=620,
)


_CONDPROBS = _descriptor.Descriptor(
  name='CondProbs',
  full_name='hello.CondProbs',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='model_id', full_name='hello.CondProbs.model_id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='output_id', full_name='hello.CondProbs.output_id', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='probs', full_name='hello.CondProbs.probs', index=2,
      number=3, type=11, cpp_type=10, label=3,
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
  serialized_start=622,
  serialized_end=706,
)


_HIDDENMARKOVMODEL = _descriptor.Descriptor(
  name='HiddenMarkovModel',
  full_name='hello.HiddenMarkovModel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='hello.HiddenMarkovModel.id', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='description', full_name='hello.HiddenMarkovModel.description', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='observation_model', full_name='hello.HiddenMarkovModel.observation_model', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='state_transition_matrix', full_name='hello.HiddenMarkovModel.state_transition_matrix', index=3,
      number=4, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='num_states', full_name='hello.HiddenMarkovModel.num_states', index=4,
      number=5, type=5, cpp_type=1, label=2,
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
  serialized_start=709,
  serialized_end=858,
)


_MEASUREMENTPARAMS = _descriptor.Descriptor(
  name='MeasurementParams',
  full_name='hello.MeasurementParams',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='num_minutes_in_meas_period', full_name='hello.MeasurementParams.num_minutes_in_meas_period', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='enable_interval_search', full_name='hello.MeasurementParams.enable_interval_search', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='natural_light_filter_start_hour', full_name='hello.MeasurementParams.natural_light_filter_start_hour', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='natural_light_filter_stop_hour', full_name='hello.MeasurementParams.natural_light_filter_stop_hour', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='light_pre_multiplier', full_name='hello.MeasurementParams.light_pre_multiplier', index=4,
      number=5, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='light_floor_lux', full_name='hello.MeasurementParams.light_floor_lux', index=5,
      number=6, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='use_waves_for_disturbances', full_name='hello.MeasurementParams.use_waves_for_disturbances', index=6,
      number=7, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='motion_count_for_disturbances', full_name='hello.MeasurementParams.motion_count_for_disturbances', index=7,
      number=8, type=1, cpp_type=5, label=1,
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
  serialized_start=861,
  serialized_end=1159,
)


_HMMBAYESNET = _descriptor.Descriptor(
  name='HmmBayesNet',
  full_name='hello.HmmBayesNet',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='measurement_parameters', full_name='hello.HmmBayesNet.measurement_parameters', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='independent_hmms', full_name='hello.HmmBayesNet.independent_hmms', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='conditional_probabilities', full_name='hello.HmmBayesNet.conditional_probabilities', index=2,
      number=3, type=11, cpp_type=10, label=3,
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
  serialized_start=1162,
  serialized_end=1338,
)

_OBSMODEL.fields_by_name['meas_type'].enum_type = _MEASTYPE
_OBSMODEL.fields_by_name['chisquare'].message_type = _CHISQUAREMODEL
_OBSMODEL.fields_by_name['gaussian'].message_type = _ONEDIMENSIONALGAUSSIANMODEL
_OBSMODEL.fields_by_name['gamma'].message_type = _GAMMAMODEL
_OBSMODEL.fields_by_name['poisson'].message_type = _POISSONMODEL
_OBSMODEL.fields_by_name['alphabet'].message_type = _DISCRETEALPHABETMODEL
_CONDPROBS.fields_by_name['probs'].message_type = _BETACONDPROB
_HIDDENMARKOVMODEL.fields_by_name['observation_model'].message_type = _OBSMODEL
_HMMBAYESNET.fields_by_name['measurement_parameters'].message_type = _MEASUREMENTPARAMS
_HMMBAYESNET.fields_by_name['independent_hmms'].message_type = _HIDDENMARKOVMODEL
_HMMBAYESNET.fields_by_name['conditional_probabilities'].message_type = _CONDPROBS
DESCRIPTOR.message_types_by_name['PoissonModel'] = _POISSONMODEL
DESCRIPTOR.message_types_by_name['DiscreteAlphabetModel'] = _DISCRETEALPHABETMODEL
DESCRIPTOR.message_types_by_name['GammaModel'] = _GAMMAMODEL
DESCRIPTOR.message_types_by_name['ChiSquareModel'] = _CHISQUAREMODEL
DESCRIPTOR.message_types_by_name['OneDimensionalGaussianModel'] = _ONEDIMENSIONALGAUSSIANMODEL
DESCRIPTOR.message_types_by_name['ObsModel'] = _OBSMODEL
DESCRIPTOR.message_types_by_name['BetaCondProb'] = _BETACONDPROB
DESCRIPTOR.message_types_by_name['CondProbs'] = _CONDPROBS
DESCRIPTOR.message_types_by_name['HiddenMarkovModel'] = _HIDDENMARKOVMODEL
DESCRIPTOR.message_types_by_name['MeasurementParams'] = _MEASUREMENTPARAMS
DESCRIPTOR.message_types_by_name['HmmBayesNet'] = _HMMBAYESNET
DESCRIPTOR.enum_types_by_name['MeasType'] = _MEASTYPE

PoissonModel = _reflection.GeneratedProtocolMessageType('PoissonModel', (_message.Message,), dict(
  DESCRIPTOR = _POISSONMODEL,
  __module__ = 'sleep_hmm_bayesnet_pb2'
  # @@protoc_insertion_point(class_scope:hello.PoissonModel)
  ))
_sym_db.RegisterMessage(PoissonModel)

DiscreteAlphabetModel = _reflection.GeneratedProtocolMessageType('DiscreteAlphabetModel', (_message.Message,), dict(
  DESCRIPTOR = _DISCRETEALPHABETMODEL,
  __module__ = 'sleep_hmm_bayesnet_pb2'
  # @@protoc_insertion_point(class_scope:hello.DiscreteAlphabetModel)
  ))
_sym_db.RegisterMessage(DiscreteAlphabetModel)

GammaModel = _reflection.GeneratedProtocolMessageType('GammaModel', (_message.Message,), dict(
  DESCRIPTOR = _GAMMAMODEL,
  __module__ = 'sleep_hmm_bayesnet_pb2'
  # @@protoc_insertion_point(class_scope:hello.GammaModel)
  ))
_sym_db.RegisterMessage(GammaModel)

ChiSquareModel = _reflection.GeneratedProtocolMessageType('ChiSquareModel', (_message.Message,), dict(
  DESCRIPTOR = _CHISQUAREMODEL,
  __module__ = 'sleep_hmm_bayesnet_pb2'
  # @@protoc_insertion_point(class_scope:hello.ChiSquareModel)
  ))
_sym_db.RegisterMessage(ChiSquareModel)

OneDimensionalGaussianModel = _reflection.GeneratedProtocolMessageType('OneDimensionalGaussianModel', (_message.Message,), dict(
  DESCRIPTOR = _ONEDIMENSIONALGAUSSIANMODEL,
  __module__ = 'sleep_hmm_bayesnet_pb2'
  # @@protoc_insertion_point(class_scope:hello.OneDimensionalGaussianModel)
  ))
_sym_db.RegisterMessage(OneDimensionalGaussianModel)

ObsModel = _reflection.GeneratedProtocolMessageType('ObsModel', (_message.Message,), dict(
  DESCRIPTOR = _OBSMODEL,
  __module__ = 'sleep_hmm_bayesnet_pb2'
  # @@protoc_insertion_point(class_scope:hello.ObsModel)
  ))
_sym_db.RegisterMessage(ObsModel)

BetaCondProb = _reflection.GeneratedProtocolMessageType('BetaCondProb', (_message.Message,), dict(
  DESCRIPTOR = _BETACONDPROB,
  __module__ = 'sleep_hmm_bayesnet_pb2'
  # @@protoc_insertion_point(class_scope:hello.BetaCondProb)
  ))
_sym_db.RegisterMessage(BetaCondProb)

CondProbs = _reflection.GeneratedProtocolMessageType('CondProbs', (_message.Message,), dict(
  DESCRIPTOR = _CONDPROBS,
  __module__ = 'sleep_hmm_bayesnet_pb2'
  # @@protoc_insertion_point(class_scope:hello.CondProbs)
  ))
_sym_db.RegisterMessage(CondProbs)

HiddenMarkovModel = _reflection.GeneratedProtocolMessageType('HiddenMarkovModel', (_message.Message,), dict(
  DESCRIPTOR = _HIDDENMARKOVMODEL,
  __module__ = 'sleep_hmm_bayesnet_pb2'
  # @@protoc_insertion_point(class_scope:hello.HiddenMarkovModel)
  ))
_sym_db.RegisterMessage(HiddenMarkovModel)

MeasurementParams = _reflection.GeneratedProtocolMessageType('MeasurementParams', (_message.Message,), dict(
  DESCRIPTOR = _MEASUREMENTPARAMS,
  __module__ = 'sleep_hmm_bayesnet_pb2'
  # @@protoc_insertion_point(class_scope:hello.MeasurementParams)
  ))
_sym_db.RegisterMessage(MeasurementParams)

HmmBayesNet = _reflection.GeneratedProtocolMessageType('HmmBayesNet', (_message.Message,), dict(
  DESCRIPTOR = _HMMBAYESNET,
  __module__ = 'sleep_hmm_bayesnet_pb2'
  # @@protoc_insertion_point(class_scope:hello.HmmBayesNet)
  ))
_sym_db.RegisterMessage(HmmBayesNet)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n com.hello.suripu.api.datascienceB\026SleepHmmBayesNetProtos'))
# @@protoc_insertion_point(module_scope)

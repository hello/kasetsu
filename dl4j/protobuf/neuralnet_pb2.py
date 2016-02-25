# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: neuralnet.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='neuralnet.proto',
  package='',
  serialized_pb='\n\x0fneuralnet.proto\"\x92\x01\n\x10NeuralNetMessage\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x06params\x18\x02 \x01(\x0c\x12\x15\n\rconfiguration\x18\x03 \x01(\t\x12/\n\ninput_type\x18\x04 \x01(\x0e\x32\x1b.NeuralNetMessage.InputType\"\x1a\n\tInputType\x12\r\n\tDIFFLIGHT\x10\x00\x42\x33\n com.hello.suripu.api.datascienceB\x0fNeuralNetProtos')



_NEURALNETMESSAGE_INPUTTYPE = _descriptor.EnumDescriptor(
  name='InputType',
  full_name='NeuralNetMessage.InputType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='DIFFLIGHT', index=0, number=0,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=140,
  serialized_end=166,
)


_NEURALNETMESSAGE = _descriptor.Descriptor(
  name='NeuralNetMessage',
  full_name='NeuralNetMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='NeuralNetMessage.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='params', full_name='NeuralNetMessage.params', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='configuration', full_name='NeuralNetMessage.configuration', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='input_type', full_name='NeuralNetMessage.input_type', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _NEURALNETMESSAGE_INPUTTYPE,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=20,
  serialized_end=166,
)

_NEURALNETMESSAGE.fields_by_name['input_type'].enum_type = _NEURALNETMESSAGE_INPUTTYPE
_NEURALNETMESSAGE_INPUTTYPE.containing_type = _NEURALNETMESSAGE;
DESCRIPTOR.message_types_by_name['NeuralNetMessage'] = _NEURALNETMESSAGE

class NeuralNetMessage(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _NEURALNETMESSAGE

  # @@protoc_insertion_point(class_scope:NeuralNetMessage)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), '\n com.hello.suripu.api.datascienceB\017NeuralNetProtos')
# @@protoc_insertion_point(module_scope)

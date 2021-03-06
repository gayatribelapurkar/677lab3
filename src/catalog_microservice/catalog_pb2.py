# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: catalog.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rcatalog.proto\"\x1b\n\x0cQueryRequest\x12\x0b\n\x03toy\x18\x01 \x01(\t\")\n\rUpdateRequest\x12\x0b\n\x03toy\x18\x01 \x01(\t\x12\x0b\n\x03num\x18\x02 \x01(\x05\"-\n\nQueryReply\x12\r\n\x05price\x18\x01 \x01(\x02\x12\x10\n\x08quantity\x18\x02 \x01(\x05\"\x1d\n\x0bUpdateReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\"2\n\x19LeaderNotificationRequest\x12\x15\n\rleaderadderss\x18\x01 \x01(\t\")\n\x17LeaderNotificationReply\x12\x0e\n\x06status\x18\x01 \x01(\x05\x32\xa8\x01\n\x07\x43\x61talog\x12%\n\x05Query\x12\r.QueryRequest\x1a\x0b.QueryReply\"\x00\x12(\n\x06Update\x12\x0e.UpdateRequest\x1a\x0c.UpdateReply\"\x00\x12L\n\x12LeaderNotification\x12\x1a.LeaderNotificationRequest\x1a\x18.LeaderNotificationReply\"\x00\x62\x06proto3')



_QUERYREQUEST = DESCRIPTOR.message_types_by_name['QueryRequest']
_UPDATEREQUEST = DESCRIPTOR.message_types_by_name['UpdateRequest']
_QUERYREPLY = DESCRIPTOR.message_types_by_name['QueryReply']
_UPDATEREPLY = DESCRIPTOR.message_types_by_name['UpdateReply']
_LEADERNOTIFICATIONREQUEST = DESCRIPTOR.message_types_by_name['LeaderNotificationRequest']
_LEADERNOTIFICATIONREPLY = DESCRIPTOR.message_types_by_name['LeaderNotificationReply']
QueryRequest = _reflection.GeneratedProtocolMessageType('QueryRequest', (_message.Message,), {
  'DESCRIPTOR' : _QUERYREQUEST,
  '__module__' : 'catalog_pb2'
  # @@protoc_insertion_point(class_scope:QueryRequest)
  })
_sym_db.RegisterMessage(QueryRequest)

UpdateRequest = _reflection.GeneratedProtocolMessageType('UpdateRequest', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEREQUEST,
  '__module__' : 'catalog_pb2'
  # @@protoc_insertion_point(class_scope:UpdateRequest)
  })
_sym_db.RegisterMessage(UpdateRequest)

QueryReply = _reflection.GeneratedProtocolMessageType('QueryReply', (_message.Message,), {
  'DESCRIPTOR' : _QUERYREPLY,
  '__module__' : 'catalog_pb2'
  # @@protoc_insertion_point(class_scope:QueryReply)
  })
_sym_db.RegisterMessage(QueryReply)

UpdateReply = _reflection.GeneratedProtocolMessageType('UpdateReply', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEREPLY,
  '__module__' : 'catalog_pb2'
  # @@protoc_insertion_point(class_scope:UpdateReply)
  })
_sym_db.RegisterMessage(UpdateReply)

LeaderNotificationRequest = _reflection.GeneratedProtocolMessageType('LeaderNotificationRequest', (_message.Message,), {
  'DESCRIPTOR' : _LEADERNOTIFICATIONREQUEST,
  '__module__' : 'catalog_pb2'
  # @@protoc_insertion_point(class_scope:LeaderNotificationRequest)
  })
_sym_db.RegisterMessage(LeaderNotificationRequest)

LeaderNotificationReply = _reflection.GeneratedProtocolMessageType('LeaderNotificationReply', (_message.Message,), {
  'DESCRIPTOR' : _LEADERNOTIFICATIONREPLY,
  '__module__' : 'catalog_pb2'
  # @@protoc_insertion_point(class_scope:LeaderNotificationReply)
  })
_sym_db.RegisterMessage(LeaderNotificationReply)

_CATALOG = DESCRIPTOR.services_by_name['Catalog']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _QUERYREQUEST._serialized_start=17
  _QUERYREQUEST._serialized_end=44
  _UPDATEREQUEST._serialized_start=46
  _UPDATEREQUEST._serialized_end=87
  _QUERYREPLY._serialized_start=89
  _QUERYREPLY._serialized_end=134
  _UPDATEREPLY._serialized_start=136
  _UPDATEREPLY._serialized_end=165
  _LEADERNOTIFICATIONREQUEST._serialized_start=167
  _LEADERNOTIFICATIONREQUEST._serialized_end=217
  _LEADERNOTIFICATIONREPLY._serialized_start=219
  _LEADERNOTIFICATIONREPLY._serialized_end=260
  _CATALOG._serialized_start=263
  _CATALOG._serialized_end=431
# @@protoc_insertion_point(module_scope)

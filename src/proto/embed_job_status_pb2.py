# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: embed-job-status.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b"\n\x16\x65mbed-job-status.proto\x12\x08services\"\xc2\x01\n\x14NotificationResponse\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05orgId\x18\x02 \x01(\x05\x12\x13\n\x0b\x63onnectorId\x18\x03 \x01(\x05\x12\x0b\n\x03\x64ur\x18\x04 \x01(\x05\x12'\n\x06status\x18\x06 \x01(\x0e\x32\x17.services.FailureStatus\x12\x0e\n\x06reason\x18\x07 \x01(\t\x12%\n\x05state\x18\x05 \x01(\x0e\x32\x16.services.ArticleState\x12\r\n\x05jobId\x18\x08 \x01(\t*(\n\rFailureStatus\x12\x0b\n\x07SUCCESS\x10\x00\x12\n\n\x06\x46\x41ILED\x10\x01*\x83\x02\n\x0c\x41rticleState\x12\x0b\n\x07RUNNING\x10\x00\x12\x15\n\x11\x43ONNECTION_FAILED\x10\x01\x12\x0f\n\x0b\x44OWNLOADING\x10\x02\x12\x13\n\x0f\x44OWNLOAD_FAILED\x10\x03\x12\x11\n\rSTANDARDIZING\x10\x04\x12\x18\n\x14STANDARDIZING_FAILED\x10\x05\x12\r\n\tUPLOADING\x10\x06\x12\x11\n\rUPLOAD_FAILED\x10\x07\x12\x0f\n\x0bNORMALIZING\x10\x08\x12\x16\n\x12NORMALIZING_FAILED\x10\t\x12\r\n\tEMBEDDING\x10\n\x12\x14\n\x10\x45MBEDDING_FAILED\x10\x0b\x12\x0c\n\x08\x43OMPLETE\x10\x0c\x62\x06proto3"
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "embed_job_status_pb2", _globals
)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals["_FAILURESTATUS"]._serialized_start = 233
    _globals["_FAILURESTATUS"]._serialized_end = 273
    _globals["_ARTICLESTATE"]._serialized_start = 276
    _globals["_ARTICLESTATE"]._serialized_end = 535
    _globals["_NOTIFICATIONRESPONSE"]._serialized_start = 37
    _globals["_NOTIFICATIONRESPONSE"]._serialized_end = 231
# @@protoc_insertion_point(module_scope)

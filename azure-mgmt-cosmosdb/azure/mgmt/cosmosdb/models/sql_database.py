# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from .resource import Resource


class SqlDatabase(Resource):
    """An Azure Cosmos DB SQL database.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar id: The unique resource identifier of the database account.
    :vartype id: str
    :ivar name: The name of the database account.
    :vartype name: str
    :ivar type: The type of Azure resource.
    :vartype type: str
    :param location: The location of the resource group to which the resource
     belongs.
    :type location: str
    :param tags:
    :type tags: dict[str, str]
    :param sql_database_id: Required. Name of the Cosmos DB SQL database
    :type sql_database_id: str
    :param _rid: A system generated property. A unique identifier.
    :type _rid: str
    :param _ts: A system generated property that denotes the last updated
     timestamp of the resource.
    :type _ts: object
    :param _etag: A system generated property representing the resource etag
     required for optimistic concurrency control.
    :type _etag: str
    :param _colls: A system generated property that specified the addressable
     path of the collections resource.
    :type _colls: str
    :param _users: A system generated property that specifies the addressable
     path of the users resource.
    :type _users: str
    """

    _validation = {
        'id': {'readonly': True},
        'name': {'readonly': True},
        'type': {'readonly': True},
        'sql_database_id': {'required': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
        'location': {'key': 'location', 'type': 'str'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'sql_database_id': {'key': 'properties.id', 'type': 'str'},
        '_rid': {'key': 'properties._rid', 'type': 'str'},
        '_ts': {'key': 'properties._ts', 'type': 'object'},
        '_etag': {'key': 'properties._etag', 'type': 'str'},
        '_colls': {'key': 'properties._colls', 'type': 'str'},
        '_users': {'key': 'properties._users', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(SqlDatabase, self).__init__(**kwargs)
        self.sql_database_id = kwargs.get('sql_database_id', None)
        self._rid = kwargs.get('_rid', None)
        self._ts = kwargs.get('_ts', None)
        self._etag = kwargs.get('_etag', None)
        self._colls = kwargs.get('_colls', None)
        self._users = kwargs.get('_users', None)
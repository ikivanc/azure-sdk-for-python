# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum

from ._error import _ERROR_ATTRIBUTE_MISSING


class TableEntity(dict):
    """
    An entity object. Can be accessed as a dict or as an obj. The attributes of
    the entity will be created dynamically. For example, the following are both
    valid::
        TableEntity = TableEntity()
        TableEntity.a = 'b'
        TableEntity['x'] = 'y'

    """

    def _set_metadata(self):
        if 'Timestamp' in self.keys():
            self._metadata = {'etag': self.pop('etag'), "timestamp": self.pop('Timestamp')}  # pylint:disable=W0201
        else:
            self._metadata = {'etag': self.pop('etag')}  # pylint:disable=W0201

    def metadata(self, **kwargs):  # pylint: disable = W0613
        # type: (...) -> Dict[str,Any]
        """Resets metadata to be a part of the entity
        :return Dict of entity metadata
        :rtype Dict[str, Any]
        """
        return self._metadata

    def __getattr__(self, name):
        """
        :param name:name of entity entry
        :type name: str
        :return: TableEntity dictionary
        :rtype: dict[str,str]
        """
        try:
            return self[name]
        except KeyError:
            raise AttributeError(_ERROR_ATTRIBUTE_MISSING.format('TableEntity', name))

    __setattr__ = dict.__setitem__

    def __delattr__(self, name):
        """
        :param name:name of entity entry
        :type name: str
        """
        try:
            if name is not None:
                del self[name]
        except KeyError:
            raise AttributeError(_ERROR_ATTRIBUTE_MISSING.format('TableEntity', name))

    def __dir__(self):
        return dir({}) + list(self.keys())


class EntityProperty(object):
    """
    An entity property. Used to explicitly set :class:`~EdmType` when necessary.

    Values which require explicit typing are GUID, INT32, and BINARY. Other EdmTypes
    may be explicitly create as EntityProperty objects but need not be. For example,
    the below with both create STRING typed properties on the entity::
        entity = Entity()
        entity.a = 'b'
        entity.x = EntityProperty(EdmType.STRING, 'y')
    """

    def __init__(self,
                 type=None,  # type: Union[str,EdmType] # pylint:disable=W0622
                 value=None  # type: Any
                 ):
        """
        Represents an Azure Table. Returned by list_tables.

        :param Union[str, EdmType] type: The type of the property.
        :param Any value: The value of the property.
        """
        self.type = type
        self.value = value


class EdmType(str, Enum):
    """
    Used by :class:`~.EntityProperty` to represent the type of the entity property
    to be stored by the Table service.
    """

    BINARY = "Edm.Binary"
    ''' Represents byte data. This type will be inferred for Python bytes.. '''

    INT64 = "Edm.Int64"
    ''' Represents a number between -(2^31) and 2^31. This is the default type for Python numbers. '''

    GUID = "Edm.Guid"
    ''' Represents a GUID. This type will be inferred for uuid.UUID. '''

    DATETIME = "Edm.DateTime"
    ''' Represents a date. This type will be inferred for Python datetime objects. '''

    STRING = "Edm.String"
    ''' Represents a string. This type will be inferred for Python strings. '''

    INT32 = "Edm.Int32"
    ''' Represents a number between -(2^15) and 2^15. Must be specified or numbers will default to INT64. '''

    DOUBLE = "Edm.Double"
    ''' Represents a double. This type will be inferred for Python floating point numbers. '''

    BOOLEAN = "Edm.Boolean"
    ''' Represents a boolean. This type will be inferred for Python bools. '''

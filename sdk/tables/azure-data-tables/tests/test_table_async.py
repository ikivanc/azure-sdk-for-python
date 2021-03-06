import locale
import os
import sys
from datetime import datetime, timedelta

import pytest
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError, HttpResponseError
from _shared.asynctestcase import AsyncTableTestCase
from _shared.testcase import GlobalStorageAccountPreparer
from azure.data.tables import AccessPolicy, TableSasPermissions, ResourceTypes, AccountSasPermissions
from azure.data.tables.aio import TableServiceClient
from azure.data.tables._generated.models import QueryOptions
from azure.data.tables._table_shared_access_signature import generate_account_sas

TEST_TABLE_PREFIX = 'pytableasync'


# ------------------------------------------------------------------------------

class TableTestAsync(AsyncTableTestCase):
    # --Helpers-----------------------------------------------------------------
    def _get_table_reference(self, prefix=TEST_TABLE_PREFIX):
        table_name = self.get_resource_name(prefix)
        return table_name

    async def _create_table(self, ts, prefix=TEST_TABLE_PREFIX, table_list=None):
        table_name = self._get_table_reference(prefix)
        try:
            table = await ts.create_table(table_name)
            if table_list is not None:
                table_list.append(table)
        except ResourceExistsError:
            table = await ts.get_table_client(table_name)
        return table

    async def _delete_table(self, ts, table):
        if table is None:
            return
        try:
            await ts.delete_table(table.table_name)
        except ResourceNotFoundError:
            pass

    # --Test cases for tables --------------------------------------------------
    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_create_table(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()

        # Act
        created = await ts.create_table(table_name=table_name)

        # Assert
        assert created.table_name == table_name

        await ts.delete_table(table_name=table_name)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_create_table_fail_on_exist(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()

        # Act
        created = await ts.create_table(table_name=table_name)
        with self.assertRaises(ResourceExistsError):
            await ts.create_table(table_name=table_name)

        # Assert
        self.assertTrue(created)
        await ts.delete_table(table_name=table_name)

    @GlobalStorageAccountPreparer()
    async def test_create_table_invalid_name(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        invalid_table_name = "my_table"

        with pytest.raises(ValueError) as excinfo:
            await ts.create_table(table_name=invalid_table_name)

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
            excinfo)

    @GlobalStorageAccountPreparer()
    async def test_delete_table_invalid_name(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        invalid_table_name = "my_table"

        with pytest.raises(ValueError) as excinfo:
            await ts.create_table(invalid_table_name)

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
            excinfo)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_list_tables(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = await self._create_table(ts)

        # Act
        tables = []
        async for t in ts.list_tables():
            tables.append(t)

        # Assert
        self.assertIsNotNone(tables)
        self.assertGreaterEqual(len(tables), 1)
        self.assertIsNotNone(tables[0])

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_query_tables_with_filter(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = await self._create_table(ts)

        # Act
        name_filter = "TableName eq '{}'".format(table.table_name)
        tables = []
        async for t in ts.query_tables(filter=name_filter):
            tables.append(t)

        # Assert
        self.assertIsNotNone(tables)
        self.assertEqual(len(tables), 1)
        # self.assertEqual(tables[0].table_name, [table.table_name])
        # table.delete_table()
        await ts.delete_table(table.table_name)

    # @pytest.mark.skip("pending")
    # TODO: the small_page is getting 16, can't figure it out, skipping for now
    @GlobalStorageAccountPreparer()
    async def test_list_tables_with_num_results(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        prefix = 'listtable'
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_list = []
        for i in range(0, 4):
            await self._create_table(ts, prefix + str(i), table_list)

        # Act
        big_page = []
        async for t in ts.list_tables():
            big_page.append(t)

        small_page = []
        async for s in ts.list_tables(results_per_page=3).by_page():
            small_page.append(s)

        self.assertEqual(len(small_page), 2)
        self.assertGreaterEqual(len(big_page), 4)

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_list_tables_with_marker(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        prefix = 'listtable'
        table_names = []
        for i in range(0, 4):
            await self._create_table(ts, prefix + str(i), table_names)

        # table_names.sort()

        # Act
        generator1 = ts.list_tables(query_options=QueryOptions(top=2)).by_page()
        tables1 = []
        async for el in await generator1: #.__anext__():
            tables1.append(el)
        generator2 = ts.list_tables(query_options=QueryOptions(top=2)).by_page(
            continuation_token=generator1.continuation_token)
        tables2 = []
        async for el in await generator2:# .__anext__():
            tables2.append(el)

        # Assert
        self.assertEqual(len(tables1), 2)
        self.assertEqual(len(tables2), 2)
        self.assertNotEqual(tables1, tables2)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_delete_table_with_existing_table(self, resource_group, location, storage_account,
                                                    storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = await self._create_table(ts)

        # Act
        # deleted = table.delete_table()
        deleted = await ts.delete_table(table_name=table.table_name)

        # Assert
        self.assertIsNone(deleted)
        # existing = list(ts.query_tables("TableName eq '{}'".format(table.table_name)))
        # self.assertEqual(existing, [])

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_delete_table_with_non_existing_table_fail_not_exist(self, resource_group, location, storage_account,
                                                                       storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table_name = self._get_table_reference()

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await ts.delete_table(table_name)

        # Assert

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_unicode_create_table_unicode_name(self, resource_group, location, storage_account,
                                                     storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos URLs support unicode table names")
        ts = TableServiceClient(url, storage_account_key)
        table_name = u'啊齄丂狛狜'

        # Act
        # with self.assertRaises(HttpResponseError):

        with pytest.raises(ValueError) as excinfo:
            await ts.create_table(table_name=table_name)

        assert "Table names must be alphanumeric, cannot begin with a number, and must be between 3-63 characters long.""" in str(
            excinfo)

        # Assert

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_get_table_acl(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = await self._create_table(ts)
        try:
            # Act
            acl = await table.get_table_access_policy()
            # acl = table.get_table_access_policy()

            # Assert
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 0)
        finally:
            # self._delete_table(table)
            await ts.delete_table(table.table_name)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_set_table_acl_with_empty_signed_identifiers(self, resource_group, location, storage_account,
                                                               storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = await self._create_table(ts)
        try:
            # Act
            await table.set_table_access_policy(signed_identifiers={})

            # Assert
            acl = await table.get_table_access_policy()
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 0)
        finally:
            # self._delete_table(table)
            await ts.delete_table(table.table_name)

    @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_set_table_acl_with_empty_signed_identifier(self, resource_group, location, storage_account,
                                                              storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = await self._create_table(ts)
        try:
            # Act
            await table.set_table_access_policy(signed_identifiers={'empty': None})
            # Assert
            acl = await table.get_table_access_policy()
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 1)
            self.assertIsNotNone(acl['empty'])
            self.assertIsNone(acl['empty'].permission)
            self.assertIsNone(acl['empty'].expiry)
            self.assertIsNone(acl['empty'].start)
        finally:
            # self._delete_table(table)
            await ts.delete_table(table.table_name)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_set_table_acl_with_signed_identifiers(self, resource_group, location, storage_account,
                                                         storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = await self._create_table(ts)
        client = ts.get_table_client(table=table.table_name)

        # Act
        identifiers = dict()
        identifiers['testid'] = AccessPolicy(start=datetime.utcnow() - timedelta(minutes=5),
                                             expiry=datetime.utcnow() + timedelta(hours=1),
                                             permission=TableSasPermissions(read=True))
        try:
            await client.set_table_access_policy(signed_identifiers=identifiers)
            # Assert
            acl = await  client.get_table_access_policy()
            self.assertIsNotNone(acl)
            self.assertEqual(len(acl), 1)
            self.assertTrue('testid' in acl)
        finally:
            # self._delete_table(table)
            await ts.delete_table(table.table_name)

    # @pytest.mark.skip("pending")
    @GlobalStorageAccountPreparer()
    async def test_set_table_acl_too_many_ids(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos endpoint does not support this")
        ts = TableServiceClient(url, storage_account_key)
        table = await self._create_table(ts)
        try:
            # Act
            identifiers = dict()
            for i in range(0, 6):
                identifiers['id{}'.format(i)] = None

            # Assert
            with self.assertRaises(ValueError):
                await table.set_table_access_policy(table_name=table.table_name, signed_identifiers=identifiers)
        finally:
            await ts.delete_table(table.table_name)

    @pytest.mark.skip("pending")
    @pytest.mark.live_test_only
    @GlobalStorageAccountPreparer()
    async def test_account_sas(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only

        # Arrange
        url = self.account_url(storage_account, "table")
        if 'cosmos' in url:
            pytest.skip("Cosmos Tables does not yet support sas")
        tsc = TableServiceClient(url, storage_account_key)
        table = await self._create_table(tsc)
        try:
            entity = {
                'PartitionKey': 'test',
                'RowKey': 'test1',
                'text': 'hello',
            }
            await table.upsert_insert_merge_entity(table_entity_properties=entity)

            entity['RowKey'] = 'test2'
            await table.upsert_insert_merge_entity(table_entity_properties=entity)

            token = generate_account_sas(
                storage_account.name,
                storage_account_key,
                resource_types=ResourceTypes(container=True),
                permission=AccountSasPermissions(list=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            # Act
            service = TableServiceClient(
                self.account_url(storage_account, "table"),
                credential=token,
            )
            entities = []
            async for e in service.list_tables():
                entities.append(e)

            # Assert
            self.assertEqual(len(entities), 1)
            # self.assertEqual(entities[0].text, 'hello')
            # self.assertEqual(entities[1].text, 'hello')
        finally:
            await self._delete_table(table=table, ts=tsc)

    @pytest.mark.skip("msrest fails deserialization: https://github.com/Azure/msrest-for-python/issues/192")
    @GlobalStorageAccountPreparer()
    async def test_locale(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        ts = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)
        table = (self._get_table_reference())
        init_locale = locale.getlocale()
        if os.name == "nt":
            culture = "Spanish_Spain"
        elif os.name == 'posix':
            culture = 'es_ES.UTF-8'
        else:
            culture = 'es_ES.utf8'

        try:
            locale.setlocale(locale.LC_ALL, culture)
            e = None

            # Act
            await table.create_table()
            try:
                resp = ts.list_tables()
            except:
                e = sys.exc_info()[0]

            # Assert
            self.assertIsNone(e)
        finally:
            await ts.delete_table(table.table_name)
            locale.setlocale(locale.LC_ALL, init_locale[0] or 'en_US')

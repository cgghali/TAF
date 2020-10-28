'''
Created on 30-August-2020

@author: umang.agrawal
'''

from TestInput import TestInputSingleton
from cbas.cbas_base import CBASBaseTest
import random, json, copy, time
from threading import Thread
from cbas_utils.cbas_utils import Dataset
from BucketLib.BucketOperations import BucketHelper
from collections_helper.collections_spec_constants import \
    MetaConstants, MetaCrudParams

class CBASDataverseAndScopes(CBASBaseTest):

    def setUp(self):
        
        self.input = TestInputSingleton.input
        if "default_bucket" not in self.input.test_params:
            self.input.test_params.update({"default_bucket": False})
        super(CBASDataverseAndScopes, self).setUp()
        
        self.entity_name = Dataset.create_name_with_cardinality(
            name_cardinality=self.input.param('cardinality', 1), 
            max_length=self.input.param('name_length', 255), 
            fixed_length=self.input.param('fixed_length', False))
        
        if self.input.param('error', None):
            self.error_msg = self.input.param('error', None).format(self.entity_name)
        else:
            self.error_msg = None
        
        self.log.info("================================================================")
        self.log.info("SETUP has finished")
        self.log.info("================================================================")

    def tearDown(self):
        
        self.log.info("================================================================")
        self.log.info("TEARDOWN has started")
        self.log.info("================================================================")
        
        super(CBASDataverseAndScopes, self).tearDown()
        
        self.log.info("================================================================")
        self.log.info("Teardown has finished")
        self.log.info("================================================================")
    
    def test_create_dataverse(self):
        """
        This testcase verifies dataverse creation.
        Supported Test params -
        :testparam default_bucket boolean, whether to load default KV bucket or not
        :testparam cardinality int, accepted values are between 0-4
        :testparam name_length int, max length of dataverse name
        :testparam fixed_length boolean, if true dataverse name length equals name_length,
        else dataverse name length <= name_length 
        :testparam error str, error msg to validate.
        :testparam validate_error boolean
        :testparam error_code int,
        """
        if not self.cbas_util.create_dataverse_on_cbas(dataverse_name=Dataset.format_name(self.entity_name),
                                                       validate_error_msg=self.input.param('validate_error', 
                                                                                           False),
                                                       expected_error=self.error_msg,
                                                       expected_error_code=self.input.param('error_code', 
                                                                                            None)):
            self.fail("Creation of Dataverse {0} failed".format(self.entity_name))
        
        self.log.info("Performing validation in Metadata.Dataverse")
        if not self.input.param('validate_error', False) and \
        not self.cbas_util.validate_dataverse_in_metadata(self.entity_name):
            self.fail("Validation in Metadata.Dataverse failed for {0}".format(self.entity_name))
    
    def test_create_analytics_scope(self):
        """
        This testcase verifies analytics scope creation.
        Supported Test params -
        :testparam default_bucket boolean, whether to load default KV bucket or not
        :testparam cardinality int, accepted values are between 0-4
        :testparam name_length int, max length of analytics scope name
        :testparam fixed_length boolean, if true analytics scope name length equals name_length,
        else analytics scope name length <= name_length 
        :testparam error str, error msg to validate.
        :testparam validate_error boolean
        :testparam error_code int,
        """
        if not self.cbas_util.create_analytics_scope(scope_name=Dataset.format_name(self.entity_name),
                                                     validate_error_msg=self.input.param('validate_error', 
                                                                                         False),
                                                     expected_error=self.error_msg,
                                                     expected_error_code=self.input.param('error_code', 
                                                                                          None)):
            self.fail("Creation of Analytics Scope {0} failed".format(self.entity_name))
        
        self.log.info("Performing validation in Metadata.Dataverse")
        if not self.input.param('validate_error', False) and \
        not self.cbas_util.validate_dataverse_in_metadata(self.entity_name):
            self.fail("Validation in Metadata.Dataverse failed for {0}".format(self.entity_name))
    
    def test_drop_dataverse(self):
        """
        This testcase verifies dropping of dataverse.
        Supported Test params -
        :testparam default_bucket boolean, whether to load default KV bucket or not
        :testparam cardinality int, accepted values are between 0-4
        :testparam name_length int, max length of dataverse name
        :testparam fixed_length boolean, if true dataverse name length equals name_length,
        else dataverse name length <= name_length 
        :testparam error str, error msg to validate.
        :testparam validate_error boolean
        :testparam error_code int,
        """
        if 0 < self.input.param('cardinality', 1) < 3:
            self.cbas_util.create_dataverse_on_cbas(dataverse_name=Dataset.format_name(self.entity_name))
        if not self.cbas_util.drop_dataverse_on_cbas(dataverse_name=Dataset.format_name(self.entity_name),
                                                     validate_error_msg=self.input.param('validate_error', 
                                                                                         False),
                                                     expected_error=self.error_msg,
                                                     expected_error_code=self.input.param('error_code', 
                                                                                          None)):
            self.fail("Dropping of Dataverse {0} failed".format(self.entity_name))
        
        self.log.info("Performing validation in Metadata.Dataverse")
        if 0 < self.input.param('cardinality', 1) < 3 and \
        self.cbas_util.validate_dataverse_in_metadata(self.entity_name):
            self.fail("Validation in Metadata.Dataverse failed for {0}".format(self.entity_name))
    
    
    def test_drop_analytics_scope(self):
        """
        This testcase verifies dropping of analytics scope.
        Supported Test params -
        :testparam default_bucket boolean, whether to load default KV bucket or not
        :testparam cardinality int, accepted values are between 0-4
        :testparam name_length int, max length of analytics scope name
        :testparam fixed_length boolean, if true analytics scope name length equals name_length,
        else analytics scope name length <= name_length 
        :testparam error str, error msg to validate.
        :testparam validate_error boolean
        :testparam error_code int,
        """
        if 0 < self.input.param('cardinality', 1) < 3:
            self.cbas_util.create_analytics_scope(scope_name=Dataset.format_name(self.entity_name))
        if not self.cbas_util.drop_analytics_scope(scope_name=Dataset.format_name(self.entity_name),
                                                   validate_error_msg=self.input.param('validate_error', 
                                                                                       False),
                                                   expected_error=self.error_msg,
                                                   expected_error_code=self.input.param('error_code', 
                                                                                        None)):
            self.fail("Dropping of scope {0} failed".format(self.entity_name))
        
        self.log.info("Performing validation in Metadata.Dataverse")
        if 0 < self.input.param('cardinality', 1) < 3 and \
        self.cbas_util.validate_dataverse_in_metadata(self.entity_name):
            self.fail("Validation in Metadata.Dataverse failed for {0}".format(self.entity_name))
    
    def test_use_statement(self):
        if 0 < int(self.input.param('cardinality', 1)) < 3:
            if not self.cbas_util.create_dataverse_on_cbas(
                dataverse_name=Dataset.format_name(self.entity_name)):
                self.fail("Creation of Dataverse {0} failed".format(self.entity_name))
        
        if self.input.param('split_name', False):
            self.entity_name = (self.entity_name).split(".")[0]
        cmd = "Use {0}".format(Dataset.format_name(self.entity_name))
        self.log.debug("Executing cmd - \n{0}\n".format(cmd))
        status, metrics, errors, results, _ = \
            self.execute_statement_on_cbas_util(cmd)
        if not status:
            if not self.cbas_util.validate_error_in_response(
                status, errors, 
                expected_error=self.input.param('error', None).format(self.entity_name)):
                self.fail("Validating error message failed. Error message was different from expected error")
            
        

class CBASDatasetsAndCollections(CBASBaseTest):

    def setUp(self):
        
        self.input = TestInputSingleton.input
        if "bucket_spec" not in self.input.test_params:
            self.input.test_params.update({"bucket_spec": "single_bucket.default"})
        super(CBASDatasetsAndCollections, self).setUp()
        self.log.info("================================================================")
        self.log.info("SETUP has finished")
        self.log.info("================================================================")

    def tearDown(self):
        
        self.log.info("================================================================")
        self.log.info("TEARDOWN has started")
        self.log.info("================================================================")
        
        super(CBASDatasetsAndCollections, self).tearDown()
        
        self.log.info("================================================================")
        self.log.info("Teardown has finished")
        self.log.info("================================================================")
        
    def test_create_dataset(self):
        """
        This testcase verifies dataset creation.
        Supported Test params -
        :testparam bucket_spec str, KV bucket spec to be used to load buckets, 
        scopes and collections.
        :testparam cardinality int, accepted values are between 1-3
        :testparam bucket_cardinality int, accepted values are between 1-3
        :testparam invalid_kv_collection, boolean
        :testparam invalid_kv_scope, boolean
        :testparam invalid_dataverse, boolean
        :testparam name_length int, max length of dataverse name
        :testparam no_dataset_name, boolean
        :testparam dataset_creation_method str, method to be used to create dataset 
        on a bucket/collection, accepted values are cbas_dataset, cbas_collection,
        enable_cbas_from_kv.
        :testparam error str, error msg to validate.
        :testparam validate_error boolean
        """
        self.log.info("Test started")
        dataset_obj = Dataset(
            bucket_util=self.bucket_util,
            cbas_util=self.cbas_util,
            consider_default_KV_scope=True, 
            consider_default_KV_collection=True,
            dataset_name_cardinality=int(self.input.param('cardinality', 1)),
            bucket_cardinality=int(self.input.param('bucket_cardinality', 3)),
            random_dataset_name=True
            )
        
        # Negative scenario 
        if self.input.param('error', None):
            error_msg = self.input.param('error', None)
        else:
            error_msg = None
        
        if self.input.param('invalid_kv_collection', False):
            dataset_obj.kv_collection_obj.name = "invalid"
            error_msg = error_msg.format(
                dataset_obj.get_fully_quantified_kv_entity_name(
                    dataset_obj.bucket_cardinality))
        elif self.input.param('invalid_kv_scope', False):
            dataset_obj.kv_scope_obj.name = "invalid"
            error_msg = error_msg.format(
                dataset_obj.get_fully_quantified_kv_entity_name(2))
        elif self.input.param('invalid_dataverse', False):
            dataset_obj.dataverse  = "invalid"
            error_msg = error_msg.format("invalid")
        elif self.input.param('name_length', 0):
            dataset_obj.dataverse, dataset_obj.name = dataset_obj.split_dataverse_dataset_name(
                dataset_obj.create_name_with_cardinality(
                    1, int(self.input.param('name_length', 0)), True))
        elif self.input.param('no_dataset_name', False):
            dataset_obj.name = ''
        # Negative scenario ends
        
        dataset_obj.setup_dataset(
            dataset_creation_method=self.input.param('dataset_creation_method', "cbas_dataset"),
            validate_metadata=True, validate_doc_count=True, create_dataverse=True, 
            validate_error=self.input.param('validate_error', False), 
            error_msg=error_msg, username=None, password=None, timeout=120, analytics_timeout=120)
        self.log.info("Test finished")
        
    def test_drop_dataset(self):
        """
        This testcase verifies dataset deletion.
        Supported Test params -
        :testparam bucket_spec str, KV bucket spec to be used to load buckets, 
        scopes and collections.
        :testparam cardinality int, accepted values are between 1-3
        :testparam bucket_cardinality int, accepted values are between 1-3
        :testparam dataset_drop_method str, method to be used to create dataset 
        on a bucket/collection, accepted values are cbas_dataset, cbas_collection,
        enable_cbas_from_kv.
        :testparam invalid_dataset, boolean
        :testparam error str, error msg to validate.
        :testparam validate_error boolean
        """
        self.log.info("Test started")
        
        dataset_obj = Dataset(
            bucket_util=self.bucket_util,
            cbas_util=self.cbas_util,
            consider_default_KV_scope=True, 
            consider_default_KV_collection=True,
            dataset_name_cardinality=int(self.input.param('cardinality', 1)),
            bucket_cardinality=int(self.input.param('bucket_cardinality', 3)),
            random_dataset_name=True
            )
        
        if not dataset_obj.setup_dataset(
            dataset_creation_method=self.input.param('dataset_creation_method', "cbas_dataset")):
            self.fail("Error while creating dataset.")
        
        # Negative scenario   
        if self.input.param('invalid_dataset', False):
            dataset_obj.name = "invalid"
        
        if self.input.param('error', None):
            error_msg = self.input.param('error', None).format("invalid")
        else:
            error_msg = None
        # Negative scenario ends
        
        if not dataset_obj.teardown_dataset(
            dataset_drop_method = self.input.param('dataset_drop_method', "cbas_dataset"),
            validate_error=self.input.param('validate_error', False), 
            error_msg=error_msg):
            self.fail("Error while dropping dataset")
        
        self.log.info("Test finished")
        
    def test_create_analytics_collection(self):
        """Only dataset_creation_method parameter will change for these testcase"""
        self.test_create_dataset()
    
    def test_drop_analytics_collection(self):
        """Only dataset_creation_method and dataset_drop_method parameter will change for these testcase"""
        self.test_drop_dataset()
    
    def test_create_multiple_datasets(self):
        """
        This testcase verifies multiple dataset creation.
        Supported Test params -
        :testparam bucket_spec str, KV bucket spec to be used to load buckets, 
        scopes and collections.
        :testparam no_of_datasets int
        :testparam dataset_creation_method str, method to be used to create dataset 
        on a bucket/collection, accepted values are cbas_dataset, cbas_collection,
        enable_cbas_from_kv.
        """
        self.log.info("Test started")
        results = list()
        for i in range(int(self.input.param('no_of_datasets', 1))):
            dataset_obj = Dataset(
                bucket_util=self.bucket_util,
                cbas_util=self.cbas_util,
                consider_default_KV_scope=True, 
                consider_default_KV_collection=True,
                dataset_name_cardinality=random.randint(1,3),
                bucket_cardinality=random.choice([1,3]),
                random_dataset_name=True)
            results.append(dataset_obj.setup_dataset(
                dataset_creation_method=self.input.param('dataset_creation_method', "cbas_dataset")))
        
        if all(results):
            self.fail("All datasets were not created.")
        self.log.info("Test finished")
        
    def test_enabling_analytics_collection_from_KV(self):
        """
        This testcase verifies enabling of analytics from KV.
        Supported Test params -
        :testparam bucket_spec str, KV bucket spec to be used to load buckets, 
        scopes and collections.
        :testparam dataset_cardinality int, accepted values are 0 or 3
        :testparam bucket_cardinality int, accepted values are between 1-3
        :testparam consider_default_KV_scope, boolean
        :testparam consider_default_KV_collection boolean
        :testparam create_dataverse, boolean
        :testparam invalid_kv_collection, boolean
        :testparam invalid_kv_scope, boolean
        :testparam invalid_kv_bucket, boolean
        :testparam precreate_dataset str, accepted values None, Named and Default
        :testparam synonym_name str, accepted values None, Collection and Bucket
        :testparam compress_dataset boolean
        :testparam dataset_creation_method str, method to be used to create dataset 
        on a bucket/collection, accepted values are cbas_dataset, cbas_collection,
        enable_cbas_from_kv.
        :testparam verify_synonym boolean        
        :testparam error str, error msg to validate.
        :testparam validate_error boolean
        """
        self.log.info("Test started")
        
        dataset_cardinality = int(self.input.param('dataset_cardinality', 0))
        if not dataset_cardinality:
            dataset_cardinality = int(self.input.param('bucket_cardinality', 1))
            
        dataset_obj = Dataset(
            bucket_util=self.bucket_util,
            cbas_util=self.cbas_util,
            consider_default_KV_scope=self.input.param('consider_default_KV_scope', True), 
            consider_default_KV_collection=self.input.param('consider_default_KV_collection', True),
            dataset_name_cardinality=dataset_cardinality,
            bucket_cardinality=int(self.input.param('bucket_cardinality', 1)),
            random_dataset_name=False
            )
        
        if self.input.param('create_dataverse', False) and \
            not self.cbas_util.create_dataverse_on_cbas(
                dataverse_name=dataset_obj.dataverse):
            self.fail("Failed to create dataverse {0}".format(dataset_obj.dataverse))
        
        # Negative scenarios
        if self.input.param('error', None):
            error_msg = self.input.param('error', None)
        else:
            error_msg = None
        
        if self.input.param('invalid_kv_collection', False):
            dataset_obj.kv_collection_obj.name = "invalid"
            error_msg = error_msg.format(
                dataset_obj.get_fully_quantified_kv_entity_name(
                    dataset_obj.bucket_cardinality).replace('`',''))
        elif self.input.param('invalid_kv_scope', False):
            dataset_obj.kv_scope_obj.name = "invalid"
        elif self.input.param('invalid_kv_bucket', False):
            dataset_obj.kv_bucket_obj = "invalid"
            error_msg = error_msg.format("invalid")
        
        # Creating dataverse before enabling analytics from KV
        precreate_dataset = self.input.param('precreate_dataset', None)
        if precreate_dataset:
            original_dataverse = dataset_obj.dataverse
            original_dataset = dataset_obj.name
            
            if precreate_dataset == "Default":
                dataset_obj.dataverse = "Default"
                dataset_obj.name = dataset_obj.kv_bucket_obj.name
            
            if not dataset_obj.setup_dataset(create_dataverse=True):
                self.fail("Error while creating dataset {0}".format(dataset_obj.full_dataset_name))
            
            dataset_obj.dataverse = original_dataverse
            dataset_obj.name = original_dataset
            
            error_msg = error_msg.format(dataset_obj.name, dataset_obj.dataverse)
        
        # Creating synonym before enabling analytics from KV
        if self.input.param('synonym_name', None) == "Bucket":
            synonym_name = dataset_obj.get_fully_quantified_kv_entity_name(1)
            error_msg = error_msg.format(synonym_name.replace('`',''))
        elif self.input.param('synonym_name', None) == "Collection":
            synonym_name = dataset_obj.get_fully_quantified_kv_entity_name(3)
            error_msg = error_msg.format(dataset_obj.split_dataverse_dataset_name(
                dataset_obj.full_dataset_name,True))
        else:
            synonym_name = None
        
        if synonym_name and not self.cbas_util.create_analytics_synonym(
            synonym_name=synonym_name,
            object_name=dataset_obj.full_dataset_name):
            self.fail("Error while creating synonym {0} on dataset {1}".format(
                synonym_name, dataset_obj.full_dataset_name))
        # Negative scenario ends
        
        if not dataset_obj.setup_dataset(
            dataset_creation_method=self.input.param('dataset_creation_method', "enable_cbas_from_kv"),
            validate_metadata=True, validate_doc_count=True, create_dataverse=False, 
            validate_error=self.input.param('validate_error', False),
            compress_dataset=self.input.param('compress_dataset', False),
            error_msg=error_msg, username=None, password=None, timeout=120, analytics_timeout=120):
            self.fail("Failed to enable analytics on {0}".format(dataset_obj.full_dataset_name))
        
        self.log.info("Validating created dataverse entry in Metadata")
        if not self.input.param('create_dataverse', False) and \
            not self.cbas_util.validate_dataverse_in_metadata(
                dataset_obj.dataverse):
            self.fail("Dataverse {0} was not created".format(dataset_obj.dataverse))
        
        self.log.info("Validating created Synonym entry in Metadata")
        synonym_validation = self.cbas_util.validate_synonym_in_metadata(
            synonym=dataset_obj.kv_bucket_obj.name,
            synonym_dataverse="Default",
            dataset_dataverse=dataset_obj.dataverse, dataset=dataset_obj.name)
         
        if not (self.input.param('verify_synonym', False) and synonym_validation):
            self.fail("Synonym {0} is not created under Dataverse {1}".format(
                dataset_obj.kv_bucket_obj.name, dataset_obj.dataverse))
        
        self.log.info("Test finished")
    
    def test_disabling_analytics_collection_from_KV(self):
        """
        This testcase verifies disabling of analytics from KV.
        Supported Test params -
        :testparam bucket_spec str, KV bucket spec to be used to load buckets, 
        scopes and collections.
        :testparam dataset_cardinality int, accepted values are 0 or 3
        :testparam bucket_cardinality int, accepted values are between 1-3
        :testparam consider_default_KV_scope, boolean
        :testparam consider_default_KV_collection boolean
        :testparam create_dataverse, boolean
        :testparam invalid_kv_collection, boolean
        :testparam create_dataset boolean
        :testparam create_synonym boolean
        :testparam dataverse_deleted boolean,
        :testparam synonym_deleted boolean
        :testparam dataset_creation_method str, method to be used to create dataset 
        on a bucket/collection, accepted values are cbas_dataset, cbas_collection,
        enable_cbas_from_kv.
        :testparam error str, error msg to validate.
        :testparam validate_error boolean
        """
        self.log.info("Test started")
        dataset_cardinality = int(self.input.param('dataset_cardinality', 0))
        if not dataset_cardinality:
            dataset_cardinality = int(self.input.param('bucket_cardinality', 1))
            
        dataset_obj = Dataset(
            bucket_util=self.bucket_util,
            cbas_util=self.cbas_util,
            consider_default_KV_scope=self.input.param('consider_default_KV_scope', True), 
            consider_default_KV_collection=self.input.param('consider_default_KV_collection', True),
            dataset_name_cardinality=dataset_cardinality,
            bucket_cardinality=int(self.input.param('bucket_cardinality', 1)),
            random_dataset_name=False
            )
        
        self.log.info("Enabling analytics from KV")
        if not dataset_obj.setup_dataset(
            dataset_creation_method=self.input.param('dataset_creation_method', "enable_cbas_from_kv"),
            validate_metadata=True, validate_doc_count=True, 
            create_dataverse=self.input.param('create_dataverse', False)):
            self.fail("Failed to enable analytics on {0}".format(dataset_obj.full_dataset_name))
        
        # Negative scenarios
        if self.input.param('error', None):
            error_msg = self.input.param('error', None)
        else:
            error_msg = None
            
        if self.input.param('invalid_kv_collection', False):
            dataset_obj.kv_collection_obj.name = "invalid"
        # Negative scenario ends
        
        if self.input.param('create_dataset', False):
            new_dataset_name = dataset_obj.create_name_with_cardinality(1)
            new_dataset_full_name = dataset_obj.format_name(dataset_obj.dataverse, new_dataset_name)
            if not self.cbas_util.create_dataset_on_bucket(
                dataset_obj.get_fully_quantified_kv_entity_name(self.bucket_cardinality), 
                new_dataset_full_name):
                self.fail("Error creating dataset {0}".format(new_dataset_full_name))
        
        if self.input.param('create_synonym', False):
            new_synonym_name = dataset_obj.create_name_with_cardinality(1)
            if not self.cbas_util.create_analytics_synonym(
                synonym_name=new_synonym_name, 
                object_name=dataset_obj.full_dataset_name,
                synonym_dataverse="Default"):
                self.fail("Error creating synonym {0}".format(new_synonym_name))
        
        self.log.info("Disabling analytics from KV")
        if not dataset_obj.teardown_dataset(
            dataset_drop_method = "enable_cbas_from_kv",
            validate_error=self.input.param('validate_error', False), 
            error_msg=error_msg, validate_metadata=True):
            self.fail("Error while disabling analytics on KV collection")
        
        self.log.info("Validating whether the dataverse is deleted or not")
        if self.input.param('dataverse_deleted', False) and self.cbas_util.validate_dataverse_in_metadata(
            dataset_obj.dataverse):
            self.fail("Dataverse {0} is still present even after disabling analytics from KV".format(
                dataset_obj.dataverse))
        elif not self.input.param('dataverse_deleted', False) and not self.cbas_util.validate_dataverse_in_metadata(
            dataset_obj.dataverse):
            self.fail("Dataverse {0} got deleted after disabling analytics from KV".format(
                dataset_obj.dataverse))
        
        self.log.info("Validating whether the synonym is deleted or not")
        if self.input.param('synonym_deleted', False) and self.cbas_util.validate_synonym_in_metadata(
            synonym=dataset_obj.kv_bucket_obj.name,
            synonym_dataverse="Default",
            dataset_dataverse=dataset_obj.dataverse, dataset=dataset_obj.name):
            self.fail("Synonym {0} is still present even after disabling analytics from KV".format(
                dataset_obj.kv_bucket_obj.name))
        
        if self.input.param('create_dataset', False):
            if not self.cbas_util.validate_dataset_in_metadata(
                new_dataset_name, dataset_obj.dataverse, BucketName=dataset_obj.kv_bucket_obj.name):
                self.fail("Explicitly created dataset got deleted after disabling analytics from KV")
        
        if self.input.param('create_synonym', False):
            if not self.cbas_util.validate_synonym_in_metadata(
                synonym=new_synonym_name, synonym_dataverse="Default", 
                dataset_dataverse=dataset_obj.dataverse, dataset=dataset_obj.name):
                self.fail("Explicitly created synonym got deleted after disabling analytics from KV")
        
        self.log.info("Test finished")
        
    def test_create_analytics_synonym(self):
        """
        This testcase verifies creation of analytics synonym.
        Supported Test params -
        :testparam bucket_spec str, KV bucket spec to be used to load buckets, 
        scopes and collections.
        :testparam cardinality int, accepted values are 1 or 3
        :testparam bucket_cardinality int, accepted values are between 1 or 3
        :testparam consider_default_KV_scope, boolean
        :testparam consider_default_KV_collection boolean
        :testparam dataset_creation_method str, method to be used to create dataset 
        on a bucket/collection, accepted values are cbas_dataset, cbas_collection,
        enable_cbas_from_kv.
        :testparam no_of_synonym int,
        :testparam dangling_synonym boolean,
        :testparam invalid_dataverse boolean,
        :testparam new_synonym_name boolean,
        :testparam synonym_dataverse str, accepted values dataset, new, Default 
        :testparam error str, error msg to validate.
        :testparam validate_error boolean
        :testparam if_not_exists boolean
        :testparam synonym_on_synonym boolean
        :testparam different_syn_on_syn_dv boolean,
        :testparam validate_error1 boolean
        :testparam action_on_dataset str, accepted values None, drop, recreate
        :testparam action_on_synonym str, accepted values None, drop, recreate
        :testparam revalidate boolean,
        :testparam validate_query_error boolean
        :testparam query_error str,
        """
        self.log.info("Test started")
        dataset_obj = Dataset(
            bucket_util=self.bucket_util,
            cbas_util=self.cbas_util,
            consider_default_KV_scope=self.input.param('consider_default_KV_scope', True), 
            consider_default_KV_collection=self.input.param('consider_default_KV_collection', True),
            dataset_name_cardinality=int(self.input.param('cardinality', 1)),
            bucket_cardinality=int(self.input.param('bucket_cardinality', 1)),
            random_dataset_name=True
            )
        
        self.log.info("Creating dataverse and dataset")
        dataset_obj.setup_dataset(
            dataset_creation_method=self.input.param('dataset_creation_method', 
                                                     "cbas_dataset"))
        
        for i in range(int(self.input.param('no_of_synonym', 1))):

            # Negative scenario 
            if self.input.param('dangling_synonym', False):
                dataset_obj.name = "invalid"
            elif self.input.param('invalid_dataverse', False):
                dataset_obj.dataverse = "invalid"
            # Negative scenario ends
            
            
            self.log.info("Creating synonym")
            if not dataset_obj.setup_synonym(
                new_synonym_name=self.input.param('new_synonym_name', True),
                synonym_dataverse=self.input.param('synonym_dataverse', "Default"),
                validate_error_msg=self.input.param('validate_error', False),
                expected_error=self.input.param('error', ''),
                validate_metadata=True,
                validate_doc_count=True,
                if_not_exists=self.input.param('if_not_exists', False)):
                self.fail("Error while creating synonym")
            
            original_synonym_name = dataset_obj.synonym_name
            original_synonym_dataverse = dataset_obj.synonym_dataverse
            
            if self.input.param("synonym_on_synonym", False):
                self.log.info("Creating synonym on synonym")
                if not self.input.param("different_syn_on_syn_dv", False):
                    synonym_dataverse = "new"
                else:
                    synonym_dataverse = self.input.param('synonym_dataverse', "Default")
                if not dataset_obj.setup_synonym(
                    new_synonym_name=self.input.param('new_synonym_name', True),
                    synonym_dataverse=synonym_dataverse,
                    validate_error_msg=self.input.param('validate_error1', False),
                    expected_error=self.input.param('error', '').format(dataset_obj.synonym_name),
                    validate_metadata=True,
                    validate_doc_count=True):
                    self.fail("Error while creating synonym on synonym")
            
            if self.input.param("action_on_dataset", None):
                self.log.info("Dropping Dataset")
                if not self.cbas_util.drop_dataset(
                    dataset_obj.format_name(
                        dataset_obj.full_dataset_name)):
                    self.fail("Error while dropping dataset")
                if self.input.param("action_on_dataset", None) == "recreate":
                    self.log.info("Recreating dataset")
                    dataset_obj.setup_dataset(
                        dataset_creation_method="cbas_dataset",
                        create_dataverse=False)
            
            if self.input.param("action_on_synonym", None):
                self.log.info("Dropping Synonym")
                if not self.cbas_util.drop_analytics_synonym(
                    synonym_name=dataset_obj.format_name(original_synonym_name), 
                    synonym_dataverse=dataset_obj.format_name(original_synonym_dataverse)):
                    self.fail("Error while dropping synonym")
                if self.input.param("action_on_synonym", None) == "recreate":
                    self.log.info("Recreating synonym")
                    if not self.cbas_util.create_analytics_synonym(
                        synonym_name=dataset_obj.format_name(original_synonym_name), 
                        object_name=dataset_obj.format_name(dataset_obj.full_dataset_name),
                        synonym_dataverse=dataset_obj.format_name(original_synonym_dataverse)):
                        self.fail("Error while creating synonym {0} on dataset {1}".format(
                            original_synonym_name, dataset_obj.full_dataset_name))
            
            if self.input.param("revalidate", False):
                self.log.info("Validating created Synonym entry in Metadata")
                if not self.cbas_util.validate_synonym_in_metadata(
                    synonym=dataset_obj.synonym_name,
                    synonym_dataverse=dataset_obj.synonym_dataverse,
                    dataset_dataverse=dataset_obj.dataverse, 
                    dataset=dataset_obj.name):
                    self.fail("Synonym metadata entry not created")
                    
                self.log.info(
                    "Validating whether querying synonym return expected result")
                if not self.cbas_util.validate_synonym_doc_count(
                    full_synonym_name=dataset_obj.format_name(
                        dataset_obj.synonym_dataverse,dataset_obj.synonym_name), 
                    full_dataset_name=dataset_obj.format_name(
                        dataset_obj.full_dataset_name),
                    validate_error_msg=self.input.param('validate_query_error', False), 
                    expected_error=self.input.param('query_error', 
                                                    '').format(dataset_obj.synonym_name)):
                    self.fail(
                        "Doc count in Synonym does not match with dataset on which it was created.")
        self.log.info("Test finished")
    
    def test_dataset_and_synonym_name_resolution_precedence(self):
        """
        This testcase verifies which is resolved first dataset or synonym.
        Supported Test params -
        :testparam bucket_spec str, KV bucket spec to be used to load buckets, 
        scopes and collections.
        :testparam cardinality int, accepted values are 1 or 3
        :testparam bucket_cardinality int, accepted values are between 1 or 3
        :testparam consider_default_KV_scope, boolean
        :testparam consider_default_KV_collection boolean
        :testparam dataset_creation_method str, method to be used to create dataset 
        on a bucket/collection, accepted values are cbas_dataset, cbas_collection,
        enable_cbas_from_kv.
        :testparam dangling_synonym boolean,
        :testparam synonym_on_synonym boolean
        :testparam different_dataverse boolean,
        """
        self.log.info("Test started")
        
        dataset_obj_1 = Dataset(
            bucket_util=self.bucket_util,
            cbas_util=self.cbas_util,
            consider_default_KV_scope=self.input.param('consider_default_KV_scope', True), 
            consider_default_KV_collection=self.input.param('consider_default_KV_collection', True),
            dataset_name_cardinality=int(self.input.param('cardinality', 1)),
            bucket_cardinality=int(self.input.param('bucket_cardinality', 1)),
            random_dataset_name=True
            )
        
        self.log.info("Creating dataverse and dataset")
        dataset_obj_1.setup_dataset(
            dataset_creation_method=self.input.param('dataset_creation_method', 
                                                     "cbas_dataset"))
        
        dataset_obj_2 = Dataset(
            bucket_util=self.bucket_util,
            cbas_util=self.cbas_util,
            consider_default_KV_scope=self.input.param('consider_default_KV_scope', True), 
            consider_default_KV_collection=self.input.param('consider_default_KV_collection', True),
            dataset_name_cardinality=int(self.input.param('cardinality', 1)),
            bucket_cardinality=int(self.input.param('bucket_cardinality', 1)),
            random_dataset_name=True,
            exclude_collection=[dataset_obj_1.kv_collection_obj.name])
        if not self.input.param('dangling_synonym', False):
            self.log.info("Creating dataverse and dataset")
            dataset_obj_2.setup_dataset(
                dataset_creation_method=self.input.param('dataset_creation_method', 
                                                         "cbas_dataset"))
        
        self.log.info("Creating synonym")
        if not self.cbas_util.create_analytics_synonym(
            synonym_name=Dataset.format_name(dataset_obj_1.name), 
            object_name=Dataset.format_name(dataset_obj_2.full_dataset_name),
            synonym_dataverse=Dataset.format_name(dataset_obj_1.dataverse)):
            self.fail("Error while creating synonym {0} on dataset {1}".format(
                dataset_obj_1.name, dataset_obj_2.full_dataset_name))
        
        full_synonym_name = Dataset.format_name(
            dataset_obj_1.dataverse,dataset_obj_1.name)
        
        if self.input.param("synonym_on_synonym", False):
            self.log.info("Creating synonym on synonym")
            synonym_name=Dataset.create_name_with_cardinality(1)
            if self.input.param("different_dataverse", False):
                synonym_dataverse = Dataset.create_name_with_cardinality(2)
                if not self.cbas_util.create_dataverse_on_cbas(synonym_dataverse):
                    self.fail("Failed to create dataverse")
            else:
                synonym_dataverse = Dataset.format_name(dataset_obj_1.dataverse)
            
            if not self.cbas_util.create_analytics_synonym(
                synonym_name=synonym_name, 
                object_name=full_synonym_name,
                synonym_dataverse=synonym_dataverse):
                self.fail("Error while creating synonym on synonym")
            
            full_synonym_name = Dataset.format_name(synonym_dataverse, synonym_name)
            
        
        if not self.cbas_util.validate_synonym_doc_count(
            full_synonym_name=full_synonym_name, 
            full_dataset_name=Dataset.format_name(
                dataset_obj_1.full_dataset_name)):
            self.fail("Querying synonym with same name as dataset, \
            is returning docs from dataset on which synonym is created\
             instead of the dataset with the same name.")
        
        self.log.info("Test finished")    
    
    def test_drop_analytics_synonym(self):
        """
        This testcase verifies dropping of analytics synonym.
        Supported Test params -
        :testparam bucket_spec str, KV bucket spec to be used to load buckets, 
        scopes and collections.
        :testparam invalid_synonym boolean,
        :testparam validate_query_error boolean
        :testparam query_error str,
        """
        self.log.info("Test started")
        dataset_obj = Dataset(
            bucket_util=self.bucket_util, cbas_util=self.cbas_util,
            consider_default_KV_scope=True, 
            consider_default_KV_collection=True,
            dataset_name_cardinality=3, bucket_cardinality=3,
            random_dataset_name=True)
        
        self.log.info("Creating dataverse and dataset")
        dataset_obj.setup_dataset(dataset_creation_method= "cbas_dataset")
        
        synonym_name = Dataset.create_name_with_cardinality(1)
        self.log.info("Creating synonym")
        if not self.cbas_util.create_analytics_synonym(
            synonym_name=Dataset.format_name(synonym_name), 
            object_name=Dataset.format_name(dataset_obj.full_dataset_name),
            synonym_dataverse=Dataset.format_name(dataset_obj.dataverse)):
            self.fail("Error while creating synonym {0} on dataset {1}".format(
                synonym_name, dataset_obj.full_dataset_name))
        
        if self.input.param('invalid_synonym', False):
            synonym_name = "invalid"
        
        self.log.info("Dropping synonym")
        if not self.cbas_util.drop_analytics_synonym(
            synonym_name=synonym_name, 
            synonym_dataverse=Dataset.format_name(dataset_obj.dataverse), 
            validate_error_msg=self.input.param('validate_error', False), 
            expected_error=self.input.param('error', '')):
            self.fail("Error while dropping Synonym")
        
        self.log.info("Validate Dataset item count after dropping synonym")
        if not self.input.param('validate_error', False) and not\
         self.cbas_util.validate_cbas_dataset_items_count(
             dataset_obj.get_fully_quantified_dataset_name(),
             Dataset.get_item_count_in_collection(
                 self.bucket_util,dataset_obj.kv_bucket_obj, 
                 dataset_obj.kv_scope_obj.name, 
                 dataset_obj.kv_collection_obj.name)):
            self.fail("Doc count mismatch")
        
        self.log.info("Test finished")
    
    def bucket_flush_and_validate(self, bucket_obj):
        """
        - Flush the entire bucket
        - Validate scope/collections are intact post flush

        :param bucket_obj: Target bucket object to flush
        :return: None
        """
        self.log.info("Flushing bucket: %s" % bucket_obj.name)
        self.bucket_util.flush_bucket(self.cluster.master, bucket_obj)

        self.log.info("Validating scope/collections mapping and doc_count")
        self.bucket_util._wait_for_stats_all_buckets()
        self.bucket_util.validate_docs_per_collections_all_buckets()

        # Print bucket stats
        self.bucket_util.print_bucket_stats()
    
    def load_initial_data(self, doc_loading_spec=None, async_load=False,
                          validate_task=True):
        """
        Reload same data from initial_load spec template to validate
        post bucket flush collection stability
        :return: None
        """
        self.log.info("Loading same docs back into collections")
        
        if not doc_loading_spec:
            doc_loading_spec = \
                self.bucket_util.get_crud_template_from_package("initial_load")

        doc_loading_task = \
            self.bucket_util.run_scenario_from_spec(
                self.task,
                self.cluster,
                self.bucket_util.buckets,
                doc_loading_spec,
                mutation_num=0,
                batch_size=self.batch_size,
                async_load=async_load,
                validate_task=validate_task)
        
        if doc_loading_task.result is False:
            self.fail("Post flush doc_creates failed")

        # Print bucket stats
        self.bucket_util.print_bucket_stats()

        self.log.info("Validating scope/collections mapping and doc_count")
        self.bucket_util._wait_for_stats_all_buckets()
        self.bucket_util.validate_docs_per_collections_all_buckets()
    
    def test_datasets_created_on_KV_collections_after_flushing_KV_bucket(self):
        """
        This testcase verifies the effects of KV flushing on datasets.
        Supported Test params -
        :testparam bucket_spec str, KV bucket spec to be used to load buckets, 
        scopes and collections.
        :testparam create_ds_on_different_bucket boolean, it set to true, create a 
        dataset on collection belonging to a bucket that is not being flushed.
        """
        self.log.info("Test started")
        
        dataset_objs = list()
        bucket = random.choice(self.bucket_util.buckets)
        bucket_helper = BucketHelper(self.cluster.master)
        
        # Create dataset on all KV collections in the bucket.
        status, content = bucket_helper.list_collections(bucket.name)
        if not status:
            self.fail("Failed to fetch all the collections in bucket {0}".format(bucket.name))
        json_parsed = json.loads(content)
        
        for scope in json_parsed["scopes"]:
            for collection in scope["collections"]:
                dataset_obj = Dataset(
                    bucket_util=self.bucket_util,
                    cbas_util=self.cbas_util,
                    dataset_name_cardinality=3,
                    bucket_cardinality=3,
                    set_kv_entity=False)
                scope_obj = self.bucket_util.get_scope_obj(bucket, scope["name"])
                collection_obj = self.bucket_util.get_collection_obj(scope_obj, collection["name"])
                dataset_obj.set_kv_entity(
                    kv_bucket_obj=bucket, 
                    kv_scope_obj=scope_obj, 
                    kv_collection_obj=collection_obj)
                if not dataset_obj.setup_dataset():
                    self.fail("Error while creating dataset {0} on {1}".format(
                        dataset_obj.get_fully_quantified_dataset_name(),
                        dataset_obj.get_fully_quantified_kv_entity_name(3)))
                dataset_objs.append(dataset_obj)
        
        if self.input.param('create_ds_on_different_bucket', False):
            new_dataset_obj = Dataset( 
                bucket_util=self.bucket_util,
                cbas_util=self.cbas_util,
                dataset_name_cardinality=3,
                bucket_cardinality=3,
                exclude_bucket=[bucket.name])
            if not new_dataset_obj.setup_dataset():
                self.fail("Error while creating dataset {0} on {1}".format(
                    new_dataset_obj.get_fully_quantified_dataset_name(),
                    new_dataset_obj.get_fully_quantified_kv_entity_name(3)))
            
        self.bucket_flush_and_validate(bucket)
        
        for dataset_obj in dataset_objs:
            self.log.info("Validating item count")
            if not self.cbas_util.validate_cbas_dataset_items_count(
                dataset_obj.get_fully_quantified_dataset_name(),
                Dataset.get_item_count_in_collection(
                    self.bucket_util,dataset_obj.kv_bucket_obj, 
                    dataset_obj.kv_scope_obj.name, 
                    dataset_obj.kv_collection_obj.name)):
                self.fail("Data is still present in dataset, even when KV collection\
                on which the dataset was created was flushed.")
        
        if self.input.param('create_ds_on_different_bucket', False):
            self.log.info("Validating item count in dataset created on a\
             different bucket than the bucket being flushed")
            if not self.cbas_util.validate_cbas_dataset_items_count(
                new_dataset_obj.get_fully_quantified_dataset_name(),
                Dataset.get_item_count_in_collection(
                    self.bucket_util,new_dataset_obj.kv_bucket_obj, 
                    new_dataset_obj.kv_scope_obj.name, 
                    new_dataset_obj.kv_collection_obj.name)):
                self.fail("Data is not present in dataset, \
                after a different bucket was flushed")
        
        self.log.info("Test finished")
    
    def test_dataset_for_data_addition_post_KV_flushing(self):
        """
        This testcase verifies the effects of adding new data post 
        KV flushing on datasets.
        Supported Test params -
        :testparam bucket_spec str, KV bucket spec to be used to load buckets, 
        scopes and collections.
        :testparam no_of_flushes int, no of times the bucket needs to be flushed.
        :testparam reload_data boolean, to reload data in KV bucket 
        """
        self.log.info("Test started")
        
        dataset_obj = Dataset(
            bucket_util=self.bucket_util,
            cbas_util=self.cbas_util,
            dataset_name_cardinality=3,
            bucket_cardinality=3)
        
        if not dataset_obj.setup_dataset():
            self.fail("Error while creating dataset {0} on {1}".format(
                dataset_obj.get_fully_quantified_dataset_name(),
                dataset_obj.get_fully_quantified_kv_entity_name(3)))
        
        for i in range(0,int(self.input.param('no_of_flushes', 1))):
            self.bucket_flush_and_validate(dataset_obj.kv_bucket_obj)
            self.sleep(10, "Waiting for flush to complete")
            self.log.info("Validating item count in dataset before adding new data in KV")
            if not self.cbas_util.validate_cbas_dataset_items_count(
                dataset_obj.get_fully_quantified_dataset_name(),
                Dataset.get_item_count_in_collection(
                    self.bucket_util,dataset_obj.kv_bucket_obj, 
                    dataset_obj.kv_scope_obj.name, 
                    dataset_obj.kv_collection_obj.name)):
                self.fail("Data is still present in dataset, even when KV collection\
                on which the dataset was created was flushed.")
            if self.input.param('reload_data', True):
                self.load_initial_data()
                self.log.info("Validating item count in dataset after adding new data in KV")
                if not self.cbas_util.validate_cbas_dataset_items_count(
                    dataset_obj.get_fully_quantified_dataset_name(),
                    Dataset.get_item_count_in_collection(
                        self.bucket_util,dataset_obj.kv_bucket_obj, 
                        dataset_obj.kv_scope_obj.name, 
                        dataset_obj.kv_collection_obj.name)):
                    self.fail("Newly added data in KV collection did not get ingested in\
                    dataset after flushing")
        
        self.log.info("Test finished")
    
    def test_dataset_for_adding_new_docs_while_flushing(self):
        self.log.info("Test started")
        
        dataset_obj = Dataset(
            bucket_util=self.bucket_util,
            cbas_util=self.cbas_util,
            dataset_name_cardinality=3,
            bucket_cardinality=3)
        
        if not dataset_obj.setup_dataset():
            self.fail("Error while creating dataset {0} on {1}".format(
                dataset_obj.get_fully_quantified_dataset_name(),
                dataset_obj.get_fully_quantified_kv_entity_name(3)))
        
        doc_loading_spec = \
                self.bucket_util.get_crud_template_from_package("initial_load")
        doc_loading_spec["doc_crud"][MetaCrudParams.DocCrud.CREATE_PERCENTAGE_PER_COLLECTION] = 50
        
        threads = list()
        thread1 = Thread(target=self.bucket_flush_and_validate,
                         name="flush_thread",
                         args=(dataset_obj.kv_bucket_obj,))
        thread1.start()
        threads.append(thread1)
        self.sleep(5, "Waiting for KV flush to start")

        thread2 = Thread(target=self.load_initial_data,
                         name="data_load_thread",
                         args=(doc_loading_spec,False,False,))
        thread2.start()
        threads.append(thread2)

        for thread in threads:
            thread.join()
        
        self.log.info("Validating item count in dataset")
        if not self.cbas_util.validate_cbas_dataset_items_count(
            dataset_obj.get_fully_quantified_dataset_name(),
            Dataset.get_item_count_in_collection(
                self.bucket_util,dataset_obj.kv_bucket_obj, 
                dataset_obj.kv_scope_obj.name, 
                dataset_obj.kv_collection_obj.name)):
            self.fail("Number of docs in dataset does not match docs in KV collection")
        
        self.log.info("Test finished")
    
    def test_dataset_when_KV_flushing_during_data_mutation(self):
        self.log.info("Test started")
        
        dataset_obj = Dataset(
            bucket_util=self.bucket_util,
            cbas_util=self.cbas_util,
            dataset_name_cardinality=3,
            bucket_cardinality=3)
        
        if not dataset_obj.setup_dataset():
            self.fail("Error while creating dataset {0} on {1}".format(
                dataset_obj.get_fully_quantified_dataset_name(),
                dataset_obj.get_fully_quantified_kv_entity_name(3)))
        
        doc_loading_spec = \
                self.bucket_util.get_crud_template_from_package("initial_load")
        doc_loading_spec["doc_crud"][MetaCrudParams.DocCrud.CREATE_PERCENTAGE_PER_COLLECTION] = 50
        
        self.load_initial_data(doc_loading_spec, True)
        self.bucket_flush_and_validate(dataset_obj.kv_bucket_obj)
                
        self.log.info("Validating item count in dataset")
        if not self.cbas_util.validate_cbas_dataset_items_count(
            dataset_obj.get_fully_quantified_dataset_name(),
            Dataset.get_item_count_in_collection(
                self.bucket_util,dataset_obj.kv_bucket_obj, 
                dataset_obj.kv_scope_obj.name, 
                dataset_obj.kv_collection_obj.name)):
            self.fail("Number of docs in dataset does not match docs in KV collection")
        
        self.log.info("Test finished")
        
    
    def test_docs_deleted_in_dataset_once_MaxTTL_reached(self):
        pass
    
    def test_dataset_after_deleting_and_recreating_KV_collection(self):
        self.log.info("Test started")
        self.log.info("Test finished")
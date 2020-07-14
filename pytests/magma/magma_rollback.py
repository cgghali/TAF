'''
Created on Dec 12, 2019

@author: riteshagarwal
'''

import copy
import time

from cb_tools.cbstats import Cbstats
from cb_tools.cbepctl import Cbepctl
from couchbase_helper.documentgenerator import doc_generator
from magma_base import MagmaBaseTest
from memcached.helper.data_helper import MemcachedClientHelper
from remote.remote_util import RemoteMachineShellConnection
from sdk_exceptions import SDKException


retry_exceptions = [SDKException.TimeoutException,
                    SDKException.AmbiguousTimeoutException,
                    SDKException.RequestCanceledException,
                    SDKException.UnambiguousTimeoutException]


class MagmaRollbackTests(MagmaBaseTest):

    def setUp(self):
        super(MagmaRollbackTests, self).setUp()

        self.create_start = 0
        self.create_end = self.num_items

        self.generate_docs(doc_ops="create")

        self.init_loading = self.input.param("init_loading", True)
        if self.init_loading:
            self.result_task = self._load_all_buckets(
                self.cluster, self.gen_create,
                "create", 0,
                batch_size=self.batch_size,
                dgm_batch=self.dgm_batch)

            if self.active_resident_threshold != 100:
                for task in self.result_task.keys():
                    self.num_items = task.doc_index

            self.log.info("Verifying num_items counts after doc_ops")
            self.bucket_util._wait_for_stats_all_buckets()
            self.bucket_util.verify_stats_all_buckets(self.num_items)

        self.cluster_util.print_cluster_stats()
        self.bucket_util.print_bucket_stats()
        self.graceful = self.input.param("graceful", False)

    def tearDown(self):
        super(MagmaRollbackTests, self).tearDown()

    def test_magma_rollback_n_times(self):
        items = self.num_items
        mem_only_items = self.input.param("rollback_items", 100000)
        if self.nodes_init < 2 or self.num_replicas < 1:
            self.fail("Not enough nodes/replicas in the cluster/bucket \
            to test rollback")
        self.num_rollbacks = self.input.param("num_rollbacks", 10)
        shell = RemoteMachineShellConnection(self.cluster_util.cluster.master)
        cbstats = Cbstats(shell)
        self.target_vbucket = cbstats.vbucket_list(self.bucket_util.buckets[0].
                                                   name)
        start = self.num_items
        self.gen_read = copy.deepcopy(self.gen_create)
        for _ in xrange(1, self.num_rollbacks+1):
            # Stopping persistence on NodeA
            mem_client = MemcachedClientHelper.direct_client(
                self.cluster_util.cluster.master, self.bucket_util.buckets[0])
            mem_client.stop_persistence()

            self.gen_create = doc_generator(
                self.key, start, mem_only_items,
                doc_size=self.doc_size, doc_type=self.doc_type,
                target_vbucket=self.target_vbucket,
                vbuckets=self.cluster_util.vbuckets,
                randomize_doc_size=self.randomize_doc_size,
                randomize_value=self.randomize_value)

            self.loadgen_docs(_sync=True,
                              retry_exceptions=retry_exceptions)
            start = self.gen_create.key_counter

            ep_queue_size_map = {self.cluster.nodes_in_cluster[0]:
                                 mem_only_items}
            vb_replica_queue_size_map = {self.cluster.nodes_in_cluster[0]: 0}

            for node in self.cluster.nodes_in_cluster[1:]:
                ep_queue_size_map.update({node: 0})
                vb_replica_queue_size_map.update({node: 0})

            for bucket in self.bucket_util.buckets:
                self.bucket_util._wait_for_stat(bucket, ep_queue_size_map)
                self.bucket_util._wait_for_stat(
                    bucket,
                    vb_replica_queue_size_map,
                    stat_name="vb_replica_queue_size")

            # Kill memcached on NodeA to trigger rollback on other Nodes
            # replica vBuckets
            for bucket in self.bucket_util.buckets:
                self.log.debug(cbstats.failover_stats(bucket.name))
            shell.kill_memcached()

            self.assertTrue(self.bucket_util._wait_warmup_completed(
                [self.cluster_util.cluster.master],
                self.bucket_util.buckets[0],
                wait_time=self.wait_timeout * 10))
            self.sleep(10, "Not Required, but waiting for 10s after warm up")

            self.bucket_util.verify_stats_all_buckets(items, timeout=300)
            for bucket in self.bucket_util.buckets:
                self.log.debug(cbstats.failover_stats(bucket.name))

        data_validation = self.task.async_validate_docs(
                self.cluster, self.bucket_util.buckets[0],
                self.gen_read, "create", 0,
                batch_size=self.batch_size,
                process_concurrency=self.process_concurrency,
                pause_secs=5, timeout_secs=self.sdk_timeout)
        self.task.jython_task_manager.get_task_result(data_validation)

        shell.disconnect()

    def test_magma_rollback_n_times_with_del_op(self):
        self.log.info("test_magma_rollback_n_times_with_del_op starts")

        if self.nodes_init < 2 or self.num_replicas < 1:
            self.fail("Not enough nodes/replicas in the cluster/bucket \
            to test rollback")

        items = self.num_items
        shell = RemoteMachineShellConnection(self.cluster_util.cluster.master)
        cbstats = Cbstats(shell)
        self.target_vbucket = cbstats.vbucket_list(self.bucket_util.buckets[0].name)
        self.gen_create = self.gen_docs_basic_for_target_vbucket(0, self.num_items,
                                                                 self.target_vbucket)

        self.doc_ops = "create"
        self.loadgen_docs(_sync=True, retry_exceptions=retry_exceptions)
        self.bucket_util._wait_for_stats_all_buckets()
        self.bucket_util.verify_stats_all_buckets(items)

        self.cluster_util.print_cluster_stats()
        self.bucket_util.print_bucket_stats()

        mem_only_items = self.input.param("rollback_items", 100000)
        self.num_rollbacks = self.input.param("num_rollbacks", 10)

        self.doc_ops = "delete"
        start = 0
        for i in range(1, self.num_rollbacks+1):
            # Stopping persistence on NodeA
            self.log.info("Iteration=={}".format(i))

            mem_client = MemcachedClientHelper.direct_client(
                self.cluster_util.cluster.master, self.bucket_util.buckets[0])
            mem_client.stop_persistence()

            self.gen_delete = self.gen_docs_basic_for_target_vbucket(start, mem_only_items,
                                                                     self.target_vbucket)

            self.loadgen_docs(_sync=True,
                              retry_exceptions=retry_exceptions)
            # start = self.gen_delete.key_counter

            ep_queue_size_map = {self.cluster.nodes_in_cluster[0]:
                                 mem_only_items}
            vb_replica_queue_size_map = {self.cluster.nodes_in_cluster[0]: 0}

            for node in self.cluster.nodes_in_cluster[1:]:
                ep_queue_size_map.update({node: 0})
                vb_replica_queue_size_map.update({node: 0})

            for bucket in self.bucket_util.buckets:
                self.bucket_util._wait_for_stat(bucket, ep_queue_size_map)
                self.bucket_util._wait_for_stat(
                    bucket,
                    vb_replica_queue_size_map,
                    stat_name="vb_replica_queue_size")

            self.validate_data("delete", self.gen_delete)

            # Kill memcached on NodeA to trigger rollback on other Nodes
            # replica vBuckets
            for bucket in self.bucket_util.buckets:
                self.log.debug(cbstats.failover_stats(bucket.name))
            shell.kill_memcached()

            self.assertTrue(self.bucket_util._wait_warmup_completed(
                [self.cluster_util.cluster.master],
                self.bucket_util.buckets[0],
                wait_time=self.wait_timeout * 10))
            self.sleep(10, "Not Required, but waiting for 10s after warm up")

            self.bucket_util.verify_stats_all_buckets(items, timeout=300)
            for bucket in self.bucket_util.buckets:
                self.log.debug(cbstats.failover_stats(bucket.name))

        shell.disconnect()
        self.log.info("test_magma_rollback_n_times_with_del_op ends")

    def test_magma_rollback_to_snapshot(self):
        items = self.num_items
        mem_only_items = self.input.param("rollback_items", 10000)

        if self.nodes_init < 2 or self.num_replicas < 1:
            self.fail("Not enough nodes/replicas in the cluster/bucket \
            to test rollback")

        self.duration = self.input.param("duration", 2)
        self.num_rollbacks = self.input.param("num_rollbacks", 10)

        self.log.info("State files after initial creates %s"
                      % self.get_state_files(self.buckets[0]))

        '''
        To ensure at least one snapshot should get created before rollback
        starts, we need to sleep for 60 seconds as per magma design which
        create state file every 60s
        '''

        self.sleep(60, "Ensures creation of at least one snapshot")
        self.log.info("State files after 60 second of sleep %s"
                      % self.get_state_files(self.buckets[0]))

        shell = RemoteMachineShellConnection(self.cluster_util.cluster.master)
        cbstats = Cbstats(shell)
        self.target_vbucket = cbstats.vbucket_list(self.bucket_util.buckets[0].
                                                   name)

        self.gen_read = copy.deepcopy(self.gen_create)
        start = self.num_items
        while_itr = 0

        for i in range(1, self.num_rollbacks+1):
            self.log.info("Roll back Iteration {}".format(i))

            mem_item_count = 0
            self.log.debug("State files before stopping persistence %s"
                           % self.get_state_files(self.buckets[0]))

            # Stopping persistence on NodeA
            mem_client = MemcachedClientHelper.direct_client(
                self.cluster_util.cluster.master, self.bucket_util.buckets[0])
            mem_client.stop_persistence()

            time_end = time.time() + 60 * self.duration
            while time.time() < time_end:
                while_itr += 1
                time_start = time.time()
                mem_item_count += mem_only_items
                self.log.info("")
                self.gen_create = self.gen_docs_basic_for_target_vbucket(start,
                                                                         mem_only_items,
                                                                         self.target_vbucket)
                self.loadgen_docs(_sync=True,
                                  retry_exceptions=retry_exceptions)

                start = self.gen_create.key_counter

                if time.time() < time_start + 60:
                    self.sleep(time_start + 60 - time.time(),
                               "Sleep to ensure creation of state files for roll back, itr = {}"
                               .format(while_itr))
                self.log.info("Iteration== {} , state files== {}".
                              format(while_itr,
                                     self.get_state_files(self.buckets[0])))

            ep_queue_size_map = {self.cluster.nodes_in_cluster[0]:
                                 mem_item_count}
            vb_replica_queue_size_map = {self.cluster.nodes_in_cluster[0]: 0}

            for node in self.cluster.nodes_in_cluster[1:]:
                ep_queue_size_map.update({node: 0})
                vb_replica_queue_size_map.update({node: 0})

            for bucket in self.bucket_util.buckets:
                self.bucket_util._wait_for_stat(bucket, ep_queue_size_map)
                self.bucket_util._wait_for_stat(
                    bucket,
                    vb_replica_queue_size_map,
                    stat_name="vb_replica_queue_size")

            # Kill memcached on NodeA to trigger rollback on other Nodes
            # replica vBuckets
            for bucket in self.bucket_util.buckets:
                self.log.debug(cbstats.failover_stats(bucket.name))

            shell.kill_memcached()

            self.assertTrue(self.bucket_util._wait_warmup_completed(
                [self.cluster_util.cluster.master],
                self.bucket_util.buckets[0],
                wait_time=self.wait_timeout * 10))

            self.log.info("State files after killing memcached {}".
                          format(self.get_state_files(self.buckets[0])))

            self.sleep(10, "Not Required, but waiting for 10s after warm up")
            self.bucket_util.verify_stats_all_buckets(items, timeout=300)
            for bucket in self.bucket_util.buckets:
                self.log.debug(cbstats.failover_stats(bucket.name))

        data_validation = self.task.async_validate_docs(
                self.cluster, self.bucket_util.buckets[0],
                self.gen_read, "create", 0,
                batch_size=self.batch_size,
                process_concurrency=self.process_concurrency,
                pause_secs=5, timeout_secs=self.sdk_timeout)
        self.task.jython_task_manager.get_task_result(data_validation)

        shell.disconnect()

    def test_magma_rollback_to_0(self):
        items = self.num_items
        mem_only_items = self.input.param("rollback_items", 10000)
        if self.nodes_init < 2 or self.num_replicas < 1:
            self.fail("Not enough nodes/replicas in the cluster/bucket\
                      to test rollback")

        self.num_rollbacks = self.input.param("num_rollbacks", 10)
        shell = RemoteMachineShellConnection(self.cluster_util.cluster.master)
        self.target_vbucket = Cbstats(shell).vbucket_list(self.bucket_util.
                                                          buckets[0].name)
        start = self.num_items

        # Stopping persistence on NodeA
        mem_client = MemcachedClientHelper.direct_client(
            self.input.servers[0], self.bucket_util.buckets[0])
        mem_client.stop_persistence()

        for i in xrange(1, self.num_rollbacks+1):
            self.gen_create = doc_generator(
                self.key, start, mem_only_items,
                doc_size=self.doc_size, doc_type=self.doc_type,
                target_vbucket=self.target_vbucket,
                vbuckets=self.cluster_util.vbuckets,
                randomize_doc_size=self.randomize_doc_size,
                randomize_value=self.randomize_value)

            self.loadgen_docs(_sync=True,
                              retry_exceptions=retry_exceptions)

            start = self.gen_create.key_counter
            stat_map = {self.cluster.nodes_in_cluster[0]: mem_only_items*i}
            for node in self.cluster.nodes_in_cluster[1:]:
                stat_map.update({node: 0})

            for bucket in self.bucket_util.buckets:
                self.bucket_util._wait_for_stat(bucket, stat_map)
            self.sleep(60)

        shell.kill_memcached()
        self.assertTrue(self.bucket_util._wait_warmup_completed(
            [self.cluster_util.cluster.master],
            self.bucket_util.buckets[0],
            wait_time=self.wait_timeout * 10))
        self.bucket_util.verify_stats_all_buckets(items)
        shell.disconnect()
        self.log.info("test_magma_rollback_n_times_during_del_op starts")

    def test_magma_rollback_to_new_snapshot(self):
        items = self.num_items
        mem_only_items = self.input.param("rollback_items", 10000)

        if self.nodes_init < 2 or self.num_replicas < 1:
            self.fail("Not enough nodes/replicas in the cluster/bucket \
            to test rollback")

        self.duration = self.input.param("duration", 2)
        self.num_rollbacks = self.input.param("num_rollbacks", 10)

        self.log.info("State files after initial creates %s"
                      % self.get_state_files(self.buckets[0]))

        '''
        To ensure at least one snapshot should get created before rollback
        starts, we need to sleep for 60 seconds as per magma design which
        create state file every 60s
        '''

        self.sleep(60, "Ensures creation of at least one snapshot")
        self.log.info("State files after 60 second of sleep %s"
                      % self.get_state_files(self.buckets[0]))

        shell = RemoteMachineShellConnection(self.cluster_util.cluster.master)
        cbstats = Cbstats(shell)
        self.target_vbucket = cbstats.vbucket_list(self.bucket_util.buckets[0].
                                                   name)

        while_itr = 0
        for i in range(1, self.num_rollbacks+1):
            start = items
            self.log.info("Roll back Iteration == {}".format(i))

            mem_item_count = 0
            self.log.debug("Iteration == {}, State files before stopping persistence == {}".
                           format(i, self.get_state_files(self.buckets[0])))

            # Stopping persistence on NodeA
            self.log.debug("Iteration == {}, stopping persistence".format(i))
            Cbepctl(shell).persistence(self.bucket_util.buckets[0].name, "stop")

            time_end = time.time() + 60 * self.duration
            while time.time() < time_end:
                while_itr += 1
                time_start = time.time()
                mem_item_count += mem_only_items

                self.gen_create = self.gen_docs_basic_for_target_vbucket(start,
                                                                         mem_only_items,
                                                                         self.target_vbucket)
                self.loadgen_docs(_sync=True,
                                  retry_exceptions=retry_exceptions)

                start = self.gen_create.key_counter

                if time.time() < time_start + 60:
                    self.sleep(time_start + 60 - time.time(),
                               "while_itr == {}, Sleep to ensure creation of state files for roll back,"
                               .format(while_itr))
                self.log.info("while_itr == {}, state files== {}".
                              format(while_itr,
                                     self.get_state_files(self.buckets[0])))

            ep_queue_size_map = {self.cluster.nodes_in_cluster[0]:
                                 mem_item_count}
            vb_replica_queue_size_map = {self.cluster.nodes_in_cluster[0]: 0}

            for node in self.cluster.nodes_in_cluster[1:]:
                ep_queue_size_map.update({node: 0})
                vb_replica_queue_size_map.update({node: 0})

            for bucket in self.bucket_util.buckets:
                self.bucket_util._wait_for_stat(bucket, ep_queue_size_map)
                self.bucket_util._wait_for_stat(
                    bucket,
                    vb_replica_queue_size_map,
                    stat_name="vb_replica_queue_size")

            # Kill memcached on NodeA to trigger rollback on other Nodes
            # replica vBuckets
            for bucket in self.bucket_util.buckets:
                self.log.debug(cbstats.failover_stats(bucket.name))

            shell.kill_memcached()

            self.assertTrue(self.bucket_util._wait_warmup_completed(
                [self.cluster_util.cluster.master],
                self.bucket_util.buckets[0],
                wait_time=self.wait_timeout * 10))

            self.log.info("Iteration == {},State files after killing memcached {}".
                          format(i, self.get_state_files(self.buckets[0])))

            self.sleep(10, "Not Required, but waiting for 10s after warm up")
            self.bucket_util.verify_stats_all_buckets(items, timeout=300)
            for bucket in self.bucket_util.buckets:
                self.log.debug(cbstats.failover_stats(bucket.name))

            self.log.debug("Iteration=={}, Re-Starting persistence".format(i))
            Cbepctl(shell).persistence(self.bucket_util.buckets[0].name, "start")

            self.create_start = items
            self.create_end = items + items // 3
            self.generate_docs(doc_ops="create")

            time_end = time.time() + 60
            while time.time() < time_end:
                time_start = time.time()
                _ = self.loadgen_docs(self.retry_exceptions,
                                      self.ignore_exceptions,
                                      _sync=True)
                self.bucket_util._wait_for_stats_all_buckets()
                if time.time() < time_start + 60:
                    self.sleep(time_start + 60 - time.time(), "After new creates, sleeping , itr={}".format(i))

            items = items + items // 3
            self.log.debug("Iteration == {}, Total num_items {}".format(i, items))

        shell.disconnect()


class MagmaSpaceAmplification(MagmaBaseTest):

    def test_space_amplification(self):
        self.num_updates = self.input.param("num_updates", 50)
        self.assertTrue(self.rest.update_autofailover_settings(False, 600),
                        "AutoFailover disabling failed")
        self.doc_ops = "update"

        initial_data_size = 0
        for bucket in self.bucket_util.buckets:
            initial_data_size += self.get_disk_usage(bucket)[0]

        metadata_size = 200
        exact_size = self.num_items*(self.doc_size + metadata_size)\
            * (1 + self.num_replicas)
        max_size = initial_data_size * 2.5
        for i in xrange(1, self.num_updates+1):
            self.log.info("Iteration: {}, updating {} items".
                          format(i, self.num_items))

            self.gen_update = doc_generator(
                self.key, 0, self.num_items,
                doc_size=self.doc_size, doc_type=self.doc_type,
                target_vbucket=self.target_vbucket,
                vbuckets=self.cluster_util.vbuckets,
                randomize_doc_size=self.randomize_doc_size,
                randomize_value=self.randomize_value)
            self.loadgen_docs(_sync=True,
                              retry_exceptions=retry_exceptions)

            self.bucket_util._wait_for_stats_all_buckets(timeout=self.wait_timeout*20)
            self.bucket_util.print_bucket_stats()

            disk_size = self.get_disk_usage(bucket)[0]
            self.assertTrue(
                disk_size >= initial_data_size and disk_size <= max_size,
                "Exact Data Size {} \n\
                Actual Size {} \n\
                Max Expected Size {}".format(exact_size, disk_size, max_size)
                )
            self.bucket_util.verify_stats_all_buckets(self.num_items,
                                                      timeout=self.wait_timeout*20)
        data_validation = self.task.async_validate_docs(
            self.cluster, self.bucket_util.buckets[0],
            self.gen_update, "update", 0, batch_size=self.batch_size,
            process_concurrency=self.process_concurrency)
        self.task.jython_task_manager.get_task_result(data_validation)
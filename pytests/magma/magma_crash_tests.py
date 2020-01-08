'''
Created on Dec 12, 2019

@author: riteshagarwal
'''

from magma_base import MagmaBaseTest
from remote.remote_util import RemoteMachineShellConnection
from couchbase_helper.documentgenerator import doc_generator
from cb_tools.cbepctl import Cbepctl
from memcached.helper.data_helper import MemcachedClientHelper
from cb_tools.cbstats import Cbstats


class MagmaCrashTests(MagmaBaseTest):
    def setUp(self):
        super(MagmaCrashTests, self).setUp()

    def tearDown(self):
        super(MagmaCrashTests, self).tearDown()

    def kill_magma_check_wal_file_size(self):
        nIter = 200
        while nIter > 0:
            shell = RemoteMachineShellConnection(self.cluster_util.cluster.master)
            shell.kill_memcached()
#             self.bucket_util._wait_warmup_completed()
            self.sleep(10, "sleep of 5s so that memcached can restart")

    def test_crash_magma_n_times(self):
        self.num_crashes = self.input.param("num_crashes", 10)
        items = self.num_items
        shell = RemoteMachineShellConnection(self.cluster_util.cluster.master)
        for i in xrange(1, self.num_crashes+1):
            shell.kill_memcached()
            self.assertTrue(self.bucket_util._wait_warmup_completed(
                [self.cluster_util.cluster.master],
                self.bucket_util.buckets[0],
                wait_time=self.wait_timeout * 10))
            self.gen_create = doc_generator(self.key,
                                            items*i,
                                            items*(i+1),
                                            doc_size=self.doc_size,
                                            doc_type=self.doc_type,
                                            target_vbucket=self.target_vbucket,
                                            vbuckets=self.vbuckets)
            self.loadgen_docs(_sync=True)
            self.bucket_util._wait_for_stats_all_buckets()
            data_validation = self.task.async_validate_docs(
                self.cluster, self.bucket_util.buckets[0],
                self.gen_create, "create", 0, batch_size=10)
            self.task.jython_task_manager.get_task_result(data_validation)
            self.bucket_util.verify_stats_all_buckets(items*(i+1))

    def test_magma_rollback_n_times(self):
        items = self.num_items
        mem_only_items = self.input.param("rollback_items", 100000)
        if self.nodes_init < 2 or self.num_replicas<1:
            self.fail("Not enough nodes/replicas in the cluster/bucket to test rollback")
        self.num_rollbacks = self.input.param("num_rollbacks", 10)
        shell = RemoteMachineShellConnection(self.cluster_util.cluster.master)
        self.target_vbucket = Cbstats(shell).vbucket_list(self.bucket_util.buckets[0].name)
        start = self.num_items
        for _ in xrange(1, self.num_rollbacks+1):
            # Stopping persistence on NodeA
            mem_client = MemcachedClientHelper.direct_client(
                self.input.servers[0], self.bucket_util.buckets[0])
            mem_client.stop_persistence()
            self.gen_create = doc_generator(self.key,
                                            start,
                                            mem_only_items,
                                            doc_size=self.doc_size,
                                            doc_type=self.doc_type,
                                            target_vbucket=self.target_vbucket,
                                            vbuckets=self.vbuckets)
            self.loadgen_docs(_sync=True)
            start = self.gen_create.key_counter
            stat_map = {self.cluster.nodes_in_cluster[0]: mem_only_items}
            for node in self.cluster.nodes_in_cluster[1:]:
                stat_map.update({node: 0})

            for bucket in self.bucket_util.buckets:
                self.bucket_util._wait_for_stat(bucket, stat_map)

#             self.task.compact_bucket(self.cluster.master,
#                                      bucket=self.bucket_util.buckets[0])
#             self.bucket_util._run_compaction(number_of_times=1)
            # Kill memcached on NodeA to trigger rollback on other Nodes
            # replica vBuckets
            shell.kill_memcached()
            self.assertTrue(self.bucket_util._wait_warmup_completed(
                [self.cluster_util.cluster.master],
                self.bucket_util.buckets[0],
                wait_time=self.wait_timeout * 10))
            self.sleep(60)
            self.bucket_util.verify_stats_all_buckets(items)
        shell.disconnect()
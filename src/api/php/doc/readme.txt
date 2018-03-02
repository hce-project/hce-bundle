Hierarchical Cluster Engine demo set and test suit for PHP language
=======================================================================

Copyright (c) 2013-2014 IOIX Ukraine,
                                 http://hierarchical-cluster-engine.com

-----------------------------------------------------------------------

Table of Contents

1. Introduction
   1.1. About the demo set and test suit
   1.2. Hierarchical Cluster Engine (HCE) usage and demo set
      1.2.1. General description of cluster data modes and structure
      1.2.2. Cluster start and stop
      1.2.3. Cluster diagnostic tools
   1.3. Hierarchical Cluster Engine (HCE) usage and test suit
      1.3.1. Localhost 1-1-2 cluster complex functional tests
      1.3.2. Localhost 1-1-2 cluster Sphinx search tests 
      1.3.3. Localhost 1-1-2 cluster DRCE exec tests
   1.4. Hierarchical Cluster Engine (HCE) usage for the DC service
      1.4.1. Single host clusters configuration and management
      1.4.2. Dual host clusters configuration and management
      1.4.3. Triple host clusters configuration and management
      1.4.4. The DTM service cluster schema creation

2. Installation
   2.1. First time installation
   2.2. Upgrade
   2.3. Deinstallation and cleanup

3. Usage
   3.1. Cluster structure models
   3.2. Spinx indexes and data schema
   3.3. Cluster start and shutdown
   3.4. Cluster state and management
   3.5. Test suit for Sphinx indexation and search
      3.5.1. Functional test ft01 - replica data nodes mode
      3.5.2. Functional test ft02 - replica data nodes mode
      3.5.3. Functional test ft02 - shard data nodes mode



Chapter 1. Introduction
=======================

Table of Contents

1.1. About the demo set and test suit
1.2. Hierarchical Cluster Engine (HCE) usage and demo set
   1.2.1. General description of cluster data modes and structure
   1.2.2. Cluster start and stop
   1.2.3. Cluster diagnostic tools
1.3. Hierarchical Cluster Engine (HCE) usage and test suit
   1.3.1. Localhost 1-1-2 cluster Sphinx search tests 
   1.3.2. Localhost 1-1-2 cluster complex functional tests



1.1. About the demo set and test suit
=====================================

The demo set and test suit for PHP language - it is mix of bash scripts, php
scripts with usage of php API for HCE projct and some data that was prepared
for tests. The main aim it is to give simple easy and light way to try the
HCE functionality, construct and up simple network cluster, test it on
productivity and stability reasons on single localhost server configuration.

The demo mode can be used to check common usage form and configuration settings
as well as to try to play with network- and CPU- dependent parameters.

Directories structure:
----------------------
/api/php/bin/   - php utilities, executable php scripts for bash environment
/api/php/cfg_default/   - bash include configuration definitions for tests
                  sets. Need to be renamet to cfg after extract.
/api/php/data/  - data files for Sphinx indexation and another data for test
                  suit
/api/php/doc/   - documentation
/api/php/inc_default/ - PHP language API includes, used by php utilities
                  and external interfaces. Need to be renamet to cfg after
                  extract.
/api/php/ini_default/ - ini files for nodes. Need to be renamet to cfg after
                  extract.
/api/php/log/   - demo test suit run-time logs
/api/php/manage/ - manage bash scripts to start, stop cluster and more
/api/php/tests/ - demo test suit bash scripts, main executable parts for
                  different structure clusters functional operations
/data/          - index data directory for Sphinx search indexes representation
/etc/           - configuration templates and related files for Sphinx search
                  functionality
/log/           - logs directory of Sphinx searchd process instances
/run/           - pid directory of Sphinx searchd process instances


1.2. Hierarchical Cluster Engine (HCE) usage and demo set
=========================================================

1.2.1 General description of cluster data modes and structure
=============================================================

The hce-node application can be tested on demo set pre-configured simple
cluster for one physical host server. This pre-configured set of settings,
configuration settings and parameters are provided by this demo test suit
archive.

The demo set defines cluster basic architecture 1-1-2-x. This means one
router, one data (shard or replica) manager, two Sphinx index manage data
(shard or replica) nodes in cluster:

       [router node]
            |
    [data manager node]
      /            \
[data node 1] [data node 2] [data node 3] [data node 4]

The cluster entry point is a roter node. It uses zmq API to receive client
connections and requests. It acts as a service with internal network protocol.
Many clients can connect to the router and make requests simultaneously.

The 1-1-2 structure can be used to simulate two types of data node sharding
model - proportional and replication.

The proportional type supposes sharding between two nodes and unique set of
document index for Sphinx search engine. This type also supposes multicast
mode of requests dispatching for two data nodes. This is simulation of
cluster unit for huge index that nedd to be split on several parts. The
search messages processing for one request handled in parallel mode.
Manager node collects results from all nodes and do reducing task. Reducing
task for Sphinx search includes merging, sort and duplicates removing.
Unique results returned as a response to the router node.

The replication type supposes mirroring of data between two nodes and
complete duplication of data. This type supposes round-robin or cyclic
executive requests dispatching between of two data nodes. In this case the
manager node do the same job as for proportional type, but number of
responses collected is always one.

To switch between this two principal modes the configuration parameter
"MANAGER_MODE" can be set as "smanager" or "rmanager" (now has two types
"rmanager-rnd" and "rmanager-round-robin") value in the

~/hce-node-bundle/api/php/cfg/c112_localhost_n0_cfg.sh

After type of data node sharding model was changed cluster needs to be
restarted.

Now several clusters with different schema and nodes mode can be configured
and started on the same local host. There is two pre-configured clusters:
c112_localhost_n0_cfg.sh
and
c112_localhost_m0_cfg.sh
that can be identified by logs suffixes "n0" and "m0".
All sets of ports and nodes can be defined independent way, but all
management and test scripts located in /manage and /tests directories
works only with one configuration.
To switch the current configuration use command:
/manage/config.sh n
/manage/config.sh m
To view current active configuration name use command:
/manage/config.sh
This way current configuration can be switched between many defined and
possible started clusters on the same local host or remote hosts.



1.2.2 Cluster start and stop
============================

After installation of hce-node package the main executable application
is ready to use, but needs to get correct parameters to sturt and construct
proper cluster tructure. The demo test suit contains complete set of bash
scripts to manage it. They are located in the /manage directory:

start_all.sh   - start cluster at localhost
stop_all.sh    - stop cluster at localhost

After cluster started once it runs several instances of hce-node application.
For localhost 1-1-2 cluster it is four instances. Total number of instances
at some period of time depends on cluster structural schema and state.

After start script finished the state of each nodes can be checked by logs
located at the:
~/hce-node-bundle/api/php/log/n0**.log
directory. The 1-1-2 cluster's nodes named as:
   n000_router.log  - router
   n010_manager.log - manager (shard or replica)
   n011_data.log    - data node admin management 1
   n012_data.log    - data node admin management 2
   n013_data.log    - data node searcher or DRCE worker 1
   n014_data.log    - data node searcher or DRCE worker 2

In case of all is okay with TCP and all required TCP ports are available
to use - the log file contains information about binding and connection
as well as periodical statistics of main indicators of node activity.

The TCP ports that is used for cluster architecture building defined in
the configuration file for corresponded cluster structure schema,
for example, for 1-1-2:
~/hce-node-bundle/api/php/cfg/c112_localhost_n0_cfg.sh - "rmanager" mode
~/hce-node-bundle/api/php/cfg/c112_localhost_m0_cfg.sh - "smanager" mode

The list of LAN ports are separated on three types:
  - Router ports: ROUTER_SERVER_PORT, ROUTER_ADMIN_PORT and ROUTER_CLIENT_PORT
  - Shard/replica manager node(s) ports: SHARD_MANAGER_ADMIN_PORT and
    SHARD_MANAGER_SERVER_PORT
  - Replica node(s) ports: REPLICAS_MANAGE_ADMIN_PORTS and
    REPLICAS_POOL_ADMIN_PORTS

The replica node admin ports separated on the manage and pool ports.
Manage ports used for data index management comand like Sphinx index
commands and general nodes management.
Pool ports used to manage the searchers or load-balancing nodes pool state
verification and management.

The cluster stop script sends shutdown command to all nodes via admin port,
but not wait on shutdown finish.
Current cluster state can be verified by any diagnostic tool script.

By default cluster 1-1-2 configured to have six nodes. See the 1.2.3 chart
schema diagnostic tool.

After all Demo Test Suit dependencies for PHP language installed and
configured proper way (please, see dependencies components installation manual
at main site documentation secton:
http://hierarchical-cluster-engine.com/install/
"Install Demo Test Suit Environment for PHP language" cluster can be started
by start all components script:

cd ~/hce-node-bundle/api/php/manage/
./start_all.sh

Before nodes instances started the log directory cleaned from logs of previous
start and all in memory node processed killed by name.

Started cluster can be stopped by stop all components script:
./stop_all.sh

The stop script calls shutdown command for each node and starts diagnostic
script tool "status.sh". Each node instance starts hce-node
process and uses from one to three ports depends on role.
After successful cluster stop all nodes instances shutdown and ports are
freed.

Some parts of cluster can be started and shutdowned separatedly to get
a possibility to manage them during the cluster session.
This can be used to do some tests and demo simulation of state of some
cluster nodes in router role, shard manager or replica. The dedicated
manage start scripts are:

start_replicas_manage.sh
start_replicas_pool.sh
start_replicas.sh
start_router.sh
start_shard_manager.sh

and stop scripts are:

stop_replicas.sh
stop_router.sh
stop_shard_manager.sh

To get more detailed start/stop management please see the manual for PHP
utility manager.php.


1.2.3. Cluster diagnostic tools
===============================

The demo test suit includes several diagnostic tools:

loglevel.sh     - get and set log level of all nodes
manager_mode.sh - get or set the shard manager node mode
properties.sh   - get properties of all handlers of all nodes
schema_chart.sh - get cluster schema in ASCII text chart format
schema_json.sh  - get cluster schema in json format
status.sh       - check status of all nodes instances processes

This tool scripts can be used to get some additional information at run-time
period. 

The logging of information of node state and messages processing
can be done in three levels:
    0 - minimal, includes only initialization and periodical statistical
        information.
    1 - middle, includes also the requests data contexts as well as additional
        information about handlers state.
    2 - maximal, includes also complete data of all messages fields and
        state, as well as additional information about functional objects
        state, like Sphinx Search Functional Object.

The properties information - it is handler's specific fields values. Each
field can be information or state. State fields can be changed by additional
API calls. Many state fields like TCP ports, data mode, logging level and so
on can be changed by dedicated API and manager commands at runtime.
The properties information can be used for diagnostic and tracking purposes.

The cluster schema - it is structural relations between all nodes that
detected at run time. It can be used to construct, check, verify and log
the cluster structure. In future this information can be used to restore
structure after some faults, to create mirrors and so on.
The ASCII chart schema for default cluster configuration looks like:

       n000
      router
     localhost
     A[*:5546]
     S[*:5557]
     C[*:5556]
        |
       n010
     rmanager
     localhost
     A[*:5549]
     S[*:5558]
 C[localhost:5557]
        |
         __________________
        |                  |
       n013               n014
      replica            replica
     localhost          localhost
     A[*:5530]          A[*:5531]
 C[localhost:5558]  C[localhost:5558]


   n011       n012
  replica    replica
 localhost  localhost
 A[*:5540]  A[*:5541]


First line of each node item - it is node name.
Second line - node mode.
Third line - the host of scanned admin port, for LAN cluster version
if diagnostic tool used at the same OS shell session it is always "localhost".
Next lines A[], S[] and C[] - represents Admin, Server and Client connection
ports used to listen to or to connect to depends on the node role.

In the example displayed above, all nodes instances in all roles uses the
Admin port 5546, 5549, 5530, 5531, 5540 and 5541 to listen on manager
connection and admin commands requests like manage, diagnostic or
administration of node or Sphinx index. But S[] and C[] connection ports used
in different way depends on roles.

The router node uses S[] port 5557 - to listen on rmanager node connection and
C[] port 5556 - to listen on manager connection and data command requests like
Sphinx search or DRCE exec. So node in router mode uses all three ports to
bind and to listen on connection.

The rmanager node uses S[] connection port to listen on replica node
connection and the C[] connection port - to connect to router node.

The replica node from pool set uses C[] connection port to connect to the
rmanager or smanager node. The replica from admin manage set does not use any
connectin ports but only A[].

So, connection ports S[] and C[] used to create and to hold the cluster
structure. The A[] connection ports used for management and diagnostic.

The status information tool "status.sh" gets only "Admin"
handler's fields. This is bit faster than all handlers fields in properties
information check. This information tool can be used to fast check nodes
state, for example, after start, shutdown, test set finish or some another
reasons.

Complete nodes handlers run-time properties can be fetched by the
"properties.sh" script. It get all handlers data from all
cluster nodes and store them in json forma in the log file.
This log file can be used to get some property by one for tracking toollike
Zabbix (c) system. For this purpose the fetcher tool named
zabbix_fetch_indicator.php included. Test script to check is the fetcher
worked also provided - zabbix_fetch_indicator.sh. It fetches the value of
"requestsTotal" property indicator of Admin handler from node localhost:5541.

Any diagnostic tool script can be started in any time without command line
arguments. Information displayed on console output or stored in the
correspondent log file in the ~hce-node-bundle/api/php/log/ directory.



1.3. Hierarchical Cluster Engine (HCE) usage and test suit
==========================================================


1.3.1. Localhost 1-1-2 cluster complex functional tests
=======================================================

The demo tests suit set contains several minimal functional tests sets to get
check of cluster functionality, productivity on concrete hardware platform,
Sphinx search tasks usage, API tests and usage checks and so on.

The functional tests combined in to the complete sequential actions that
reflects of typical usage of distributed data processing like documents
indexation and search, as well as administrative commands and dignostic tools.

Test suit contains functional tests sets that located in the:
~/hce-node-bundle/api/php/tests/*ft*.sh
files.

The *ft01*.sh test - it is complete life time simulation of the Sphinx search
cluster with replicated data nodes. Replication model is fully mirrored. So,
independently on the manager mode (shard or replica) this test will fill both
data nodes with the same documents. This is important to understand the search
results and productivity values. The correspondent mode of data nodes manager
for this test is "replica manager".

The life cycle of "ft01" includes execution of operations:
    * create new index,
    * fill index with branches document source files,
    * fill index with schema,
    * rebuild Sphinx indexes of all branches,
    * merge all branches indexes to the trunk index,
    * start index usage for Sphinx search,
    * full text search tests,
    * state diagnostic

And after testing cleanup actions like:
    * stop index usage,
    * remove index (including all data files and directories that was created)

After cluster was started - the "ft01" test suit unit can be started by
execution of the corresponded bash script, for example, for 1-1-2 cluster it
is the:
~/hce-node-bundle/api/php/tests/ft01.sh

After finish the execution logs can be checked. Logs are located in the:
~/hce-node-bundle/api/php/log/ft01.sh.log

After tests was done, any diagnostic tools or search tests can be started.
When all kind of tests or another actions finished, to cleanup the indexes
data from disk and to set cluster in initial state the ft01 cleanup script
need to be executed once, for example, for 1-1-2 localhost cluster:
~/hce-node-bundle/api/php/log/ft01_cleanup.sh

As well as for test suit unit results, cleanup execution results can be
checked in logs:
~/hce-node-bundle/api/php/log/ft01_cleanup.log

The *ft02*.sh test - it is complete life time simulation of the Sphinx search
cluster with fillng the data node indexes from data source directory and
supports shard and replication data mode. The sharding method depends on how
the cluster was started or what data mode used or manager node. If manager
node uses shard mode - smanager, indexes will be filled sequentially, from
one xml document file to another and all documents will be distributed between
several indexes managed by own data node. If manager node uses replica mode -
indexes will be filled with the same documents as complete mirrors for all
data nodes. Another operations of "ft02" - the same as for "ft01".
After "ft02" finished, logs can be checked to get information about how each
stage was finis.
The same way, after "ft02" was complete all kind of dagnostic or search can be
executed.
To cleanup the indexes data and return nodes back in to initial state the
"ft02" cleanup script nedd to be executed.

After cleanup script executed, the data node became at initial state, no more
indexes exists and search will always return empty results. Any another
operations and commands for Sphinx search index will return error.



1.3.2. Localhost 1-1-2 cluster Sphinx search tests
==================================================

The demo tests includes the Sphinx index search tests. This tests are two
processing models - single-client and multi-client. The single-client uses
one client connection to execute set of search requests. The searcher.php tool
utility used to execute search, but several required parameters are set by
bash script.
To execute set of searches in single-client mode, the script:
~/hce-node-bundle/api/php/tests/search_test.sh

can be executed. The search results located in the log file:
~/hce-node-bundle/api/php/log/search_test.sh.log

Different parameters like searched keyword, number of requests, number of
results, filters and so on can be changed inside this bash script as:
QUERY_STRING_DEFAULT, REQUESTS, RESULTS, LOG_LEVEL variables.

Multiple thread search can be started by:
~/hce-node-bundle/api/php/tests/search_test_multiclient.sh

Optional first parameter is searched string, default value is "for".

Default clients number is 16, requests per client 1000, max. results per one
search 10, log level 0. This settings defined in this file as variables:
QUERIES=1000
RESULTS=10
CLIENTS=16
TIMEOUT=5000
SEARCH_STRING="for"

and can be changed before run.



1.3.3. Localhost 1-1-2 cluster DRCE exec test #1
==================================================

The demo tests for DRCE includes set of prepared requests in json format for
different target execution environment (script programming languages, bash and
binary executable).

If the request requires source code or binary executable - it is stored as
separated file with the same name. It read and placed inside request json
by macro definition "READ_FROM_FILE:". If file is binary it need to be base64
encoded by set of highest bit in the "action" mask. Please see protocol
specification doc DRCE_Functional_object_protocol.pdf.

Three types of demo test scripts provides possibility to execute some request
in single thread (from one start to N iterations), execute all prepared
requests sequentially and to execute one of prepared request in multiple
threads parallel mode.

Set of prepared requests located in the:
~/hce-node-bundle/api/php/data/drce_ft01
directory. Each txt file contains prepared request in json format according
with the DRCE specification: DRCE_Functional_object_protocol.pdf

Each of prepared request enumerated as suffix of .txt file and can be addressed
by this number, for example file "c112_localhost_drce_json00.txt" can be
addressed as request 00, "c112_localhost_drce_json01a.txt" - as 01a and so on.

After cluster started with default configuration in balanced mode (shard
manager mode is "rmanager") single prepared request, for example, "00" can be
executed in single environment once by:
cd ~/hce-node-bundle/api/php/tests/
./drce_test.sh 00

Default log level is 4 (maximal) and log file with correspondent file name will
be stored in the log directory - "drce_test.sh.n0.log".
In case of success execution complete response message structure debugged,
including execution result stdout, execution time, and so on...

To execute all prepared requests use:
./drce_test_all.sh

The execution time depends on power of hardware platform and OS environment
settings. The log file "drce_test_all.sh.n0.log" will contain all
tests responses in the same format as single.

To execute one prepared request several times to get productivity report
for single thread parameter located in file "drce_test.sh"
REQUESTS=1

need to be changed, for example as:
REQUESTS=100

to execute specified prepared request 100 times sequentially.
The log level for multiple sequential execution can be set as 0. Parameter
LOG_LEVEL

To execute one prepared request by multiple clients, use:
./drce_test_multiclient.sh 00

Default clients number 16, requests for each client 1000, log level 0.
This will start 16 process of DRCE client utility drce.php.
The execution state can be evaluated by cluster properties statistics, nodes
logs and CPU utilization level.
Each instance of drce.php creates own log file, for example, drce_client.1.log,
drce_client.2.log and so on up to drce_client.16.log. Logs contains the same
information as single thread result.
Reqests number, clients number, timeout delay and the log level can be set by
variables:
QUERIES=1000
CLIENTS=16
TIMEOUT=5000
LOG_LEVEL=0

This test can be used to evaluate the platform power and possibility to process
some parallel tasks by target execution engine.



1.3.4. Localhost 1-1-2 cluster DRCE exec test #2
==================================================
This test set is list of algorithms taken from the project:
http://benchmarksgame.alioth.debian.org/

Languages covered:
  - c
  - C++
  - PHP
  - Python
  - Ruby
  - Perl
  - Java

Algorithms list:
  - binarytrees

Dependencies:
BC Math:
sudo apt-get install bc

~/hce_hce-node-bundle/api/php/data/c112_localhost_drce_ft02/binarytrees.gcc-7.c
Require the libapr1-dev package that can be installed by:
sudo apt-get install libapr1-dev

~/hce_hce-node-bundle/api/php/data/c112_localhost_drce_ft02/pidigits.c
sudo apt-get install libgmp-dev

~/hce_hce-node-bundle/api/php/data/c112_localhost_drce_ft02/pidigits.gpp-3.c++
sudo apt-get install libboost-dev

~/hce_hce-node-bundle/api/php/data/c112_localhost_drce_ft02/pidigits.php-5.php
sudo apt-get install php5-gmp
Add extension=gmp.so in /etc/php/php.ini file.

~/hce_hce-node-bundle/api/php/data/c112_localhost_drce_ft02/pidigits.python3-2.py
sudo apt-get install python-setuptools
sudo easy_install pip
sudo pip install virtualenv
sudo apt-get install python-dev
sudo apt-get install libmpfr-dev
sudo apt-get install libmpc-dev
sudo pip install gmpy2 --global-option=build_ext --global-option=-Ddir=/home/case/local
sudo apt-get install python-gmpy

~/hce_hce-node-bundle/api/php/data/c112_localhost_drce_ft02/pidigits.perl-4.perl
sudo perl -MCPAN -e 'install Net::SSH::Perl'



1.4. Hierarchical Cluster Engine (HCE) usage for the DC service
==========================================================
DC service uses HCE node clusters of several different types. Default
configuration and automation tools supports three typs: n-, m- and r-type.
The m- and r-type clusters used by the DC service directly for synchronous
DRCE tasks execution. Also, the DC service uses the DTM service. Te DTM service
uses n-type cluster for asynchronous DRCE tasks execution. This way the DC
service got adwantages of multi-processing and parallelism on the same and
different hosts for single and multi-host configurations.


1.4.1. Single host clusters configuration and management
========================================================
All nodes of single host clusters are located on the same host. Depends on
type from three (m-type) to six (r-type) nodes instances started. Always
the router and manager instances are started. For the n-type two data replica
nodes are started, for the m-type - one shard data node and for the r-type
- four replica data nodes started.
After the bundle archive extracted the single host configuration is ready to
run. All configuration files are set as default and single host configuration
is activated in the:
~/hce_hce-node-bundle/api/php/cfg/current_cfg.sh
section "Single-host configuration".
The DC service requires two types of clusters so called n-type for replica
balanced and m-type - for shard multicast. Also, optionally the r-type cluster
can be started for the real-time requests. The r-type also replica balanced
but configured to have four or more replicas instances per host to give the
advantage of multi-process parallelism and stability fail safe features.
Configuration files for the n, m and r types are:
c112_localhost_n0_cfg.sh
c112_localhost_m0_cfg.sh
c112_localhost_r0_cfg.sh
To start both n and m clusters use automation script:
~/hce_hce-node-bundle/api/php/manage/start_nm.sh
To start the r-type cluster use automation script:
~/hce_hce-node-bundle/api/php/manage/start_r.sh
To do any another management actions the current configuration need to be
switched from n-type to configuration of required cluster. For example, to
get schema chart of r-type cluster use:
./config.sh r
to switch current configuration and then:
./schema_chart.sh
to generate the schema and store it in the log directory.

To stop all n and m type clusters use:
~/hce_hce-node-bundle/api/php/manage/stop_nm.sh
To stop t-type cluster use:
~/hce_hce-node-bundle/api/php/manage/stop_r.sh

Any management scripts that no have "_nm" or "_r" suffix in the file
name acts using current cluster configuration (n-type after install).
Management scripts with suffixes switches configuration and return it back
always to the n-type.


1.4.2. Dual host clusters configuration and management
========================================================
The dual hosts clusters nodes instances are located on two physical or
logical hosts. First host holds router and manager nodes and data nodes.
Second host - only data nodes. That is minimal multi-host configuration.
The n-type cluster configured the same way as single node - two replica
node instances, but located on different hosts - one on first and one
on second host. The m-type cluster configured the same way as n-type - two
shard node instances one on first and one on second host.
Configuration files for first and second hosts are different. For the
first host of n-type:
c112_localhost_n0_2h_cfg.sh
for the second host n-type:
c112_localhost_n0_2h-data_cfg.sh
For the first host of m-type:
c112_localhost_m0_2h_cfg.sh
and for the second host of m-type:
c112_localhost_m0_2h-data_cfg.sh
For the first host of r-type:
c112_localhost_r0_2h_cfg.sh
and for the second host of r-type:
c112_localhost_r0_2h-data_cfg.sh

To activate the dual host configuration some changes need to be done for
current_cfg.sh file on each host different way. In each of three sections
for n-, m- and r-type clusters the default single host configuration line
need to be commented out and correspondent first or second host line of the
dual host configuration comment need to be removed. In result for the first
host only three lines titled as:
"Multi-host configuration for first host of dual hosts"
need to be uncommented and for the second host - only three lines titled as:
"Multi-host configuration for second host of dual hosts"
need to be uncommented for the n-, m- and r-type of clusters.

Configuration files need to be modified to specify the IP addresses of hosts.
Configuration files for the first host "c112_localhost_?0_2h_cfg.sh" need to
be modified with definition of the second host IP address:
REMOTE_HOSTS="10.0.0.2"
instead of the 10.0.0.2 the second host IP address need to be specified.
Configuration files for the second host: "c112_localhost_?0_2h-data_cfg.sh"
need to be modified with definition of the manager host IP address:
MANAGER="10.0.0.1"
instead of the 10.0.0.1 the first host IP address need to be specified.

The node_pool1.ini file used for all data nodes need to be modified to
specify own IP address and notification service IP address. Line:
node_host=localhost
the localhost need to be replaced with this host IP address (different for
the first and second hosts).
Line:
state_notification_host=127.0.0.1
the 127.0.0.1 need to be replaced with the first host server IP address,
because the DTM service located on that host.

After all that modifications was done cluster nodes can be started on both
hosts in any order (first or second host).

To start all nodes of n- and m-type clusters on first host use:
~/hce_hce-node-bundle/api/php/manage/start_nm.sh
and on the second host use:
~/hce_hce-node-bundle/api/php/manage/start_replicas_pool_nm.sh
because no router or manager nodes here.      

To stop all nodes on the first host use:
~/hce_hce-node-bundle/api/php/manage/stop_nm.sh
and on the second host:
~/hce_hce-node-bundle/api/php/manage/stop_replicas_nm.sh




1.4.3. Triple host clusters configuration and management
========================================================

...



1.4.4. The DTM service cluster schema creation
========================================================
To create n-type cluster schema used for the DTM service use this automations:
./config.sh n
./schema_json.sh
the schema json file will be created in the log directory. Then move and replace
default schema json file with actual in the python ini directory:
mv ~/hce_hce-node-bundle/api/php/log/schema_json.sh.n0-2h.log ~/hce-node-bundle/api/python/ini/hce_cluster_schema.json
for the dual host configuration.
After the n-type cluster schema was created and stored in the python ini directory the DTM service can be started.


to be continued...

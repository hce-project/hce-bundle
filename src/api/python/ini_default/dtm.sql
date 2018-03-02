SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `dtm`
--
CREATE DATABASE IF NOT EXISTS `dtm` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `dtm`;
-- --------------------------------------------------------

--
-- Table structure for table `ee_responses_table`
--

DROP TABLE IF EXISTS `ee_responses_table`;
CREATE TABLE IF NOT EXISTS `ee_responses_table` (
  `id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `data` longblob DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `resources_table`
--

DROP TABLE IF EXISTS `resources_table`;
CREATE TABLE IF NOT EXISTS `resources_table` (
  `nodeId` varchar(256) NOT NULL DEFAULT '0',
  `nodeName` varchar(256) NOT NULL DEFAULT '0',
  `host` varchar(256) NOT NULL DEFAULT '0',
  `port` int(10) unsigned NOT NULL DEFAULT '0',
  `cpu` int(10) unsigned NOT NULL DEFAULT '0',
  `io` int(10) unsigned NOT NULL DEFAULT '0',
  `ramRU` bigint(20) unsigned NOT NULL DEFAULT '0',
  `ramVU` bigint(20) unsigned NOT NULL DEFAULT '0',
  `ramR` bigint(20) unsigned NOT NULL DEFAULT '0',
  `ramV` bigint(20) unsigned NOT NULL DEFAULT '0',
  `swap` bigint(20) unsigned NOT NULL DEFAULT '0',
  `swapU` bigint(20) unsigned NOT NULL DEFAULT '0',
  `disk` bigint(20) unsigned NOT NULL DEFAULT '0',
  `diskU` bigint(20) unsigned NOT NULL DEFAULT '0',
  `state` int(10) unsigned NOT NULL DEFAULT '0',
  `uDate` datetime DEFAULT NULL,
  `cpuCores` int(10) unsigned NOT NULL DEFAULT '0',
  `threads` int(10) unsigned NOT NULL DEFAULT '0',
  `processes` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`nodeId`),
  KEY `nodeId` (`nodeId`),
  KEY `nodeName` (`nodeName`),
  KEY `host` (`host`),
  KEY `state` (`state`),
  KEY `uDate` (`uDate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `resources_table`
--

DROP TABLE IF EXISTS `scheduler_task_scheme`;
CREATE TABLE IF NOT EXISTS `scheduler_task_scheme` (
  `id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `rTime` bigint(20) unsigned NOT NULL DEFAULT '0',
  `rTimeMax` bigint(20) unsigned NOT NULL DEFAULT '0',
  `state` int(10) unsigned NOT NULL DEFAULT '0',
  `priority` int(10) unsigned NOT NULL DEFAULT '0',
  `strategy` text(8192) DEFAULT NULL,
  `tries` bigint(20) unsigned NOT NULL DEFAULT '0',
  `cdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `rTime` (`rTime`),
  KEY `state` (`state`),
  KEY `priority` (`priority`),
  KEY `tries` (`tries`),
  KEY `cdate` (`cdate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `task_back_log_scheme`
--

DROP TABLE IF EXISTS `task_back_log_scheme`;
CREATE TABLE IF NOT EXISTS `task_back_log_scheme` (
  `id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `pId` bigint(20) unsigned DEFAULT '0',
  `nodeName` varchar(128) DEFAULT '',
  `cDate` datetime DEFAULT NULL,
  `sDate` datetime DEFAULT NULL,
  `rDate` datetime DEFAULT NULL,
  `fDate` datetime DEFAULT NULL,
  `pTime` bigint(20) unsigned DEFAULT '0',
  `pTimeMax` bigint(20) unsigned DEFAULT '0',
  `state` int(10) unsigned DEFAULT '0',
  `uRRAM` bigint(20) unsigned DEFAULT '0',
  `uVRAM` bigint(20) unsigned DEFAULT '0',
  `uCPU` int(10) unsigned DEFAULT '0',
  `uThreads` int(10) unsigned DEFAULT '0',
  `tries` int(10) unsigned DEFAULT '0',
  `host` varchar(256) DEFAULT '',
  `port` varchar(256) DEFAULT '',
  `deleteTaskId` int(10) unsigned DEFAULT '0',
  `autoCleanupFields` text(8192) DEFAULT '',
  `type` int(10) unsigned DEFAULT '0',
  `name` varchar(256) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `pId` (`pId`),
  KEY `cDate` (`cDate`),
  KEY `sDate` (`sDate`),
  KEY `rDate` (`rDate`),
  KEY `fDate` (`fDate`),
  KEY `state` (`state`),
  KEY `deleteTaskId` (`deleteTaskId`),
  KEY `type` (`type`),
  KEY `host` (`host`),
  KEY `nodeName` (`nodeName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


-- --------------------------------------------------------

--
-- Table structure for table `task_log_scheme`
--

DROP TABLE IF EXISTS `task_log_scheme`;
CREATE TABLE IF NOT EXISTS `task_log_scheme` (
  `id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `pId` bigint(20) unsigned DEFAULT '0',
  `nodeName` varchar(128) DEFAULT '',
  `cDate` datetime DEFAULT NULL,
  `sDate` datetime DEFAULT NULL,
  `rDate` datetime DEFAULT NULL,
  `fDate` datetime DEFAULT NULL,
  `pTime` bigint(20) unsigned DEFAULT '0',
  `pTimeMax` bigint(20) unsigned DEFAULT '0',
  `state` int(10) unsigned DEFAULT '0',
  `uRRAM` bigint(20) unsigned DEFAULT '0',
  `uVRAM` bigint(20) unsigned DEFAULT '0',
  `uCPU` int(10) unsigned DEFAULT '0',
  `uThreads` int(10) unsigned DEFAULT '0',
  `tries` int(10) unsigned DEFAULT '0',
  `host` varchar(256) DEFAULT '',
  `port` varchar(256) DEFAULT '',
  `deleteTaskId` int(10) unsigned DEFAULT '0',
  `autoCleanupFields` text(8192) DEFAULT '',
  `type` int(10) unsigned DEFAULT '0',
  `name` varchar(256) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `pId` (`pId`),
  KEY `cDate` (`cDate`),
  KEY `sDate` (`sDate`),
  KEY `rDate` (`rDate`),
  KEY `fDate` (`fDate`),
  KEY `state` (`state`),
  KEY `deleteTaskId` (`deleteTaskId`),
  KEY `type` (`type`),
  KEY `host` (`host`),
  KEY `nodeName` (`nodeName`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


-- --------------------------------------------------------

--
-- Table structure for table `tasks_data_table`
--

DROP TABLE IF EXISTS `tasks_data_table`;
CREATE TABLE IF NOT EXISTS `tasks_data_table` (
  `id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `data` longblob DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

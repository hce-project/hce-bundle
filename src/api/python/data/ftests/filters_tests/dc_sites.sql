-- phpMyAdmin SQL  Dump
-- version 4.1.12
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 15, 2014 at 10:35 AM
-- Server version: 5.5.35-0+wheezy1
-- PHP Version: 5.4.4-14+deb7u8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `dc_sites`
--
CREATE DATABASE IF NOT EXISTS `dc_sites` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `dc_sites`;

-- --------------------------------------------------------

--
-- Table structure for table `sites`
--

DROP TABLE IF EXISTS `sites`;
CREATE TABLE IF NOT EXISTS `sites` (
  `Id` varchar(32) NOT NULL,
  `UDate` datetime DEFAULT NULL COMMENT 'Update some fields date',
  `TcDate` datetime DEFAULT NULL COMMENT 'Touch date, when some action was performed with site or it''s URLs',
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Resources` bigint(20) unsigned NOT NULL DEFAULT '0',
  `Contents` bigint(20) unsigned NOT NULL DEFAULT '0',
  `CollectedURLs` bigint(20) unsigned NOT NULL DEFAULT '0',
  `Iterations` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'Crawling iterations counter',
  `State` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '1 - Active, 2 - Disabled, 3 - Suspended',
  `Priority` int(10) unsigned NOT NULL DEFAULT '0',
  `MaxURLs` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '0- means unlimited',
  `MaxURLsFromPage` bigint(20) unsigned NOT NULL DEFAULT '200' COMMENT 'Max URLs collected from one page. 0- means unlimited',
  `MaxResources` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '0 - means unlimited',
  `MaxErrors` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '0 - means unlimited',
  `MaxResourceSize` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '0 - means unlimited',
  `RequestDelay` bigint(20) unsigned NOT NULL DEFAULT '500' COMMENT 'HTTP request delay',
  `ProcessingDelay` bigint(20) unsigned NOT NULL DEFAULT '1000' COMMENT 'Content processing delay',
  `HTTPTimeout` bigint(20) unsigned DEFAULT '30000' COMMENT 'HTTP response timeout, msec',
  `ErrorMask` bigint(64) unsigned NOT NULL DEFAULT '0' COMMENT 'Error bit set mask, see DC_application_architecture spec.',
  `Errors` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Errors counter',
  `Size` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'the sum of all raw content files sizes of resources crawled',
  `AVGSpeed` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT  'AVG bytes per second (BPS) rate',
  `AVGSpeedCounter` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'total times of claculating avg speed',
  `URLType` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0 - Regular, collect URLs and insert only for this site according filters; 1 - Single, do not collect URLs, 3 - collect URLs, create sites and insert for all',
  `User_Id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `RecrawlPeriod` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'Re-crawl period, min; 0 - means not re-crawl',
  `RecrawlDate` datetime DEFAULT NULL COMMENT 'Exact date of re-crawl',
  `FetchType` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '1 - static (default), 2 - dynamic, 3 - external',
  PRIMARY KEY (`Id`),
  KEY `TcDate` (`TcDate`),
  KEY `CDate` (`CDate`),
  KEY `UDate` (`UDate`),
  KEY `Iterations` (`Iterations`),
  KEY `State` (`State`),
  KEY `Priority` (`Priority`),
  KEY `MaxURLs` (`MaxURLs`),
  KEY `MaxResources` (`MaxResources`),
  KEY `MaxErrors` (`MaxErrors`),
  KEY `MaxResourceSize` (`MaxResourceSize`),
  KEY `ErrorMask` (`ErrorMask`),
  KEY `Errors` (`Errors`),
  KEY `URLType` (`URLType`),
  KEY `User_Id` (`User_Id`),
  KEY `RecrawlPeriod` (`RecrawlPeriod`),
  KEY `RecrawlDate` (`RecrawlDate`),
  KEY `FetchType` (`FetchType`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `sites_filters`
--

DROP TABLE IF EXISTS `sites_filters`;
CREATE TABLE IF NOT EXISTS `sites_filters` (
  `Site_Id` varchar(32) DEFAULT '0',
  `Pattern` varchar(4096) NOT NULL DEFAULT '""',
  `Type` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0 - Exclude, 1 - include',
  `Stage` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0 - Processing, 1 - before pre processing, 2 - after pre processing, 3 - after processing, 4-after processed',
  `Subject` varchar(500) NOT NULL DEFAULT '' COMMENT 'Subject', 
  `Action` tinyint(3) signed NOT NULL DEFAULT 0 COMMENT '1 - allow insert to urls table, -1 - not allow insert to urls table, 2 - not URLDelete, -2 - do URLDelete',
  `UDate` datetime DEFAULT NULL COMMENT 'Update date',
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Mode` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '0 - URLs of Site, 1 - URLs of media content',
  `State` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '',
  KEY `Site_Id` (`Site_Id`),
  KEY `UDate` (`UDate`),
  KEY `CDate` (`CDate`),
  KEY `Type` (`Type`),
  KEY `Mode` (`Mode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `sites_properties`
--

DROP TABLE IF EXISTS `sites_properties`;
CREATE TABLE IF NOT EXISTS `sites_properties` (
  `Site_Id` varchar(32) NOT NULL DEFAULT '""',
  `Name` varchar(64) NOT NULL DEFAULT '""',
  `Value` varchar(8192) NOT NULL DEFAULT '""',
  `UDate` datetime DEFAULT NULL COMMENT 'Update date',
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `Site_Id` (`Site_Id`),
  KEY `UDate` (`UDate`),
  KEY `CDate` (`CDate`),
  KEY `Name` (`Name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `sites_urls`
--

DROP TABLE IF EXISTS `sites_urls`;
CREATE TABLE IF NOT EXISTS `sites_urls` (
  `Site_Id` varchar(32) NOT NULL DEFAULT '""',
  `URL` varchar(4096) NOT NULL DEFAULT '""',
  `State` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0 - Enabled, 1 - disabled, 2 - error',
  `Crawled` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'Number of crawling iterations',
  `Processed` int(10) unsigned NOT NULL DEFAULT '0',
  `CrDate` datetime DEFAULT NULL COMMENT 'Last crawling date',
  `PrDate` datetime DEFAULT NULL COMMENT 'Processing date',
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `User_Id` bigint(20) unsigned NOT NULL DEFAULT '0',
  KEY `Site_Id` (`Site_Id`,`State`,`Crawled`,`Processed`,`CDate`),
  KEY `CrDate` (`CrDate`),
  KEY `PrDate` (`PrDate`),
  KEY `User_Id` (`User_Id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

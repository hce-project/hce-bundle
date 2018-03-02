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
  `Description` varchar(64) NOT NULL,
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `UDate` datetime DEFAULT NULL COMMENT 'Update some fields date',
  `TcDate` datetime DEFAULT NULL COMMENT 'Touch date for crawling, when some action was performed with site or it`s URLs',
  `TcDateProcess` datetime DEFAULT NULL COMMENT 'Touch date for processing, when some action was performed with site or it`s URLs',
  `Resources` bigint(20) unsigned NOT NULL DEFAULT '0',
  `Contents` bigint(20) unsigned NOT NULL DEFAULT '0',
  `CollectedURLs` bigint(20) unsigned NOT NULL DEFAULT '0',
  `NewURLs` bigint(20) unsigned NOT NULL DEFAULT '0',
  `DeletedURLs` bigint(20) unsigned NOT NULL DEFAULT '0',
  `Iterations` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'Crawling iterations counter',
  `State` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '1 - Active, 2 - Disabled, 3 - Suspended, 4 - recrawling',
  `Priority` int(10) unsigned NOT NULL DEFAULT '0',
  `MaxURLs` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '0- means unlimited',
  `MaxURLsFromPage` bigint(20) unsigned NOT NULL DEFAULT '200' COMMENT 'Max URLs collected from one page. 0- means unlimited',
  `MaxResources` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '0 - means unlimited',
  `MaxErrors` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '0 - means unlimited',
  `MaxResourceSize` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '0 - means unlimited',
  `RequestDelay` bigint(20) unsigned NOT NULL DEFAULT '500' COMMENT 'HTTP request delay',
  `ProcessingDelay` bigint(20) unsigned NOT NULL DEFAULT '1000' COMMENT 'Content processing delay',
  `HTTPTimeout` double NOT NULL DEFAULT '30000' COMMENT 'HTTP response timeout, msec',
  `ErrorMask` bigint(64) unsigned NOT NULL DEFAULT '0' COMMENT 'Error bit set mask, see DC_application_architecture spec.',
  `Errors` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Errors counter',
  `Size` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'the sum of all raw content files sizes of resources crawled',
  `AVGSpeed` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT  'AVG bytes per second (BPS) rate',
  `AVGSpeedCounter` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'total times of claculating avg speed',
  `URLType` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0 - Regular, collect URLs and insert only for this site according filters; 1 - Single, do not collect URLs, 3 - collect URLs, create sites and insert for all',
  `User_Id` bigint(20) unsigned NOT NULL DEFAULT '1',
  `RecrawlPeriod` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'Re-crawl period, min; 0 - means not re-crawl',
  `RecrawlDate` datetime DEFAULT NULL COMMENT 'Exact date of re-crawl',
  `FetchType` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '1 - static (default), 2 - dynamic, 3 - external',
  `Category_Id` int(10) unsigned NOT NULL DEFAULT '1' COMMENT 'Site specific category Id, 1 - the default category',
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
  KEY `FetchType` (`FetchType`),
  KEY `Description` (`Description`),
  KEY `NewURLs` (`NewURLs`),
  KEY `DeletedURLs` (`DeletedURLs`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `sites_filters`
--

DROP TABLE IF EXISTS `sites_filters`;
CREATE TABLE IF NOT EXISTS `sites_filters` (
  `Site_Id` varchar(32) DEFAULT '0',
  `Pattern` varchar(4096) NOT NULL DEFAULT '',
  `Subject` varchar(4096) NOT NULL DEFAULT '',
  `OperationCode` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '0 - re expression, 1 - equal, 2 - not equal, 3 - equal or less, 4 - equal or more, 5 - less, 6 - more, 7 - sql expression',
  `Stage` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '0 - collect urls, 1 - before dom pre, 2 - after dom pre, 3 - after dom, 4 - after processing, 5 - all stages, 6 - collect urls HTTP protocol, 7 - before processing',
  `Action` int(10) NOT NULL DEFAULT '0' COMMENT '>0 - Include, 1> - Exclude',
  `Type` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT 'Reserved',
  `UDate` datetime DEFAULT NULL COMMENT 'Update date',
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Mode` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '0 - URLs of Site, 1 - URLs of media content',
  `State` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '0 - Disabled, 1 - Enabled',
  `Group_Id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'The same value of filters recombination by AND, different - by OR',
  KEY `Site_Id` (`Site_Id`),
  KEY `UDate` (`UDate`),
  KEY `CDate` (`CDate`),
  KEY `Type` (`Type`),
  KEY `Mode` (`Mode`),
  KEY `State` (`State`),
  KEY `Group_Id` (`Group_Id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO `sites_filters` VALUES('0', 'htt(.*)', '', 0, 0, 1, 1, '2015-01-01 01:01:01', '2015-01-01 01:01:01', 0, 1, 0);
INSERT INTO `sites_filters` VALUES('0', '%TYPE%<>6 AND %STATUS%=4 AND %STATE%=0 AND %CRAWLED%>0 AND %SIZE%>0 AND ((%ERRORMASK% & 4198399) = 0) AND %CONTENTTYPE% IN (\'text/html\', \'text/json\') AND %HTTPCODE%=\'200\'', '', 7, 7, 1, 1, '2015-01-01 01:01:01', '2015-01-01 01:01:01', 0, 1, 0);

-- --------------------------------------------------------

--
-- Table structure for table `sites_properties`
--

DROP TABLE IF EXISTS `sites_properties`;
CREATE TABLE IF NOT EXISTS `sites_properties` (
  `Site_Id` varchar(32) NOT NULL DEFAULT '0',
  `URLMd5` varchar(32) NOT NULL DEFAULT '',
  `Name` varchar(64) NOT NULL DEFAULT '',
  `Value` varchar(8192) NOT NULL DEFAULT '',
  `UDate` datetime DEFAULT NULL COMMENT 'Update date',
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY `Site_Id` (`Site_Id`),
  KEY `URLMd5` (`URLMd5`),
  KEY `UDate` (`UDate`),
  KEY `CDate` (`CDate`),
  KEY `Name` (`Name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `sites_urls`
--

-- DROP TABLE IF EXISTS `sites_urls`;
-- CREATE TABLE IF NOT EXISTS `sites_urls` (
--   `Site_Id` varchar(32) NOT NULL DEFAULT '',
--   `URL` varchar(4096) NOT NULL DEFAULT '',
--   `State` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0 - Enabled, 1 - Disabled',
--   `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   `User_Id` bigint(20) unsigned NOT NULL DEFAULT '0',
--   KEY `Site_Id` (`Site_Id`),
--   KEY `User_Id` (`User_Id`)
-- ) ENGINE=MyISAM DEFAULT CHARSET=utf8;

INSERT INTO `sites_properties` (`Site_Id`, `URLMd5`, `Name`, `Value`, `UDate`, `CDate`) VALUES
('0', '', 'PROCESS_CTYPES', 'text/html,text/xml,application/rss+xml,text/json', NULL, NOW());

-- --------------------------------------------------------

DROP TABLE IF EXISTS `sites_urls`;
CREATE TABLE IF NOT EXISTS `sites_urls` (
  `Site_Id` varchar(32) NOT NULL DEFAULT '0',
  `URL` varchar(4096) NOT NULL DEFAULT '',
  `Type` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0 - Regular, collect URLs and insert only for this site according filters; 1 - Single, do not collect URLs, 3 - collect URLs, create sites and insert for all',
  `State` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '0 - Enabled, 1 - disabled, 2 - error',
  `Status` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '0 - Undefined, 1 - New, 2 - selected for crawling, 3 - crawling, 4 - crawled, 5 - selected to process, 6 - processing, 7 - processed, 8 - as 2 for incremental',
  `Crawled` bigint(20) unsigned NOT NULL DEFAULT '0',
  `Processed` bigint(20) unsigned NOT NULL DEFAULT '0',
  `URLMd5` varchar(32) NOT NULL DEFAULT '',
  `ContentType` varchar(32) NOT NULL DEFAULT '' COMMENT 'MIME content-type string',
  `RequestDelay` bigint(20) unsigned NOT NULL DEFAULT '500' COMMENT 'Delay before HTTP request',
  `ProcessingDelay` bigint(20) unsigned NOT NULL DEFAULT '1000' COMMENT 'Content processing delay',
  `HTTPTimeout` double NOT NULL DEFAULT '30000' COMMENT 'HTTP response timeout, msec',
  `Charset` varchar(32) NOT NULL DEFAULT '',
  `Batch_Id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'Batch task Id of DTM',
  `ErrorMask` bigint(64) unsigned DEFAULT '0' COMMENT 'Error mask bits set',
  `CrawlingTime` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Time of crawling, msec',
  `ProcessingTime` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'After crawling processing time, msec',
  `TotalTime` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Total crawling time, msec',
  `HTTPCode` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'HTTP response code',
  `HTTPMethod` varchar(10) NOT NULL DEFAULT '',
  `Size` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Resource size, byte',
  `LinksI` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'number of internal links',
  `LinksE` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'number of external links',
  `Freq` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Frequency of usage of the page URL on another pages of this site',
  `Depth` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'url depth',
  `RawContentMd5` varchar(32) NOT NULL DEFAULT '' COMMENT 'md5 sum of raw content',
  `ParentMd5` varchar(32) NOT NULL DEFAULT '' COMMENT 'MD5 Id of the parent page URL',
  `LastModified` datetime DEFAULT NULL COMMENT 'Last-Modified tag value',
  `ETag` varchar(32) NOT NULL DEFAULT '' COMMENT 'etag value in response headers',
  `MRate` float(10,8) NOT NULL DEFAULT 0 COMMENT 'AVG mutability rate',
  `MRateCounter` bigint(20) NOT NULL DEFAULT 0 COMMENT 'counter for AVG mutability rate',
  `UDate` datetime DEFAULT NULL COMMENT 'Update date',
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `TcDate` datetime DEFAULT NULL COMMENT 'Touch date',
  `MaxURLsFromPage` bigint(20) unsigned NOT NULL DEFAULT '200' COMMENT 'Max URLs collected from one page. 0- means unlimited',
  `TagsMask` bigint(64) unsigned DEFAULT '0' COMMENT 'Tags mask bits set',
  `TagsCount` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Tags count from article',
  `PDate` datetime DEFAULT NULL COMMENT 'Exact date of publication',
  `ContentURLMd5` varchar(32) NOT NULL DEFAULT '',
  `Priority` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'Priority by default inherited from parent URL or set by another source',
  `ClassifierMask` bigint(20) unsigned NOT NULL DEFAULT '0',
  `User_Id` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`Site_Id`,`URLMd5`),
  KEY (`URLMd5`),
  KEY `Site_Id` (`Site_Id`),
  KEY `User_Id` (`User_Id`),
  KEY `UDate` (`UDate`),
  KEY `CDate` (`CDate`),
  KEY `State` (`State`),
  KEY `Crawled` (`Crawled`),
  KEY `Processed` (`Processed`),
  KEY `Status` (`Status`),
  KEY `Type` (`Type`),
  KEY `ContentType` (`ContentType`),
  KEY `Charset` (`Charset`),
  KEY `ErrorMask` (`ErrorMask`),
  KEY `HTTPCode` (`HTTPCode`),
  KEY `CrawlingTime` (`CrawlingTime`),
  KEY `ProcessingTime` (`ProcessingTime`),
  KEY `Size` (`Size`),
  KEY `MRate` (`MRate`),
  KEY `TagsMask` (`TagsMask`),
  KEY `TagsCount` (`TagsCount`),
  KEY `PDate` (`PDate`),
  KEY `ContentURLMd5` (`ContentURLMd5`),
  KEY `Priority` (`Priority`),
  KEY `Batch_Id` (`Batch_Id`),
  KEY `Depth` (`Depth`),
  KEY `RawContentMd5` (`RawContentMd5`),
  KEY `ParentMd5` (`ParentMd5`),
  KEY `LastModified` (`LastModified`),
  KEY `TcDate` (`TcDate`),
  KEY `URL` (`URL`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `sites_proxy`
--
CREATE TABLE `sites_proxy` (
  `Id` bigint(20) UNSIGNED NOT NULL,
  `Site_Id` varchar(32) NOT NULL DEFAULT '0',
  `Host` varchar(128) NOT NULL DEFAULT '0',
  `Domains` varchar(8192) DEFAULT NULL,
  `Priority` int(10) UNSIGNED NOT NULL DEFAULT '0',
  `State` int(10) UNSIGNED NOT NULL DEFAULT '0',
  `CountryCode` varchar(2) NOT NULL COMMENT 'ISO Country code two character',
  `CountryName` varchar(64) NOT NULL,
  `RegionCode` int(10) UNSIGNED NOT NULL DEFAULT '0',
  `RegionName` varchar(64) NOT NULL,
  `CityName` varchar(64) CHARACTER SET utf8mb4 NOT NULL,
  `ZipCode` varchar(8) NOT NULL,
  `TimeZone` varchar(64) NOT NULL,
  `Latitude` double NOT NULL,
  `Longitude` double NOT NULL,
  `MetroCode` int(10) UNSIGNED NOT NULL,
  `Faults` int(10) UNSIGNED NOT NULL DEFAULT '0',
  `FaultsMax` int(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT '0 - unlimited',
  `Category_Id` int(10) UNSIGNED NOT NULL,
  `Limits` varchar(8192) DEFAULT NULL,
  `Description` text,
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `UDate` datetime NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Indexes for table `sites_proxy`
--
ALTER TABLE `sites_proxy`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `Site_Id` (`Site_Id`),
  ADD KEY `Host` (`Host`),
  ADD KEY `Priority` (`Priority`),
  ADD KEY `State` (`State`),
  ADD KEY `CountryCode` (`CountryCode`),
  ADD KEY `CountryName` (`CountryName`),
  ADD KEY `RegionCode` (`RegionCode`),
  ADD KEY `RegionName` (`RegionName`),
  ADD KEY `CityName` (`CityName`),
  ADD KEY `ZipCode` (`ZipCode`),
  ADD KEY `TimeZone` (`TimeZone`),
  ADD KEY `Latitude` (`Latitude`),
  ADD KEY `Longitude` (`Longitude`),
  ADD KEY `MetroCode` (`MetroCode`),
  ADD KEY `Faults` (`Faults`),
  ADD KEY `FaultsMax` (`FaultsMax`),
  ADD KEY `CategoryId` (`Category_Id`),
  ADD KEY `CDate` (`CDate`),
  ADD KEY `UDate` (`UDate`);
--
-- AUTO_INCREMENT for table `sites_proxy`
--
ALTER TABLE `sites_proxy`
  MODIFY `Id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;


/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
--
-- Database: `dc_stat_freqs`
--
CREATE DATABASE IF NOT EXISTS `dc_stat_freqs` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `dc_stat_freqs`;

-- --------------------------------------------------------
DROP TABLE IF EXISTS `freq_0`;
CREATE TABLE IF NOT EXISTS `freq_0` (
  `URLMd5` varchar(32) NOT NULL DEFAULT '',
  `FIns` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Frequency of insert',
  `FDel` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Frequency of delete',
  `FUpd` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Frequency of update',
  `FNew` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Frequency of new url.status',
  `FCrawled` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Frequency of crawled url.status',
  `FProcessed` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Frequency of processed url.status',
  `FAged` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Frequency of aged state',
  `FDeleted` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Frequency of deleted state',
  `FPurged` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Frequency of purged state',
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `MDate` datetime DEFAULT NULL COMMENT 'Modification date',
  PRIMARY KEY (`URLMd5`),
  KEY `CDate` (`CDate`),
  KEY `MDate` (`MDate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
--
-- Database: `dc_stat_logs`
--
CREATE DATABASE IF NOT EXISTS `dc_stat_logs` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `dc_stat_logs`;

-- --------------------------------------------------------
DROP TABLE IF EXISTS `log_0`;
CREATE TABLE IF NOT EXISTS `log_0` (
  `URLMd5` varchar(32) NOT NULL DEFAULT '',
  `OpCode` tinyint(3) unsigned NOT NULL DEFAULT '20' COMMENT 'URL: 20 - Insert, 21 - Delete, 22 - Update; Status: 1 - New, 2 - Selected to crawl, 3 - Crawling, 4 - Crawled, 5 - Selected to process, 6 - Processing, 7 - Processed',
  `Object` text NOT NULL,
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ODate` datetime DEFAULT NULL COMMENT 'Operation date',
  PRIMARY KEY (`URLMd5`),
  KEY `CDate` (`CDate`),
  KEY `ODate` (`ODate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
--
-- Database: `dc_attributes`
--
CREATE DATABASE IF NOT EXISTS `dc_attributes` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `dc_attributes`;

-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `att_0` (
  `Id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(32) NOT NULL DEFAULT '',
  `URLMd5` varchar(32) NOT NULL DEFAULT '',
  `Value` longblob NOT NULL,
   PRIMARY KEY (`Id`),
   UNIQUE KEY `Name` (`Name`,`URLMd5`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


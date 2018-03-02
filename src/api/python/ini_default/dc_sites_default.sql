SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `dc_sites`
--
USE `dc_sites`;

INSERT INTO `sites` (`Id`, `Description`, `UDate`, `TcDate`, `TcDateProcess`, `CDate`, `Resources`, `Contents`, `Iterations`, `State`, `Priority`, `MaxURLs`, `MaxResources`, `MaxErrors`, `MaxResourceSize`, `RequestDelay`, `ProcessingDelay`, `HTTPTimeout`, `ErrorMask`, `Errors`, `Size`, `AVGSpeed`, `AVGSpeedCounter`, `URLType`) VALUES
('0', 'System default', NOW(), NOW(), NULL, NOW(), 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 30000, 0, 0, 0, 0, 0, 1);
--
-- Database: `dc_urls`
--
USE `dc_urls`;

CREATE TABLE IF NOT EXISTS `urls_0` (
  `Site_Id` varchar(32) NOT NULL DEFAULT '0',
  `URL` varchar(4096) NOT NULL DEFAULT '',
  `Type` tinyint(3) unsigned NOT NULL DEFAULT '1' COMMENT '0 - Regular, collect URLs and insert only for this site according filters; 1 - Single, do not collect URLs, 3 - collect URLs, create sites and insert for all',
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
  `TagsCount` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'Tags counter from article',
  `PDate` datetime DEFAULT NULL COMMENT 'Exact date of publication',
  `ContentURLMd5` varchar(32) NOT NULL DEFAULT '',
  `Priority` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'Priority by default inherited from parent URL or set by another source',
  `ClassifierMask` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`URLMd5`),
  KEY `Site_Id` (`Site_Id`),
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
  KEY `TcDate` (`TcDate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

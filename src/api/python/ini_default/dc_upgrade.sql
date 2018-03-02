--
-- Database upgrade changes in format - two lines: date line Y-m-d and SQL queries set
--

-- 2015-10-18
USE `dc_sites`;
alter table `sites` add column `Category_Id` int(10) unsigned NOT NULL DEFAULT '0';

-- 2015-11-10
USE 'dc_processor';
INSERT INTO  `scraper_main` (  `Name` ,  `Hits` ,  `Value` ,  `User_Id` ,  `CDate` ,  `UDate` ) 
VALUES (
'ScraperMultiItemsTask', 0, '{"properties":{"algorithm":{"algorithm_name":"regular"},"modules":{"regular":["ScrapyExtractor","GooseExtractor","NewspaperExtractor","MLExtractor"],"concurrency":["NewspaperExtractor","ScrapyExtractor","GooseExtractor"],"training":["ScrapyExtractor","DiffBotExtractor"],"ML":["MLExtractor"],"SCRAPY":["ScrapyExtractor"],"GOOSE":["GooseExtractor"],"NEWSPAPER":["NewspaperExtractor"],"prediction":["MLExtractor"]}}}', 0,  '',  '');

-- 2015-12-03
-- --------------------------------------------------------

--
-- Table structure for table `sites_proxy`
--
USE `dc_sites`;

DROP TABLE IF EXISTS `sites_proxy`;
CREATE TABLE IF NOT EXISTS `sites_proxy` (
  `Site_Id` varchar(32) NOT NULL DEFAULT '0',
  `Host` varchar(128) NOT NULL DEFAULT '0',
  `Domains` text(8192) DEFAULT NULL,
  `Priority` int(10) unsigned NOT NULL DEFAULT '0',
  `State` int(10) unsigned NOT NULL DEFAULT '0',
  `Limits` text(8192) DEFAULT NULL,
  `Description` text(8192) DEFAULT NULL,
  KEY `Site_Id` (`Site_Id`),
  KEY `Host` (`Host`),
  KEY `Priority` (`Priority`),
  KEY `State` (`State`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


-- 2016-01-05
-- Added `ClassifierMask` field
USE `dc_sites`
alter table `sites_urls` add column `ClassifierMask` bigint(20) unsigned NOT NULL DEFAULT '0';

USE `dc_urls`
-- for each table in dc_urls
alter table `urls_%siteId%` add column `ClassifierMask` bigint(20) unsigned NOT NULL DEFAULT '0';

USE `dc_urls_deleted`
-- for each table in dc_urls_deleted
alter table `urls_%siteId%` add column `ClassifierMask` bigint(20) unsigned NOT NULL DEFAULT '0';

-- 2016-02-16
-- Create dc_attributes DB
source dc_attributes.sql;

-- Table att_<site_id>
USE dc_attributes;

CREATE TABLE IF NOT EXISTS `att_%SITE_ID%` (
  `Id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(32) NOT NULL DEFAULT '',
  `URLMd5` varchar(32) NOT NULL DEFAULT '',
  `Value` longblob NOT NULL,
   PRIMARY KEY (`Id`),
   UNIQUE KEY `Name` (`Name`,`URLMd5`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- for each table in dc_attributes
ALTER TABLE `att_%SITE_ID%` ADD `CDate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `Value`, ADD INDEX (`CDate`);
ALTER TABLE `att_%SITE_ID%` ADD INDEX (`URLMd5`);

-- 2016-05-11
USE `dc_sites`;
ALTER TABLE `sites_proxy` ADD `CountryCode` VARCHAR(2) NOT NULL COMMENT 'ISO Country code two character' AFTER `State`, ADD INDEX (`CountryCode`(2));
ALTER TABLE `sites_proxy` ADD `CountryName` VARCHAR(64) NOT NULL AFTER `CountryCode`, ADD INDEX (`CountryName`(64));
ALTER TABLE `sites_proxy` ADD `RegionCode` INT UNSIGNED NOT NULL DEFAULT '0' AFTER `CountryName`, ADD INDEX (`RegionCode`);
ALTER TABLE `sites_proxy` ADD `RegionName` VARCHAR(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL AFTER `RegionCode`, ADD INDEX (`RegionName`(64));
ALTER TABLE `sites_proxy` ADD `CityName` VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL AFTER `RegionName`, ADD INDEX (`CityName`(64));
ALTER TABLE `sites_proxy` ADD `ZipCode` VARCHAR(8) NOT NULL AFTER `CityName`, ADD INDEX (`ZipCode`(8));
ALTER TABLE `sites_proxy` ADD `TimeZone` VARCHAR(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL AFTER `ZipCode`, ADD INDEX (`TimeZone`(64));
ALTER TABLE `sites_proxy` ADD `Latitude` DOUBLE NOT NULL AFTER `TimeZone`, ADD INDEX (`Latitude`);
ALTER TABLE `sites_proxy` ADD `Longitude` DOUBLE NOT NULL AFTER `Latitude`, ADD INDEX (`Longitude`);
ALTER TABLE `sites_proxy` ADD `MetroCode` INT UNSIGNED NOT NULL AFTER `Longitude`, ADD INDEX (`MetroCode`);
ALTER TABLE `sites_proxy` ADD `Faults` INT UNSIGNED NOT NULL DEFAULT '0' AFTER `MetroCode`, ADD INDEX (`Faults`);
ALTER TABLE `sites_proxy` ADD `FaultsMax` INT UNSIGNED NOT NULL DEFAULT '0' COMMENT '0 - unlimited' AFTER `Faults`, ADD INDEX (`FaultsMax`);
ALTER TABLE `sites_proxy` ADD `Category_Id` INT UNSIGNED NOT NULL AFTER `FaultsMax`, ADD INDEX (`Category_Id`);
ALTER TABLE `sites_proxy` ADD `Id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT FIRST, ADD PRIMARY KEY (`Id`);
ALTER TABLE `sites_proxy` ADD `CDate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `Description`, ADD INDEX (`CDate`);
ALTER TABLE `sites_proxy` ADD `UDate` DATETIME NOT NULL AFTER `CDate`, ADD INDEX (`UDate`);

UPDATE `sites_proxy` SET `CDate`=NOW(),`UDate`=NOW() WHERE 1

--2016-07-05 text/html,text/xml,application/rss+xml,text/json
USE `dc_sites`;
DELETE FROM `sites_filters` WHERE `Stage`='7' AND `OperationCode`='7' AND `Site_Id`='0';
INSERT INTO `sites_filters` VALUES('0', '%TYPE%<>6 AND %STATUS%=4 AND %STATE%=0 AND %CRAWLED%>0 AND %SIZE%>0 AND ((%ERRORMASK% & 4198399) = 0) AND %CONTENTTYPE% IN (\'text/html\', \'text/xml\',\'application/rss+xml\', \'text/json\') AND %HTTPCODE%=\'200\'', '', 7, 7, 1, 1, '2015-01-01 01:01:01', '2015-01-01 01:01:01', 0, 1, 0);

UPDATE `sites_properties` SET `Value`='text/html,text/xml,application/rss+xml,text/json' WHERE `Site_Id`='0' AND `Name`='PROCESS_CTYPES';


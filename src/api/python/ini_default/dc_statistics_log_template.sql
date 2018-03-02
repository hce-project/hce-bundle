CREATE TABLE IF NOT EXISTS `log_%SITE_ID%` (
  `URLMd5` varchar(32) NOT NULL DEFAULT '',
  `OpCode` tinyint(3) unsigned NOT NULL DEFAULT '20' COMMENT 'URL: 20 - Insert, 21 - Delete, 22 - Update, 23 - Cleanup, 24 - Aging, 25 - Content; Status: 1 - New, 2 - Selected to crawl, 3 - Crawling, 4 - Crawled, 5 - Selected to process, 6 - Processing, 7 - Processed',
  `Object` text NOT NULL,
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ODate` datetime DEFAULT NULL COMMENT 'Operation date',
  KEY `URLMd5` (`URLMd5`),
  KEY `OpCode` (`OpCode`),
  KEY `CDate` (`CDate`),
  KEY `ODate` (`ODate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

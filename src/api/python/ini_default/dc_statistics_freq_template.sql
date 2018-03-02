CREATE TABLE IF NOT EXISTS `freq_%SITE_ID%` (
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

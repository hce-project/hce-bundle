CREATE TABLE IF NOT EXISTS `att_%SITE_ID%` (
  `Id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(32) NOT NULL DEFAULT '',
  `URLMd5` varchar(32) NOT NULL DEFAULT '',
  `Value` longblob NOT NULL,
  `CDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (`Id`),
   UNIQUE KEY `Name` (`Name`,`URLMd5`),
   KEY `CDate` (`CDate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `contents_%SITE_ID%` (
  `id` varchar(32) NOT NULL DEFAULT '',
  `data` longblob NOT NULL,
  `CDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY `id` (`id`),
  KEY `CDate` (`CDate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

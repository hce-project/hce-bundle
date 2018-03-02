-- Create table `social_data_cache` for `news_hub` database
-- --------------------------------------------------------
--
-- Table structure for table `social_data_cache`
--
USE `news_hub`;

CREATE TABLE IF NOT EXISTS `social_data_cache` (
  `Id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,  
  `URLMd5` varchar(32) NOT NULL DEFAULT '',
  `URL` varchar(4096) NOT NULL DEFAULT '',
  `SocialData` longtext NOT NULL DEFAULT '',
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `URLMd5` (`URLMd5`),
  KEY `CDate` (`CDate`)    
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


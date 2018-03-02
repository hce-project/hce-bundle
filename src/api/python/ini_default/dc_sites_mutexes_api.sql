SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

-- Example of usage: SELECT mutexLock("SELECT_LOCK", 111, 30);

USE `dc_sites`;

DROP TABLE IF EXISTS `mutexes`;
CREATE TABLE IF NOT EXISTS `mutexes` (
  `Id` tinyint(3) unsigned NOT NULL AUTO_INCREMENT,
  `Application_Id` int(10) unsigned NOT NULL DEFAULT '0',
  `Name` varchar(64) NOT NULL DEFAULT '',
  `Value` tinyint(3) unsigned NOT NULL DEFAULT '0',
  `TTL` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'TTL seconds',
  `UDate` datetime NOT NULL COMMENT 'Modification date',
  PRIMARY KEY (`Id`),
  UNIQUE KEY `Application_Id_2` (`Application_Id`,`Name`),
  KEY `Application_Id` (`Application_Id`),
  KEY `Name` (`Name`),
  KEY `TTL` (`TTL`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=6 ;

--
-- Dumping data for table `mutexes`
--

INSERT INTO `mutexes` VALUES(NULL, 0, 'SELECT_LOCK', 0, 0, NOW());
INSERT INTO `mutexes` VALUES(NULL, 0, 'DELETE_LOCK', 0, 0, NOW());

--
-- Functions definition
--

DELIMITER $$

DROP FUNCTION IF EXISTS `mutexLock` $$
CREATE FUNCTION `mutexLock` (P_Name varchar(64), P_Application_Id int(3), TTL int(10)) RETURNS INT
READS SQL DATA
BEGIN

  DECLARE Mutex_Id INT DEFAULT 0;
  DECLARE TTLExpired INT DEFAULT 0;
  DECLARE done INT DEFAULT 0;
  DECLARE cur1 CURSOR FOR SELECT `Id` FROM `mutexes` WHERE `Name`=P_Name AND `Application_Id`=P_Application_Id AND `Value`=0 LIMIT 1;
  DECLARE cur2 CURSOR FOR SELECT `Id`, (DATE_ADD(`UDate`, INTERVAL `TTL` SECOND)<NOW() AND `TTL`>0) FROM `mutexes` WHERE `Name`=P_Name AND `Application_Id`=P_Application_Id LIMIT 1;
  DECLARE cur3 CURSOR FOR SELECT `Id` FROM `mutexes` WHERE `Name`=P_Name AND `Application_Id`=P_Application_Id AND `Value`>0 LIMIT 1;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done=1;

-- Check for unlocked mutex exists
  OPEN cur1;
    t_loop: LOOP
      FETCH cur1 INTO Mutex_Id;
      IF done=1 THEN
       LEAVE t_loop;
      END IF;
    END LOOP t_loop;
  CLOSE cur1;

  IF Mutex_Id>0 THEN
-- If exists - update value to LOCKED state
    UPDATE `mutexes` SET `Value`=1, `UDate`=NOW() WHERE `Id`=Mutex_Id LIMIT 1;
-- Ensure that state updated
    SET Mutex_Id=0;
    OPEN cur3;
      t_loop4: LOOP
        FETCH cur3 INTO Mutex_Id;
        IF done=1 THEN
         LEAVE t_loop4;
        END IF;
      END LOOP t_loop4;
    CLOSE cur3;
  ELSE
-- If not exists in unlocked state - check in any state
    OPEN cur2;
      t_loop2: LOOP
        FETCH cur2 INTO Mutex_Id, TTLExpired;
        IF done=1 THEN
         LEAVE t_loop2;
        END IF;
      END LOOP t_loop2;
    CLOSE cur2;
-- If not exists at all - create in LOCKED state
    IF Mutex_Id=0 THEN
      INSERT INTO `mutexes` SET `Name`=P_Name, `Application_Id`=P_Application_Id, `Value`=1, `UDate`=NOW(), `TTL`=TTL;
-- Ensure that mutex created
      OPEN cur3;
        t_loop3: LOOP
          FETCH cur3 INTO Mutex_Id;
          IF done=1 THEN
           LEAVE t_loop3;
          END IF;
        END LOOP t_loop3;
      CLOSE cur3;
    ELSE
-- If exists in LOCKED state - check the TTL
      IF TTLExpired>0 THEN
-- TTL is expired, refresh UDate, update to locked (redundand) and return it to get to reuse with new TTL
        UPDATE `mutexes` SET `Value`=1, `UDate`=NOW(), `TTL`=TTL WHERE `Id`=Mutex_Id LIMIT 1;
      ELSE
-- Return false to indicate fault of lock of locked mutex
        SET Mutex_Id=0;
      END IF;
    END IF;
  END IF;

-- Return the mutex Id
  RETURN Mutex_Id;
END $$

DROP FUNCTION IF EXISTS `mutexUnlock` $$
CREATE FUNCTION `mutexUnlock` (P_Name varchar(64), P_Application_Id int(3)) RETURNS INT
READS SQL DATA
BEGIN

  DECLARE Mutex_Id INT DEFAULT 0;
  DECLARE done INT DEFAULT 0;
  DECLARE cur1 CURSOR FOR SELECT `Id` FROM `mutexes` WHERE `Name`=P_Name AND `Application_Id`=P_Application_Id AND `Value`>0 LIMIT 1;
  DECLARE cur2 CURSOR FOR SELECT `Id` FROM `mutexes` WHERE `Name`=P_Name AND `Application_Id`=P_Application_Id AND `Value`=0 LIMIT 1;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done=1;

-- Check the locked mutex
  OPEN cur1;
    t_loop: LOOP
      FETCH cur1 INTO Mutex_Id;
      IF done=1 THEN
       LEAVE t_loop;
      END IF;
    END LOOP t_loop;
  CLOSE cur1;

-- If exists locked mutex - set to UNLOCKED state
  IF Mutex_Id>0 THEN
    UPDATE `mutexes` SET `Value`=0, `UDate`=NOW() WHERE `Id`=Mutex_Id LIMIT 1;
-- Ensure that state changed
    SET Mutex_Id=0;
    OPEN cur2;
      t_loop2: LOOP
        FETCH cur2 INTO Mutex_Id;
        IF done=1 THEN
         LEAVE t_loop2;
        END IF;
      END LOOP t_loop2;
    CLOSE cur2;
  END IF;

-- Return the mutex Id
  RETURN Mutex_Id;
END $$

DELIMITER ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

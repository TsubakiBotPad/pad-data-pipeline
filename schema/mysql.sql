-- MySQL dump 10.13  Distrib 5.7.26, for Linux (x86_64)
--
-- Host: localhost    Database: dadguide
-- ------------------------------------------------------
-- Server version	5.7.26-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `awakening`
--

DROP TABLE IF EXISTS `awakening`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awakening` (
  `awakening_id` int(11) NOT NULL AUTO_INCREMENT,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `desc_jp` text NOT NULL,
  `desc_na` text NOT NULL,
  `desc_kr` text NOT NULL,
  `adj_hp` int(11) NOT NULL,
  `adj_atk` int(11) NOT NULL,
  `adj_rcv` int(11) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`awakening_id`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB AUTO_INCREMENT=16463 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `d_attribute`
--

DROP TABLE IF EXISTS `d_attribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `d_attribute` (
  `attribute_id` bigint(20) NOT NULL,
  `name` varchar(30) NOT NULL,
  PRIMARY KEY (`attribute_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `d_condition`
--

DROP TABLE IF EXISTS `d_condition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `d_condition` (
  `condition_type` int(11) NOT NULL,
  `name` text NOT NULL,
  PRIMARY KEY (`condition_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `d_type`
--

DROP TABLE IF EXISTS `d_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `d_type` (
  `name` varchar(29) NOT NULL,
  `tt_seq` bigint(20) NOT NULL,
  PRIMARY KEY (`tt_seq`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dungeon`
--

DROP TABLE IF EXISTS `dungeon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dungeon` (
  `dungeon_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `dungeon_type` int(11) NOT NULL,
  `comment_jp` text,
  `comment_kr` text,
  `comment_na` text,
  `icon_id` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_kr` text NOT NULL,
  `name_us` text NOT NULL,
  `order_idx` int(11) NOT NULL,
  `show_yn` tinyint(1) NOT NULL,
  `tdt_seq` int(11) NOT NULL,
  `tstamp` bigint(20) NOT NULL,
  PRIMARY KEY (`dungeon_id`),
  KEY `tstamp` (`tstamp`),
  KEY `tdt_seq` (`tdt_seq`),
  KEY `icon_seq` (`icon_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1674 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dungeon_monster`
--

DROP TABLE IF EXISTS `dungeon_monster`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dungeon_monster` (
  `dungeon_monster_id` int(11) NOT NULL,
  `dungeon_id` int(11) NOT NULL,
  `dungeon_sublevel_id` int(11) NOT NULL,
  `monster_id` int(11) NOT NULL,
  `floor` int(11) NOT NULL,
  `order_idx` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `turn` int(11) NOT NULL,
  `hp` bigint(20) NOT NULL,
  `atk` int(11) NOT NULL,
  `def` bigint(20) NOT NULL,
  `comment_jp` text,
  `comment_kr` text,
  `comment_us` text,
  `drop_monster_id` int(11) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`dungeon_monster_id`),
  KEY `tstamp` (`tstamp`),
  KEY `tsd_seq` (`dungeon_sublevel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dungeon_monster_drop`
--

DROP TABLE IF EXISTS `dungeon_monster_drop`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dungeon_monster_drop` (
  `monster_no` int(11) NOT NULL,
  `order_idx` bigint(20) NOT NULL,
  `status` bigint(20) NOT NULL,
  `tdmd_seq` bigint(20) NOT NULL AUTO_INCREMENT,
  `tdm_seq` bigint(20) NOT NULL,
  `tstamp` bigint(20) NOT NULL,
  PRIMARY KEY (`tdmd_seq`),
  KEY `tstamp` (`tstamp`),
  KEY `dungeon_monster_drop_list_ibfk_1` (`monster_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dungeon_sublevel`
--

DROP TABLE IF EXISTS `dungeon_sublevel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dungeon_sublevel` (
  `coin_max` int(11) NOT NULL,
  `coin_min` int(11) NOT NULL,
  `dungeon_seq` bigint(20) NOT NULL,
  `exp_max` int(11) NOT NULL,
  `exp_min` int(11) NOT NULL,
  `order_idx` int(11) NOT NULL,
  `stage` int(11) NOT NULL,
  `stamina` bigint(20) NOT NULL,
  `name_jp` varchar(200) DEFAULT NULL,
  `name_kr` varchar(200) NOT NULL,
  `name_us` varchar(200) NOT NULL,
  `tsd_seq` bigint(20) NOT NULL AUTO_INCREMENT,
  `tstamp` bigint(20) NOT NULL,
  PRIMARY KEY (`tsd_seq`),
  KEY `tstamp` (`tstamp`),
  KEY `sub_dungeon_list_ibfk_1` (`dungeon_seq`),
  CONSTRAINT `dungeon_sublevel_ibfk_1` FOREIGN KEY (`dungeon_seq`) REFERENCES `dungeon` (`dungeon_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dungeon_type`
--

DROP TABLE IF EXISTS `dungeon_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dungeon_type` (
  `order_idx` bigint(20) NOT NULL,
  `tdt_name_jp` varchar(29) NOT NULL,
  `tdt_name_kr` varchar(26) NOT NULL,
  `tdt_name_us` varchar(39) NOT NULL,
  `tdt_seq` bigint(20) NOT NULL AUTO_INCREMENT,
  `tstamp` bigint(20) NOT NULL,
  PRIMARY KEY (`tdt_seq`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `evolution`
--

DROP TABLE IF EXISTS `evolution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `evolution` (
  `evolution_id` int(11) NOT NULL,
  `evolution_type` int(11) NOT NULL,
  `from_id` int(11) NOT NULL,
  `to_id` int(11) NOT NULL,
  `mat_1_id` int(11) NOT NULL,
  `mat_2_id` int(11) DEFAULT NULL,
  `mat_3_id` int(11) DEFAULT NULL,
  `mat_4_id` int(11) DEFAULT NULL,
  `mat_5_id` int(11) DEFAULT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`evolution_id`),
  KEY `monster_no` (`from_id`),
  KEY `to_no` (`to_id`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `monster`
--

DROP TABLE IF EXISTS `monster`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monster` (
  `monster_id` bigint(20) NOT NULL,
  `monster_no_jp` int(11) NOT NULL,
  `monster_no_na` int(11) NOT NULL,
  `monster_no_kr` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `pronunciation_jp` text NOT NULL,
  `comment_jp` text,
  `comment_na` text,
  `comment_kr` text,
  `hp_max` int(11) NOT NULL,
  `hp_min` int(11) NOT NULL,
  `hp_scale` float NOT NULL,
  `atk_max` int(11) NOT NULL,
  `atk_min` int(11) NOT NULL,
  `atk_scale` float NOT NULL,
  `rcv_max` int(11) NOT NULL,
  `rcv_min` int(11) NOT NULL,
  `rcv_scale` float NOT NULL,
  `cost` int(11) NOT NULL,
  `exp` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `rarity` int(11) NOT NULL,
  `limit_mult` int(11) DEFAULT NULL,
  `attribute_main` int(11) NOT NULL,
  `attribute_sub` int(11) DEFAULT NULL,
  `leader_skill_id` int(11) DEFAULT NULL,
  `active_skill_id` int(11) DEFAULT NULL,
  `type_1` int(11) NOT NULL,
  `type_2` int(11) DEFAULT NULL,
  `type_3` int(11) DEFAULT NULL,
  `inheritable` tinyint(1) NOT NULL,
  `fodder_exp` int(11) NOT NULL,
  `sell_gold` int(11) NOT NULL,
  `sell_mp` int(11) NOT NULL,
  `buy_mp` int(11) DEFAULT NULL,
  `reg_date` date NOT NULL,
  `on_jp` tinyint(1) NOT NULL,
  `on_na` tinyint(1) NOT NULL,
  `on_kr` tinyint(1) NOT NULL,
  `pal_egg` tinyint(1) NOT NULL,
  `rem_egg` tinyint(1) NOT NULL,
  `series_id` int(11) DEFAULT NULL,
  `name_na_override` text,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`monster_id`),
  KEY `ta_seq` (`attribute_main`),
  KEY `ts_seq_leader` (`leader_skill_id`),
  KEY `ts_seq_skill` (`active_skill_id`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `monster_active_skill`
--

DROP TABLE IF EXISTS `monster_active_skill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monster_active_skill` (
  `active_skill_id` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `desc_jp` text NOT NULL,
  `desc_na` text NOT NULL,
  `desc_kr` text NOT NULL,
  `turn_max` int(11) NOT NULL,
  `turn_min` int(11) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`active_skill_id`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `monster_awakening`
--

DROP TABLE IF EXISTS `monster_awakening`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monster_awakening` (
  `monster_awakening_id` int(11) NOT NULL,
  `monster_id` int(11) NOT NULL,
  `awakening_id` int(11) NOT NULL,
  `is_super` tinyint(1) NOT NULL,
  `order_idx` int(11) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`monster_awakening_id`),
  KEY `monster_no` (`monster_id`),
  KEY `tstamp` (`tstamp`),
  KEY `ma_fk_1_idx` (`awakening_id`),
  CONSTRAINT `ma_fk_1` FOREIGN KEY (`awakening_id`) REFERENCES `awakening` (`awakening_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `monster_leader_skill`
--

DROP TABLE IF EXISTS `monster_leader_skill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monster_leader_skill` (
  `leader_skill_id` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `desc_jp` text NOT NULL,
  `desc_na` text NOT NULL,
  `desc_kr` text NOT NULL,
  `max_hp` float NOT NULL,
  `max_atk` float NOT NULL,
  `max_rcv` float NOT NULL,
  `max_shield` float NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`leader_skill_id`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news`
--

DROP TABLE IF EXISTS `news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `news` (
  `news_id` int(11) NOT NULL,
  `server` varchar(2) NOT NULL,
  `language` text NOT NULL,
  `title` text NOT NULL,
  `url` text NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`news_id`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rank_reward`
--

DROP TABLE IF EXISTS `rank_reward`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rank_reward` (
  `add_cost` int(11) NOT NULL,
  `add_friend` int(11) NOT NULL,
  `add_stamina` int(11) NOT NULL,
  `cost` int(11) NOT NULL,
  `exp` bigint(20) NOT NULL,
  `friend` int(11) NOT NULL,
  `rank` int(11) NOT NULL,
  `stamina` int(11) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`rank`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `schedule`
--

DROP TABLE IF EXISTS `schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `schedule` (
  `close_date` datetime NOT NULL,
  `close_hour` bigint(20) NOT NULL,
  `close_minute` bigint(20) NOT NULL,
  `close_weekday` tinyint(1) NOT NULL,
  `dungeon_seq` bigint(20) NOT NULL,
  `event_seq` bigint(20) NOT NULL,
  `event_type` bigint(20) NOT NULL,
  `open_date` datetime NOT NULL,
  `open_hour` bigint(20) NOT NULL,
  `open_minute` bigint(20) NOT NULL,
  `open_weekday` tinyint(1) NOT NULL,
  `schedule_seq` bigint(20) NOT NULL,
  `server` varchar(22) NOT NULL,
  `server_open_date` datetime NOT NULL,
  `server_open_hour` bigint(20) NOT NULL,
  `team_data` varchar(21) DEFAULT NULL,
  `tstamp` bigint(20) NOT NULL,
  `url` varchar(126) DEFAULT NULL,
  `open_timestamp` bigint(20) NOT NULL,
  `close_timestamp` bigint(20) NOT NULL,
  PRIMARY KEY (`schedule_seq`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `series`
--

DROP TABLE IF EXISTS `series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `series` (
  `series_id` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`series_id`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `skill_condition`
--

DROP TABLE IF EXISTS `skill_condition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `skill_condition` (
  `condition_id` int(11) NOT NULL,
  `condition_type` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_kr` text NOT NULL,
  `name_us` text NOT NULL,
  `order_idx` int(11) NOT NULL,
  `tstamp` bigint(20) NOT NULL,
  PRIMARY KEY (`condition_id`),
  KEY `t_condition` (`condition_id`),
  KEY `fk_skill_condition_1_idx` (`condition_type`),
  CONSTRAINT `fk_skill_condition_1` FOREIGN KEY (`condition_type`) REFERENCES `d_condition` (`condition_type`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `timestamp`
--

DROP TABLE IF EXISTS `timestamp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `timestamp` (
  `name` varchar(40) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`name`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-06-20 22:37:16

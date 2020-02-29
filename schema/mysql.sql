-- MySQL dump 10.13  Distrib 5.7.28, for Linux (x86_64)
--
-- Host: localhost    Database: dadguide
-- ------------------------------------------------------
-- Server version	5.7.28-0ubuntu0.18.04.4

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
-- Table structure for table `active_skill_tags`
--

DROP TABLE IF EXISTS `active_skill_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `active_skill_tags` (
  `active_skill_tag_id` int(11) NOT NULL AUTO_INCREMENT,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `order_idx` int(11) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`active_skill_tag_id`),
  KEY `tstamp_idx` (`tstamp`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `active_skills`
--

DROP TABLE IF EXISTS `active_skills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `active_skills` (
  `active_skill_id` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `desc_jp` text NOT NULL,
  `desc_na` text NOT NULL,
  `desc_kr` text NOT NULL,
  `turn_max` int(11) NOT NULL,
  `turn_min` int(11) NOT NULL,
  `tags` text NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`active_skill_id`),
  KEY `tstamp_idx` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `awakenings`
--

DROP TABLE IF EXISTS `awakenings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awakenings` (
  `awakening_id` int(11) NOT NULL AUTO_INCREMENT,
  `monster_id` int(11) NOT NULL,
  `awoken_skill_id` int(11) NOT NULL,
  `is_super` tinyint(1) NOT NULL,
  `order_idx` int(11) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`awakening_id`),
  KEY `monster_id_idx` (`monster_id`),
  KEY `tstamp_idx` (`tstamp`),
  KEY `awoken_skill_id_idx` (`awoken_skill_id`),
  CONSTRAINT `awakenings_fk_awoken_skill_id` FOREIGN KEY (`awoken_skill_id`) REFERENCES `awoken_skills` (`awoken_skill_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `awakenings_fk_monster_id` FOREIGN KEY (`monster_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=99314 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `awoken_skills`
--

DROP TABLE IF EXISTS `awoken_skills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `awoken_skills` (
  `awoken_skill_id` int(11) NOT NULL AUTO_INCREMENT,
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
  PRIMARY KEY (`awoken_skill_id`),
  KEY `tstamp_idx` (`tstamp`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `d_attributes`
--

DROP TABLE IF EXISTS `d_attributes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `d_attributes` (
  `attribute_id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL,
  PRIMARY KEY (`attribute_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `d_egg_machine_types`
--

DROP TABLE IF EXISTS `d_egg_machine_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `d_egg_machine_types` (
  `egg_machine_type_id` int(11) NOT NULL,
  `name` text NOT NULL,
  PRIMARY KEY (`egg_machine_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `d_event_types`
--

DROP TABLE IF EXISTS `d_event_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `d_event_types` (
  `event_type_id` int(11) NOT NULL,
  `name` text NOT NULL,
  PRIMARY KEY (`event_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `d_servers`
--

DROP TABLE IF EXISTS `d_servers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `d_servers` (
  `server_id` int(11) NOT NULL,
  `name` text NOT NULL,
  PRIMARY KEY (`server_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `d_types`
--

DROP TABLE IF EXISTS `d_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `d_types` (
  `type_id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  PRIMARY KEY (`type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deleted_rows`
--

DROP TABLE IF EXISTS `deleted_rows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deleted_rows` (
  `deleted_row_id` int(11) NOT NULL AUTO_INCREMENT,
  `table_name` text NOT NULL,
  `table_row_id` int(11) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`deleted_row_id`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `drops`
--

DROP TABLE IF EXISTS `drops`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `drops` (
  `drop_id` int(11) NOT NULL AUTO_INCREMENT,
  `encounter_id` int(11) NOT NULL,
  `monster_id` int(11) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`drop_id`),
  KEY `tstamp` (`tstamp`),
  KEY `dungeon_monster_drop_list_ibfk_1` (`encounter_id`),
  KEY `monster_id` (`monster_id`),
  CONSTRAINT `drops_fk_encounter_id` FOREIGN KEY (`encounter_id`) REFERENCES `encounters` (`encounter_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `drops_fk_monster_id` FOREIGN KEY (`monster_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=34891 DEFAULT CHARSET=utf8;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dungeons`
--

DROP TABLE IF EXISTS `dungeons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dungeons` (
  `dungeon_id` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `dungeon_type` int(11) NOT NULL,
  `series_id` int(11) DEFAULT NULL,
  `icon_id` int(11) DEFAULT NULL,
  `reward_jp` text,
  `reward_kr` text,
  `reward_na` text,
  `reward_icon_ids` text,
  `visible` tinyint(1) NOT NULL,
  `tstamp` bigint(20) NOT NULL,
  PRIMARY KEY (`dungeon_id`),
  KEY `tstamp` (`tstamp`),
  KEY `tdt_seq` (`series_id`),
  KEY `icon_seq` (`icon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `egg_machines`
--

DROP TABLE IF EXISTS `egg_machines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `egg_machines` (
  `egg_machine_id` int(11) NOT NULL AUTO_INCREMENT,
  `server_id` int(11) NOT NULL,
  `egg_machine_type_id` int(11) NOT NULL,
  `start_timestamp` int(11) NOT NULL,
  `end_timestamp` int(11) NOT NULL,
  `machine_row` int(11) NOT NULL,
  `machine_type` int(11) NOT NULL,
  `name` text NOT NULL,
  `cost` int(11) NOT NULL,
  `contents` text NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`egg_machine_id`),
  UNIQUE KEY `server_id` (`server_id`,`machine_row`,`machine_type`),
  KEY `tstamp` (`tstamp`),
  KEY `egg_machine_type_id` (`egg_machine_type_id`),
  CONSTRAINT `egg_machine_fk_server_id` FOREIGN KEY (`server_id`) REFERENCES `d_servers` (`server_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `egg_machines_ibfk_1` FOREIGN KEY (`egg_machine_type_id`) REFERENCES `d_egg_machine_types` (`egg_machine_type_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `encounters`
--

DROP TABLE IF EXISTS `encounters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `encounters` (
  `encounter_id` int(11) NOT NULL AUTO_INCREMENT,
  `dungeon_id` int(11) NOT NULL,
  `sub_dungeon_id` int(11) NOT NULL,
  `enemy_id` int(11) DEFAULT NULL,
  `monster_id` int(11) NOT NULL,
  `stage` int(11) NOT NULL,
  `comment_jp` text,
  `comment_na` text,
  `comment_kr` text,
  `amount` int(11) DEFAULT NULL,
  `order_idx` int(11) NOT NULL,
  `turns` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `hp` bigint(20) NOT NULL,
  `atk` bigint(20) NOT NULL,
  `defence` bigint(20) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`encounter_id`),
  KEY `tstamp` (`tstamp`),
  KEY `tsd_seq` (`sub_dungeon_id`),
  KEY `fk_dungeon_id_idx` (`dungeon_id`),
  KEY `fk_monster_id_idx` (`monster_id`),
  CONSTRAINT `encounters_fk_dungeon_id` FOREIGN KEY (`dungeon_id`) REFERENCES `dungeons` (`dungeon_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `encounters_fk_monster_id` FOREIGN KEY (`monster_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `encounters_fk_sub_dungeon_id` FOREIGN KEY (`sub_dungeon_id`) REFERENCES `sub_dungeons` (`sub_dungeon_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=75048 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `enemy_data`
--

DROP TABLE IF EXISTS `enemy_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `enemy_data` (
  `enemy_id` int(11) NOT NULL,
  `behavior` blob NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`enemy_id`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `enemy_skills`
--

DROP TABLE IF EXISTS `enemy_skills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `enemy_skills` (
  `enemy_skill_id` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `desc_jp` text NOT NULL,
  `desc_na` text NOT NULL,
  `desc_kr` text NOT NULL,
  `min_hits` int(11) NOT NULL,
  `max_hits` int(11) NOT NULL,
  `atk_mult` int(11) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`enemy_skill_id`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `evolutions`
--

DROP TABLE IF EXISTS `evolutions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `evolutions` (
  `evolution_id` int(11) NOT NULL AUTO_INCREMENT,
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
  KEY `from_id_idx` (`from_id`),
  KEY `to_id_idx` (`to_id`),
  KEY `mat_1_id_idx` (`mat_1_id`),
  KEY `mat_2_id_idx` (`mat_2_id`),
  KEY `mat_3_id_idx` (`mat_3_id`),
  KEY `mat_4_id_idx` (`mat_4_id`),
  KEY `mat_5_id_idx` (`mat_5_id`),
  KEY `tstamp_idx` (`tstamp`),
  CONSTRAINT `evolutions_fk_from_id` FOREIGN KEY (`from_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `evolutions_fk_mat_1_id` FOREIGN KEY (`mat_1_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `evolutions_fk_mat_2_id` FOREIGN KEY (`mat_2_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `evolutions_fk_mat_3_id` FOREIGN KEY (`mat_3_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `evolutions_fk_mat_4_id` FOREIGN KEY (`mat_4_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `evolutions_fk_mat_5_id` FOREIGN KEY (`mat_5_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `evolutions_fk_to_id` FOREIGN KEY (`to_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=30555 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `exchanges`
--

DROP TABLE IF EXISTS `exchanges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `exchanges` (
  `exchange_id` int(11) NOT NULL AUTO_INCREMENT,
  `trade_id` int(11) NOT NULL,
  `server_id` int(11) NOT NULL,
  `target_monster_id` int(11) NOT NULL,
  `required_monster_ids` text NOT NULL,
  `required_count` tinyint(1) NOT NULL,
  `start_timestamp` int(11) NOT NULL,
  `end_timestamp` int(11) NOT NULL,
  `permanent` tinyint(1) NOT NULL DEFAULT '0',
  `menu_idx` tinyint(1) NOT NULL,
  `order_idx` int(11) NOT NULL,
  `flags` tinyint(1) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`exchange_id`),
  UNIQUE KEY `trade_id` (`trade_id`,`server_id`),
  KEY `tstamp` (`tstamp`),
  KEY `exchanges_fk_server_id` (`server_id`),
  KEY `exchanges_fk_target_monster_id` (`target_monster_id`),
  CONSTRAINT `exchanges_fk_server_id` FOREIGN KEY (`server_id`) REFERENCES `d_servers` (`server_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `exchanges_fk_target_monster_id` FOREIGN KEY (`target_monster_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=754 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `purchases`
--

DROP TABLE IF EXISTS `purchases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `purchases` (
  `server_id` int(11) NOT NULL,
  `target_monster_id` int(11) NOT NULL,
  `mp_cost` tinyint(1) NOT NULL,
  `start_timestamp` int(11) NOT NULL,
  `end_timestamp` int(11) NOT NULL,
  `permanent` tinyint(1) NOT NULL DEFAULT '0',
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`purchase_id`),
  KEY `tstamp` (`tstamp`),
  KEY `purchases_fk_server_id` (`server_id`),
  KEY `purchases_fk_target_monster_id` (`target_monster_id`),
  CONSTRAINT `purchases_fk_server_id` FOREIGN KEY (`server_id`) REFERENCES `d_servers` (`server_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `purchases_fk_target_monster_id` FOREIGN KEY (`target_monster_id`) REFERENCES `monsters` (`monster_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=754 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `leader_skill_tags`
--

DROP TABLE IF EXISTS `leader_skill_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `leader_skill_tags` (
  `leader_skill_tag_id` int(11) NOT NULL AUTO_INCREMENT,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `order_idx` int(11) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`leader_skill_tag_id`),
  KEY `tstamp_idx` (`tstamp`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `leader_skills`
--

DROP TABLE IF EXISTS `leader_skills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `leader_skills` (
  `leader_skill_id` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `desc_jp` text NOT NULL,
  `desc_na` text NOT NULL,
  `desc_kr` text NOT NULL,
  `max_hp` decimal(8,2) NOT NULL,
  `max_atk` decimal(8,2) NOT NULL,
  `max_rcv` decimal(8,2) NOT NULL,
  `max_shield` decimal(8,2) NOT NULL,
  `tags` text NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`leader_skill_id`),
  KEY `tstamp` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `monsters`
--

DROP TABLE IF EXISTS `monsters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monsters` (
  `monster_id` int(11) NOT NULL,
  `monster_no_jp` int(11) NOT NULL,
  `monster_no_na` int(11) NOT NULL,
  `monster_no_kr` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `pronunciation_jp` text NOT NULL,
  `hp_max` int(11) NOT NULL,
  `hp_min` int(11) NOT NULL,
  `hp_scale` decimal(5,2) NOT NULL,
  `atk_max` int(11) NOT NULL,
  `atk_min` int(11) NOT NULL,
  `atk_scale` decimal(5,2) NOT NULL,
  `rcv_max` int(11) NOT NULL,
  `rcv_min` int(11) NOT NULL,
  `rcv_scale` decimal(5,2) NOT NULL,
  `cost` int(11) NOT NULL,
  `exp` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `rarity` int(11) NOT NULL,
  `limit_mult` int(11) DEFAULT NULL,
  `attribute_1_id` int(11) NOT NULL,
  `attribute_2_id` int(11) DEFAULT NULL,
  `leader_skill_id` int(11) DEFAULT NULL,
  `active_skill_id` int(11) DEFAULT NULL,
  `type_1_id` int(11) NOT NULL,
  `type_2_id` int(11) DEFAULT NULL,
  `type_3_id` int(11) DEFAULT NULL,
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
  `series_id` int(11) NOT NULL,
  `has_animation` tinyint(1) NOT NULL DEFAULT '0',
  `has_hqimage` tinyint(1) NOT NULL DEFAULT '0',
  `orb_skin_id` int(11) DEFAULT NULL,
  `voice_id_jp` int(11) DEFAULT NULL,
  `voice_id_na` int(11) DEFAULT NULL,
  `name_na_override` text,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`monster_id`),
  KEY `attribute_1_idx` (`attribute_1_id`),
  KEY `attribute_2_idx` (`attribute_2_id`),
  KEY `type_1_id_idx` (`type_1_id`),
  KEY `type_2_id_idx` (`type_2_id`),
  KEY `tstamp_idx` (`tstamp`),
  KEY `type_3_id_idx` (`type_3_id`),
  CONSTRAINT `monsters_fk_attribute_1_id` FOREIGN KEY (`attribute_1_id`) REFERENCES `d_attributes` (`attribute_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `monsters_fk_attribute_2_id` FOREIGN KEY (`attribute_2_id`) REFERENCES `d_attributes` (`attribute_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `monsters_fk_type_1_id` FOREIGN KEY (`type_1_id`) REFERENCES `d_types` (`type_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `monsters_fk_type_2_id` FOREIGN KEY (`type_2_id`) REFERENCES `d_types` (`type_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `monsters_fk_type_3_id` FOREIGN KEY (`type_3_id`) REFERENCES `d_types` (`type_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
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
-- Table structure for table `rank_rewards`
--

DROP TABLE IF EXISTS `rank_rewards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rank_rewards` (
  `rank` int(11) NOT NULL,
  `exp` bigint(20) NOT NULL,
  `add_cost` int(11) NOT NULL,
  `add_friend` int(11) NOT NULL,
  `add_stamina` int(11) NOT NULL,
  `cost` int(11) NOT NULL,
  `friend` int(11) NOT NULL,
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
  `event_id` int(11) NOT NULL AUTO_INCREMENT,
  `server_id` int(11) NOT NULL,
  `event_type_id` int(11) NOT NULL,
  `start_timestamp` int(11) NOT NULL,
  `end_timestamp` int(11) NOT NULL,
  `icon_id` int(11) DEFAULT NULL,
  `group_name` text,
  `dungeon_id` int(11) DEFAULT NULL,
  `url` text,
  `info_jp` text,
  `info_na` text,
  `info_kr` text,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`event_id`),
  KEY `tstamp_idx` (`tstamp`),
  KEY `server_id_idx` (`server_id`),
  KEY `event_type_id_idx` (`event_type_id`),
  KEY `dungeon_id_idx` (`dungeon_id`),
  CONSTRAINT `schedule_fk_dungeon_id` FOREIGN KEY (`dungeon_id`) REFERENCES `dungeons` (`dungeon_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `schedule_fk_event_type_id` FOREIGN KEY (`event_type_id`) REFERENCES `d_event_types` (`event_type_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `schedule_fk_server_id` FOREIGN KEY (`server_id`) REFERENCES `d_servers` (`server_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=13046 DEFAULT CHARSET=utf8;
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
  KEY `t_condition` (`condition_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sub_dungeons`
--

DROP TABLE IF EXISTS `sub_dungeons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sub_dungeons` (
  `sub_dungeon_id` int(11) NOT NULL,
  `dungeon_id` int(11) NOT NULL,
  `name_jp` text NOT NULL,
  `name_na` text NOT NULL,
  `name_kr` text NOT NULL,
  `reward_jp` text,
  `reward_na` text,
  `reward_kr` text,
  `reward_icon_ids` text,
  `coin_max` int(11) DEFAULT NULL,
  `coin_min` int(11) DEFAULT NULL,
  `coin_avg` int(11) DEFAULT NULL,
  `exp_max` int(11) DEFAULT NULL,
  `exp_min` int(11) DEFAULT NULL,
  `exp_avg` int(11) DEFAULT NULL,
  `mp_avg` int(11) DEFAULT NULL,
  `icon_id` int(11) DEFAULT NULL,
  `floors` int(11) NOT NULL,
  `stamina` int(11) NOT NULL,
  `hp_mult` decimal(8,4) NOT NULL,
  `atk_mult` decimal(8,4) NOT NULL,
  `def_mult` decimal(8,4) NOT NULL,
  `s_rank` int(11) DEFAULT NULL,
  `rewards` text,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`sub_dungeon_id`),
  KEY `tstamp_idx` (`tstamp`),
  KEY `dungeon_id_idx` (`dungeon_id`),
  CONSTRAINT `subdungeon_fk_dungeon_id` FOREIGN KEY (`dungeon_id`) REFERENCES `dungeons` (`dungeon_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `timestamps`
--

DROP TABLE IF EXISTS `timestamps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `timestamps` (
  `name` varchar(40) NOT NULL,
  `tstamp` int(11) NOT NULL,
  PRIMARY KEY (`name`),
  KEY `tstamp_idx` (`tstamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wave_data`
--

DROP TABLE IF EXISTS `wave_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wave_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server` varchar(2) NOT NULL,
  `dungeon_id` int(11) NOT NULL,
  `floor_id` int(11) NOT NULL,
  `stage` int(11) NOT NULL,
  `slot` int(11) NOT NULL,
  `spawn_type` int(11) NOT NULL,
  `monster_id` int(11) NOT NULL,
  `monster_level` int(11) NOT NULL,
  `drop_monster_id` int(11) NOT NULL,
  `drop_monster_level` int(11) NOT NULL,
  `plus_amount` int(11) NOT NULL,
  `pull_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `pull_id` int(11) NOT NULL,
  `entry_id` int(11) NOT NULL,
  `leader_id` int(11) DEFAULT NULL,
  `friend_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `dungeon_id` (`dungeon_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1446304 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-12-01 23:32:06

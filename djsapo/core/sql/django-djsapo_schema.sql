-- Scroll down to about line 80 to see the table definitions for those that
-- related to the Student Outreach System.

SET NAMES utf8;
SET time_zone = '+00:00';

CREATE DATABASE `django_djsapo` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;
USE `django_djsapo`;

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8_unicode_ci NOT NULL,
  `first_name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


--
-- Here are the table definitions for the data models unique to the
-- Student Outreach System.
--
-- Wherever you see a field name that ends with _id, that indicates that it is
-- a foreign key field. When you see a table name that corresponds to another
-- but has a suffix like _category, that is an indication that there is a
-- ManyToMany relionship. core_alert is the Alert() data model, and
-- core_alert_category corresponds to the category field in the Alert() data
-- model. So an alert can have any number of categories associated with it.
-- In core_alert_category, there are two foreign key fields: one for the Alert
-- and one for the GenericChoice model (which is what categories are in this
-- schema).

-- Any field that is a tinyint(1) means that it is a Boolean type.
--
-- Note: parent_id is a foreign key to the alert table itself, which is a simple
-- way of setting up a parent/child relationship. This will allow us to merge an
-- alert into a "Parent" grouping, which was a feature in the original
-- Requirements document.

CREATE TABLE `core_alert` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `relationship` varchar(24) COLLATE utf8_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8_unicode_ci NOT NULL,
  `course` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `interaction` varchar(4) COLLATE utf8_unicode_ci NOT NULL,
  `outcome` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_by_id` int(11) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `student_id` int(11) NOT NULL,
  `updated_by_id` int(11) DEFAULT NULL,
  `interaction_date` date DEFAULT NULL,
  `interaction_details` longtext COLLATE utf8_unicode_ci,
  `interaction_type` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `status` varchar(128) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_alert_parent_id_81e19559_fk_core_alert_id` (`parent_id`),
  KEY `core_alert_created_by_id_b591c86b_fk_auth_user_id` (`created_by_id`),
  KEY `core_alert_updated_by_id_00b0727f_fk_auth_user_id` (`updated_by_id`),
  KEY `core_alert_student_id_e3eacf45_fk_auth_user_id` (`student_id`),
  CONSTRAINT `core_alert_created_by_id_b591c86b_fk_auth_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `core_alert_parent_id_81e19559_fk_core_alert_id` FOREIGN KEY (`parent_id`) REFERENCES `core_alert` (`id`),
  CONSTRAINT `core_alert_student_id_e3eacf45_fk_auth_user_id` FOREIGN KEY (`student_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `core_alert_updated_by_id_00b0727f_fk_auth_user_id` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- ManytoMany table for the Alert data model which has a category field that
-- is M2M to the GenericChoice data model.
--

CREATE TABLE `core_alert_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `alert_id` int(11) NOT NULL,
  `genericchoice_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_alert_category_alert_id_genericchoice_id_1263b4e3_uniq` (`alert_id`,`genericchoice_id`),
  KEY `core_alert_category_genericchoice_id_98419195_fk_core_gene` (`genericchoice_id`),
  CONSTRAINT `core_alert_category_alert_id_b71c7788_fk_core_alert_id` FOREIGN KEY (`alert_id`) REFERENCES `core_alert` (`id`),
  CONSTRAINT `core_alert_category_genericchoice_id_98419195_fk_core_gene` FOREIGN KEY (`genericchoice_id`) REFERENCES `core_genericchoice` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Annotation() data model correspond to comments (what we are now calling
-- "Follow-up"), notes, or email content.
--

CREATE TABLE `core_annotation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `body` longtext COLLATE utf8_unicode_ci NOT NULL,
  `status` tinyint(1) NOT NULL,
  `alert_id` int(11) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_annotation_alert_id_757f817c_fk_core_alert_id` (`alert_id`),
  KEY `core_annotation_created_by_id_46a3b903_fk_auth_user_id` (`created_by_id`),
  CONSTRAINT `core_annotation_alert_id_757f817c_fk_core_alert_id` FOREIGN KEY (`alert_id`) REFERENCES `core_alert` (`id`),
  CONSTRAINT `core_annotation_created_by_id_46a3b903_fk_auth_user_id` FOREIGN KEY (`created_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Recipients are the folks who received an email that was sent from the app.
--

CREATE TABLE `core_annotation_recipients` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `annotation_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_annotation_recipients_annotation_id_user_id_8417e1df_uniq` (`annotation_id`,`user_id`),
  KEY `core_annotation_recipients_user_id_77dfe5cb_fk_auth_user_id` (`user_id`),
  CONSTRAINT `core_annotation_reci_annotation_id_5e50d921_fk_core_anno` FOREIGN KEY (`annotation_id`) REFERENCES `core_annotation` (`id`),
  CONSTRAINT `core_annotation_recipients_user_id_77dfe5cb_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- files uploaded for any given Alert.
--

CREATE TABLE `core_document` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `name` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `phile` varchar(767) COLLATE utf8_unicode_ci DEFAULT NULL,
  `alert_id` int(11) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `updated_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `core_document_created_by_id_27ee15cc_fk_core_member_id` (`created_by_id`),
  KEY `core_document_alert_id_dee1c644_fk_core_alert_id` (`alert_id`),
  KEY `core_document_updated_by_id_8dadd68d_fk_auth_user_id` (`updated_by_id`),
  CONSTRAINT `core_document_alert_id_dee1c644_fk_core_alert_id` FOREIGN KEY (`alert_id`) REFERENCES `core_alert` (`id`),
  CONSTRAINT `core_document_updated_by_id_8dadd68d_fk_auth_user_id` FOREIGN KEY (`updated_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- rank allows us to order the display of the GenericChoice elements instead of
-- alphabetically, like when they want the "Other" option to be listed last in
-- a multiple select field.
--

CREATE TABLE `core_genericchoice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `value` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `rank` int(11) DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `admin` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `value` (`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- ManytoMany table for the GenericChoice data model which has a group field that
-- is M2M to the Group data model.
--

CREATE TABLE `core_genericchoice_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `genericchoice_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_genericchoice_group_genericchoice_id_group_id_358717f4_uniq` (`genericchoice_id`,`group_id`),
  KEY `core_genericchoice_group_group_id_902366d2_fk_auth_group_id` (`group_id`),
  CONSTRAINT `core_genericchoice_g_genericchoice_id_ab36b6ee_fk_core_gene` FOREIGN KEY (`genericchoice_id`) REFERENCES `core_genericchoice` (`id`),
  CONSTRAINT `core_genericchoice_group_group_id_902366d2_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Alert Team members.
--

CREATE TABLE `core_member` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` tinyint(1) NOT NULL,
  `case_manager` tinyint(1) NOT NULL,
  `alert_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_member_user_id_alert_id_f4cc7f0b_uniq` (`user_id`,`alert_id`),
  KEY `core_member_alert_id_4fb83004_fk_core_alert_id` (`alert_id`),
  CONSTRAINT `core_member_alert_id_4fb83004_fk_core_alert_id` FOREIGN KEY (`alert_id`) REFERENCES `core_alert` (`id`),
  CONSTRAINT `core_member_user_id_cc03c6cf_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Message content for automated emails. Since the number of automatic emails
-- have been reduced over the scope of the project, this data model might be
-- irrelvant.
--

CREATE TABLE `core_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `body` longtext COLLATE utf8_unicode_ci NOT NULL,
  `status` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- We use the profile model to link users with "Types of Concerns" so that we
-- can generate the support matrix of folks who might become team members based
-- on the Types of Concern that the submitter chose.
--

CREATE TABLE `core_profile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `core_profile_user_id_bf8ada58_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- ManytoMany table for the Profile data model that has a category field that
-- is M2M to the GenericChoice data model.
--

CREATE TABLE `core_profile_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `profile_id` int(11) NOT NULL,
  `genericchoice_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_profile_category_profile_id_genericchoice_id_23948a5f_uniq` (`profile_id`,`genericchoice_id`),
  KEY `core_profile_categor_genericchoice_id_101dca5e_fk_core_gene` (`genericchoice_id`),
  CONSTRAINT `core_profile_categor_genericchoice_id_101dca5e_fk_core_gene` FOREIGN KEY (`genericchoice_id`) REFERENCES `core_genericchoice` (`id`),
  CONSTRAINT `core_profile_category_profile_id_e63f975d_fk_core_profile_id` FOREIGN KEY (`profile_id`) REFERENCES `core_profile` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- End schema specific to the Student Outreach System
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext COLLATE utf8_unicode_ci NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_site_domain_a2e37b91_uniq` (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `taggit_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `slug` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `taggit_taggeditem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `object_id` int(11) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `taggit_taggeditem_content_type_id_object_id_tag_id_4bb97a8e_uniq` (`content_type_id`,`object_id`,`tag_id`),
  KEY `taggit_taggeditem_tag_id_f4f5b767_fk_taggit_tag_id` (`tag_id`),
  KEY `taggit_taggeditem_object_id_e2d7d1df` (`object_id`),
  KEY `taggit_taggeditem_content_type_id_object_id_196cc965_idx` (`content_type_id`,`object_id`),
  CONSTRAINT `taggit_taggeditem_content_type_id_9957a03c_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `taggit_taggeditem_tag_id_f4f5b767_fk_taggit_tag_id` FOREIGN KEY (`tag_id`) REFERENCES `taggit_tag` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

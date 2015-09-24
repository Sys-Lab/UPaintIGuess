drop database if exists xiaoyu;

create database xiaoyu;

use xiaoyu;

create table user (
    `uid` INT(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `phonenum` varchar(32) not null,
    `password` varchar(32) not null,
    `permission` tinyint(1),
    `online` tinyint(2), # Login status: Online, offline, hide to friends, hide to strangers, hide to all
    `created_at` real,
    `last_login` real
) engine=innodb default charset=utf8;

create table user_school (
    `uid` int(10) not null primary key,
    `school_name` text,
    `degree` int(9),
    `school_id` int(10),
    `school_province` int(10),
    `school_city` int(10),
    `auth_photo` text,
    `pass` boolean 
) engine=innodb default charset=utf8;

create table user_meta (
    `uid` int(10) not null primary key,
    `nickname` varchar(32),
    `realname` varchar(32),
    `gender` tinyint(2),
    `age` tinyint(3),
    `height` real,
    `birthday` real,
    `horoscope` tinyint(3),
    `hometown_province` int(9), 
    `hometown_city` int(9),
    `hometown_addr` text,
    `workplace_province` int(9),
    `workplace_city` int(9),
    `workplace_addr` text,
    `contact` text,
    `motto` text,
	`show_name` boolean,
	`show_contact` boolean
) engine=innodb default charset=utf8;

create table user_ext (
    `uid` int(10) not null primary key,
    `content` text  # JSON key-value data
) engine=innodb default charset=utf8;

create table wall (
    `uid` int(10) not null primary key,
    `photos` text, # JSON array
    `upvotes` int(10),
    `filter` text
);

create table photos (
    `id` int(10) not null primary key auto_increment,
    `user` int(10) not null,
    `url` text,
    `desc` text,
    `created_at` real,
) engine=innodb default charset=utf8;

create table tweets (
    `id` int(10) not null primary key auto_increment,
    `user` int(10) not null,
    `content` text,
    `visibility` tinyint(2),
    `created_at` real,
) engine=innodb default charset=utf8;

create table replies (
    `id` int(10) not null primary key auto_increment,
    `user` int(10) not null,
    `target` int(10) not null,
    `content` text,
    `visibility` tinyint(2),
    `created_at` real
) engine=innodb default charset=utf8;

create table messages (
    `id` int(10) not null primary key auto_increment,
    `user` int(10) not null,
    `target` int(10) not null,
    `content` text,
    `visibility` tinyint(2),
    `created_at` real
) engine=innodb default charset=utf8;
    
create table friends (
    `id` int(10) not null primary key auto_increment,
    `user` int(10) not null,
    `to` int(10) not null,
    `group` tinyint(2),
    `agree` tinyint(2),
) engine=innodb default charset=utf8;

create table friend_group (
    `user` int(10) not null primary key,
    `content` text  # A json array.
) engine=innodb default charset=utf8;

create table blacklist (
    `id` int(10) not null primary key auto_increment,
    `user` int(10) not null,
    `to` int(10) not null
) engine=innodb default charset=utf8;

create table notification (
    `id` int(10) not null primary key auto_increment,
    `from` int(10) not null,
    `to` int(10) not null,
    `content` text,
    `created_at` real
) engine=innodb default charse=utf8;

create table abuse_report (
    `id` int(10) not null primary key auto_increment,
    `from` int(10) not null,
    `target` int(10) not null,
    `content` text,
    `created_at` real
) engine=innodb default charset=utf8;

create table license (
    `id` int(9) not null primary key auto_increment,
    `content` text
) engine=innodb default charset=utf8;

create table horoscope (
    `id` int(9) not null primary key auto_increment,
    `name` text,
    `desc` text
) engine=innodb default charset=utf8;

create table province (
    `id` int(9) not null primary key auto_increment,
    `name` text
) engine=innodb default charset=utf8;

create table city (
    `id` int(9) not null primary key auto_increment,
    `province` int(9) not null,
    `name` text
) engine=innodb default charset=utf8;

create table schools (
    `id` int(9) not null primary key auto_increment,
    `name` text
) engine=innodb default charset=utf8;

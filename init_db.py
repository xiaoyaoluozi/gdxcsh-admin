#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = '/var/www/gdxcsh-admin/data/admin.db'

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 新闻表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT,
            content TEXT,
            category TEXT DEFAULT '商会动态',
            image_url TEXT,
            link_url TEXT,
            publish_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 活动表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            location TEXT,
            start_time TEXT,
            end_time TEXT,
            organizer TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 会员企业表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT,
            contact_person TEXT,
            phone TEXT,
            address TEXT,
            description TEXT,
            member_level TEXT DEFAULT '普通会员',
            join_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 入会申请表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            applicant_name TEXT NOT NULL,
            position TEXT,
            phone TEXT NOT NULL,
            city TEXT,
            industry TEXT,
            intro TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TEXT,
            reviewed_by TEXT
        )
    ''')
    
    # 插入示例数据
    cursor.execute('''
        INSERT OR IGNORE INTO news (title, summary, category, publish_date) VALUES
        ('第三届三次常务理事会会议：务实高效，引领商会新发展', '会议讨论激烈，务实高效，为商会未来的发展指明了方向', '商会动态', '2025-09-23'),
        ('广东宣城商会双节活动：情暖他乡，共筑团圆梦', '掼蛋联谊，情系桑梓。二十多位东莞片区的成员和乡友们齐聚一堂', '活动报道', '2025-10-09'),
        ('广东宣城商会成立两周年庆典暨春茗会隆重举行', '近 500 余人共同见证了此次盛典', '商会动态', '2019-03-16')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO events (title, description, location, start_time, organizer, status) VALUES
        ('敬老院慰问关怀活动', '公益委组织慰问旌德、绩溪两县敬老院', '旌德、绩溪两县敬老院', '2026-09-24 09:00', '公益委', 'upcoming'),
        ('广东名医专家宣城义诊活动', '8 名医学教授为期一周的义诊', '宣城市中心医院', '2026-10-24 09:00', '商会', 'upcoming'),
        ('掼蛋联谊活动', '每月一期，会员自由参与', '东莞/广州/深圳', '2026-10-01 14:00', '联谊会', 'upcoming')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO companies (name, industry, contact_person, member_level) VALUES
        ('深圳市筑福环保科技', '制造业', '朱财福', '常务副会长'),
        ('粤宣投资集团', '金融业', '执行会长', '执行会长'),
        ('华南商贸集团', '商贸业', '刘团结', '副会长'),
        ('芯丰园老字号', '商贸业', '刘团结', '会员')
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")
    print(f"📁 数据库位置：{DB_PATH}")

if __name__ == '__main__':
    init_db()

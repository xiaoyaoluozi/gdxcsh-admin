#!/usr/bin/env python3
"""
数据库迁移脚本 - 更新会员企业表结构
"""
import sqlite3, os

DB_PATH = '/var/www/gdxcsh-admin/data/admin.db'

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 添加新字段
    fields = [
        ('member_no', 'TEXT'),
        ('company_name', 'TEXT'),
        ('chamber_position', 'TEXT'),
        ('name', 'TEXT'),
        ('company_position', 'TEXT'),
        ('shenzhen_district', 'TEXT'),
        ('jiguang', 'TEXT')
    ]
    
    for field_name, field_type in fields:
        try:
            c.execute(f'ALTER TABLE companies ADD COLUMN {field_name} {field_type}')
            print(f'✅ 添加字段：{field_name}')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print(f'⚠️  字段已存在：{field_name}')
            else:
                raise
    
    # 迁移旧数据到新字段
    c.execute('''UPDATE companies SET 
        company_name = name,
        name = contact_person,
        industry = industry,
        member_level = member_level
        WHERE company_name IS NULL''')
    
    conn.commit()
    conn.close()
    print('✅ 数据库迁移完成')

if __name__ == '__main__':
    migrate()

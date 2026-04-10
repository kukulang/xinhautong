# 儿童小主持教培业务系统

> 新华童 · 童声飞扬 —— 面向少儿小主持人培训机构的全业务闭环管理系统

## 业务模块

| 模块 | 功能 |
| --- | --- |
| 工作台 | 实时业务数据看板,含收入、学员、趋势图、等级分布 |
| 学员管理 | 学员档案、家长信息、等级、入学状态的完整 CRUD |
| 教师管理 | 教师档案、职称、擅长领域、在职状态管理 |
| 课程管理 | 启蒙/初级/中级/高级/金牌级五级课程体系维护 |
| 班级管理 | 开班、师资配置、学员报名(多学员加入) |
| 排课中心 | 按班级排课,支持日期筛选 |
| 考勤点评 | 基于课次的出勤、迟到、请假、课堂表现打分与点评 |
| 订单学费 | 学费订单、收款、退款、多种支付方式 |
| 考级证书 | 小主持等级考试报考、成绩、证书编号管理(通过自动升级学员等级) |
| 演出活动 | 汇报演出、比赛、公益活动管理 |

## 技术栈

- **后端**: Python + Flask 3 + Flask-SQLAlchemy
- **数据库**: SQLite(开箱即用)
- **前端**: Jinja2 + Bootstrap 5 + Bootstrap Icons + ECharts
- **架构**: 前后端同源,RESTful API(`/api/*`) + 服务端模板

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库(含示例数据)
python init_db.py

# 3. 启动服务
python app.py
```

浏览器访问 http://127.0.0.1:5000

## 目录结构

```
xinhautong/
├── app.py              # Flask 应用入口 + 所有 API 路由
├── models.py           # 数据模型 (10 张表)
├── config.py           # 配置
├── init_db.py          # 初始化 + 示例数据
├── requirements.txt
├── templates/          # 页面模板
│   ├── base.html       # 布局(侧边栏 + 顶栏)
│   ├── dashboard.html  # 工作台
│   ├── students.html
│   ├── teachers.html
│   ├── courses.html
│   ├── classes.html
│   ├── schedules.html
│   ├── attendance.html
│   ├── orders.html
│   ├── grading.html
│   └── performances.html
└── static/
    ├── css/style.css
    └── js/app.js       # fetch 封装 + Toast 工具
```

## 数据模型概览

- `Student` 学员  |  `Teacher` 教师  |  `Course` 课程
- `ClassGroup` 班级  ←→  `Enrollment` 学员-班级
- `Schedule` 排课  ←→  `Attendance` 考勤
- `Order` 订单
- `GradingExam` 考级记录
- `Performance` 演出活动

## 主要 API

```
GET  /api/dashboard/stats         工作台数据
GET/POST/PUT/DELETE /api/students        学员
GET/POST/PUT/DELETE /api/teachers        教师
GET/POST/PUT/DELETE /api/courses         课程
GET/POST/PUT/DELETE /api/classes         班级
POST /api/classes/<id>/students          班级添加学员
GET/POST/PUT/DELETE /api/schedules       排课
GET  /api/schedules/<id>/attendance      获取考勤
POST /api/schedules/<id>/attendance      保存考勤
GET/POST/DELETE /api/orders              订单
POST /api/orders/<id>/pay                收款
POST /api/orders/<id>/refund             退款
GET/POST/PUT/DELETE /api/exams           考级
GET/POST/PUT/DELETE /api/performances    演出
```

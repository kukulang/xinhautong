"""初始化数据库 + 灌入示例数据"""
from datetime import date, datetime, timedelta
import random

from app import app
from models import (
    db, Student, Teacher, Course, ClassGroup, Enrollment,
    Schedule, Attendance, Order, GradingExam, Performance,
    TrialClass, TrialEnrollment,
)


def run():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # 教师
        teachers = [
            Teacher(name="李语嫣", gender="女", phone="13800010001", title="金牌讲师",
                    specialty="播音主持、舞台表演", intro="央视少儿特邀导师,从业10年"),
            Teacher(name="王梓涵", gender="女", phone="13800010002", title="高级讲师",
                    specialty="气息训练、绕口令", intro="国家一级播音员"),
            Teacher(name="陈启明", gender="男", phone="13800010003", title="中级讲师",
                    specialty="即兴口语、新闻播报", intro="电台主持人出身"),
            Teacher(name="赵雨欣", gender="女", phone="13800010004", title="初级讲师",
                    specialty="启蒙发声、儿歌朗诵", intro="幼儿教育专业"),
        ]
        db.session.add_all(teachers)

        # 课程
        courses = [
            Course(name="小小主持人·启蒙班", level="启蒙级", age_range="4-6岁",
                   description="针对4-6岁儿童,通过儿歌、童谣、简单绕口令激发表达兴趣",
                   total_lessons=24, price=2880),
            Course(name="童声飞扬·初级班", level="初级", age_range="5-7岁",
                   description="发音正音训练、故事讲述、基础台风训练",
                   total_lessons=32, price=3680),
            Course(name="金话筒·中级班", level="中级", age_range="7-9岁",
                   description="诗歌朗诵、新闻播报、即兴演讲、镜头表现力",
                   total_lessons=36, price=4580),
            Course(name="小主播·高级班", level="高级", age_range="9-12岁",
                   description="综合舞台表演、辩论技巧、电视演播室实训",
                   total_lessons=40, price=5680),
            Course(name="金牌小主持·冲刺班", level="金牌级", age_range="10-14岁",
                   description="艺考衔接、比赛冲刺、全能型舞台表演",
                   total_lessons=48, price=7880),
        ]
        db.session.add_all(courses)
        db.session.commit()

        # 学员
        sample_names = [
            ("张子悦","女"),("李浩宇","男"),("王梓萱","女"),("刘欣怡","女"),("陈子轩","男"),
            ("杨语桐","女"),("赵梓豪","男"),("黄若汐","女"),("周俊熙","男"),("吴诗涵","女"),
            ("郑铭轩","男"),("孙佳怡","女"),("朱俊杰","男"),("胡梓晴","女"),("林子涵","男"),
            ("何欣然","女"),("高浩然","男"),("徐雨桐","女"),("马俊哲","男"),("朱奕辰","男"),
        ]
        schools = ["新华路小学", "实验小学", "阳光幼儿园", "第二实验小学", "星光幼儿园", "育才小学"]
        levels = ["启蒙级", "初级", "中级", "高级"]
        today = date.today()
        students = []
        for i, (name, g) in enumerate(sample_names):
            age = random.randint(5, 12)
            bd = date(today.year - age, random.randint(1, 12), random.randint(1, 28))
            s = Student(
                name=name, gender=g, birthday=bd,
                parent_name=name[0] + "先生" if i % 2 else name[0] + "女士",
                parent_phone=f"138{random.randint(10000000, 99999999)}",
                address=f"新华区XX路{random.randint(1, 200)}号",
                school=random.choice(schools),
                level=random.choice(levels),
                enroll_date=today - timedelta(days=random.randint(0, 90)),
                status="在读",
                remark="性格活泼,表达能力强" if i % 3 == 0 else "",
            )
            students.append(s)
        db.session.add_all(students)
        db.session.commit()

        # 班级
        classes = [
            ClassGroup(name="启蒙1班(周六上午)", course_id=courses[0].id, teacher_id=teachers[3].id,
                       classroom="101教室", start_date=today - timedelta(days=30), capacity=12, status="开课中"),
            ClassGroup(name="初级2班(周日下午)", course_id=courses[1].id, teacher_id=teachers[1].id,
                       classroom="102教室", start_date=today - timedelta(days=45), capacity=15, status="开课中"),
            ClassGroup(name="中级3班(周六下午)", course_id=courses[2].id, teacher_id=teachers[0].id,
                       classroom="多功能厅", start_date=today - timedelta(days=60), capacity=15, status="开课中"),
            ClassGroup(name="高级冲刺班", course_id=courses[3].id, teacher_id=teachers[2].id,
                       classroom="演播室", start_date=today - timedelta(days=20), capacity=10, status="开课中"),
        ]
        db.session.add_all(classes)
        db.session.commit()

        # 分配学员到班级
        for i, s in enumerate(students):
            cg = classes[i % len(classes)]
            db.session.add(Enrollment(student_id=s.id, class_id=cg.id))
        db.session.commit()

        # 排课 (每个班排 3 节课)
        topics = ["绕口令训练营", "诗歌朗诵《春晓》", "即兴演讲:我的梦想",
                  "新闻播报基础", "童话故事讲述", "舞台礼仪与台风"]
        schedules = []
        for cg in classes:
            for offset in [-7, 0, 7]:
                sc = Schedule(
                    class_id=cg.id,
                    lesson_date=today + timedelta(days=offset),
                    start_time="09:00" if offset % 2 == 0 else "14:00",
                    end_time="10:30" if offset % 2 == 0 else "15:30",
                    topic=random.choice(topics),
                    content="1. 热身发声练习\n2. 主题训练\n3. 学员展示与点评",
                    status="已上课" if offset < 0 else "待上课",
                )
                schedules.append(sc)
        db.session.add_all(schedules)
        db.session.commit()

        # 考勤(给已上课的排课加考勤)
        for sc in schedules:
            if sc.status != "已上课":
                continue
            for e in sc.class_group.enrollments:
                db.session.add(Attendance(
                    schedule_id=sc.id, student_id=e.student_id,
                    status=random.choice(["出勤", "出勤", "出勤", "迟到", "请假"]),
                    score=random.randint(80, 98),
                    comment=random.choice(["表现积极", "发音准确", "需加强气息", "台风大方", ""]),
                ))
        db.session.commit()

        # 订单
        for i, s in enumerate(students[:15]):
            course = random.choice(courses[:4])
            o = Order(
                order_no=f"XHT{datetime.now().strftime('%Y%m%d')}{1000+i}",
                student_id=s.id, course_id=course.id,
                amount=course.price, discount=random.choice([0, 0, 100, 200, 500]),
                pay_method=random.choice(["微信", "支付宝", "刷卡"]),
                status=random.choice(["已付款", "已付款", "已付款", "待付款"]),
            )
            if o.status == "已付款":
                o.pay_time = datetime.now() - timedelta(days=random.randint(0, 20))
            db.session.add(o)

        # 考级
        for s in random.sample(students, 8):
            e = GradingExam(
                student_id=s.id,
                level=random.choice(["初级", "中级", "高级"]),
                exam_date=today + timedelta(days=random.randint(-30, 30)),
                exam_place="新华区文化馆",
                score=random.randint(75, 98),
                result=random.choice(["通过", "通过", "待考试"]),
                certificate_no=f"XH{random.randint(10000,99999)}" if random.random() > 0.3 else "",
            )
            db.session.add(e)

        # 演出活动
        performances = [
            Performance(title="2026春季汇报演出", category="汇报演出",
                        perform_date=today + timedelta(days=25),
                        place="新华剧院", description="全体学员汇报演出,家长观摩",
                        status="筹备中"),
            Performance(title="省小金话筒大赛选拔", category="比赛",
                        perform_date=today + timedelta(days=45),
                        place="省电视台演播厅", description="省级比赛选拔赛",
                        status="报名中"),
            Performance(title="六一儿童节公益朗诵", category="公益",
                        perform_date=today + timedelta(days=52),
                        place="儿童福利院", description="走进福利院公益朗诵活动",
                        status="筹备中"),
        ]
        db.session.add_all(performances)
        db.session.commit()

        # 试听课
        trial_names = [
            "春季启蒙试听班 A", "春季启蒙试听班 B", "周末试听试听班",
            "周二晚间试听", "周四晚间试听", "周五晚间试听",
            "周六亲子体验课", "金话筒体验班",
        ]
        classrooms = ["1号教室", "2号教室", "多功能厅", "演播室"]
        statuses = ["待预约", "预约中", "预约中", "已满员"]
        trials = []
        for i, name in enumerate(trial_names):
            t = TrialClass(
                name=name,
                trial_date=today + timedelta(days=random.randint(-3, 14)),
                start_time=random.choice(["09:00", "10:00", "14:00", "16:00", "19:00"]),
                end_time="",
                teacher_id=random.choice(teachers).id,
                classroom=random.choice(classrooms),
                capacity=random.choice([4, 6, 8]),
                course_id=random.choice(courses[:3]).id,
                status=random.choice(statuses),
                remark="",
            )
            # end_time 基于 start_time + 1.5h
            sh, sm = map(int, t.start_time.split(":"))
            eh = sh + 1
            em = sm + 30
            if em >= 60: eh += 1; em -= 60
            t.end_time = f"{eh:02d}:{em:02d}"
            trials.append(t)
        db.session.add_all(trials)
        db.session.commit()

        # 试听学员
        child_names = [("张小明","男"),("李小红","女"),("王小明","男"),("赵小美","女"),
                       ("刘小乐","男"),("陈小佳","女"),("周小宝","男"),("吴小雅","女"),
                       ("郑小杰","男"),("孙小萌","女")]
        for t in trials:
            n = random.randint(1, min(t.capacity, 5))
            picks = random.sample(child_names, n)
            for cn, _ in picks:
                st = random.choice(["已预约", "已预约", "已签到", "已签到", "已缺席"])
                db.session.add(TrialEnrollment(
                    trial_id=t.id,
                    child_name=cn,
                    age=random.randint(4, 9),
                    parent_phone=f"138{random.randint(10000000, 99999999)}",
                    status=st,
                ))
            # 满员自动标记
            if n >= t.capacity:
                t.status = "已满员"
        db.session.commit()
        print(f"✅ 初始化完成: {len(students)}位学员, {len(teachers)}位教师, {len(courses)}门课程, {len(classes)}个班级")


if __name__ == "__main__":
    run()

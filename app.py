"""
儿童小主持教培业务系统 - 主应用入口
XinHuaTong Young Host Training Management System
"""
import os
import uuid
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
from sqlalchemy import func

from config import Config
from models import (
    db, Student, Teacher, Course, ClassGroup, Enrollment,
    Schedule, Attendance, Order, GradingExam, Performance,
    TrialClass, TrialEnrollment,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


# ---------- 工具函数 ----------
def parse_date(s, default=None):
    if not s:
        return default
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return default


def gen_order_no():
    return "XHT" + datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:4].upper()


def ok(data=None, msg="ok"):
    return jsonify({"code": 0, "msg": msg, "data": data})


def fail(msg="操作失败", code=1):
    return jsonify({"code": code, "msg": msg, "data": None})


# ---------- 路由注册 ----------
def register_routes(app: Flask):

    # ========== 页面路由 ==========
    @app.route("/")
    def index():
        return render_template("dashboard.html", active="dashboard")

    @app.route("/students")
    def page_students():
        return render_template("students.html", active="students")

    @app.route("/teachers")
    def page_teachers():
        return render_template("teachers.html", active="teachers")

    @app.route("/courses")
    def page_courses():
        return render_template("courses.html", active="courses")

    @app.route("/classes")
    def page_classes():
        return render_template("classes.html", active="classes")

    @app.route("/schedules")
    def page_schedules():
        return render_template("schedules.html", active="schedules")

    @app.route("/attendance")
    def page_attendance():
        return render_template("attendance.html", active="attendance")

    @app.route("/orders")
    def page_orders():
        return render_template("orders.html", active="orders")

    @app.route("/grading")
    def page_grading():
        return render_template("grading.html", active="grading")

    @app.route("/performances")
    def page_performances():
        return render_template("performances.html", active="performances")

    @app.route("/trials")
    def page_trials():
        return render_template("trials.html", active="trials")

    # ========== Dashboard API ==========
    @app.route("/api/dashboard/stats")
    def dashboard_stats():
        today = date.today()
        month_start = today.replace(day=1)
        stats = {
            "student_total": Student.query.filter_by(status="在读").count(),
            "teacher_total": Teacher.query.filter_by(status="在职").count(),
            "class_total": ClassGroup.query.filter_by(status="开课中").count(),
            "course_total": Course.query.filter_by(status="在售").count(),
            "month_income": db.session.query(func.coalesce(func.sum(Order.amount - Order.discount), 0))
                .filter(Order.status == "已付款", Order.pay_time >= month_start).scalar() or 0,
            "month_new_students": Student.query.filter(Student.enroll_date >= month_start).count(),
            "today_lessons": Schedule.query.filter_by(lesson_date=today).count(),
            "pending_exams": GradingExam.query.filter_by(result="待考试").count(),
        }

        # 近7天报名趋势
        trend = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            cnt = Student.query.filter(Student.enroll_date == d).count()
            trend.append({"date": d.strftime("%m-%d"), "count": cnt})
        stats["enroll_trend"] = trend

        # 等级分布
        level_dist = db.session.query(Student.level, func.count(Student.id)) \
            .group_by(Student.level).all()
        stats["level_dist"] = [{"level": l or "未分级", "count": c} for l, c in level_dist]
        return ok(stats)

    # ========== 学员 CRUD ==========
    @app.route("/api/students", methods=["GET"])
    def list_students():
        kw = request.args.get("kw", "").strip()
        level = request.args.get("level", "").strip()
        status = request.args.get("status", "").strip()
        q = Student.query
        if kw:
            q = q.filter(db.or_(Student.name.contains(kw), Student.parent_phone.contains(kw)))
        if level:
            q = q.filter_by(level=level)
        if status:
            q = q.filter_by(status=status)
        rows = q.order_by(Student.id.desc()).all()
        return ok([r.to_dict() for r in rows])

    @app.route("/api/students", methods=["POST"])
    def create_student():
        d = request.json or {}
        if not d.get("name") or not d.get("parent_phone"):
            return fail("姓名和家长电话必填")
        s = Student(
            name=d["name"],
            gender=d.get("gender", "男"),
            birthday=parse_date(d.get("birthday")),
            parent_name=d.get("parent_name", ""),
            parent_phone=d["parent_phone"],
            address=d.get("address", ""),
            school=d.get("school", ""),
            level=d.get("level", "启蒙级"),
            enroll_date=parse_date(d.get("enroll_date"), date.today()),
            status=d.get("status", "在读"),
            remark=d.get("remark", ""),
        )
        db.session.add(s)
        db.session.commit()
        return ok(s.to_dict(), "新增成功")

    @app.route("/api/students/<int:sid>", methods=["PUT"])
    def update_student(sid):
        s = Student.query.get_or_404(sid)
        d = request.json or {}
        for k in ["name", "gender", "parent_name", "parent_phone", "address", "school", "level", "status", "remark"]:
            if k in d:
                setattr(s, k, d[k])
        if "birthday" in d:
            s.birthday = parse_date(d["birthday"])
        if "enroll_date" in d:
            s.enroll_date = parse_date(d["enroll_date"])
        db.session.commit()
        return ok(s.to_dict(), "更新成功")

    @app.route("/api/students/<int:sid>", methods=["DELETE"])
    def delete_student(sid):
        s = Student.query.get_or_404(sid)
        db.session.delete(s)
        db.session.commit()
        return ok(msg="删除成功")

    # ========== 教师 CRUD ==========
    @app.route("/api/teachers", methods=["GET"])
    def list_teachers():
        kw = request.args.get("kw", "").strip()
        q = Teacher.query
        if kw:
            q = q.filter(db.or_(Teacher.name.contains(kw), Teacher.phone.contains(kw)))
        return ok([r.to_dict() for r in q.order_by(Teacher.id.desc()).all()])

    @app.route("/api/teachers", methods=["POST"])
    def create_teacher():
        d = request.json or {}
        if not d.get("name") or not d.get("phone"):
            return fail("姓名和电话必填")
        t = Teacher(
            name=d["name"],
            gender=d.get("gender", "女"),
            phone=d["phone"],
            title=d.get("title", "初级讲师"),
            specialty=d.get("specialty", ""),
            intro=d.get("intro", ""),
            hire_date=parse_date(d.get("hire_date"), date.today()),
            status=d.get("status", "在职"),
        )
        db.session.add(t)
        db.session.commit()
        return ok(t.to_dict(), "新增成功")

    @app.route("/api/teachers/<int:tid>", methods=["PUT"])
    def update_teacher(tid):
        t = Teacher.query.get_or_404(tid)
        d = request.json or {}
        for k in ["name", "gender", "phone", "title", "specialty", "intro", "status"]:
            if k in d:
                setattr(t, k, d[k])
        if "hire_date" in d:
            t.hire_date = parse_date(d["hire_date"])
        db.session.commit()
        return ok(t.to_dict(), "更新成功")

    @app.route("/api/teachers/<int:tid>", methods=["DELETE"])
    def delete_teacher(tid):
        t = Teacher.query.get_or_404(tid)
        db.session.delete(t)
        db.session.commit()
        return ok(msg="删除成功")

    # ========== 课程 CRUD ==========
    @app.route("/api/courses", methods=["GET"])
    def list_courses():
        return ok([r.to_dict() for r in Course.query.order_by(Course.id.desc()).all()])

    @app.route("/api/courses", methods=["POST"])
    def create_course():
        d = request.json or {}
        if not d.get("name"):
            return fail("课程名称必填")
        c = Course(
            name=d["name"],
            level=d.get("level", "启蒙级"),
            age_range=d.get("age_range", "5-7岁"),
            description=d.get("description", ""),
            total_lessons=int(d.get("total_lessons", 24)),
            price=float(d.get("price", 0)),
            status=d.get("status", "在售"),
        )
        db.session.add(c)
        db.session.commit()
        return ok(c.to_dict(), "新增成功")

    @app.route("/api/courses/<int:cid>", methods=["PUT"])
    def update_course(cid):
        c = Course.query.get_or_404(cid)
        d = request.json or {}
        for k in ["name", "level", "age_range", "description", "status"]:
            if k in d:
                setattr(c, k, d[k])
        if "total_lessons" in d:
            c.total_lessons = int(d["total_lessons"])
        if "price" in d:
            c.price = float(d["price"])
        db.session.commit()
        return ok(c.to_dict(), "更新成功")

    @app.route("/api/courses/<int:cid>", methods=["DELETE"])
    def delete_course(cid):
        c = Course.query.get_or_404(cid)
        db.session.delete(c)
        db.session.commit()
        return ok(msg="删除成功")

    # ========== 班级 CRUD ==========
    @app.route("/api/classes", methods=["GET"])
    def list_classes():
        return ok([r.to_dict() for r in ClassGroup.query.order_by(ClassGroup.id.desc()).all()])

    @app.route("/api/classes", methods=["POST"])
    def create_class():
        d = request.json or {}
        if not d.get("name") or not d.get("course_id"):
            return fail("班级名称和课程必填")
        cg = ClassGroup(
            name=d["name"],
            course_id=int(d["course_id"]),
            teacher_id=int(d["teacher_id"]) if d.get("teacher_id") else None,
            classroom=d.get("classroom", ""),
            start_date=parse_date(d.get("start_date"), date.today()),
            end_date=parse_date(d.get("end_date")),
            capacity=int(d.get("capacity", 15)),
            status=d.get("status", "开课中"),
        )
        db.session.add(cg)
        db.session.commit()
        return ok(cg.to_dict(), "新增成功")

    @app.route("/api/classes/<int:cid>", methods=["PUT"])
    def update_class(cid):
        cg = ClassGroup.query.get_or_404(cid)
        d = request.json or {}
        for k in ["name", "classroom", "status"]:
            if k in d:
                setattr(cg, k, d[k])
        if "course_id" in d:
            cg.course_id = int(d["course_id"])
        if "teacher_id" in d:
            cg.teacher_id = int(d["teacher_id"]) if d["teacher_id"] else None
        if "capacity" in d:
            cg.capacity = int(d["capacity"])
        if "start_date" in d:
            cg.start_date = parse_date(d["start_date"])
        if "end_date" in d:
            cg.end_date = parse_date(d["end_date"])
        db.session.commit()
        return ok(cg.to_dict(), "更新成功")

    @app.route("/api/classes/<int:cid>", methods=["DELETE"])
    def delete_class(cid):
        cg = ClassGroup.query.get_or_404(cid)
        db.session.delete(cg)
        db.session.commit()
        return ok(msg="删除成功")

    @app.route("/api/classes/<int:cid>/students", methods=["GET"])
    def class_students(cid):
        cg = ClassGroup.query.get_or_404(cid)
        return ok([e.student.to_dict() for e in cg.enrollments])

    @app.route("/api/classes/<int:cid>/students", methods=["POST"])
    def class_add_student(cid):
        d = request.json or {}
        sid = int(d.get("student_id", 0))
        if not sid:
            return fail("请选择学员")
        if Enrollment.query.filter_by(class_id=cid, student_id=sid).first():
            return fail("该学员已在此班级")
        db.session.add(Enrollment(class_id=cid, student_id=sid))
        db.session.commit()
        return ok(msg="添加成功")

    @app.route("/api/classes/<int:cid>/students/<int:sid>", methods=["DELETE"])
    def class_remove_student(cid, sid):
        e = Enrollment.query.filter_by(class_id=cid, student_id=sid).first_or_404()
        db.session.delete(e)
        db.session.commit()
        return ok(msg="移除成功")

    # ========== 排课 CRUD ==========
    @app.route("/api/schedules", methods=["GET"])
    def list_schedules():
        start = parse_date(request.args.get("start"))
        end = parse_date(request.args.get("end"))
        q = Schedule.query
        if start:
            q = q.filter(Schedule.lesson_date >= start)
        if end:
            q = q.filter(Schedule.lesson_date <= end)
        return ok([r.to_dict() for r in q.order_by(Schedule.lesson_date.desc(), Schedule.start_time).all()])

    @app.route("/api/schedules", methods=["POST"])
    def create_schedule():
        d = request.json or {}
        if not d.get("class_id") or not d.get("lesson_date"):
            return fail("班级和日期必填")
        s = Schedule(
            class_id=int(d["class_id"]),
            lesson_date=parse_date(d["lesson_date"]),
            start_time=d.get("start_time", "09:00"),
            end_time=d.get("end_time", "10:30"),
            topic=d.get("topic", ""),
            content=d.get("content", ""),
            status=d.get("status", "待上课"),
        )
        db.session.add(s)
        db.session.commit()
        return ok(s.to_dict(), "排课成功")

    @app.route("/api/schedules/<int:sid>", methods=["PUT"])
    def update_schedule(sid):
        s = Schedule.query.get_or_404(sid)
        d = request.json or {}
        for k in ["start_time", "end_time", "topic", "content", "status"]:
            if k in d:
                setattr(s, k, d[k])
        if "lesson_date" in d:
            s.lesson_date = parse_date(d["lesson_date"])
        if "class_id" in d:
            s.class_id = int(d["class_id"])
        db.session.commit()
        return ok(s.to_dict(), "更新成功")

    @app.route("/api/schedules/<int:sid>", methods=["DELETE"])
    def delete_schedule(sid):
        s = Schedule.query.get_or_404(sid)
        db.session.delete(s)
        db.session.commit()
        return ok(msg="删除成功")

    # ========== 考勤 ==========
    @app.route("/api/schedules/<int:sid>/attendance", methods=["GET"])
    def get_attendance(sid):
        s = Schedule.query.get_or_404(sid)
        # 班级所有学员 + 已录考勤
        att_map = {a.student_id: a for a in s.attendances}
        rows = []
        for e in s.class_group.enrollments:
            a = att_map.get(e.student_id)
            rows.append({
                "student_id": e.student_id,
                "student_name": e.student.name,
                "attendance_id": a.id if a else None,
                "status": a.status if a else "出勤",
                "score": a.score if a else 0,
                "comment": a.comment if a else "",
            })
        return ok({"schedule": s.to_dict(), "list": rows})

    @app.route("/api/schedules/<int:sid>/attendance", methods=["POST"])
    def save_attendance(sid):
        s = Schedule.query.get_or_404(sid)
        items = request.json or []
        # 清空后重新写入
        Attendance.query.filter_by(schedule_id=sid).delete()
        for it in items:
            db.session.add(Attendance(
                schedule_id=sid,
                student_id=int(it["student_id"]),
                status=it.get("status", "出勤"),
                score=int(it.get("score") or 0),
                comment=it.get("comment", ""),
            ))
        s.status = "已上课"
        db.session.commit()
        return ok(msg="考勤已保存")

    # ========== 订单 ==========
    @app.route("/api/orders", methods=["GET"])
    def list_orders():
        status = request.args.get("status", "").strip()
        q = Order.query
        if status:
            q = q.filter_by(status=status)
        return ok([r.to_dict() for r in q.order_by(Order.id.desc()).all()])

    @app.route("/api/orders", methods=["POST"])
    def create_order():
        d = request.json or {}
        if not d.get("student_id") or not d.get("course_id"):
            return fail("学员和课程必填")
        o = Order(
            order_no=gen_order_no(),
            student_id=int(d["student_id"]),
            course_id=int(d["course_id"]),
            amount=float(d.get("amount", 0)),
            discount=float(d.get("discount", 0)),
            pay_method=d.get("pay_method", "微信"),
            status=d.get("status", "待付款"),
            remark=d.get("remark", ""),
        )
        if o.status == "已付款":
            o.pay_time = datetime.now()
        db.session.add(o)
        db.session.commit()
        return ok(o.to_dict(), "订单创建成功")

    @app.route("/api/orders/<int:oid>/pay", methods=["POST"])
    def pay_order(oid):
        o = Order.query.get_or_404(oid)
        o.status = "已付款"
        o.pay_time = datetime.now()
        db.session.commit()
        return ok(o.to_dict(), "收款成功")

    @app.route("/api/orders/<int:oid>/refund", methods=["POST"])
    def refund_order(oid):
        o = Order.query.get_or_404(oid)
        o.status = "已退款"
        db.session.commit()
        return ok(o.to_dict(), "退款成功")

    @app.route("/api/orders/<int:oid>", methods=["DELETE"])
    def delete_order(oid):
        o = Order.query.get_or_404(oid)
        db.session.delete(o)
        db.session.commit()
        return ok(msg="删除成功")

    # ========== 考级 ==========
    @app.route("/api/exams", methods=["GET"])
    def list_exams():
        return ok([r.to_dict() for r in GradingExam.query.order_by(GradingExam.exam_date.desc()).all()])

    @app.route("/api/exams", methods=["POST"])
    def create_exam():
        d = request.json or {}
        if not d.get("student_id") or not d.get("level"):
            return fail("学员和等级必填")
        e = GradingExam(
            student_id=int(d["student_id"]),
            level=d["level"],
            exam_date=parse_date(d.get("exam_date"), date.today()),
            exam_place=d.get("exam_place", ""),
            score=float(d.get("score", 0)),
            result=d.get("result", "待考试"),
            certificate_no=d.get("certificate_no", ""),
            remark=d.get("remark", ""),
        )
        db.session.add(e)
        db.session.commit()
        return ok(e.to_dict(), "新增成功")

    @app.route("/api/exams/<int:eid>", methods=["PUT"])
    def update_exam(eid):
        e = GradingExam.query.get_or_404(eid)
        d = request.json or {}
        for k in ["level", "exam_place", "result", "certificate_no", "remark"]:
            if k in d:
                setattr(e, k, d[k])
        if "exam_date" in d:
            e.exam_date = parse_date(d["exam_date"])
        if "score" in d:
            e.score = float(d["score"])
        # 及格自动更新学员等级
        if e.result == "通过":
            stu = Student.query.get(e.student_id)
            if stu:
                stu.level = e.level
        db.session.commit()
        return ok(e.to_dict(), "更新成功")

    @app.route("/api/exams/<int:eid>", methods=["DELETE"])
    def delete_exam(eid):
        e = GradingExam.query.get_or_404(eid)
        db.session.delete(e)
        db.session.commit()
        return ok(msg="删除成功")

    # ========== 演出活动 ==========
    @app.route("/api/performances", methods=["GET"])
    def list_performances():
        return ok([r.to_dict() for r in Performance.query.order_by(Performance.perform_date.desc()).all()])

    @app.route("/api/performances", methods=["POST"])
    def create_performance():
        d = request.json or {}
        if not d.get("title") or not d.get("perform_date"):
            return fail("标题和日期必填")
        p = Performance(
            title=d["title"],
            category=d.get("category", "汇报演出"),
            perform_date=parse_date(d["perform_date"]),
            place=d.get("place", ""),
            description=d.get("description", ""),
            status=d.get("status", "筹备中"),
        )
        db.session.add(p)
        db.session.commit()
        return ok(p.to_dict(), "新增成功")

    @app.route("/api/performances/<int:pid>", methods=["PUT"])
    def update_performance(pid):
        p = Performance.query.get_or_404(pid)
        d = request.json or {}
        for k in ["title", "category", "place", "description", "status"]:
            if k in d:
                setattr(p, k, d[k])
        if "perform_date" in d:
            p.perform_date = parse_date(d["perform_date"])
        db.session.commit()
        return ok(p.to_dict(), "更新成功")

    @app.route("/api/performances/<int:pid>", methods=["DELETE"])
    def delete_performance(pid):
        p = Performance.query.get_or_404(pid)
        db.session.delete(p)
        db.session.commit()
        return ok(msg="删除成功")


    # ========== 试课管理 ==========
    @app.route("/api/trials", methods=["GET"])
    def list_trials():
        month = request.args.get("month", "")  # yyyy-mm
        kw = request.args.get("kw", "").strip()
        status = request.args.get("status", "").strip()
        teacher_id = request.args.get("teacher_id", "").strip()
        classroom = request.args.get("classroom", "").strip()

        q = TrialClass.query
        if month:
            try:
                y, m = map(int, month.split("-"))
                start = date(y, m, 1)
                end = date(y + (m // 12), (m % 12) + 1, 1)
                q = q.filter(TrialClass.trial_date >= start, TrialClass.trial_date < end)
            except ValueError:
                pass
        if kw:
            q = q.filter(TrialClass.name.contains(kw))
        if status:
            q = q.filter_by(status=status)
        if teacher_id:
            q = q.filter_by(teacher_id=int(teacher_id))
        if classroom:
            q = q.filter_by(classroom=classroom)
        rows = q.order_by(TrialClass.trial_date, TrialClass.start_time).all()
        return ok([r.to_dict() for r in rows])

    @app.route("/api/trials/<int:tid>", methods=["GET"])
    def get_trial(tid):
        t = TrialClass.query.get_or_404(tid)
        return ok(t.to_dict(with_enrollments=True))

    @app.route("/api/trials", methods=["POST"])
    def create_trial():
        d = request.json or {}
        if not d.get("name") or not d.get("trial_date"):
            return fail("名称和日期必填")
        t = TrialClass(
            name=d["name"],
            trial_date=parse_date(d["trial_date"]),
            start_time=d.get("start_time", "09:00"),
            end_time=d.get("end_time", "10:30"),
            teacher_id=int(d["teacher_id"]) if d.get("teacher_id") else None,
            classroom=d.get("classroom", "1号教室"),
            capacity=int(d.get("capacity", 6)),
            course_id=int(d["course_id"]) if d.get("course_id") else None,
            status=d.get("status", "待预约"),
            remark=d.get("remark", ""),
        )
        db.session.add(t)
        db.session.commit()
        return ok(t.to_dict(), "创建成功")

    @app.route("/api/trials/<int:tid>", methods=["PUT"])
    def update_trial(tid):
        t = TrialClass.query.get_or_404(tid)
        d = request.json or {}
        for k in ["name", "start_time", "end_time", "classroom", "status", "remark"]:
            if k in d:
                setattr(t, k, d[k])
        if "trial_date" in d:
            t.trial_date = parse_date(d["trial_date"])
        if "teacher_id" in d:
            t.teacher_id = int(d["teacher_id"]) if d["teacher_id"] else None
        if "course_id" in d:
            t.course_id = int(d["course_id"]) if d["course_id"] else None
        if "capacity" in d:
            t.capacity = int(d["capacity"])
        db.session.commit()
        return ok(t.to_dict(), "更新成功")

    @app.route("/api/trials/<int:tid>", methods=["DELETE"])
    def delete_trial(tid):
        t = TrialClass.query.get_or_404(tid)
        db.session.delete(t)
        db.session.commit()
        return ok(msg="删除成功")

    @app.route("/api/trials/<int:tid>/enrollments", methods=["POST"])
    def add_trial_enrollment(tid):
        t = TrialClass.query.get_or_404(tid)
        d = request.json or {}
        if not d.get("child_name") or not d.get("parent_phone"):
            return fail("姓名和电话必填")
        if len(t.enrollments) >= t.capacity:
            return fail("试听名额已满")
        e = TrialEnrollment(
            trial_id=tid,
            child_name=d["child_name"],
            age=int(d.get("age", 5)),
            parent_phone=d["parent_phone"],
            status=d.get("status", "已预约"),
            remark=d.get("remark", ""),
        )
        db.session.add(e)
        if len(t.enrollments) + 1 >= t.capacity:
            t.status = "已满员"
        db.session.commit()
        return ok(e.to_dict(), "添加成功")

    @app.route("/api/trials/enrollments/<int:eid>", methods=["PUT"])
    def update_trial_enrollment(eid):
        e = TrialEnrollment.query.get_or_404(eid)
        d = request.json or {}
        for k in ["child_name", "parent_phone", "status", "remark"]:
            if k in d:
                setattr(e, k, d[k])
        if "age" in d:
            e.age = int(d["age"])
        db.session.commit()
        return ok(e.to_dict(), "更新成功")

    @app.route("/api/trials/enrollments/<int:eid>", methods=["DELETE"])
    def delete_trial_enrollment(eid):
        e = TrialEnrollment.query.get_or_404(eid)
        db.session.delete(e)
        db.session.commit()
        return ok(msg="移除成功")


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

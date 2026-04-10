"""数据模型 - 儿童小主持教培业务系统"""
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ========= 学员管理 =========
class Student(db.Model):
    """学员(小朋友)"""
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, comment="姓名")
    gender = db.Column(db.String(4), default="男", comment="性别")
    birthday = db.Column(db.Date, comment="出生日期")
    avatar = db.Column(db.String(128), default="", comment="头像")
    parent_name = db.Column(db.String(32), comment="家长姓名")
    parent_phone = db.Column(db.String(20), nullable=False, comment="家长电话")
    address = db.Column(db.String(200), default="", comment="家庭住址")
    school = db.Column(db.String(64), default="", comment="就读学校")
    level = db.Column(db.String(16), default="启蒙级", comment="当前等级")
    enroll_date = db.Column(db.Date, default=date.today, comment="入学日期")
    status = db.Column(db.String(16), default="在读", comment="状态: 在读/休学/结业")
    remark = db.Column(db.Text, default="", comment="备注")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship("Enrollment", backref="student", cascade="all, delete-orphan")
    attendances = db.relationship("Attendance", backref="student", cascade="all, delete-orphan")
    orders = db.relationship("Order", backref="student", cascade="all, delete-orphan")
    exams = db.relationship("GradingExam", backref="student", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birthday": self.birthday.isoformat() if self.birthday else "",
            "age": (date.today().year - self.birthday.year) if self.birthday else "",
            "parent_name": self.parent_name,
            "parent_phone": self.parent_phone,
            "address": self.address,
            "school": self.school,
            "level": self.level,
            "enroll_date": self.enroll_date.isoformat() if self.enroll_date else "",
            "status": self.status,
            "remark": self.remark,
        }


# ========= 教师管理 =========
class Teacher(db.Model):
    """教师"""
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, comment="姓名")
    gender = db.Column(db.String(4), default="女", comment="性别")
    phone = db.Column(db.String(20), nullable=False, comment="联系电话")
    title = db.Column(db.String(32), default="初级讲师", comment="职称")
    specialty = db.Column(db.String(128), default="", comment="擅长领域")
    intro = db.Column(db.Text, default="", comment="个人简介")
    hire_date = db.Column(db.Date, default=date.today, comment="入职日期")
    status = db.Column(db.String(16), default="在职", comment="状态")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    classes = db.relationship("ClassGroup", backref="teacher")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "phone": self.phone,
            "title": self.title,
            "specialty": self.specialty,
            "intro": self.intro,
            "hire_date": self.hire_date.isoformat() if self.hire_date else "",
            "status": self.status,
        }


# ========= 课程管理 =========
class Course(db.Model):
    """课程(小主持课程体系)"""
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="课程名称")
    level = db.Column(db.String(16), default="启蒙级", comment="等级: 启蒙/初级/中级/高级/金牌")
    age_range = db.Column(db.String(16), default="5-7岁", comment="适合年龄")
    description = db.Column(db.Text, default="", comment="课程简介")
    total_lessons = db.Column(db.Integer, default=24, comment="总课时")
    price = db.Column(db.Float, default=0, comment="价格(元)")
    status = db.Column(db.String(16), default="在售", comment="状态")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    classes = db.relationship("ClassGroup", backref="course")
    orders = db.relationship("Order", backref="course")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "age_range": self.age_range,
            "description": self.description,
            "total_lessons": self.total_lessons,
            "price": self.price,
            "status": self.status,
        }


# ========= 班级管理 =========
class ClassGroup(db.Model):
    """班级"""
    __tablename__ = "class_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="班级名称")
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    classroom = db.Column(db.String(32), default="", comment="教室")
    start_date = db.Column(db.Date, default=date.today, comment="开班日期")
    end_date = db.Column(db.Date, comment="结班日期")
    capacity = db.Column(db.Integer, default=15, comment="容纳人数")
    status = db.Column(db.String(16), default="开课中", comment="状态")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    enrollments = db.relationship("Enrollment", backref="class_group", cascade="all, delete-orphan")
    schedules = db.relationship("Schedule", backref="class_group", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "course_id": self.course_id,
            "course_name": self.course.name if self.course else "",
            "teacher_id": self.teacher_id,
            "teacher_name": self.teacher.name if self.teacher else "",
            "classroom": self.classroom,
            "start_date": self.start_date.isoformat() if self.start_date else "",
            "end_date": self.end_date.isoformat() if self.end_date else "",
            "capacity": self.capacity,
            "student_count": len(self.enrollments),
            "status": self.status,
        }


class Enrollment(db.Model):
    """学员-班级 报名关联"""
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("class_groups.id"), nullable=False)
    enroll_date = db.Column(db.Date, default=date.today)

    __table_args__ = (db.UniqueConstraint("student_id", "class_id"),)


# ========= 排课管理 =========
class Schedule(db.Model):
    """排课 - 一节具体的课"""
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey("class_groups.id"), nullable=False)
    lesson_date = db.Column(db.Date, nullable=False, comment="上课日期")
    start_time = db.Column(db.String(8), nullable=False, comment="开始时间")
    end_time = db.Column(db.String(8), nullable=False, comment="结束时间")
    topic = db.Column(db.String(128), default="", comment="课程主题")
    content = db.Column(db.Text, default="", comment="教学内容")
    status = db.Column(db.String(16), default="待上课", comment="状态: 待上课/已上课/已取消")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendances = db.relationship("Attendance", backref="schedule", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "class_id": self.class_id,
            "class_name": self.class_group.name if self.class_group else "",
            "teacher_name": self.class_group.teacher.name if self.class_group and self.class_group.teacher else "",
            "classroom": self.class_group.classroom if self.class_group else "",
            "lesson_date": self.lesson_date.isoformat(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "topic": self.topic,
            "content": self.content,
            "status": self.status,
        }


# ========= 考勤管理 =========
class Attendance(db.Model):
    """考勤"""
    __tablename__ = "attendances"

    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey("schedules.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    status = db.Column(db.String(16), default="出勤", comment="出勤/请假/迟到/缺勤")
    score = db.Column(db.Integer, default=0, comment="课堂表现分(0-100)")
    comment = db.Column(db.String(255), default="", comment="教师点评")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "schedule_id": self.schedule_id,
            "student_id": self.student_id,
            "student_name": self.student.name if self.student else "",
            "status": self.status,
            "score": self.score,
            "comment": self.comment,
        }


# ========= 订单/学费管理 =========
class Order(db.Model):
    """订单 - 学员购买课程的学费记录"""
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False, comment="订单号")
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False, comment="金额")
    discount = db.Column(db.Float, default=0, comment="优惠金额")
    pay_method = db.Column(db.String(16), default="微信", comment="支付方式")
    status = db.Column(db.String(16), default="待付款", comment="待付款/已付款/已退款")
    pay_time = db.Column(db.DateTime, comment="支付时间")
    remark = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "order_no": self.order_no,
            "student_id": self.student_id,
            "student_name": self.student.name if self.student else "",
            "course_id": self.course_id,
            "course_name": self.course.name if self.course else "",
            "amount": self.amount,
            "discount": self.discount,
            "pay_method": self.pay_method,
            "status": self.status,
            "pay_time": self.pay_time.strftime("%Y-%m-%d %H:%M") if self.pay_time else "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "",
            "remark": self.remark,
        }


# ========= 考级管理 =========
class GradingExam(db.Model):
    """考级记录 - 小主持等级考试"""
    __tablename__ = "grading_exams"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    level = db.Column(db.String(16), nullable=False, comment="报考等级")
    exam_date = db.Column(db.Date, nullable=False, comment="考试日期")
    exam_place = db.Column(db.String(64), default="", comment="考点")
    score = db.Column(db.Float, default=0, comment="分数")
    result = db.Column(db.String(16), default="待考试", comment="待考试/通过/未通过")
    certificate_no = db.Column(db.String(64), default="", comment="证书编号")
    remark = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student.name if self.student else "",
            "level": self.level,
            "exam_date": self.exam_date.isoformat() if self.exam_date else "",
            "exam_place": self.exam_place,
            "score": self.score,
            "result": self.result,
            "certificate_no": self.certificate_no,
            "remark": self.remark,
        }


# ========= 试课管理 =========
class TrialClass(db.Model):
    """试听课"""
    __tablename__ = "trial_classes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, comment="试听班名称")
    trial_date = db.Column(db.Date, nullable=False, comment="试听日期")
    start_time = db.Column(db.String(8), default="09:00")
    end_time = db.Column(db.String(8), default="10:30")
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    classroom = db.Column(db.String(32), default="1号教室")
    capacity = db.Column(db.Integer, default=6, comment="计划人数")
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))
    status = db.Column(db.String(16), default="待预约",
                       comment="待预约/预约中/已满员/已结束/已取消")
    remark = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teacher = db.relationship("Teacher")
    course = db.relationship("Course")
    enrollments = db.relationship("TrialEnrollment", backref="trial",
                                  cascade="all, delete-orphan")

    def to_dict(self, with_enrollments=False):
        signed = sum(1 for e in self.enrollments if e.status == "已签到")
        absent = sum(1 for e in self.enrollments if e.status == "已缺席")
        booked = len(self.enrollments)
        waiting = booked - signed - absent
        d = {
            "id": self.id,
            "name": self.name,
            "trial_date": self.trial_date.isoformat(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "teacher_id": self.teacher_id,
            "teacher_name": self.teacher.name if self.teacher else "未指定",
            "classroom": self.classroom,
            "capacity": self.capacity,
            "course_id": self.course_id,
            "course_name": self.course.name if self.course else "",
            "status": self.status,
            "remark": self.remark,
            "stats": {
                "capacity": self.capacity,
                "booked": booked,
                "waiting": waiting,
                "signed": signed,
                "absent": absent,
            },
        }
        if with_enrollments:
            d["enrollments"] = [e.to_dict() for e in self.enrollments]
        return d


class TrialEnrollment(db.Model):
    """试听报名"""
    __tablename__ = "trial_enrollments"

    id = db.Column(db.Integer, primary_key=True)
    trial_id = db.Column(db.Integer, db.ForeignKey("trial_classes.id"), nullable=False)
    child_name = db.Column(db.String(32), nullable=False, comment="小朋友姓名")
    age = db.Column(db.Integer, default=5)
    parent_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(16), default="已预约",
                       comment="已预约/已签到/已缺席")
    remark = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "trial_id": self.trial_id,
            "child_name": self.child_name,
            "age": self.age,
            "parent_phone": self.parent_phone,
            "phone_mask": self.parent_phone[:3] + "****" + self.parent_phone[-4:]
                if len(self.parent_phone) >= 7 else self.parent_phone,
            "status": self.status,
            "remark": self.remark,
        }


# ========= 演出/活动管理 =========
class Performance(db.Model):
    """演出 / 比赛活动"""
    __tablename__ = "performances"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, comment="活动名称")
    category = db.Column(db.String(16), default="汇报演出", comment="类型: 汇报演出/比赛/公益")
    perform_date = db.Column(db.Date, nullable=False)
    place = db.Column(db.String(128), default="")
    description = db.Column(db.Text, default="")
    status = db.Column(db.String(16), default="筹备中")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "perform_date": self.perform_date.isoformat() if self.perform_date else "",
            "place": self.place,
            "description": self.description,
            "status": self.status,
        }

// ========== 通用工具 ==========
const api = {
    async get(url) {
        const r = await fetch(url);
        return r.json();
    },
    async post(url, data) {
        const r = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data || {})
        });
        return r.json();
    },
    async put(url, data) {
        const r = await fetch(url, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data || {})
        });
        return r.json();
    },
    async del(url) {
        const r = await fetch(url, {method: 'DELETE'});
        return r.json();
    }
};

function toast(msg, type = 'primary') {
    const el = document.getElementById('globalToast');
    if (!el) { alert(msg); return; }
    el.className = `toast align-items-center text-bg-${type} border-0`;
    document.getElementById('toastMsg').textContent = msg;
    bootstrap.Toast.getOrCreateInstance(el, {delay: 2000}).show();
}

function confirmBox(msg) {
    return new Promise(resolve => resolve(window.confirm(msg)));
}

function escapeHtml(s) {
    if (s == null) return '';
    return String(s).replace(/[&<>"']/g, c => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[c]);
}

function statusTag(s) {
    const map = {
        '在读': 'green', '在职': 'green', '在售': 'green', '开课中': 'green',
        '已付款': 'green', '通过': 'green', '已上课': 'green',
        '待付款': 'orange', '待考试': 'orange', '待上课': 'orange', '筹备中': 'orange',
        '休学': 'gray', '离职': 'gray', '停售': 'gray', '已结束': 'gray', '已取消': 'gray',
        '结业': 'blue',
        '未通过': 'red', '已退款': 'red', '缺勤': 'red',
        '出勤': 'green', '请假': 'orange', '迟到': 'orange',
    };
    const color = map[s] || 'pink';
    return `<span class="tag tag-${color}">${escapeHtml(s)}</span>`;
}

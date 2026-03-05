// 卡通头像随输入联动
window.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('username');
    const avatar = document.getElementById('avatar-svg');
    if (!usernameInput || !avatar) return;
    usernameInput.addEventListener('input', function(e) {
        const val = usernameInput.value.trim();
        // 简单用用户名长度和首字母决定表情和颜色
        let mood = 'smile', color = '#667eea';
        if (val.length === 0) {
            mood = 'smile'; color = '#667eea';
        } else if (val.length < 4) {
            mood = 'wink'; color = '#ff6a00';
        } else if (/\d/.test(val)) {
            mood = 'surprise'; color = '#764ba2';
        } else if (/a|A/.test(val[0])) {
            mood = 'cool'; color = '#42c6ff';
        } else {
            mood = 'smile'; color = '#ff8c42';
        }
        // 切换SVG表情
        for (const g of avatar.querySelectorAll('g')) g.style.display = 'none';
        const show = avatar.querySelector('g.'+mood);
        if (show) show.style.display = '';
        avatar.querySelector('circle.face').setAttribute('fill', color);
    });
});

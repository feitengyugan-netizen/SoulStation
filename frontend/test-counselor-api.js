// 测试咨询师API调用
const API_BASE = 'http://localhost:8000/api';

async function testCounselorDashboard() {
    console.log('=== 咨询师工作台API测试 ===\n');

    // 1. 测试登录
    console.log('1. 测试咨询师登录...');
    try {
        const loginResponse = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: 'teacher_wang@example.com',
                password: '123456'
            })
        });

        const loginResult = await loginResponse.json();
        console.log('登录响应:', JSON.stringify(loginResult, null, 2));

        if (loginResult.code !== 200) {
            console.error('❌ 登录失败');
            return;
        }

        const token = loginResult.data.token;
        const userInfo = loginResult.data.userInfo;
        console.log(`✅ 登录成功: ${userInfo.nickname} (${userInfo.role})`);

        // 2. 测试申请状态
        console.log('\n2. 测试申请状态...');
        const statusResponse = await fetch(`${API_BASE}/counselor/application/status`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const statusResult = await statusResponse.json();
        console.log('申请状态响应:', JSON.stringify(statusResult, null, 2));

        if (statusResult.code === 200) {
            console.log(`✅ 申请状态: ${statusResult.data.application_status}`);
            console.log(`   咨询师ID: ${statusResult.data.counselor_id}`);
        } else {
            console.error('❌ 获取申请状态失败');
            return;
        }

        // 3. 测试订单列表
        console.log('\n3. 测试订单列表...');
        const ordersResponse = await fetch(`${API_BASE}/consultation/counselor/orders`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const ordersResult = await ordersResponse.json();
        console.log('订单列表响应:', JSON.stringify(ordersResult, null, 2));

        if (ordersResult.code === 200) {
            const orders = ordersResult.data.items;
            console.log(`✅ 获取订单成功: ${ordersResult.data.total}个订单`);

            console.log('\n订单详情:');
            orders.forEach((order, index) => {
                console.log(`${index + 1}. ${order.appointment_no}`);
                console.log(`   用户: ${order.user_name}`);
                console.log(`   状态: ${order.status}`);
                console.log(`   类型: ${order.consultation_type}`);
                console.log(`   日期: ${order.appointment_date}`);
            });

            // 4. 模拟前端数据处理
            console.log('\n4. 模拟前端数据处理...');
            const statistics = {
                totalOrders: ordersResult.data.total,
                pendingOrders: orders.filter(o => o.status === 'pending').length,
                confirmedOrders: orders.filter(o => o.status === 'confirmed').length,
                completedOrders: orders.filter(o => o.status === 'completed').length,
                inProgressOrders: orders.filter(o => o.status === 'in_progress').length
            };

            console.log('统计数据:', JSON.stringify(statistics, null, 2));

            console.log('\n✅ 所有API测试通过！');
            console.log('\n前端应该能够正确显示:');
            console.log(`- 总订单数: ${statistics.totalOrders}`);
            console.log(`- 待处理: ${statistics.pendingOrders}`);
            console.log(`- 已确认: ${statistics.confirmedOrders}`);
            console.log(`- 已完成: ${statistics.completedOrders}`);

        } else {
            console.error('❌ 获取订单列表失败');
        }

    } catch (error) {
        console.error('❌ 测试失败:', error.message);
    }
}

// 运行测试
testCounselorDashboard();

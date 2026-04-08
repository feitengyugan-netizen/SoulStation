// 测试知识API调用
const axios = require('axios');

async function testKnowledgeAPI() {
  try {
    // 1. 登录
    console.log('1. 登录中...');
    const loginRes = await axios.post('http://localhost:8000/api/auth/login', {
      email: 'xiaoming@example.com',
      password: '123456'
    });
    const token = loginRes.data.data.token;
    console.log('登录成功，Token:', token.substring(0, 20) + '...');

    // 2. 获取知识列表
    console.log('2. 获取知识列表...');
    const knowledgeRes = await axios.get('http://localhost:8000/api/knowledge/list', {
      headers: { Authorization: `Bearer ${token}` },
      params: { page: 1, page_size: 5 }
    });
    
    console.log('API响应状态:', knowledgeRes.status);
    console.log('文章总数:', knowledgeRes.data.data.total);
    console.log('返回数据结构:', Object.keys(knowledgeRes.data.data));
    console.log('第一篇文章:', {
      id: knowledgeRes.data.data.items[0].id,
      title: knowledgeRes.data.data.items[0].title,
      view_count: knowledgeRes.data.data.items[0].view_count
    });

    console.log('✅ API测试成功！');
  } catch (error) {
    console.error('❌ API测试失败:', error.message);
    if (error.response) {
      console.error('错误状态码:', error.response.status);
      console.error('错误信息:', error.response.data);
    }
  }
}

testKnowledgeAPI();

// 路由配置
import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
const HomePage = () => import('@/views/HomePage.vue')

// 用户认证
const Login = () => import('@/views/auth/Login.vue')
const Register = () => import('@/views/auth/Register.vue')
const ForgotPassword = () => import('@/views/auth/ForgotPassword.vue')

// 智能问答
const ChatIndex = () => import('@/views/chat/ChatIndex.vue')
const ChatDetail = () => import('@/views/chat/ChatDetail.vue')
const TagManage = () => import('@/views/chat/TagManage.vue')

// 心理测试
const TestList = () => import('@/views/test/TestList.vue')
const TestTaking = () => import('@/views/test/TestTaking.vue')
const TestResult = () => import('@/views/test/TestResult.vue')
const TestTrend = () => import('@/views/test/TestTrend.vue')

// 个人中心
const Profile = () => import('@/views/profile/Profile.vue')
const ProfileEdit = () => import('@/views/profile/ProfileEdit.vue')
const PrivacySettings = () => import('@/views/profile/PrivacySettings.vue')
const DataStatistics = () => import('@/views/profile/DataStatistics.vue')

// 咨询师预约
const CounselorList = () => import('@/views/counselor/CounselorList.vue')
const CounselorDetail = () => import('@/views/counselor/CounselorDetail.vue')
const CounselorRegister = () => import('@/views/counselor/CounselorRegister.vue')
const AppointmentForm = () => import('@/views/counselor/AppointmentForm.vue')
const AppointmentManage = () => import('@/views/counselor/AppointmentManage.vue')
const ReviewForm = () => import('@/views/counselor/ReviewForm.vue')

// 咨询对话
const CounselorOrders = () => import('@/views/consultation/CounselorOrders.vue')
const ConsultationChatUser = () => import('@/views/consultation/ConsultationChatUser.vue')
const ConsultationChatCounselor = () => import('@/views/consultation/ConsultationChatCounselor.vue')

// 心理知识
const KnowledgeList = () => import('@/views/knowledge/KnowledgeList.vue')
const KnowledgeDetail = () => import('@/views/knowledge/KnowledgeDetail.vue')

// 后台管理
const AdminLogin = () => import('@/views/admin/AdminLogin.vue')
const AdminDashboard = () => import('@/views/admin/AdminDashboard.vue')
const CounselorReview = () => import('@/views/admin/CounselorReview.vue')
const KnowledgeManage = () => import('@/views/admin/KnowledgeManage.vue')
const ArticleEditor = () => import('@/views/admin/ArticleEditor.vue')
const UserManage = () => import('@/views/admin/UserManage.vue')
const OrderManage = () => import('@/views/admin/OrderManage.vue')

const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: HomePage,
    meta: { title: '首页 - 心理咨询平台' }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录 - 心理咨询平台', requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: '注册 - 心理咨询平台', requiresGuest: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword,
    meta: { title: '忘记密码 - 心理咨询平台', requiresGuest: true }
  },
  {
    path: '/chat',
    name: 'ChatIndex',
    component: ChatIndex,
    meta: { title: '智能问答 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/chat/:id',
    name: 'ChatDetail',
    component: ChatDetail,
    meta: { title: '对话详情 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/chat/tags',
    name: 'TagManage',
    component: TagManage,
    meta: { title: '标签管理 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/test',
    name: 'TestList',
    component: TestList,
    meta: { title: '心理测试 - 心理咨询平台' }
  },
  {
    path: '/test/:id/taking',
    name: 'TestTaking',
    component: TestTaking,
    meta: { title: '进行测试 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/test/:id/result',
    name: 'TestResult',
    component: TestResult,
    meta: { title: '测试结果 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/test/trend',
    name: 'TestTrend',
    component: TestTrend,
    meta: { title: '测试趋势 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { title: '个人中心 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/profile/edit',
    name: 'ProfileEdit',
    component: ProfileEdit,
    meta: { title: '编辑资料 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/profile/privacy',
    name: 'PrivacySettings',
    component: PrivacySettings,
    meta: { title: '隐私设置 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/profile/statistics',
    name: 'DataStatistics',
    component: DataStatistics,
    meta: { title: '数据统计 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/counselor',
    name: 'CounselorList',
    component: CounselorList,
    meta: { title: '找咨询师 - 心理咨询平台' }
  },
  {
    path: '/counselor/register',
    name: 'CounselorRegister',
    component: CounselorRegister,
    meta: { title: '咨询师入驻 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/counselor/:id',
    name: 'CounselorDetail',
    component: CounselorDetail,
    meta: { title: '咨询师详情 - 心理咨询平台' }
  },
  {
    path: '/counselor/appointment',
    name: 'AppointmentForm',
    component: AppointmentForm,
    meta: { title: '预约咨询 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/counselor/orders',
    name: 'AppointmentManage',
    component: AppointmentManage,
    meta: { title: '我的预约 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/counselor/review/:id',
    name: 'ReviewForm',
    component: ReviewForm,
    meta: { title: '评价咨询 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/consultation/counselor/orders',
    name: 'CounselorOrders',
    component: CounselorOrders,
    meta: { title: '咨询师工作台 - 心理咨询平台', requiresAuth: true, requiresCounselor: true }
  },
  {
    path: '/consultation/user/:id',
    name: 'ConsultationChatUser',
    component: ConsultationChatUser,
    meta: { title: '咨询对话 - 心理咨询平台', requiresAuth: true }
  },
  {
    path: '/consultation/counselor/:id',
    name: 'ConsultationChatCounselor',
    component: ConsultationChatCounselor,
    meta: { title: '咨询对话 - 心理咨询平台', requiresAuth: true, requiresCounselor: true }
  },
  {
    path: '/knowledge',
    name: 'KnowledgeList',
    component: KnowledgeList,
    meta: { title: '心理知识 - 心理咨询平台' }
  },
  {
    path: '/knowledge/:id',
    name: 'KnowledgeDetail',
    component: KnowledgeDetail,
    meta: { title: '知识详情 - 心理咨询平台' }
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin,
    meta: { title: '管理员登录 - 心理咨询平台' }
  },
  {
    path: '/admin',
    redirect: '/admin/dashboard'
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { title: '后台管理 - 心理咨询平台', requiresAdmin: true }
  },
  {
    path: '/admin/counselor-review',
    name: 'CounselorReview',
    component: CounselorReview,
    meta: { title: '咨询师审核 - 心理咨询平台', requiresAdmin: true }
  },
  {
    path: '/admin/knowledge',
    name: 'KnowledgeManage',
    component: KnowledgeManage,
    meta: { title: '知识管理 - 心理咨询平台', requiresAdmin: true }
  },
  {
    path: '/admin/article-editor',
    name: 'ArticleEditor',
    component: ArticleEditor,
    meta: { title: '编辑文章 - 心理咨询平台', requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'UserManage',
    component: UserManage,
    meta: { title: '用户管理 - 心理咨询平台', requiresAdmin: true }
  },
  {
    path: '/admin/orders',
    name: 'OrderManage',
    component: OrderManage,
    meta: { title: '订单管理 - 心理咨询平台', requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '心理咨询平台'

  // 获取token
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('userRole')

  // 需要登录的页面
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // 需要咨询师角色的页面
  if (to.meta.requiresCounselor && userRole !== 'counselor') {
    next('/')
    return
  }

  // 需要管理员角色的页面
  if (to.meta.requiresAdmin && userRole !== 'admin') {
    next('/admin/login')
    return
  }

  // 已登录用户访问登录/注册页，跳转首页
  if (to.meta.requiresGuest && token) {
    next('/')
    return
  }

  next()
})

export default router

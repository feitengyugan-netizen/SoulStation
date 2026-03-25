<template>
  <div class="home-page">
    <!-- 页面头部 -->
    <PageHeader />

    <!-- 轮播图区域 -->
    <section class="hero-section">
      <div class="container">
        <el-carousel :interval="5000" arrow="always" height="400px" indicator-position="outside">
          <el-carousel-item v-for="(item, index) in carouselItems" :key="index">
            <div class="carousel-item" :style="{ backgroundImage: `url(${item.image})` }">
              <div class="carousel-content">
                <h1>{{ item.title }}</h1>
                <p>{{ item.subtitle }}</p>
                <el-button type="primary" size="large" @click="handleCarouselClick(item)">
                  立即体验
                </el-button>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>
    </section>

    <!-- 功能导航 -->
    <section class="features-section">
      <div class="container">
        <div class="features-grid">
          <div
            v-for="feature in features"
            :key="feature.id"
            class="feature-card"
            @click="navigateTo(feature.path)"
          >
            <div class="feature-icon" :style="{ background: feature.color }">
              <el-icon :size="40">
                <component :is="feature.icon" />
              </el-icon>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
            <span class="feature-link">了解更多 →</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 热门心理知识 -->
    <section class="knowledge-section">
      <div class="container">
        <div class="section-header">
          <h2>热门心理知识</h2>
          <el-link type="primary" @click="navigateTo('/knowledge')">查看更多 →</el-link>
        </div>
        <div class="knowledge-grid">
          <el-skeleton v-if="loadingKnowledge" :rows="3" animated />
          <div
            v-for="article in hotArticles"
            :key="article.id"
            class="knowledge-card"
            @click="viewArticle(article.id)"
          >
            <div class="article-cover">
              <img :src="article.coverImage" :alt="article.title" />
            </div>
            <div class="article-info">
              <h3>{{ article.title }}</h3>
              <p class="article-meta">
                <span>{{ article.category }}</span>
                <span>👁️ {{ formatNumber(article.views) }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 推荐咨询师 -->
    <section class="counselor-section">
      <div class="container">
        <div class="section-header">
          <h2>推荐咨询师</h2>
          <el-link type="primary" @click="navigateTo('/counselor')">查看更多 →</el-link>
        </div>
        <div class="counselor-grid">
          <el-skeleton v-if="loadingCounselors" :rows="3" animated />
          <div
            v-for="counselor in recommendedCounselors"
            :key="counselor.id"
            class="counselor-card"
          >
            <div class="counselor-avatar">
              <el-avatar :size="80" :src="counselor.avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
            </div>
            <h3>{{ counselor.name }}</h3>
            <div class="counselor-rating">
              <el-rate v-model="counselor.rating" disabled show-score text-color="#ff9900" />
            </div>
            <p class="counselor-specialty">
              擅长: {{ counselor.specialties?.join('、') }}
            </p>
            <div class="counselor-price">
              <span class="price">¥{{ counselor.price }}</span>
              <span class="unit">/小时</span>
            </div>
            <el-button type="primary" @click="bookCounselor(counselor.id)">预约</el-button>
          </div>
        </div>
      </div>
    </section>

    <!-- 平台数据 -->
    <section class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div v-for="stat in platformStats" :key="stat.id" class="stat-item">
            <div class="stat-icon" :style="{ background: stat.color }">
              <el-icon :size="32">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-content">
              <h3>{{ formatNumber(stat.value) }}</h3>
              <p>{{ stat.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="page-footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h4>关于我们</h4>
            <p>心理咨询平台致力于为用户提供专业的心理健康服务</p>
          </div>
          <div class="footer-section">
            <h4>快速链接</h4>
            <ul>
              <li><a href="/chat">智能问答</a></li>
              <li><a href="/test">心理测试</a></li>
              <li><a href="/counselor">找咨询师</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h4>联系我们</h4>
            <p>邮箱: support@soulstation.com</p>
            <p>电话: 400-123-4567</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© 2026 心理咨询平台 - 关注心理健康</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, ChatDotSquare, Document, Calendar, DataAnalysis, TrendCharts } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'

const router = useRouter()

// 加载状态
const loadingKnowledge = ref(true)
const loadingCounselors = ref(true)

// 轮播图数据
const carouselItems = ref([
  {
    title: '关注心理健康',
    subtitle: '从这里开始，探索内心世界',
    image: 'https://images.unsplash.com/photo-1499209974431-2761b8c71e43?w=1200',
    path: '/chat'
  },
  {
    title: '专业心理测试',
    subtitle: '科学评估，了解真实的自己',
    image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200',
    path: '/test'
  },
  {
    title: '预约专业咨询师',
    subtitle: '一对一服务，解决心理困扰',
    image: 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=1200',
    path: '/counselor'
  }
])

// 功能导航数据
const features = ref([
  {
    id: 1,
    title: '智能问答',
    description: '24h在线，AI心理咨询助手',
    icon: ChatDotSquare,
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    path: '/chat'
  },
  {
    id: 2,
    title: '心理测试',
    description: '专业评估，科学分析',
    icon: Document,
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    path: '/test'
  },
  {
    id: 3,
    title: '预约咨询',
    description: '专家团队，贴心服务',
    icon: Calendar,
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    path: '/counselor'
  },
  {
    id: 4,
    title: '心理知识',
    description: '科普文章，助您成长',
    icon: DataAnalysis,
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    path: '/knowledge'
  }
])

// 热门文章（模拟数据）
const hotArticles = ref([
  {
    id: 1,
    title: '如何缓解焦虑情绪 - 实用技巧分享',
    category: '焦虑症',
    views: 1234,
    coverImage: 'https://images.unsplash.com/photo-1499209974431-2761b8c71e43?w=400'
  },
  {
    id: 2,
    title: '抑郁症的早期信号与自我调节',
    category: '抑郁症',
    views: 980,
    coverImage: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400'
  },
  {
    id: 3,
    title: '职场压力管理技巧',
    category: '职场',
    views: 856,
    coverImage: 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400'
  },
  {
    id: 4,
    title: '改善睡眠质量的科学方法',
    category: '健康',
    views: 723,
    coverImage: 'https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=400'
  }
])

// 推荐咨询师（模拟数据）
const recommendedCounselors = ref([
  {
    id: 1,
    name: '张老师',
    avatar: 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=200',
    rating: 4.9,
    specialties: ['焦虑', '抑郁', '情感'],
    price: 300
  },
  {
    id: 2,
    name: '李老师',
    avatar: 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=200',
    rating: 4.8,
    specialties: ['职场', '家庭', '情感'],
    price: 500
  },
  {
    id: 3,
    name: '王老师',
    avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=200',
    rating: 4.9,
    specialties: ['情感', '婚姻', '亲子'],
    price: 400
  },
  {
    id: 4,
    name: '赵老师',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200',
    rating: 4.7,
    specialties: ['学业', '职业', '社交'],
    price: 350
  }
])

// 平台数据
const platformStats = ref([
  { id: 1, label: '用户数', value: 1234, icon: User, color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { id: 2, label: '咨询师', value: 89, icon: Calendar, color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { id: 3, label: '服务次数', value: 2567, icon: TrendCharts, color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { id: 4, label: '满意度', value: 98, icon: DataAnalysis, color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', suffix: '%' }
])

// 格式化数字
const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

// 导航到指定路径
const navigateTo = (path) => {
  router.push(path)
}

// 轮播图点击处理
const handleCarouselClick = (item) => {
  if (item.path) {
    navigateTo(item.path)
  }
}

// 查看文章详情
const viewArticle = (id) => {
  router.push(`/knowledge/${id}`)
}

// 预约咨询师
const bookCounselor = (id) => {
  router.push(`/counselor/${id}`)
}

// 加载数据
onMounted(() => {
  // 模拟数据加载
  setTimeout(() => {
    loadingKnowledge.value = false
    loadingCounselors.value = false
  }, 1000)
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.home-page {
  min-height: 100vh;
  background: $bg-color;
}

.hero-section {
  padding: $spacing-lg 0;
}

.carousel-item {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.4);
  }
}

.carousel-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: white;

  h1 {
    font-size: 48px;
    margin-bottom: $spacing-md;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }

  p {
    font-size: $font-size-large;
    margin-bottom: $spacing-lg;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
}

.features-section {
  padding: $spacing-xl 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-lg;
}

.feature-card {
  background: $bg-white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  text-align: center;
  cursor: pointer;
  transition: $transition-base;
  box-shadow: $box-shadow-base;

  &:hover {
    transform: translateY(-8px);
    box-shadow: $box-shadow-dark;
  }

  .feature-icon {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto $spacing-md;
    color: white;
  }

  h3 {
    font-size: $font-size-large;
    margin-bottom: $spacing-sm;
    color: $text-primary;
  }

  p {
    color: $text-secondary;
    margin-bottom: $spacing-md;
  }

  .feature-link {
    color: $primary-color;
    font-weight: 500;
  }
}

.knowledge-section,
.counselor-section {
  padding: $spacing-xl 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;

  h2 {
    font-size: $font-size-extra-large;
    color: $text-primary;
    font-weight: 600;
  }
}

.knowledge-grid,
.counselor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: $spacing-lg;
}

.knowledge-card {
  background: $bg-white;
  border-radius: $border-radius-md;
  overflow: hidden;
  cursor: pointer;
  transition: $transition-base;
  box-shadow: $box-shadow-base;

  &:hover {
    transform: translateY(-4px);
    box-shadow: $box-shadow-dark;
  }

  .article-cover {
    width: 100%;
    height: 160px;
    overflow: hidden;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: $transition-base;

      &:hover {
        transform: scale(1.05);
      }
    }
  }

  .article-info {
    padding: $spacing-md;

    h3 {
      font-size: $font-size-base;
      color: $text-primary;
      margin-bottom: $spacing-sm;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .article-meta {
      display: flex;
      justify-content: space-between;
      font-size: $font-size-small;
      color: $text-secondary;
    }
  }
}

.counselor-card {
  background: $bg-white;
  border-radius: $border-radius-md;
  padding: $spacing-lg;
  text-align: center;
  transition: $transition-base;
  box-shadow: $box-shadow-base;

  &:hover {
    box-shadow: $box-shadow-dark;
  }

  .counselor-avatar {
    margin-bottom: $spacing-md;
  }

  h3 {
    font-size: $font-size-large;
    color: $text-primary;
    margin-bottom: $spacing-sm;
  }

  .counselor-specialty {
    color: $text-secondary;
    font-size: $font-size-small;
    margin: $spacing-sm 0;
  }

  .counselor-price {
    margin: $spacing-md 0;

    .price {
      font-size: $font-size-extra-large;
      color: $primary-color;
      font-weight: 600;
    }

    .unit {
      font-size: $font-size-small;
      color: $text-secondary;
    }
  }
}

.stats-section {
  padding: $spacing-xl 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-lg;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;

  .stat-icon {
    width: 64px;
    height: 64px;
    border-radius: $border-radius-md;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.2);
  }

  .stat-content {
    h3 {
      font-size: $font-size-extra-large;
      font-weight: 600;
      margin-bottom: $spacing-xs;
    }

    p {
      font-size: $font-size-base;
      opacity: 0.9;
    }
  }
}

.page-footer {
  background: #2c3e50;
  color: white;
  padding: $spacing-xl 0 $spacing-lg;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-xl;
  margin-bottom: $spacing-lg;
}

.footer-section {
  h4 {
    font-size: $font-size-large;
    margin-bottom: $spacing-md;
  }

  p {
    font-size: $font-size-base;
    opacity: 0.8;
    line-height: 1.8;
    margin-bottom: $spacing-sm;
  }

  ul {
    list-style: none;
    padding: 0;

    li {
      margin-bottom: $spacing-sm;

      a {
        color: rgba(255, 255, 255, 0.8);
        text-decoration: none;
        transition: $transition-base;

        &:hover {
          color: white;
        }
      }
    }
  }
}

.footer-bottom {
  text-align: center;
  padding-top: $spacing-lg;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  opacity: 0.8;
}

// 响应式
@media (max-width: $breakpoint-md) {
  .carousel-content h1 {
    font-size: 32px;
  }

  .features-grid,
  .knowledge-grid,
  .counselor-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: $breakpoint-sm) {
  .carousel-content h1 {
    font-size: 24px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>

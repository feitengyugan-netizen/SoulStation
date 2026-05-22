<template>
  <div class="article-editor">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
      <h2>{{ isEdit ? '编辑文章' : '新建文章' }}</h2>
      <div class="header-actions">
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveArticle">保存</el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="文章标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入文章标题" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="文章分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 200px">
            <el-option label="焦虑抑郁" value="anxiety" />
            <el-option label="人际关系" value="relationship" />
            <el-option label="职业发展" value="career" />
            <el-option label="家庭婚姻" value="family" />
            <el-option label="个人成长" value="growth" />
            <el-option label="情绪管理" value="emotion" />
            <el-option label="心理咨询" value="counseling" />
            <el-option label="正念冥想" value="meditation" />
            <el-option label="压力管理" value="stress" />
            <el-option label="睡眠健康" value="health" />
            <el-option label="创伤治疗" value="depression" />
          </el-select>
        </el-form-item>

        <el-form-item label="文章摘要">
          <el-input
            v-model="form.summary"
            type="textarea"
            :rows="3"
            placeholder="请输入文章摘要（选填）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="文章内容" prop="content">
          <div class="editor-container">
            <div class="editor-toolbar">
              <el-button-group>
                <el-button size="small" @click="insertFormat('bold')"><b>B</b></el-button>
                <el-button size="small" @click="insertFormat('italic')"><i>I</i></el-button>
              </el-button-group>
              <el-button-group style="margin-left: 10px">
                <el-button size="small" @click="insertFormat('h2')">H2</el-button>
                <el-button size="small" @click="insertFormat('h3')">H3</el-button>
              </el-button-group>
              <el-button-group style="margin-left: 10px">
                <el-button size="small" @click="insertList('ul')">列表</el-button>
              </el-button-group>
            </div>
            <el-input
              ref="editorRef"
              v-model="form.content"
              type="textarea"
              :rows="20"
              placeholder="支持 Markdown 格式，也可以使用上方工具栏插入格式..."
            />
          </div>
        </el-form-item>

        <el-form-item label="发布设置">
          <el-checkbox v-model="form.published">立即发布</el-checkbox>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { saveKnowledgeArticle } from '@/api/admin'
import { getKnowledgeDetail } from '@/api/knowledge'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const editorRef = ref(null)

const isEdit = !!route.params.id
const loading = ref(false)
const saving = ref(false)

const form = reactive({
  id: route.params.id || '',
  title: '',
  category: '',
  summary: '',
  content: '',
  published: true,
  top: false
})

const rules = {
  title: [{ required: true, message: '请输入文章标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择文章分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入文章内容', trigger: 'blur' }]
}

const loadArticle = async () => {
  if (!isEdit) return
  try {
    loading.value = true
    const res = await getKnowledgeDetail(route.params.id)
    Object.assign(form, res.data)
  } finally {
    loading.value = false
  }
}

const insertFormat = (type) => {
  const formats = {
    bold: '**粗体**',
    italic: '*斜体*',
    underline: '~~下划线~~',
    h2: '## 标题2',
    h3: '### 标题3'
  }
  insertText(formats[type] || '')
}

const insertList = (type) => {
  const text = type === 'ul' ? '- 列表项' : '1. 列表项'
  insertText(text)
}

const insertText = (text) => {
  const textarea = editorRef.value?.textarea || editorRef.value?.$el?.querySelector('textarea')
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const value = form.content

  form.content = value.substring(0, start) + text + value.substring(end)

  setTimeout(() => {
    textarea.focus()
    textarea.selectionStart = textarea.selectionEnd = start + text.length
  }, 0)
}

const saveArticle = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    saving.value = true

    // 转换表单数据以匹配后端 API
    const articleData = {
      id: form.id || undefined,
      title: form.title,
      category: form.category,
      content: form.content,
      summary: form.summary || undefined,
      content_type: 'markdown',
      status: form.published ? 'published' : 'draft'
    }

    await saveKnowledgeArticle(articleData)
    ElMessage.success(isEdit ? '更新成功' : '创建成功')
    goBack()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.push('/admin/knowledge')
}

onMounted(() => loadArticle())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;
.article-editor { padding: $spacing-lg; }
.page-header { display: flex; align-items: center; gap: $spacing-lg; margin-bottom: $spacing-lg; }
.page-header h2 { flex: 1; margin: 0; }
.header-actions { display: flex; gap: $spacing-sm; }

.editor-container { width: 100%; }
.editor-toolbar { display: flex; align-items: center; padding: $spacing-sm; background: #f5f7fa; border: 1px solid $border-color; border-bottom: none; border-radius: $border-radius $border-radius 0 0; }
:deep(.el-textarea__inner) { border-radius: 0 0 $border-radius $border-radius; }
</style>

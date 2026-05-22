// 用户状态检查工具
// 在浏览器控制台中粘贴并运行此代码来检查用户登录状态

function checkUserStatus() {
  console.log('=== 用户状态检查 ===')

  // 检查 sessionStorage
  const token = sessionStorage.getItem('token')
  const userInfo = sessionStorage.getItem('userInfo')

  console.log('1. sessionStorage 状态:')
  console.log('  token:', token ? '存在' : '不存在')
  console.log('  userInfo:', userInfo ? '存在' : '不存在')

  if (userInfo) {
    try {
      const parsedUserInfo = JSON.parse(userInfo)
      console.log('  解析后的用户信息:', parsedUserInfo)
      console.log('  用户ID:', parsedUserInfo.id)
    } catch (e) {
      console.error('  userInfo 解析失败:', e)
    }
  } else {
    console.warn('⚠️ 用户未登录或登录状态丢失')
  }

  // 检查 Pinia store (如果可用)
  try {
    const userStore = window.pinia?.state?.value?.user
    if (userStore) {
      console.log('2. Pinia Store 状态:')
      console.log('  token:', userStore.token)
      console.log('  userInfo:', userStore.userInfo)
      console.log('  isLoggedIn:', userStore.isLoggedIn)
    }
  } catch (e) {
    console.log('2. Pinia Store: 无法访问')
  }

  console.log('===================')
  return {
    hasToken: !!token,
    hasUserInfo: !!userInfo,
    userInfo: userInfo ? JSON.parse(userInfo) : null
  }
}

// 运行检查
checkUserStatus()

/**
 * 日期格式化工具函数
 */

/**
 * 格式化日期时间
 * @param {string|Date} date - 日期
 * @param {string} format - 格式化模式
 * @returns {string} 格式化后的日期字符串
 */
export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return '-'
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期
 * @param {string|Date} date - 日期
 * @param {string} format - 格式化模式
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  return formatDateTime(date, format)
}

/**
 * 格式化时间
 * @param {string|Date} date - 日期
 * @param {string} format - 格式化模式
 * @returns {string} 格式化后的时间字符串
 */
export function formatTime(date, format = 'HH:mm:ss') {
  return formatDateTime(date, format)
}

/**
 * 获取相对时间描述
 * @param {string|Date} date - 日期
 * @returns {string} 相对时间描述
 */
export function getRelativeTime(date) {
  if (!date) return '-'
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return '-'
  
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const months = Math.floor(days / 30)
  const years = Math.floor(days / 365)
  
  if (years > 0) {
    return `${years}年前`
  } else if (months > 0) {
    return `${months}个月前`
  } else if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else if (seconds > 0) {
    return `${seconds}秒前`
  } else {
    return '刚刚'
  }
}

/**
 * 计算日期差值（天数）
 * @param {string|Date} startDate - 开始日期
 * @param {string|Date} endDate - 结束日期
 * @returns {number} 天数差值
 */
export function getDaysDiff(startDate, endDate) {
  if (!startDate || !endDate) return 0
  
  const start = new Date(startDate)
  const end = new Date(endDate)
  
  if (isNaN(start.getTime()) || isNaN(end.getTime())) return 0
  
  const diff = end.getTime() - start.getTime()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}

/**
 * 计算距离今天的天数
 * @param {string|Date} date - 日期
 * @returns {number} 天数（正数表示未来，负数表示过去）
 */
export function getDaysFromToday(date) {
  if (!date) return 0
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return 0
  
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  d.setHours(0, 0, 0, 0)
  
  const diff = d.getTime() - today.getTime()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}

/**
 * 判断日期是否为今天
 * @param {string|Date} date - 日期
 * @returns {boolean} 是否为今天
 */
export function isToday(date) {
  if (!date) return false
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return false
  
  const today = new Date()
  return d.toDateString() === today.toDateString()
}

/**
 * 判断日期是否为昨天
 * @param {string|Date} date - 日期
 * @returns {boolean} 是否为昨天
 */
export function isYesterday(date) {
  if (!date) return false
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return false
  
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  return d.toDateString() === yesterday.toDateString()
}

/**
 * 判断日期是否为本周
 * @param {string|Date} date - 日期
 * @returns {boolean} 是否为本周
 */
export function isThisWeek(date) {
  if (!date) return false
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return false
  
  const today = new Date()
  const startOfWeek = new Date(today)
  startOfWeek.setDate(today.getDate() - today.getDay())
  startOfWeek.setHours(0, 0, 0, 0)
  
  const endOfWeek = new Date(startOfWeek)
  endOfWeek.setDate(startOfWeek.getDate() + 6)
  endOfWeek.setHours(23, 59, 59, 999)
  
  return d >= startOfWeek && d <= endOfWeek
}

/**
 * 判断日期是否为本月
 * @param {string|Date} date - 日期
 * @returns {boolean} 是否为本月
 */
export function isThisMonth(date) {
  if (!date) return false
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return false
  
  const today = new Date()
  return d.getFullYear() === today.getFullYear() && d.getMonth() === today.getMonth()
}

/**
 * 判断日期是否为本年
 * @param {string|Date} date - 日期
 * @returns {boolean} 是否为本年
 */
export function isThisYear(date) {
  if (!date) return false
  
  const d = new Date(date)
  if (isNaN(d.getTime())) return false
  
  const today = new Date()
  return d.getFullYear() === today.getFullYear()
}

/**
 * 获取日期范围描述
 * @param {string|Date} startDate - 开始日期
 * @param {string|Date} endDate - 结束日期
 * @returns {string} 日期范围描述
 */
export function getDateRangeText(startDate, endDate) {
  if (!startDate && !endDate) return '-'
  if (!startDate) return `截止到 ${formatDate(endDate)}`
  if (!endDate) return `从 ${formatDate(startDate)} 开始`
  
  const start = formatDate(startDate)
  const end = formatDate(endDate)
  
  if (start === end) {
    return start
  }
  
  return `${start} ~ ${end}`
}

/**
 * 获取月份名称
 * @param {number} month - 月份（0-11）
 * @param {boolean} short - 是否使用简写
 * @returns {string} 月份名称
 */
export function getMonthName(month, short = false) {
  const months = short
    ? ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    : ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
  
  return months[month] || ''
}

/**
 * 获取星期名称
 * @param {number} day - 星期（0-6，0为周日）
 * @param {boolean} short - 是否使用简写
 * @returns {string} 星期名称
 */
export function getDayName(day, short = false) {
  const days = short
    ? ['日', '一', '二', '三', '四', '五', '六']
    : ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  
  return days[day] || ''
}

/**
 * 验证日期格式
 * @param {string} dateString - 日期字符串
 * @param {string} format - 期望的格式
 * @returns {boolean} 是否符合格式
 */
export function validateDateFormat(dateString, format = 'YYYY-MM-DD') {
  if (!dateString) return false
  
  // 简单的格式验证
  if (format === 'YYYY-MM-DD') {
    const regex = /^\d{4}-\d{2}-\d{2}$/
    if (!regex.test(dateString)) return false
  } else if (format === 'YYYY-MM-DD HH:mm:ss') {
    const regex = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/
    if (!regex.test(dateString)) return false
  }
  
  // 验证日期是否有效
  const date = new Date(dateString)
  return !isNaN(date.getTime())
}

/**
 * 获取当前时间戳
 * @returns {number} 时间戳
 */
export function getCurrentTimestamp() {
  return Date.now()
}

/**
 * 时间戳转日期
 * @param {number} timestamp - 时间戳
 * @param {string} format - 格式化模式
 * @returns {string} 格式化后的日期字符串
 */
export function timestampToDate(timestamp, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!timestamp) return '-'
  
  const date = new Date(timestamp)
  return formatDateTime(date, format)
}

/**
 * 日期转时间戳
 * @param {string|Date} date - 日期
 * @returns {number} 时间戳
 */
export function dateToTimestamp(date) {
  if (!date) return 0
  
  const d = new Date(date)
  return isNaN(d.getTime()) ? 0 : d.getTime()
}

export default {
  formatDateTime,
  formatDate,
  formatTime,
  getRelativeTime,
  getDaysDiff,
  getDaysFromToday,
  isToday,
  isYesterday,
  isThisWeek,
  isThisMonth,
  isThisYear,
  getDateRangeText,
  getMonthName,
  getDayName,
  validateDateFormat,
  getCurrentTimestamp,
  timestampToDate,
  dateToTimestamp
}
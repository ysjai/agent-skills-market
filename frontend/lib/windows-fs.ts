/**
 * Windows文件系统工具模块
 * 提供Windows文件名验证和清理功能
 */

/** Windows保留字符正则表达式 */
export const WINDOWS_RESERVED_CHARS = /[<>:"|?*\x00-\x1f]/g;

/**
 * 检查文件名是否包含Windows保留字符
 * @param fileName 文件名
 * @returns 是否包含保留字符
 */
export function hasWindowsReservedChars(fileName: string): boolean {
  return WINDOWS_RESERVED_CHARS.test(fileName);
}

/**
 * 获取文件名中的Windows保留字符列表
 * @param fileName 文件名
 * @returns 保留字符数组（去重）
 */
export function getWindowsReservedChars(fileName: string): string[] {
  const matches = fileName.match(WINDOWS_RESERVED_CHARS);
  return matches ? [...new Set(matches)] : [];
}

/**
 * 清理文件名，移除Windows保留字符
 * @param fileName 原始文件名
 * @returns 清理后的文件名
 */
export function sanitizeFileName(fileName: string): string {
  return fileName
    .replace(/[<>:"|?*\x00-\x1f]/g, '_')
    .replace(/\.{2,}/g, '_')
    .replace(/[\s.]+$/, '')
    .trim() || 'unnamed';
}

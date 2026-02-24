/**
 * Tailwind CSS classes for Markdown rendering typography.
 * These styles provide consistent formatting for rendered markdown content.
 */
export const MARKDOWN_TYPOGRAPHY_STYLES = `
  [&>h1]:text-3xl [&>h1]:font-bold [&>h1]:text-gray-900 [&>h1]:mb-6 [&>h1]:pb-3 [&>h1]:border-b [&>h1]:border-gray-200
  [&>h2]:text-xl [&>h2]:font-semibold [&>h2]:text-gray-800 [&>h2]:mt-8 [&>h2]:mb-4 [&>h2]:flex [&>h2]:items-center [&>h2]:gap-2
  [&>h3]:text-lg [&>h3]:font-semibold [&>h3]:text-gray-800 [&>h3]:mt-6 [&>h3]:mb-3
  [&>h4]:text-base [&>h4]:font-semibold [&>h4]:text-gray-800 [&>h4]:mt-5 [&>h4]:mb-2
  [&>p]:text-gray-700 [&>p]:leading-relaxed [&>p]:mb-4 [&>p]:text-[15px]
  [&>p>strong]:text-gray-900 [&>p>strong]:font-semibold
  [&>ul]:list-disc [&>ul]:pl-6 [&>ul]:mb-4 [&>ul]:space-y-2
  [&>ol]:list-decimal [&>ol]:pl-6 [&>ol]:mb-4 [&>ol]:space-y-2
  [&>ul>li]:text-gray-700 [&>ul>li]:leading-relaxed [&>ul>li]:text-[15px]
  [&>ol>li]:text-gray-700 [&>ol>li]:leading-relaxed [&>ol>li]:text-[15px]
  [&>ul>li>strong]:text-gray-900 [&>ul>li>strong]:font-semibold
  [&>ol>li>strong]:text-gray-900 [&>ol>li>strong]:font-semibold
  [&>blockquote]:border-l-4 [&>blockquote]:border-indigo-400 [&>blockquote]:pl-4 [&>blockquote]:py-1 [&>blockquote]:my-6 [&>blockquote]:bg-indigo-50/50 [&>blockquote]:italic [&>blockquote]:text-gray-700 [&>blockquote]:rounded-r-md
  [&>pre]:bg-gray-900 [&>pre]:text-gray-100 [&>pre]:p-4 [&>pre]:rounded-lg [&>pre]:overflow-x-auto [&>pre]:my-4 [&>pre]:text-sm [&>pre]:leading-relaxed [&>pre]:font-mono [&>pre]:shadow-inner
  [&>p>code]:bg-gray-100 [&>p>code]:text-indigo-600 [&>p>code]:px-1.5 [&>p>code]:py-0.5 [&>p>code]:rounded [&>p>code]:text-sm [&>p>code]:font-mono [&>p>code]:border [&>p>code]:border-gray-200
  [&>ul>li>code]:bg-gray-100 [&>ul>li>code]:text-indigo-600 [&>ul>li>code]:px-1.5 [&>ul>li>code]:py-0.5 [&>ul>li>code]:rounded [&>ul>li>code]:text-sm [&>ul>li>code]:font-mono
  [&>a]:text-indigo-600 [&>a]:underline [&>a]:underline-offset-2 [&>a]:hover:text-indigo-800 [&>a]:transition-colors
  [&>hr]:border-gray-200 [&>hr]:my-8
  [&>table]:w-full [&>table]:border-collapse [&>table]:my-4 [&>table]:text-sm
  [&>table>thead>tr]:border-b [&>table>thead>tr]:border-gray-300
  [&>table>thead>tr>th]:py-2 [&>table>thead>tr>th]:px-3 [&>table>thead>tr>th]:text-left [&>table>thead>tr>th]:font-semibold [&>table>thead>tr>th]:text-gray-700
  [&>table>tbody>tr]:border-b [&>table>tbody>tr]:border-gray-100 [&>table>tbody>tr:last-child]:border-0
  [&>table>tbody>tr>td]:py-2 [&>table>tbody>tr>td]:px-3 [&>table>tbody>tr>td]:text-gray-600
`;

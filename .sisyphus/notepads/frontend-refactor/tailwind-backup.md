# Tailwind Config Backup

Original file: `frontend/tailwind.config.ts`

## Complete Theme Configuration

### Colors

#### Primary (Purple)
```
primary-50:  #f5f3ff
primary-100: #ede9fe
primary-200: #ddd6fe
primary-300: #c4b5fd
primary-400: #a78bfa
primary-500: #8b5cf6
primary-600: #7c3aed
primary-700: #6d28d9
primary-800: #5b21b6
primary-900: #4c1d95
```

#### Gray
```
gray-50:  #fafafa
gray-100: #f4f4f5
gray-200: #e4e4e7
gray-300: #d4d4d8
gray-400: #a1a1aa
gray-500: #71717a
gray-600: #52525b
gray-700: #3f3f46
gray-800: #27272a
gray-900: #18181b
```

#### Semantic Colors
```
success: #22c55e
warning: #f59e0b
error:   #ef4444
info:    #3b82f6
```

### Font Family

```
sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif']
mono: ['JetBrains Mono', 'Fira Code', 'SF Mono', 'monospace']
```

### Spacing

```
spacing-18: 4.5rem
```

### Border Radius

```
radius-sm:  0.375rem
radius-md:  0.5rem
radius-lg:  0.75rem
radius-xl:  1rem
radius-2xl: 1.5rem
```

### Box Shadow

```
shadow-glow: 0 0 20px rgba(139, 92, 246, 0.3)
```

### Animations

```
animation-slide-in: slideIn 0.3s ease
animation-fade-in:  fadeIn 0.2s ease-out
```

### Keyframes

```css
@keyframes slideIn {
  0% { transform: translateX(100%); opacity: 0; }
  100% { transform: translateX(0); opacity: 1; }
}

@keyframes fadeIn {
  0% { opacity: 0; transform: translateY(8px); }
  100% { opacity: 1; transform: translateY(0); }
}
```

### Content Paths

```
./app/**/*.{js,ts,jsx,tsx,mdx}
./components/**/*.{js,ts,jsx,tsx,mdx}
```

### Dark Mode

```
darkMode: 'class'
```

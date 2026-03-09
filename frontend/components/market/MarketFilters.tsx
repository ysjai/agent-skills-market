'use client';

import { Search } from 'lucide-react';
import { useTranslations } from 'next-intl';

interface MarketFiltersProps {
  filters: { keyword: string; category_id: string; sort_by: string };
  categories: Array<{ id: string; name: string }>;
  onFilterChange: (filters: Partial<{ keyword: string; category_id: string; sort_by: string }>) => void;
}

export function MarketFilters({ filters, categories, onFilterChange }: MarketFiltersProps) {
  const t = useTranslations('market');

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-6">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder={t('search_placeholder')}
          value={filters.keyword}
          onChange={(e) => onFilterChange({ keyword: e.target.value })}
          className="w-full rounded-lg border border-gray-200 bg-white pl-10 pr-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <select
          value={filters.category_id}
          onChange={(e) => onFilterChange({ category_id: e.target.value })}
          className="rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-700 focus:border-indigo-500 focus:outline-none"
        >
          <option value="">--- {t('filter_all_categories')} ---</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>

        <select
          value={filters.sort_by}
          onChange={(e) => onFilterChange({ sort_by: e.target.value })}
          className="rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-700 focus:border-indigo-500 focus:outline-none"
        >
          <option value="newest">{t('sort_newest')}</option>
          <option value="popular">{t('sort_popular')}</option>
        </select>
      </div>
    </div>
  );
}

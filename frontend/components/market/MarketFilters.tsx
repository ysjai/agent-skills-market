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
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6">
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder={t('search_placeholder')}
          value={filters.keyword}
          onChange={(e) => onFilterChange({ keyword: e.target.value })}
          className="w-full rounded-lg border-gray-300 pl-10 pr-4 py-2 text-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
      </div>

      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <select
          value={filters.category_id}
          onChange={(e) => onFilterChange({ category_id: e.target.value })}
          className="rounded-lg border-gray-300 py-2 pl-3 pr-8 text-sm focus:border-indigo-500 focus:ring-indigo-500 bg-white"
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
          className="rounded-lg border-gray-300 py-2 pl-3 pr-8 text-sm focus:border-indigo-500 focus:ring-indigo-500 bg-white"
        >
          <option value="newest">{t('sort_newest')}</option>
          <option value="popular">{t('sort_popular')}</option>
        </select>
      </div>
    </div>
  );
}

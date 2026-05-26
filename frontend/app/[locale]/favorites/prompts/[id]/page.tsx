'use client';

import { use } from 'react';

import { SharedPromptDetail } from '@/components/market/SharedPromptDetail';

export default function FavoritePromptDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <SharedPromptDetail id={id} backPath="/favorites" backLabelKey="back_to_favorites" />;
}

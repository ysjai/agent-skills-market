'use client';

import { use } from 'react';
import { SharedPromptDetail } from '@/components/market/SharedPromptDetail';

export default function MarketPromptDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <SharedPromptDetail id={id} backPath="/market" backLabelKey="back_to_market" />;
}

'use client';

import { use } from 'react';
import { SharedPromptDetail } from '@/components/market/SharedPromptDetail';

export default function PlazaPromptDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <SharedPromptDetail id={id} backPath="/plaza/prompts" backLabelKey="back_to_plaza" />;
}

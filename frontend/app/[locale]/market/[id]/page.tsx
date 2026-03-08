'use client';

import { use } from 'react';
import { SharedSkillDetail } from '@/components/market/SharedSkillDetail';

export default function MarketSkillDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  return <SharedSkillDetail id={id} backPath="/market" backLabelKey="back_to_market" />;
}

'use client';

import { use } from 'react';

import { SharedSkillDetail } from '@/components/market/SharedSkillDetail';

export default function PlazaSkillDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  return <SharedSkillDetail id={id} backPath="/plaza/skills" backLabelKey="back_to_plaza" />;
}

'use client';

import { use } from 'react';
import { SharedSkillDetail } from '@/components/market/SharedSkillDetail';

export default function FavoriteSkillDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  return <SharedSkillDetail id={id} backPath="/favorites" backLabelKey="back_to_favorites" />;
}

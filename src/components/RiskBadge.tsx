import { Badge } from '@/components/ui/badge';
import { AlertCircle, AlertTriangle, CheckCircle } from 'lucide-react';

interface RiskBadgeProps {
  level: 'high' | 'medium' | 'low';
  score?: number;
  showIcon?: boolean;
  className?: string;
}

export function RiskBadge({ level, score, showIcon = true, className = '' }: RiskBadgeProps) {
  const config = {
    high: {
      variant: 'destructive' as const,
      icon: AlertCircle,
      label: 'High Risk',
      color: 'text-red-600'
    },
    medium: {
      variant: 'default' as const,
      icon: AlertTriangle,
      label: 'Medium Risk',
      color: 'text-amber-600'
    },
    low: {
      variant: 'secondary' as const,
      icon: CheckCircle,
      label: 'Low Risk',
      color: 'text-green-600'
    }
  };

  const { variant, icon: Icon, label, color } = config[level];

  return (
    <Badge variant={variant} className={`gap-1 ${className}`}>
      {showIcon && <Icon className="h-3 w-3" />}
      {label}
      {score !== undefined && ` (${score})`}
    </Badge>
  );
}

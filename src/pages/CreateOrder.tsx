import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { RiskBadge } from '@/components/RiskBadge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Loader2, 
  Package, 
  Building2, 
  Truck, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle,
  Shield,
  Scale,
  ArrowRight
} from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

interface EntityRiskSummary {
  name: string;
  country: string;
  entity_type: string;
  risk_level: 'high' | 'medium' | 'low';
  risk_score: number;
  is_blacklisted: boolean;
  flags: string[];
  news_summary: string | null;
}

interface OrderAssessmentResponse {
  order_id: string;
  overall_risk_level: 'high' | 'medium' | 'low';
  overall_risk_score: number;
  requires_approval: boolean;
  approval_status: 'pending_approval' | 'auto_approved' | 'approved' | 'rejected';
  shipper_assessment: EntityRiskSummary;
  buyer_assessment: EntityRiskSummary;
  flags: string[];
  recommendations: string[];
  ai_summary: string;
}

const countries = [
  'China', 'Pakistan', 'Japan', 'Germany', 'USA', 'India', 'Vietnam', 
  'Nigeria', 'Colombia', 'Mexico', 'Brazil', 'Panama', 'Taiwan', 'South Korea', 'Other'
];

const commodities = [
  'Soccer Balls', 'Auto Parts', 'Electronics', 'Textiles', 'Machinery', 
  'Hibiscus Flowers', 'Toys', 'Consumer Electronics', 'Chemicals', 'Other'
];

export default function CreateOrder() {
  const [formData, setFormData] = useState({
    shipper_name: '',
    shipper_country: '',
    buyer_name: '',
    buyer_country: 'Mexico',
    commodity: '',
    origin: '',
    value: '',
    order_reference: ''
  });

  const [isChecking, setIsChecking] = useState(false);
  const [checkStep, setCheckStep] = useState(0);
  const [assessment, setAssessment] = useState<OrderAssessmentResponse | null>(null);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCreateOrder = async () => {
    setIsChecking(true);
    setCheckStep(1);
    setAssessment(null);

    try {
      // Simulate step progression for UX
      const stepInterval = setInterval(() => {
        setCheckStep(prev => Math.min(prev + 1, 3));
      }, 2000);

      const orderData = {
        shipper_name: formData.shipper_name,
        shipper_country: formData.shipper_country,
        buyer_name: formData.buyer_name,
        buyer_country: formData.buyer_country,
        commodity: formData.commodity,
        origin: formData.origin,
        value: formData.value ? parseFloat(formData.value) : undefined,
        order_reference: formData.order_reference || undefined,
      };

      const response = await fetch('/api/orders/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData),
      });

      clearInterval(stepInterval);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.details || 'Order pre-check failed');
      }

      const result = await response.json();
      setAssessment(result);
      
      if (result.requires_approval) {
        toast.warning('Order requires approval', {
          description: 'Risk factors detected - manual review required',
        });
      } else {
        toast.success('Order cleared', {
          description: 'No significant risk factors detected',
        });
      }
    } catch (error) {
      console.error('Order pre-check error:', error);
      toast.error('Pre-check failed', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
      });
    } finally {
      setIsChecking(false);
      setCheckStep(0);
    }
  };

  const handleApprove = () => {
    toast.success('Order approved', {
      description: 'Order has been approved and can proceed',
    });
  };

  const handleReject = () => {
    toast.error('Order rejected', {
      description: 'Order has been rejected',
    });
  };

  const handleEscalate = () => {
    toast.info('Escalated to Legal', {
      description: 'Order has been sent to legal department for review',
    });
  };

  const isFormValid = 
    formData.shipper_name && 
    formData.shipper_country && 
    formData.buyer_name && 
    formData.buyer_country &&
    formData.commodity && 
    formData.origin;

  const renderEntityCard = (entity: EntityRiskSummary, icon: React.ReactNode, title: string) => (
    <Card className={entity.is_blacklisted ? 'border-red-500 border-2' : ''}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            {icon}
            {title}
          </CardTitle>
          <RiskBadge level={entity.risk_level} score={entity.risk_score} />
        </div>
        <CardDescription>{entity.name} • {entity.country}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {entity.is_blacklisted && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertTitle>Blacklisted</AlertTitle>
            <AlertDescription>This entity is on the 60B tax blacklist</AlertDescription>
          </Alert>
        )}
        
        {entity.flags.length > 0 && (
          <div>
            <p className="text-sm font-medium mb-2">Risk Flags ({entity.flags.length})</p>
            <div className="space-y-1">
              {entity.flags.slice(0, 3).map((flag, idx) => (
                <div key={idx} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <AlertTriangle className="h-3 w-3 mt-1 text-amber-500 shrink-0" />
                  <span>{flag}</span>
                </div>
              ))}
              {entity.flags.length > 3 && (
                <p className="text-xs text-muted-foreground">+{entity.flags.length - 3} more flags</p>
              )}
            </div>
          </div>
        )}

        {entity.news_summary && (
          <div>
            <p className="text-sm font-medium mb-1">Recent News</p>
            <p className="text-xs text-muted-foreground">{entity.news_summary}</p>
          </div>
        )}

        {entity.flags.length === 0 && !entity.is_blacklisted && (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle2 className="h-4 w-4" />
            <span className="text-sm">No significant issues found</span>
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl" data-page="create-order">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-2">Create Order</h1>
          <p className="text-muted-foreground">
            Enter order details for automated risk pre-check on both parties
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Order Form */}
          <Card data-section="order-form">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5" />
                Order Details
              </CardTitle>
              <CardDescription>Enter shipper, buyer, and order information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Shipper Section */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-sm font-semibold text-muted-foreground">
                  <Truck className="h-4 w-4" />
                  SHIPPER (SELLER)
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="shipper_name">Company Name *</Label>
                    <Input
                      id="shipper_name"
                      placeholder="e.g., Global Trade Corp"
                      value={formData.shipper_name}
                      onChange={(e) => handleInputChange('shipper_name', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="shipper_country">Country *</Label>
                    <Select value={formData.shipper_country} onValueChange={(value) => handleInputChange('shipper_country', value)}>
                      <SelectTrigger id="shipper_country">
                        <SelectValue placeholder="Select country" />
                      </SelectTrigger>
                      <SelectContent>
                        {countries.map(country => (
                          <SelectItem key={country} value={country}>{country}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Buyer Section */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-sm font-semibold text-muted-foreground">
                  <Building2 className="h-4 w-4" />
                  BUYER (IMPORTER)
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="buyer_name">Company Name *</Label>
                    <Input
                      id="buyer_name"
                      placeholder="e.g., Mexico Imports SA"
                      value={formData.buyer_name}
                      onChange={(e) => handleInputChange('buyer_name', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="buyer_country">Country *</Label>
                    <Select value={formData.buyer_country} onValueChange={(value) => handleInputChange('buyer_country', value)}>
                      <SelectTrigger id="buyer_country">
                        <SelectValue placeholder="Select country" />
                      </SelectTrigger>
                      <SelectContent>
                        {countries.map(country => (
                          <SelectItem key={country} value={country}>{country}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Order Details Section */}
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-sm font-semibold text-muted-foreground">
                  <Package className="h-4 w-4" />
                  ORDER INFORMATION
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="commodity">Commodity *</Label>
                    <Select value={formData.commodity} onValueChange={(value) => handleInputChange('commodity', value)}>
                      <SelectTrigger id="commodity">
                        <SelectValue placeholder="Select commodity" />
                      </SelectTrigger>
                      <SelectContent>
                        {commodities.map(commodity => (
                          <SelectItem key={commodity} value={commodity}>{commodity}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="origin">Origin Country *</Label>
                    <Select value={formData.origin} onValueChange={(value) => handleInputChange('origin', value)}>
                      <SelectTrigger id="origin">
                        <SelectValue placeholder="Select origin" />
                      </SelectTrigger>
                      <SelectContent>
                        {countries.map(country => (
                          <SelectItem key={country} value={country}>{country}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="value">Value (USD)</Label>
                    <Input
                      id="value"
                      type="number"
                      placeholder="50000"
                      value={formData.value}
                      onChange={(e) => handleInputChange('value', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="order_reference">Order Reference</Label>
                    <Input
                      id="order_reference"
                      placeholder="e.g., PO-2024-001"
                      value={formData.order_reference}
                      onChange={(e) => handleInputChange('order_reference', e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <Button
                onClick={handleCreateOrder}
                disabled={!isFormValid || isChecking}
                className="w-full"
                size="lg"
              >
                {isChecking ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Running Pre-Check...
                  </>
                ) : (
                  <>
                    <Shield className="mr-2 h-4 w-4" />
                    Create Order with Pre-Check
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Results Section */}
          <div className="space-y-4">
            {isChecking && (
              <Card data-section="checking">
                <CardContent className="p-8">
                  <div className="flex flex-col items-center justify-center text-center space-y-6">
                    <div className="rounded-full bg-primary/10 p-4">
                      <Shield className="h-8 w-8 text-primary animate-pulse" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg mb-4">Pre-Check in Progress</h3>
                      <div className="space-y-3 text-sm">
                        <div className={`flex items-center gap-2 justify-center ${checkStep >= 1 ? 'text-foreground' : 'text-muted-foreground'}`}>
                          {checkStep >= 1 ? <CheckCircle2 className="h-4 w-4 text-green-600" /> : <Loader2 className="h-4 w-4 animate-spin" />}
                          <span>Checking shipper against blacklists...</span>
                        </div>
                        <div className={`flex items-center gap-2 justify-center ${checkStep >= 2 ? 'text-foreground' : 'text-muted-foreground'}`}>
                          {checkStep >= 2 ? <CheckCircle2 className="h-4 w-4 text-green-600" /> : checkStep === 1 ? <Loader2 className="h-4 w-4 animate-spin" /> : <div className="h-4 w-4" />}
                          <span>Checking buyer against blacklists...</span>
                        </div>
                        <div className={`flex items-center gap-2 justify-center ${checkStep >= 3 ? 'text-foreground' : 'text-muted-foreground'}`}>
                          {checkStep >= 3 ? <CheckCircle2 className="h-4 w-4 text-green-600" /> : checkStep === 2 ? <Loader2 className="h-4 w-4 animate-spin" /> : <div className="h-4 w-4" />}
                          <span>Analyzing risk factors with AI...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {assessment && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
                data-section="assessment-results"
              >
                {/* Overall Status Card */}
                <Card className={assessment.requires_approval ? 'border-amber-500 border-2' : 'border-green-500 border-2'}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          {assessment.requires_approval ? (
                            <AlertTriangle className="h-5 w-5 text-amber-500" />
                          ) : (
                            <CheckCircle2 className="h-5 w-5 text-green-500" />
                          )}
                          Order {assessment.order_id}
                        </CardTitle>
                        <CardDescription>
                          {assessment.requires_approval 
                            ? 'This order requires manual approval' 
                            : 'Order cleared - no significant risks detected'}
                        </CardDescription>
                      </div>
                      <RiskBadge level={assessment.overall_risk_level} score={assessment.overall_risk_score} />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2 mb-4">
                      <Badge variant={assessment.approval_status === 'auto_approved' ? 'secondary' : 'outline'}>
                        {assessment.approval_status.replace('_', ' ').toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{assessment.ai_summary}</p>
                  </CardContent>
                </Card>

                {/* Entity Assessments */}
                <div className="grid gap-4 md:grid-cols-2">
                  {renderEntityCard(
                    assessment.shipper_assessment, 
                    <Truck className="h-4 w-4" />, 
                    'Shipper'
                  )}
                  {renderEntityCard(
                    assessment.buyer_assessment, 
                    <Building2 className="h-4 w-4" />, 
                    'Buyer'
                  )}
                </div>

                {/* Recommendations */}
                {assessment.recommendations.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center gap-2">
                        <Scale className="h-5 w-5" />
                        Recommendations
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {assessment.recommendations.map((rec, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-sm">
                            <ArrowRight className="h-4 w-4 mt-0.5 text-primary shrink-0" />
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Approval Actions */}
                {assessment.requires_approval ? (
                  <Card className="bg-amber-50 dark:bg-amber-900/10">
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-amber-500" />
                        Approval Required
                      </CardTitle>
                      <CardDescription>
                        This order has been flagged and requires manual review before proceeding
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-3">
                        <Button onClick={handleApprove} className="gap-2">
                          <CheckCircle2 className="h-4 w-4" />
                          Approve Order
                        </Button>
                        <Button variant="destructive" onClick={handleReject} className="gap-2">
                          <XCircle className="h-4 w-4" />
                          Reject Order
                        </Button>
                        <Button variant="outline" onClick={handleEscalate} className="gap-2">
                          <Scale className="h-4 w-4" />
                          Escalate to Legal
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <Card className="bg-green-50 dark:bg-green-900/10">
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                        Order Cleared
                      </CardTitle>
                      <CardDescription>
                        No significant risk factors detected - order can proceed
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <Button className="gap-2">
                        <ArrowRight className="h-4 w-4" />
                        Proceed with Order
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </motion.div>
            )}

            {!assessment && !isChecking && (
              <Card className="h-[400px]">
                <CardContent className="h-full flex items-center justify-center">
                  <div className="text-center text-muted-foreground space-y-4">
                    <Shield className="h-16 w-16 mx-auto opacity-20" />
                    <div>
                      <p className="font-medium">Automated Pre-Check</p>
                      <p className="text-sm">Fill in order details to run risk assessment on both shipper and buyer</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}


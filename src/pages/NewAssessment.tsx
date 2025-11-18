import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { RiskBadge } from '@/components/RiskBadge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Brain, CheckCircle2, AlertTriangle, FileText } from 'lucide-react';
import { motion } from 'framer-motion';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';

export default function NewAssessment() {
  const [formData, setFormData] = useState({
    shipper: '',
    importer: '',
    manufacturer: '',
    commodity: '',
    origin: '',
    destination: '',
    value: '',
    weight: '',
    hsCode: '',
    notes: ''
  });

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [assessment, setAssessment] = useState<{
    riskLevel: 'high' | 'medium' | 'low';
    riskScore: number;
    flags: string[];
    entityChecks: Record<string, string>;
    recommendations: string[];
    patternAnalysis: string;
    aiInsights: string;
  } | null>(null);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAssess = async () => {
    setIsAnalyzing(true);
    setAssessment(null);

    try {
      // Prepare shipment data for API
      const shipmentData = {
        shipper: formData.shipper,
        importer: formData.importer,
        manufacturer: formData.manufacturer || undefined,
        commodity: formData.commodity,
        origin: formData.origin,
        destination: formData.destination || undefined,
        value: formData.value ? parseFloat(formData.value) : undefined,
        weight: formData.weight ? parseFloat(formData.weight) : undefined,
        hsCode: formData.hsCode || undefined,
        notes: formData.notes || undefined,
      };

      const response = await fetch('/api/assess', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(shipmentData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.details || 'Assessment failed');
      }

      const result = await response.json();
      setAssessment(result);
    } catch (error) {
      console.error('Assessment error:', error);
      toast.error('Failed to assess shipment', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const isFormValid = formData.shipper && formData.importer && formData.commodity && formData.origin;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl" data-page="new-assessment">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-2">New Shipment Assessment</h1>
          <p className="text-muted-foreground">
            Enter shipment details for AI-powered risk analysis
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Input Form */}
          <Card data-section="assessment-form">
            <CardHeader>
              <CardTitle>Shipment Information</CardTitle>
              <CardDescription>Complete all required fields for analysis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="shipper">Shipper Name *</Label>
                <Input
                  id="shipper"
                  placeholder="e.g., Global Trade Corp"
                  value={formData.shipper}
                  onChange={(e) => handleInputChange('shipper', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="importer">Importer Name *</Label>
                <Input
                  id="importer"
                  placeholder="e.g., Mexico Imports SA"
                  value={formData.importer}
                  onChange={(e) => handleInputChange('importer', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="manufacturer">Manufacturer</Label>
                <Input
                  id="manufacturer"
                  placeholder="e.g., Factory Name"
                  value={formData.manufacturer}
                  onChange={(e) => handleInputChange('manufacturer', e.target.value)}
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="commodity">Commodity *</Label>
                  <Select value={formData.commodity} onValueChange={(value) => handleInputChange('commodity', value)}>
                    <SelectTrigger id="commodity">
                      <SelectValue placeholder="Select commodity" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Soccer Balls">Soccer Balls</SelectItem>
                      <SelectItem value="Auto Parts">Auto Parts</SelectItem>
                      <SelectItem value="Electronics">Electronics</SelectItem>
                      <SelectItem value="Textiles">Textiles</SelectItem>
                      <SelectItem value="Machinery">Machinery</SelectItem>
                      <SelectItem value="Hibiscus Flowers">Hibiscus Flowers</SelectItem>
                      <SelectItem value="Toys">Toys</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="origin">Country of Origin *</Label>
                  <Select value={formData.origin} onValueChange={(value) => handleInputChange('origin', value)}>
                    <SelectTrigger id="origin">
                      <SelectValue placeholder="Select country" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="China">China</SelectItem>
                      <SelectItem value="Pakistan">Pakistan</SelectItem>
                      <SelectItem value="Japan">Japan</SelectItem>
                      <SelectItem value="Germany">Germany</SelectItem>
                      <SelectItem value="USA">USA</SelectItem>
                      <SelectItem value="India">India</SelectItem>
                      <SelectItem value="Vietnam">Vietnam</SelectItem>
                      <SelectItem value="Nigeria">Nigeria</SelectItem>
                      <SelectItem value="Colombia">Colombia</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="value">Declared Value (USD)</Label>
                  <Input
                    id="value"
                    type="number"
                    placeholder="50000"
                    value={formData.value}
                    onChange={(e) => handleInputChange('value', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="weight">Weight (kg)</Label>
                  <Input
                    id="weight"
                    type="number"
                    placeholder="1000"
                    value={formData.weight}
                    onChange={(e) => handleInputChange('weight', e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="hsCode">HS Code</Label>
                <Input
                  id="hsCode"
                  placeholder="e.g., 8703.23.10"
                  value={formData.hsCode}
                  onChange={(e) => handleInputChange('hsCode', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Additional Notes</Label>
                <Textarea
                  id="notes"
                  placeholder="Any additional information about this shipment..."
                  rows={3}
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                />
              </div>

              <Button
                onClick={handleAssess}
                disabled={!isFormValid || isAnalyzing}
                className="w-full"
                size="lg"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing with AI...
                  </>
                ) : (
                  <>
                    <Brain className="mr-2 h-4 w-4" />
                    Run Risk Assessment
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Assessment Results */}
          <div className="space-y-4">
            {isAnalyzing && (
              <Card data-section="analyzing">
                <CardContent className="p-8">
                  <div className="flex flex-col items-center justify-center text-center space-y-4">
                    <div className="rounded-full bg-primary/10 p-4">
                      <Brain className="h-8 w-8 text-primary animate-pulse" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg mb-2">AI Analysis in Progress</h3>
                      <div className="space-y-2 text-sm text-muted-foreground">
                        <p>✓ Checking government blacklists...</p>
                        <p>✓ Analyzing trading patterns...</p>
                        <p>✓ Searching for entity news...</p>
                        <p className="animate-pulse">⟳ Evaluating risk factors...</p>
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
                {/* Risk Score Card */}
                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>Risk Assessment Result</span>
                      <RiskBadge level={assessment.riskLevel} score={assessment.riskScore} />
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">AI Insights</h4>
                      <p className="text-sm text-muted-foreground">{assessment.aiInsights}</p>
                    </div>

                    <Separator />

                    <div>
                      <h4 className="font-semibold mb-2">Risk Flags Detected</h4>
                      <div className="space-y-2">
                        {assessment.flags.map((flag: string, idx: number) => (
                          <Alert key={idx} variant="destructive">
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>{flag}</AlertDescription>
                          </Alert>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Entity Checks */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Entity Verification</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {Object.entries(assessment.entityChecks).map(([entity, status]) => (
                      <div key={entity} className="flex items-start gap-3">
                        {(status as string).toLowerCase().includes('clean') ? (
                          <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                        ) : (
                          <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5" />
                        )}
                        <div>
                          <p className="font-medium capitalize">{entity}</p>
                          <p className="text-sm text-muted-foreground">{status as string}</p>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Pattern Analysis */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Pattern Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{assessment.patternAnalysis}</p>
                  </CardContent>
                </Card>

                {/* Recommendations */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      Recommended Actions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {assessment.recommendations.map((rec: string, idx: number) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <span className="text-primary mt-1">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                <div className="flex gap-2">
                  <Button variant="default" className="flex-1">
                    Approve Shipment
                  </Button>
                  <Button variant="destructive" className="flex-1">
                    Reject Shipment
                  </Button>
                </div>
              </motion.div>
            )}

            {!assessment && !isAnalyzing && (
              <Card>
                <CardContent className="p-8">
                  <div className="flex flex-col items-center justify-center text-center space-y-4 text-muted-foreground">
                    <Brain className="h-12 w-12 opacity-20" />
                    <p>Fill in the shipment details and click "Run Risk Assessment" to begin AI analysis</p>
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

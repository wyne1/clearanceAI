import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { RiskBadge } from '@/components/RiskBadge';
import { Badge } from '@/components/ui/badge';
import { Search, Building2, TrendingUp, AlertCircle, CheckCircle, XCircle, Newspaper, RefreshCw } from 'lucide-react';
import { mockEntities } from '@/lib/mockData';
import type { EntityProfile, NewsItem } from '@/lib/mockData';
import { motion } from 'framer-motion';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { toast } from 'sonner';

interface EntityResearchData {
  name: string;
  type: string;
  country?: string;
  riskLevel: 'high' | 'medium' | 'low';
  riskScore: number;
  blacklistStatus: {
    list60B: boolean;
    approvedManufacturer: boolean;
    otherFlags: string[];
  };
  newsItems: NewsItem[];
  tradingPatterns: Array<{
    commodity: string;
    frequency: number;
    lastShipment: string;
    normalOrigins: string[];
  }>;
}

export default function EntityIntelligence() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEntity, setSelectedEntity] = useState<EntityProfile | null>(null);
  const [researchData, setResearchData] = useState<EntityResearchData | null>(null);
  const [isResearching, setIsResearching] = useState(false);

  const filteredEntities = searchTerm
    ? mockEntities.filter(e =>
        e.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        e.country.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : mockEntities;

  const handleResearchEntity = async (entity: EntityProfile) => {
    setIsResearching(true);
    try {
      const response = await fetch('/api/entities/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: entity.name,
          type: entity.type,
          country: entity.country,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.details || 'Research failed');
      }

      const data = await response.json();
      setResearchData(data);
      toast.success('Entity research completed', {
        description: `Updated intelligence for ${entity.name}`,
      });
    } catch (error) {
      console.error('Entity research error:', error);
      toast.error('Failed to research entity', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
      });
    } finally {
      setIsResearching(false);
    }
  };

  // Use research data if available, otherwise use mock entity data
  const displayEntity = selectedEntity ? (researchData || selectedEntity) : null;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl" data-page="entity-intelligence">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-2">Entity Intelligence</h1>
          <p className="text-muted-foreground">
            Search and analyze shippers, importers, and manufacturers
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Search & Entity List */}
          <Card className="lg:col-span-1" data-section="entity-search">
            <CardHeader>
              <CardTitle>Search Entities</CardTitle>
              <CardDescription>Find companies in the database</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by name or country..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>

              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {filteredEntities.map((entity) => (
                  <button
                    key={entity.id}
                    onClick={() => setSelectedEntity(entity)}
                    className={`w-full text-left p-4 rounded-lg border transition-colors hover:bg-accent ${
                      selectedEntity?.id === entity.id ? 'bg-accent border-primary' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-muted-foreground" />
                        <span className="font-semibold text-sm">{entity.name}</span>
                      </div>
                      <RiskBadge level={entity.riskLevel} showIcon={false} />
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Badge variant="outline" className="text-xs">
                        {entity.type}
                      </Badge>
                      <span>{entity.country}</span>
                    </div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Entity Details */}
          <div className="lg:col-span-2 space-y-4">
            {selectedEntity ? (
              <motion.div
                key={selectedEntity.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
                data-section="entity-details"
              >
                {/* Overview */}
                <Card>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-2xl">{displayEntity.name}</CardTitle>
                        <CardDescription className="flex items-center gap-2 mt-2">
                          <Badge variant="outline">{displayEntity.type}</Badge>
                          <span>•</span>
                          <span>{displayEntity.country}</span>
                        </CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleResearchEntity(selectedEntity)}
                          disabled={isResearching}
                          className="gap-2"
                        >
                          <RefreshCw className={`h-4 w-4 ${isResearching ? 'animate-spin' : ''}`} />
                          {isResearching ? 'Researching...' : 'Research'}
                        </Button>
                        <RiskBadge 
                          level={displayEntity.riskLevel} 
                          score={'riskScore' in displayEntity ? displayEntity.riskScore : undefined} 
                        />
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {researchData ? (
                      <div className="text-sm text-muted-foreground">
                        <p>Data refreshed via AI research</p>
                      </div>
                    ) : 'registrationDate' in selectedEntity ? (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Registration Date</p>
                          <p className="font-medium">{new Date(selectedEntity.registrationDate).toLocaleDateString()}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Last Activity</p>
                          <p className="font-medium">{new Date(selectedEntity.lastActivity).toLocaleDateString()}</p>
                        </div>
                      </div>
                    ) : null}
                  </CardContent>
                </Card>

                {/* Blacklist Status */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertCircle className="h-5 w-5" />
                      Blacklist & Compliance Checks
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                      <div className="flex items-center gap-3">
                        {displayEntity.blacklistStatus.list60B ? (
                          <XCircle className="h-5 w-5 text-red-600" />
                        ) : (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        )}
                        <span className="font-medium">60B Tax List</span>
                      </div>
                      <Badge variant={displayEntity.blacklistStatus.list60B ? 'destructive' : 'secondary'}>
                        {displayEntity.blacklistStatus.list60B ? 'FLAGGED' : 'Clear'}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                      <div className="flex items-center gap-3">
                        {displayEntity.blacklistStatus.approvedManufacturer ? (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        ) : (
                          <AlertCircle className="h-5 w-5 text-amber-600" />
                        )}
                        <span className="font-medium">Approved Manufacturer</span>
                      </div>
                      <Badge variant={displayEntity.blacklistStatus.approvedManufacturer ? 'secondary' : 'outline'}>
                        {displayEntity.blacklistStatus.approvedManufacturer ? 'Verified' : 'Not Listed'}
                      </Badge>
                    </div>

                    {displayEntity.blacklistStatus.otherFlags.length > 0 && (
                      <>
                        <Separator />
                        <div>
                          <p className="text-sm font-medium mb-2">Other Flags</p>
                          <div className="space-y-2">
                            {displayEntity.blacklistStatus.otherFlags.map((flag, idx) => (
                              <Alert key={idx} variant="destructive">
                                <AlertCircle className="h-4 w-4" />
                                <AlertDescription>{flag}</AlertDescription>
                              </Alert>
                            ))}
                          </div>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>

                {/* News & Intelligence */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Newspaper className="h-5 w-5" />
                      News & Intelligence
                    </CardTitle>
                    <CardDescription>Recent news articles and mentions</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {displayEntity.newsItems.map((news: NewsItem, idx: number) => (
                      <div key={idx} className="border-l-4 border-muted pl-4 py-2">
                        <div className="flex items-start justify-between mb-1">
                          <h4 className="font-semibold text-sm">{news.headline}</h4>
                          <Badge
                            variant={
                              news.sentiment === 'negative'
                                ? 'destructive'
                                : news.sentiment === 'positive'
                                ? 'secondary'
                                : 'outline'
                            }
                            className="ml-2"
                          >
                            {news.sentiment}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground mb-2">
                          {news.source} • {new Date(news.date).toLocaleDateString()}
                        </p>
                        <p className="text-sm text-muted-foreground">{news.excerpt}</p>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Trading Patterns */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5" />
                      Trading Patterns
                    </CardTitle>
                    <CardDescription>Historical commodity analysis</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {displayEntity.tradingPatterns.map((pattern, idx) => (
                        <div key={idx} className="p-4 rounded-lg bg-muted/50">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold">{pattern.commodity}</span>
                            <Badge variant="outline">{pattern.frequency} shipments</Badge>
                          </div>
                          <div className="text-sm text-muted-foreground space-y-1">
                            <p>Last Shipment: {new Date(pattern.lastShipment).toLocaleDateString()}</p>
                            <p>Typical Origins: {pattern.normalOrigins.join(', ')}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ) : (
              <Card className="h-[600px]">
                <CardContent className="h-full flex items-center justify-center">
                  <div className="text-center text-muted-foreground space-y-4">
                    <Search className="h-16 w-16 mx-auto opacity-20" />
                    <p>Select an entity from the list to view detailed intelligence</p>
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
